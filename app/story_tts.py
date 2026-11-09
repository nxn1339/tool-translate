import os
import re
import json
import time
import shutil
import logging
import asyncio
import subprocess
import urllib.request
import urllib.parse
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

from app.downloader import get_ffmpeg_path, get_ffprobe_path
from app.capcut_tts import CAPCUT_VOICES, generate_capcut_tts
from app.tts import get_audio_duration

# Base directory for story TTS temporary storage
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
STORY_TEMP_DIR = os.path.join(PROJECT_ROOT, "app", "temp", "story_tts")
os.makedirs(STORY_TEMP_DIR, exist_ok=True)


def get_api_settings() -> Dict[str, Any]:
    """Loads API keys and model configurations from settings.json or .env"""
    settings_path = os.path.join(PROJECT_ROOT, "app", "data", "settings.json")
    settings = {}
    if os.path.exists(settings_path):
        try:
            with open(settings_path, "r", encoding="utf-8") as f:
                settings = json.load(f)
        except Exception as e:
            logger.warning(f"Failed to read settings.json: {e}")
    
    # Environment variables fallback
    if not settings.get("groq_api_key"):
        settings["groq_api_key"] = os.environ.get("GROQ_API_KEY", "")
    if not settings.get("gemini_api_key"):
        settings["gemini_api_key"] = os.environ.get("GEMINI_API_KEY", "")
    return settings


# ==============================================================================
# 1. YOUTUBE TRANSCRIPT EXTRACTION
# ==============================================================================

def clean_vtt_text(vtt_content: str) -> str:
    """Extracts and deduplicates subtitle text from WebVTT format."""
    lines = vtt_content.splitlines()
    text_lines = []
    seen = set()

    for line in lines:
        line = line.strip()
        # Skip VTT headers, timestamps, and cue settings
        if not line or line.startswith("WEBVTT") or line.startswith("Kind:") or line.startswith("Language:"):
            continue
        if "-->" in line:
            continue
        if line.isdigit():
            continue
        # Remove tags like <c>, </c>, <00:00:01.000>
        cleaned = re.sub(r'<[^>]+>', '', line).strip()
        cleaned = re.sub(r'[\u200b-\u200f\ufeff]', '', cleaned)
        if cleaned and cleaned not in seen:
            text_lines.append(cleaned)
            seen.add(cleaned)

    # Join into coherent paragraphs
    result = " ".join(text_lines)
    result = re.sub(r'\s+', ' ', result).strip()
    return result


def parse_json3_subtitles(json_content: str) -> str:
    """Parses text from YouTube json3 timedtext format."""
    try:
        data = json.loads(json_content)
        events = data.get("events", [])
        text_parts = []
        for ev in events:
            segs = ev.get("segs", [])
            for s in segs:
                t = s.get("utf8", "").strip()
                if t and t != "\n":
                    text_parts.append(t)
        res = " ".join(text_parts)
        res = re.sub(r'\s+', ' ', res).strip()
        return res
    except Exception as e:
        logger.warning(f"Failed to parse json3 subtitles: {e}")
        return ""


