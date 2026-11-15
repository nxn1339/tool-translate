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
PROJECTS_DIR = os.path.join(PROJECT_ROOT, "app", "projects")
os.makedirs(STORY_TEMP_DIR, exist_ok=True)
os.makedirs(PROJECTS_DIR, exist_ok=True)

# In-memory progress and verbose log storage for story tasks
story_tasks: Dict[str, Dict[str, Any]] = {}


def append_story_log(task_id: Optional[str], message: str, level: str = "INFO"):
    """Appends formatted timestamped log line to story task in-memory and disk."""
    if not task_id:
        return
    from datetime import datetime
    now_str = datetime.now().strftime("%H:%M:%S")
    clean_line = f"[{now_str}] [{level}] {message}"
    if task_id not in story_tasks:
        story_tasks[task_id] = {"status": "processing", "progress": 0, "logs": [], "message": message}
    if "logs" not in story_tasks[task_id]:
        story_tasks[task_id]["logs"] = []
    story_tasks[task_id]["logs"].append(clean_line)
    if len(story_tasks[task_id]["logs"]) > 400:
        story_tasks[task_id]["logs"] = story_tasks[task_id]["logs"][-400:]

    # Persist log to project directory if exists
    try:
        p_dir = os.path.join(PROJECTS_DIR, task_id)
        if os.path.isdir(p_dir):
            with open(os.path.join(p_dir, "project_logs.json"), "w", encoding="utf-8") as f:
                json.dump(story_tasks[task_id]["logs"], f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def get_story_task_status(task_id: str) -> Dict[str, Any]:
    """Returns real-time progress, message and logs for a story synthesis task."""
    task = story_tasks.get(task_id)
    if task:
        return task
    # Fallback to disk if project already completed
    p_dir = os.path.join(PROJECTS_DIR, task_id)
    if os.path.isdir(p_dir):
        logs = []
        logs_file = os.path.join(p_dir, "project_logs.json")
        if os.path.isfile(logs_file):
            try:
                with open(logs_file, "r", encoding="utf-8") as f:
                    logs = json.load(f)
            except Exception:
                pass
        mp3_file = os.path.join(p_dir, "final_story.mp3")
        srt_file = os.path.join(p_dir, "final_story.srt")
        if os.path.isfile(mp3_file):
            return {
                "status": "completed",
                "progress": 100,
                "message": "Đã hoàn tất bản thu âm!",
                "logs": logs,
                "result": {
                    "task_id": task_id,
                    "mp3_path": mp3_file,
                    "srt_path": srt_file
                }
            }
    return {
        "status": "not_found",
        "progress": 0,
        "message": "Không tìm thấy tác vụ.",
        "logs": []
    }


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
# 2. CHANNEL INTRO GENERATOR & PRESETS (ĐOẠN GIỚI THIỆU KÊNH)
# ==============================================================================

CHANNEL_INTRO_TEMPLATES = {
    "storytelling": "Chào mừng các bạn đã quay trở lại với {channel}. Hôm nay, hãy cùng lắng nghe và đắm chìm vào câu chuyện tiếp theo ngay sau đây.",
    "dramatic": "{channel} xin chào tất cả các bạn! Hôm nay chúng ta sẽ cùng bước vào một câu chuyện vô cùng kịch tính và khó đoán. Đừng quên bấm theo dõi kênh để không bỏ lỡ những diễn biến hấp dẫn nhất.",
    "review": "Xin chào các bạn, chào mừng đã đến với {channel}. Ngay sau đây, mình sẽ gửi tới các bạn bản tóm tắt trọn vẹn và cuốn hút nhất của câu chuyện này.",
    "short": "Chào mừng các bạn đến với kênh {channel}! Cùng theo dõi câu chuyện ngày hôm nay nhé."
}

SYSTEM_INTRO_PROMPT = """Bạn là biên kịch chuyên nghiệp chuyên tạo các câu mở đầu (intro hook) cho kênh YouTube/TikTok đọc truyện, tóm tắt phim và podcast.
Nhiệm vụ của bạn: Viết 1 đến 2 câu mở đầu (tối đa 40-50 từ) thật lôi cuốn, mượt mà và tự nhiên để người đọc AI phát âm.

YÊU CẦU BẮT BUỘC:
1. Phải nhắc đến tên kênh một cách tự nhiên ở đầu câu (ví dụ: "Chào mừng các bạn đã quay trở lại với kênh [Tên Kênh]...", "Kênh [Tên Kênh] xin chào các bạn...").
2. Tạo cảm giác tò mò, háo hức hoặc lắng đọng dẫn dắt mượt mà vào câu chuyện (dựa vào bối cảnh kịch bản được cung cấp).
3. KHÔNG thêm bất kỳ chú thích đạo diễn nào như [Nhạc nổi lên], (Cười)... CHỈ TRẢ VỀ ĐÚNG NỘI DUNG LỜI NÓI.
4. Ngắt câu rõ ràng bằng dấu chấm hoặc dấu phẩy để giọng đọc AI ngắt nghỉ chuẩn xác."""


def generate_channel_intro(
    channel_name: str = "Hạt Tiêu Vietsub",
    story_text: str = "",
    style: str = "storytelling"
) -> Dict[str, Any]:
    """
    Generates a personalized, engaging channel intro hook using Groq or Gemini.
    Falls back to curated templates if AI is unavailable or fails.
    """
    channel_name = channel_name.strip() or "Hạt Tiêu Vietsub"
    template_intro = CHANNEL_INTRO_TEMPLATES.get(
        style, CHANNEL_INTRO_TEMPLATES["storytelling"]
    ).format(channel=channel_name)

    # If story_text is empty or too short, directly return template
    if not story_text or len(story_text.strip()) < 15:
        return {
            "status": "ok",
            "intro_text": template_intro,
            "engine": "Preset Template",
            "channel_name": channel_name
        }

    settings = get_api_settings()
    groq_api_key = settings.get("groq_api_key", "").strip()
    gemini_api_key = settings.get("gemini_api_key", "").strip()

    if not groq_api_key and not gemini_api_key:
        return {
            "status": "ok",
            "intro_text": template_intro,
            "engine": "Preset Template (Chưa cấu hình API Key)",
            "channel_name": channel_name
        }

    sample_text = story_text.strip()[:800]
    user_prompt = (
        f"Tên kênh: {channel_name}\n"
        f"Phong cách mở đầu: {style}\n"
        f"Đoạn trích câu chuyện sẽ kể:\n\"\"\"{sample_text}\"\"\"\n\n"
        f"Hãy viết 1-2 câu mở đầu (intro hook) thật ấn tượng, chào khán giả và dẫn dắt người nghe vào câu chuyện:"
    )

    # 1. Try Groq
    if groq_api_key:
        groq_model = settings.get("groq_model", "llama-3.3-70b-versatile")
        try:
            req_data = {
                "model": groq_model,
                "messages": [
                    {"role": "system", "content": SYSTEM_INTRO_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 250
            }
            req = urllib.request.Request(
                "https://api.groq.com/openai/v1/chat/completions",
                data=json.dumps(req_data).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {groq_api_key}",
                    "Content-Type": "application/json"
                }
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                res_json = json.loads(resp.read().decode("utf-8"))
                intro_text = res_json["choices"][0]["message"]["content"].strip()
                intro_text = re.sub(r'^["\']|["\']$', '', intro_text).strip()
                return {
                    "status": "ok",
                    "intro_text": intro_text,
                    "engine": f"Groq ({groq_model})",
                    "channel_name": channel_name
                }
        except Exception as e:
            logger.warning(f"Groq intro generation failed: {e}")

    # 2. Try Gemini
    if gemini_api_key:
        gemini_model = settings.get("gemini_model", "gemini-2.5-flash")
        try:
            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{gemini_model}:generateContent?key={gemini_api_key}"
            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {"text": f"{SYSTEM_INTRO_PROMPT}\n\n{user_prompt}"}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 250
                }
            }
            req = urllib.request.Request(
                api_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                res_json = json.loads(resp.read().decode("utf-8"))
                candidates = res_json.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    intro_text = "".join([p.get("text", "") for p in parts]).strip()
                    intro_text = re.sub(r'^["\']|["\']$', '', intro_text).strip()
                    return {
                        "status": "ok",
                        "intro_text": intro_text,
                        "engine": f"Gemini ({gemini_model})",
                        "channel_name": channel_name
                    }
        except Exception as e:
            logger.warning(f"Gemini intro generation failed: {e}")

    return {
        "status": "ok",
        "intro_text": template_intro,
        "engine": "Preset Template (Fallback)",
        "channel_name": channel_name
    }


# ==============================================================================
# Legacy AI Story Rewriter (kept for backwards compatibility)
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
    Streams progress and verbose logs to story_tasks and project_logs.json.
    """
    if not text.strip():
        return {"status": "error", "message": "Nội dung kịch bản không được để trống."}

    if not task_id:
        task_id = f"story_{int(time.time())}"

    # Use persistent project dir if directory exists in PROJECTS_DIR
    proj_dir_candidate = os.path.join(PROJECTS_DIR, task_id)
    if os.path.isdir(proj_dir_candidate):
        task_dir = proj_dir_candidate
    else:
        task_dir = os.path.join(STORY_TEMP_DIR, task_id)
    os.makedirs(task_dir, exist_ok=True)

    if task_id not in story_tasks:
        story_tasks[task_id] = {
            "status": "processing",
            "progress": 5,
            "message": "Đang phân tích cấu trúc kịch bản...",
            "logs": []
        }

    append_story_log(task_id, f"Bắt đầu tác vụ tạo audio đọc truyện ({len(text)} ký tự)...", "INFO")

    voice_info = CAPCUT_VOICES.get(voice_key, CAPCUT_VOICES.get("capcut_cogaithoatngon"))
    voice_type = voice_info.get("voice_type", "BV074_streaming")
    resource_id = voice_info.get("resource_id")
    voice_name = voice_info.get("name", voice_key)

    sentences = split_story_sentences(text)
    if not sentences:
        append_story_log(task_id, "Lỗi: Không thể phân tích câu từ văn bản đã nhập.", "ERROR")
        if task_id in story_tasks:
            story_tasks[task_id]["status"] = "failed"
        return {"status": "error", "message": "Không thể phân tích câu từ văn bản đã nhập."}

    append_story_log(task_id, f"Phân tích kịch bản thành {len(sentences)} câu thoại ngắt nhịp tự nhiên.", "INFO")
    append_story_log(task_id, f"Sử dụng giọng đọc TikTok: '{voice_name}' (Voice code: {voice_type}).", "INFO")

    ffmpeg_path = get_ffmpeg_path()
    if not ffmpeg_path:
        append_story_log(task_id, "Lỗi: Không tìm thấy ffmpeg trên hệ thống.", "ERROR")
        if task_id in story_tasks:
            story_tasks[task_id]["status"] = "failed"
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
    append_story_log(task_id, f"Đã tạo đoạn ngắt lặng {pause_ms}ms ({silence_dur_sec:.2f}s) giữa các câu thoại.", "INFO")

    audio_segments = []
    srt_entries = []
    current_time_sec = 0.0
    total_sents = len(sentences)

    for i, item in enumerate(sentences):
        sent_id = item["id"]
        sent_text = item["text"]
        out_wav = os.path.join(task_dir, f"sent_{sent_id:04d}.wav")

        preview = (sent_text[:38] + "...") if len(sent_text) > 38 else sent_text
        append_story_log(task_id, f"[{i + 1}/{total_sents}] Đang đọc: \"{preview}\"...", "INFO")

        ok = await generate_capcut_tts(sent_text, voice_type, out_wav, resource_id=resource_id)
        if not ok or not os.path.exists(out_wav) or os.path.getsize(out_wav) < 500:
            append_story_log(task_id, f"[{i + 1}/{total_sents}] Cảnh báo: Lỗi API giọng đọc, chèn khoảng lặng dự phòng 0.5s.", "WARN")
            subprocess.run(
                [ffmpeg_path, "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", "0.5", out_wav],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        else:
            w_size = os.path.getsize(out_wav)
            duration = get_audio_duration(out_wav)
            append_story_log(task_id, f"[{i + 1}/{total_sents}] Hoàn tất câu ({duration:.1f}s, {w_size:,} bytes).", "SUCCESS")

        duration = get_audio_duration(out_wav)
        start_ts = format_srt_timestamp(current_time_sec)
        end_ts = format_srt_timestamp(current_time_sec + duration)

        srt_entries.append(f"{i + 1}\n{start_ts} --> {end_ts}\n{sent_text}\n")

        audio_segments.append(out_wav)
        audio_segments.append(silence_path)
        current_time_sec += duration + silence_dur_sec

        # Dynamic progress percentage
        pct = 10 + int(((i + 1) / total_sents) * 75)
        if task_id in story_tasks:
            story_tasks[task_id]["progress"] = pct
            story_tasks[task_id]["message"] = f"Đang tạo giọng đọc câu {i + 1}/{total_sents} ({pct}%)..."

    # Write concat list for ffmpeg
    concat_list_path = os.path.join(task_dir, "concat.txt")
    with open(concat_list_path, "w", encoding="utf-8") as f:
        for seg in audio_segments:
            escaped_seg = seg.replace("\\", "/")
            f.write(f"file '{escaped_seg}'\n")

    if task_id in story_tasks:
        story_tasks[task_id]["progress"] = 88
        story_tasks[task_id]["message"] = "Đang ghép nối toàn bộ các đoạn âm thanh bằng FFmpeg..."

    append_story_log(task_id, f"Đang ghép nối {len(audio_segments)} đoạn âm thanh và khoảng lặng (FFmpeg libmp3lame 192k)...", "INFO")

    # Output final MP3
    final_mp3_path = os.path.join(task_dir, "final_story.mp3")
    concat_cmd = [
        ffmpeg_path, "-y", "-f", "concat", "-safe", "0",
        "-i", concat_list_path,
        "-c:a", "libmp3lame", "-b:a", "192k",
        final_mp3_path
    ]
    subprocess.run(concat_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if task_id in story_tasks:
        story_tasks[task_id]["progress"] = 96
        story_tasks[task_id]["message"] = "Đang xuất file phụ đề SRT đồng bộ..."

    # Output final SRT
    final_srt_path = os.path.join(task_dir, "final_story.srt")
    with open(final_srt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_entries))

    append_story_log(task_id, f"Đã xuất file phụ đề đồng bộ SRT ({len(srt_entries)} dòng cue).", "INFO")

    if os.path.exists(final_mp3_path) and os.path.getsize(final_mp3_path) > 1000:
        mp3_size_mb = os.path.getsize(final_mp3_path) / (1024 * 1024)
        append_story_log(task_id, f"🎉 Hoàn thành toàn bộ! Thời lượng tổng: {round(current_time_sec, 2)}s (~{round(current_time_sec/60, 1)} phút), dung lượng: {mp3_size_mb:.2f} MB.", "SUCCESS")
        
        result_payload = {
            "status": "ok",
            "task_id": task_id,
            "total_sentences": len(sentences),
            "total_duration_sec": round(current_time_sec, 2),
            "mp3_path": final_mp3_path,
            "srt_path": final_srt_path,
            "voice_name": voice_name
        }

        if task_id in story_tasks:
            story_tasks[task_id]["progress"] = 100
            story_tasks[task_id]["status"] = "completed"
            story_tasks[task_id]["message"] = "Đã tạo thành công bản thu âm và phụ đề SRT!"
            story_tasks[task_id]["result"] = result_payload

        return result_payload
    else:
        append_story_log(task_id, "Lỗi: Không thể xuất file MP3 hoàn chỉnh qua FFmpeg.", "ERROR")
        if task_id in story_tasks:
            story_tasks[task_id]["status"] = "failed"
            story_tasks[task_id]["message"] = "Lỗi ghép nối âm thanh MP3 hoàn chỉnh."
        return {"status": "error", "message": "Lỗi ghép nối âm thanh MP3 hoàn chỉnh."}