def extract_youtube_transcript(url: str) -> Dict[str, Any]:
    """
    Extracts video title, channel, description, and available transcripts/subtitles
    using yt-dlp metadata extraction (download=False) and direct timedtext fetching.
    Avoids HTTP 429 rate limits by downloading only 1 targeted subtitle track.
    """
    import yt_dlp

    url = url.strip()
    if not url:
        return {"status": "error", "message": "URL không được để trống."}

    ydl_opts = {
        'skip_download': True,
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                return {"status": "error", "message": "Không tìm thấy thông tin video từ liên kết này."}

            title = info.get("title", "Video YouTube")
            channel = info.get("uploader", "Không rõ kênh")
            duration = info.get("duration", 0)
            description = info.get("description", "")

            subtitles = info.get("subtitles") or {}
            auto_subs = info.get("automatic_captions") or {}

            # Prioritize Vietnamese, then English, then original / other languages
            lang_priority = ["vi", "vi-orig", "vi-VN", "en", "en-orig", "en-US", "zh-Hans", "zh-Hant", "zh", "ja", "ko"]
            
            chosen_formats = None
            chosen_lang = ""

            # 1. Search manual subtitles first
            for lang in lang_priority:
                if lang in subtitles and subtitles[lang]:
                    chosen_formats = subtitles[lang]
                    chosen_lang = lang
                    break

            # 2. If not found in manual, check auto captions
            if not chosen_formats:
                for lang in lang_priority:
                    if lang in auto_subs and auto_subs[lang]:
                        chosen_formats = auto_subs[lang]
                        chosen_lang = lang
                        break

            # 3. Fallback to any available language track
            if not chosen_formats:
                if subtitles:
                    first_lang = list(subtitles.keys())[0]
                    chosen_formats = subtitles[first_lang]
                    chosen_lang = first_lang
                elif auto_subs:
                    first_lang = list(auto_subs.keys())[0]
                    chosen_formats = auto_subs[first_lang]
                    chosen_lang = first_lang

            transcript = ""
            if chosen_formats:
                # Prioritize json3 format, then vtt, then others
                fmt_priority = ["json3", "vtt", "srv3", "srv1", "ttml"]
                sorted_fmts = sorted(
                    chosen_formats,
                    key=lambda f: fmt_priority.index(f.get("ext", "")) if f.get("ext", "") in fmt_priority else 99
                )

                for fmt in sorted_fmts:
                    sub_url = fmt.get("url")
                    sub_ext = fmt.get("ext")
                    if not sub_url:
                        continue
                    try:
                        req = urllib.request.Request(
                            sub_url,
                            headers={
                                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                            }
                        )
                        with urllib.request.urlopen(req, timeout=15) as resp:
                            raw_content = resp.read().decode("utf-8", errors="ignore")
                            if sub_ext == "json3":
                                transcript = parse_json3_subtitles(raw_content)
                            else:
                                transcript = clean_vtt_text(raw_content)
                            if transcript:
                                break
                    except urllib.error.HTTPError as he:
                        logger.warning(f"HTTPError {he.code} fetching subtitle format {sub_ext}: {he}")
                        continue
                    except Exception as fe:
                        logger.warning(f"Error fetching subtitle format {sub_ext}: {fe}")
                        continue

            if transcript:
                return {
                    "status": "ok",
                    "title": title,
                    "channel": channel,
                    "duration": duration,
                    "transcript": transcript,
                    "has_subtitles": True,
                    "language": chosen_lang,
                    "word_count": len(transcript.split())
                }
            else:
                fallback_text = description[:1500].strip() if description else ""
                msg = (
                    "YouTube không cung cấp phụ đề có sẵn (hoặc giới hạn tải tự động). "
                    "Hệ thống đã tự động lấy mô tả của video để bạn xào nấu kịch bản."
                    if fallback_text
                    else "Video này không có phụ đề sẵn có. Bạn có thể tự dán nội dung kịch bản vào ô bên dưới."
                )
                return {
                    "status": "ok",
                    "title": title,
                    "channel": channel,
                    "duration": duration,
                    "transcript": fallback_text,
                    "has_subtitles": False,
                    "message": msg
                }
    except Exception as e:
        logger.error(f"Error extracting YouTube transcript: {e}")
        return {"status": "error", "message": f"Không thể lấy dữ liệu từ YouTube: {str(e)}"}


# ==============================================================================
# 2. AI STORY REWRITER (XÀO NẤU NỘI DUNG)
# ==============================================================================

STYLE_PROMPTS = {
    "storytelling": (
        "Phong cách KỂ CHUYỆN TRUYỀN CẢM: Hãy viết lại toàn bộ nội dung thành một kịch bản truyện hoặc kịch bản kể chuyện "
        "giàu cảm xúc, hành văn mượt mà, văn phong lôi cuốn người nghe. Chú trọng nhịp điệu kể, mở bài hấp dẫn, "
        "dẫn dắt các chi tiết mạch lạc và kết thúc lắng đọng."
    ),
    "review": (
        "Phong cách REVIEW TÓM TẮT KỊCH TÍNH: Hãy viết lại câu chuyện theo văn phong review phim/truyện cuốn hút, "
        "nhịp độ nhanh, dồn dập, giật gân. Làm nổi bật các nút thắt, cao trào và tình huống bất ngờ để người nghe "
        "không thể rời tai."
    ),
    "paraphrase": (
        "Phong cách VIẾT LẠI NÉ BẢN QUYỀN: Hãy diễn đạt lại toàn bộ ý chính bằng 100% câu từ mới, tránh trùng lặp "
        "với bản gốc nhưng giữ trọn vẹn diễn biến và cốt lõi của nội dung."
    )
}

SYSTEM_REWRITE_PROMPT = """Bạn là biên kịch chuyên nghiệp chuyên viết kịch bản đọc truyện, podcast và review cho các kênh YouTube/TikTok triệu view.
Nhiệm vụ của bạn: Viết lại (xào nấu) đoạn nội dung được cung cấp thành một kịch bản hoàn chỉnh, sẵn sàng đưa vào giọng đọc AI.

QUY TẮC BẮT BUỘC:
1. LỌC BỎ 100% các câu chào mời của YouTube/TikTok như: "Chào mừng các bạn đã quay trở lại kênh...", "Hãy nhấn like và subscribe...", "Để lại bình luận bên dưới...", "Được tài trợ bởi...".
2. Chỉ giữ lại phần cốt lõi của câu chuyện, tình tiết và diễn biến.
3. Câu văn phải tự nhiên, tròn vành rõ chữ, có ngắt câu mạch lạc để giọng đọc AI phát âm chuẩn xác nhất.
4. KHÔNG thêm bất kỳ chú thích đạo diễn nào như [Nhạc nền nổi lên], [Hình ảnh minh họa], (Cười lớn)... CHỈ TRẢ VỀ ĐÚNG LỜI ĐỌC CỦA KỊCH BẢN.
5. Giữ độ dài cân đối, không được cắt xén cụt lủn những chi tiết quan trọng."""


def rewrite_story_content(
    text: str,
    style: str = "storytelling",
    custom_instruction: str = ""
) -> Dict[str, Any]:
    """
    Rewrites story content using Groq (llama-3.3-70b-versatile) or Gemini fallback.
    """
    settings = get_api_settings()
    groq_api_key = settings.get("groq_api_key", "").strip()
    gemini_api_key = settings.get("gemini_api_key", "").strip()

    if not groq_api_key and not gemini_api_key:
        return {
            "status": "error",
            "message": "Chưa cấu hình API Key (Groq hoặc Gemini) trong Cài đặt API."
        }

    style_instruction = STYLE_PROMPTS.get(style, STYLE_PROMPTS["storytelling"])
    user_prompt = f"{style_instruction}\n"
    if custom_instruction:
        user_prompt += f"Yêu cầu bổ sung của tác giả: {custom_instruction}\n"
    user_prompt += f"\n--- NỘI DUNG GỐC CẦN XÀO NẤU ---\n{text}\n--- HẾT NỘI DUNG GỐC ---\n\nHãy viết lại bản kịch bản hoàn chỉnh:"

    # 1. Try Groq first
    if groq_api_key:
        groq_model = settings.get("groq_model", "llama-3.3-70b-versatile")
        try:
            req_data = {
                "model": groq_model,
                "messages": [
                    {"role": "system", "content": SYSTEM_REWRITE_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 4096
            }
            req = urllib.request.Request(
                "https://api.groq.com/openai/v1/chat/completions",
                data=json.dumps(req_data).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {groq_api_key}",
                    "Content-Type": "application/json"
                }
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                res_json = json.loads(resp.read().decode("utf-8"))
                rewritten_text = res_json["choices"][0]["message"]["content"].strip()
                return {
                    "status": "ok",
                    "engine": f"Groq ({groq_model})",
                    "rewritten_text": rewritten_text,
                    "word_count": len(rewritten_text.split())
                }
        except Exception as e:
            logger.warning(f"Groq rewrite failed, trying Gemini: {e}")

    # 2. Fallback to Gemini
    if gemini_api_key:
        gemini_model = settings.get("gemini_model", "gemini-2.5-flash")
        try:
            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{gemini_model}:generateContent?key={gemini_api_key}"
            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {"text": f"{SYSTEM_REWRITE_PROMPT}\n\n{user_prompt}"}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 4096
                }
            }
            req = urllib.request.Request(
                api_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                res_json = json.loads(resp.read().decode("utf-8"))
                candidates = res_json.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    rewritten_text = "".join([p.get("text", "") for p in parts]).strip()
                    return {
                        "status": "ok",
                        "engine": f"Gemini ({gemini_model})",
                        "rewritten_text": rewritten_text,
                        "word_count": len(rewritten_text.split())
                    }
        except Exception as e:
            logger.error(f"Gemini rewrite failed: {e}")

    return {"status": "error", "message": "Không thể kết nối đến AI để xào nấu kịch bản. Vui lòng kiểm tra lại API Key."}


# ==============================================================================
# 3. TEXT CHUNKING & AUDIO SYNTHESIS
# ==============================================================================

def split_story_sentences(text: str, max_chunk_len: int = 180) -> List[Dict[str, Any]]:
    """
    Splits text into sentences based on punctuation and pauses.
    Guarantees no sentence exceeds max_chunk_len characters for reliable TTS.
    """
    text = text.strip()
    text = re.sub(r'[\r\n]+', '\n', text)
    paragraphs = text.split('\n')

    sentences = []
    idx = 1

    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        
        # Split by sentence terminators: . ? ! … ;
        raw_chunks = re.split(r'([.?!…;]+)', p)
        cur_sentence = ""

        for part in raw_chunks:
            if not part:
                continue
            if re.match(r'^[.?!…;]+$', part):
                cur_sentence += part
                cleaned = cur_sentence.strip()
                if cleaned:
                    # Break long sentences at commas or conjunctions if too long
                    if len(cleaned) > max_chunk_len:
                        sub_parts = re.split(r'([,，:–—]+)', cleaned)
                        buf = ""
                        for sp in sub_parts:
                            if len(buf) + len(sp) > max_chunk_len and buf.strip():
                                sentences.append({"id": idx, "text": buf.strip(), "pause_after_ms": 350})
                                idx += 1
                                buf = sp
                            else:
                                buf += sp
                        if buf.strip():
                            sentences.append({"id": idx, "text": buf.strip(), "pause_after_ms": 400})
                            idx += 1
                    else:
                        sentences.append({"id": idx, "text": cleaned, "pause_after_ms": 400})
                        idx += 1
                cur_sentence = ""
            else:
                cur_sentence += part

        if cur_sentence.strip():
            sentences.append({"id": idx, "text": cur_sentence.strip(), "pause_after_ms": 600})
            idx += 1

    return sentences


def format_srt_timestamp(seconds: float) -> str:
    """Formats float seconds into SRT timestamp 00:00:00,000"""
    millis = int(round(seconds * 1000))
    hours = millis // 3600000
    millis %= 3600000
    minutes = millis // 60000
    millis %= 60000
    secs = millis // 1000
    msecs = millis % 1000
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{msecs:03d}"


async def synthesize_story_session(
    text: str,
    voice_key: str = "capcut_cogaithoatngon",
    pause_ms: int = 350,
    task_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Synthesizes full story audio using the selected TikTok female voice.
    Generates concatenated MP3 and synchronized SRT subtitle file.
    """
    if not text.strip():
        return {"status": "error", "message": "Nội dung kịch bản không được để trống."}

    if not task_id:
        task_id = f"story_{int(time.time())}"

    task_dir = os.path.join(STORY_TEMP_DIR, task_id)
    os.makedirs(task_dir, exist_ok=True)

    voice_info = CAPCUT_VOICES.get(voice_key, CAPCUT_VOICES.get("capcut_cogaithoatngon"))
    voice_type = voice_info.get("voice_type", "BV074_streaming")
    resource_id = voice_info.get("resource_id")

    sentences = split_story_sentences(text)
    if not sentences:
        return {"status": "error", "message": "Không thể phân tích câu từ văn bản đã nhập."}

    ffmpeg_path = get_ffmpeg_path()
    if not ffmpeg_path:
        return {"status": "error", "message": "Không tìm thấy ffmpeg trên hệ thống."}

    # Create silence audio snippet
    silence_path = os.path.join(task_dir, "silence.wav")
    silence_dur_sec = max(0.1, pause_ms / 1000.0)
    subprocess.run(
        [
            ffmpeg_path, "-y", "-f", "lavfi",
            "-i", f"anullsrc=r=24000:cl=mono",
            "-t", f"{silence_dur_sec:.3f}",
            silence_path
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    audio_segments = []
    srt_entries = []
    current_time_sec = 0.0

    for i, item in enumerate(sentences):
        sent_id = item["id"]
        sent_text = item["text"]
        out_wav = os.path.join(task_dir, f"sent_{sent_id:04d}.wav")

        ok = await generate_capcut_tts(sent_text, voice_type, out_wav, resource_id=resource_id)
        if not ok or not os.path.exists(out_wav) or os.path.getsize(out_wav) < 500:
            # Fallback tiny silence if a line failed
            subprocess.run(
                [ffmpeg_path, "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", "0.5", out_wav],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

        duration = get_audio_duration(out_wav)
        start_ts = format_srt_timestamp(current_time_sec)
        end_ts = format_srt_timestamp(current_time_sec + duration)

        srt_entries.append(f"{i + 1}\n{start_ts} --> {end_ts}\n{sent_text}\n")

        audio_segments.append(out_wav)
        audio_segments.append(silence_path)
        current_time_sec += duration + silence_dur_sec

    # Write concat list for ffmpeg
    concat_list_path = os.path.join(task_dir, "concat.txt")
    with open(concat_list_path, "w", encoding="utf-8") as f:
        for seg in audio_segments:
            escaped_seg = seg.replace("\\", "/")
            f.write(f"file '{escaped_seg}'\n")

    # Output final MP3
    final_mp3_path = os.path.join(task_dir, "final_story.mp3")
    concat_cmd = [
        ffmpeg_path, "-y", "-f", "concat", "-safe", "0",
        "-i", concat_list_path,
        "-c:a", "libmp3lame", "-b:a", "192k",
        final_mp3_path
    ]
    subprocess.run(concat_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Output final SRT
    final_srt_path = os.path.join(task_dir, "final_story.srt")
    with open(final_srt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_entries))

    if os.path.exists(final_mp3_path) and os.path.getsize(final_mp3_path) > 1000:
        return {
            "status": "ok",
            "task_id": task_id,
            "total_sentences": len(sentences),
            "total_duration_sec": round(current_time_sec, 2),
            "mp3_path": final_mp3_path,
            "srt_path": final_srt_path,
            "voice_name": voice_info.get("name", voice_key)
        }
    else:
        return {"status": "error", "message": "Lỗi ghép nối âm thanh MP3 hoàn chỉnh."}

