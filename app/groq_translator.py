"""
Groq High-Speed AI Translation Engine for Subtitles & Dubbing.
Powered by Qwen 2.5/3.8 27B & GPT-OSS 120B via Groq Cloud API.
Features a 2-Step Architecture:
  Step 1: Pre-flight Story & Character Bible Reasoning (Genre, Pronouns, Character Dynamics)
  Step 2: Context-Aware, Duration-Constrained Dialogue Dubbing (Natural Voiceover Rhythm)
"""

import os
import re
import json
import time
import logging
import urllib.request
import urllib.parse
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"
FALLBACK_GROQ_MODELS = ["openai/gpt-oss-120b", "qwen/qwen3-32b"]


def analyze_story_context(
    all_texts: List[str],
    api_key: str,
    model_name: str = DEFAULT_GROQ_MODEL
) -> str:
    """
    Step 1: Analyzes sampled dialogue across the whole video to deduce the plot,
    main character roles, and consistent pronoun mapping for the entire video.
    """
    if not all_texts:
        return ""

    n = len(all_texts)
    sample_indices = []
    if n <= 70:
        sample_indices = list(range(n))
    else:
        sample_indices.extend(range(min(25, n)))
        step = max(1, (n - 45) // 25)
        sample_indices.extend(range(25, n - 20, step))
        sample_indices.extend(range(max(0, n - 20), n))

    sample_indices = sorted(list(set(sample_indices)))
    sampled_lines = "\n".join([f"- {all_texts[i].strip()}" for i in sample_indices if all_texts[i].strip()])

    glossary_hint_str = ""
    try:
        from app.hanviet import build_hanviet_glossary_hints
        hv_hints = build_hanviet_glossary_hints(all_texts, max_items=25)
        if hv_hints:
            glossary_hint_str = f"\nDanh sách âm Hán-Việt tham khảo cho các tên riêng xuất hiện trong kịch bản: {hv_hints}\n"
    except Exception:
        pass

    system_prompt = (
        "Bạn là đạo diễn phim và tổng biên kịch lồng tiếng phim truyện.\n"
        "Nhiệm vụ: Đọc các câu thoại tiêu biểu của một tập phim/video tiếng Trung dưới đây, "
        "suy luận cốt truyện và lập bản 'Hồ sơ nhân vật, Bảng tên chuẩn Hán-Việt & Quy tắc xưng hô' ngắn gọn, chính xác để đội ngũ dịch bám sát.\n"
        f"{glossary_hint_str}"
        "Hãy xác định rõ:\n"
        "1. Thể loại phim (Hào môn thế gia, Cung đấu, Ngôn tình hiện đại, Tu tiên...)\n"
        "2. Nhân vật chính người kể chuyện (Giới tính, vai trò: thiên kim thật, con gái ruột, tổng tài...)\n"
        "3. Bảng tên nhân vật chuẩn Hán-Việt (Ví dụ: 沈毅 = Thẩm Nghị, 苏晚晴 = Tô Vãn Tình, 赵睿 = Triệu Duệ... Chú ý nếu có ký tự OCR gần giống như 苏晚睛 thì chuẩn hóa về cùng 1 tên chuẩn Tô Vãn Tình).\n"
        "4. Bản đồ xưng hô cụ thể giữa các nhân vật (Với bố mẹ hào môn: con - bố/mẹ; Với thiên kim giả/anh chàng giả: tôi - anh/cô/cậu; Độc thoại: tôi...)\n"
        "5. Phong cách lời thoại (khẩu ngữ đời thường, ngắn gọn, hài hước, dứt khoát...)\n"
        "Trả về DUY NHẤT một JSON object: {\"story_summary\": \"...\", \"character_glossary\": \"...\", \"pronoun_rules\": \"...\", \"voiceover_tone\": \"...\"}"
    )

    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Dưới đây là các câu thoại mẫu trích từ video:\n{sampled_lines}"}
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"}
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key.strip()}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
    )

    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                if resp.status == 200:
                    res_body = json.loads(resp.read().decode("utf-8"))
                    raw = res_body["choices"][0]["message"]["content"].strip()
                    parsed = json.loads(raw)
                    parts = []
                    if "story_summary" in parsed:
                        parts.append(f"Cốt truyện: {parsed['story_summary']}")
                    if "character_glossary" in parsed:
                        parts.append(f"Tên nhân vật chuẩn Hán-Việt: {parsed['character_glossary']}")
                    if "pronoun_rules" in parsed:
                        parts.append(f"Xưng hô nhân vật: {parsed['pronoun_rules']}")
                    if "voiceover_tone" in parsed:
                        parts.append(f"Văn phong: {parsed['voiceover_tone']}")
                    if not parts and isinstance(parsed, dict):
                        parts = [f"{k}: {v}" for k, v in parsed.items()]
                    summary = " | ".join(parts)
                    logger.info(f"Story Bible generated successfully: {summary[:120]}...")
                    return summary
        except Exception as e:
            err = str(e)
            if "429" in err:
                time.sleep(5.0)
            else:
                time.sleep(1.5)

    return "Bối cảnh: Phim truyền hình / drama hào môn hiện đại. Xưng hô: con - mẹ/bố, tôi - anh/cậu. Khẩu ngữ tự nhiên."


def groq_translate_chunk(
    chunk_texts: List[str],
    api_key: str,
    model_name: str = DEFAULT_GROQ_MODEL,
    source_code: str = "zh-CN",
    target_code: str = "vi",
    story_context: Optional[str] = None,
    durations: Optional[List[float]] = None,
    prev_context_pairs: Optional[List[Tuple[str, str]]] = None
) -> Optional[List[str]]:
    """
    Translates a chunk of subtitle lines using Groq Chat Completions API with:
    - Injected Story Bible & Character Pronoun Mapping
    - Non-destructive Sino-Vietnamese Glossary Hints for proper names in this chunk
    - Sliding Context Window (previous lines) so split multi-segment sentences connect seamlessly
    - Duration-constrained Word Count Budget (Voiceover Pace)
    - Enforced strict JSON schema returning: {"translations": ["line 1", "line 2", ...]}.
    """
    if not chunk_texts:
        return []

    # Build numbered lines with duration constraints
    numbered_lines_list = []
    for i, line in enumerate(chunk_texts):
        dur = durations[i] if (durations and i < len(durations)) else 2.0
        # Voiceover pacing: ~3.8 - 4.2 words per second, floor at 8 words to prevent clipping natural dialogue
        max_words = max(8, int(dur * 4.2))
        numbered_lines_list.append(f"[{i + 1}] ({dur:.1f}s - tối đa ~{max_words} từ nếu câu dài): {line}")
    numbered_lines = "\n".join(numbered_lines_list)

    ctx_block = f"\nHỒ SƠ BỐI CẢNH & QUY TẮC XƯNG HÔ TOÀN BỘ PHIM:\n{story_context}\n" if story_context else ""

    chunk_hv_block = ""
    try:
        from app.hanviet import build_hanviet_glossary_hints
        chunk_hv = build_hanviet_glossary_hints(chunk_texts, max_items=20)
        if chunk_hv:
            chunk_hv_block = (
                f"\nBẢNG TRA CỨU ÂM HÁN-VIỆT CHO TÊN RIÊNG TRONG ĐOẠN NÀY (Chỉ dùng khi từ đó thực sự là tên người/địa danh trong ngữ cảnh, bỏ qua nếu là từ vựng thông thường):\n"
                f"{chunk_hv}\n"
            )
    except Exception:
        pass

    prev_ctx_block = ""
    if prev_context_pairs:
        prev_lines_str = "\n".join([f"  • {zh} => {vi}" for zh, vi in prev_context_pairs if zh and vi])
        if prev_lines_str:
            prev_ctx_block = (
                f"\nNGỮ CẢNH CÁC CÂU NGAY TRƯỚC ĐÓ (Chỉ đọc để nối mạch câu bị ngắt quãng và giữ nguyên xưng hô, KHÔNG dịch lại các câu này):\n"
                f"{prev_lines_str}\n"
            )

    system_instruction = (
        "Bạn là biên kịch lồng tiếng phim truyện (dubbing scriptwriter) hàng đầu Việt Nam.\n"
        f"{ctx_block}"
        f"{chunk_hv_block}"
        f"{prev_ctx_block}"
        "Nhiệm vụ: Dịch danh sách các câu thoại tiếng Trung sang tiếng Việt tự nhiên, giàu cảm xúc, chuẩn nhịp điệu đọc lồng tiếng.\n"
        "QUY TẮC BẮT BUỘC:\n"
        "1. TUÂN THỦ HỒ SƠ XƯNG HÔ & TÊN NHÂN VẬT: Bắt buộc dùng đúng ngôi xưng hô và tên nhân vật Hán-Việt chuẩn đã định nghĩa (vd: con - bố/mẹ, tôi - anh/cậu; 沈毅 -> Thẩm Nghị, 苏晚晴 -> Tô Vãn Tình, 赵睿 -> Triệu Duệ). Không được đổi ngôi hoặc dịch nghĩa đen từng chữ của tên người.\n"
        "2. LIÊN KẾT MẠCH CÂU BỊ TÁCH DÒNG: Phụ đề video thường tách 1 câu dài thành 2-3 dòng liên tiếp. Hãy đọc liền mạch các dòng kế nhau để dịch khớp ngữ pháp tiếng Việt tự nhiên giữa dòng trước và dòng sau.\n"
        "3. PHÂN BIỆT TÊN RIÊNG VỚI TỪ VỰNG THÔNG THƯỜNG: Tuyệt đối KHÔNG biến các đại từ, phó từ, cụm từ thông dụng thành tên người Hán-Việt (Ví dụ: 任何人 = 'bất kỳ ai', 明天 = 'ngày mai', 明明 = 'rõ ràng', 对方能 = 'đối phương có thể', 都傻了 = 'đều ngây người ra', 胡言 = 'nói năng hàm hồ').\n"
        "4. CÂU THOẠI ĐẦY ĐỦ, TỰ NHIÊN (CẤM CỘC LỐC): Ưu tiên câu thoại tự nhiên, trôi chảy. Chỉ khi một câu quá dài vượt số từ quy định mới rút gọn từ đệm thừa.\n"
        "5. VIỆT HÓA 100% TIẾNG LÓNG & THÀNH NGỮ (CẤM DỊCH THÔ / NỬA NẠC NỬA MỠ):\n"
        "   - Tuyệt đối không dịch nghĩa đen từng chữ hay để nguyên từ Hán-Việt khô khan:\n"
        "     + 吃瓜 -> 'hóng hớt', 'xem kịch vui' (CẤM dịch 'ăn dưa')\n"
        "     + 吃醋 -> 'ghen tuông', 'ghen đỏ mắt' (CẤM dịch 'ăn giấm')\n"
        "     + 套路 -> 'chiêu trò', 'bài cũ' (CẤM dịch 'sáo lộ')\n"
        "     + 脑回路 -> 'cách nghĩ', 'suy nghĩ dị thường' (CẤM dịch 'mạch não')\n"
        "     + 画风 -> 'bầu không khí', 'thái độ' (CẤM dịch 'phong cách vẽ')\n"
        "     + 甩脸色 -> 'tỏ thái độ', 'làm mặt lạnh'\n"
        "     + 下马威 -> 'đòn phủ đầu'\n"
        "     + 作妖 -> 'giở trò', 'kiếm chuyện quậy phá'\n"
        "     + 恋爱脑 -> 'lụy tình mù quáng'\n"
        "     + 打脸 -> 'tự vả', 'bẽ mặt'\n"
        "     + 蹭热度 -> 'hám fame', 'ké nhiệt', 'dựa hơi'\n"
        "     + 傻白甜 -> 'ngây thơ ngờ nghệch'\n"
        "     + 鸡飞狗跳 -> 'gà bay chó sủa', 'náo loạn'\n"
        "   - TUYỆT ĐỐI CẤM ĐỂ SÓT CHỮ HÁN TRONG CÂU TIẾNG VIỆT: Mọi ký tự tiếng Trung bắt buộc phải chuyển sạch 100% sang tiếng Việt.\n"
        "6. ĐỊNH DẠNG ĐẦU RA: Trả về DUY NHẤT một JSON Object với key 'translations' chứa mảng chuỗi đúng bằng số lượng câu đầu vào:\n"
        "{\"translations\": [\"câu 1\", \"câu 2\", ...]}"
    )

    user_content = f"Dịch {len(chunk_texts)} câu phụ đề sau sang tiếng Việt tự nhiên (chú ý số từ tối đa nếu câu quá dài):\n{numbered_lines}"

    models_to_try = [model_name] + [m for m in FALLBACK_GROQ_MODELS if m != model_name]

    for current_model in models_to_try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        payload = {
            "model": current_model,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_content}
            ],
            "temperature": 0.25,
            "response_format": {"type": "json_object"}
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Authorization": f"Bearer {api_key.strip()}",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )

        max_attempts = 2
        for attempt in range(max_attempts):
            try:
                with urllib.request.urlopen(req, timeout=45) as resp:
                    if resp.status == 200:
                        res_body = json.loads(resp.read().decode("utf-8"))
                        raw_content = res_body["choices"][0]["message"]["content"].strip()
                        parsed = json.loads(raw_content)

                        # Extract array from JSON object
                        lines: List[str] = []
                        if isinstance(parsed, dict):
                            for key in ("translations", "result", "lines", "subtitles"):
                                if key in parsed and isinstance(parsed[key], list):
                                    lines = [str(x).strip() for x in parsed[key]]
                                    break
                            if not lines:
                                for v in parsed.values():
                                    if isinstance(v, list) and len(v) == len(chunk_texts):
                                        lines = [str(x).strip() for x in v]
                                        break
                        elif isinstance(parsed, list):
                            lines = [str(x).strip() for x in parsed]

                        if lines:
                            if len(lines) == len(chunk_texts):
                                return lines
                            logger.warning(f"Groq {current_model} returned {len(lines)} items for {len(chunk_texts)} inputs, aligning...")
                            aligned = []
                            for k in range(len(chunk_texts)):
                                aligned.append(lines[k] if k < len(lines) else "")
                            return aligned
            except Exception as e:
                err_detail = str(e)
                if hasattr(e, 'read'):
                    try:
                        err_detail += f" - Response: {e.read().decode('utf-8')}"
                    except Exception:
                        pass

                is_429 = "429" in err_detail or "Too Many Requests" in err_detail or "rate_limit_exceeded" in err_detail
                if is_429:
                    if attempt >= 1 and current_model != models_to_try[-1]:
                        logger.info(f"Model {current_model} vẫn chạm trần 429 TPM, xoay vòng sang model dự phòng chất lượng cao {models_to_try[-1]}...")
                        break

                    wait_sec = 5.0
                    match = re.search(r'try again in\s+([0-9\.]+)\s*s', err_detail, re.IGNORECASE)
                    if match:
                        try:
                            wait_sec = min(12.0, max(2.5, float(match.group(1)) + 0.5))
                        except Exception:
                            pass

                    logger.warning(
                        f"Groq TPM Rate limit (429) chạm trần phút với model {current_model}. "
                        f"Tạm dừng {wait_sec:.1f}s để hồi phục hạn mức phút..."
                    )
                    time.sleep(wait_sec)
                    continue

                logger.warning(f"Groq API attempt {attempt + 1} with model {current_model} failed: {err_detail}")
                time.sleep(1.5)

    return None


def groq_batch_translate(
    texts: List[str],
    source_code: str = "zh-CN",
    target_code: str = "vi",
    batch_size: int = 45,
    durations: Optional[List[float]] = None,
    progress_callback=None
) -> Tuple[List[str], List[int]]:
    """
    Translates a list of subtitle texts using Groq Cloud API in batches.
    Executes 2-step architecture:
      1. Pre-flight Story & Character Bible Reasoning
      2. Context-Injected, Duration-Constrained Chunk Dubbing
    """
    from app.gemini_translator import load_settings
    settings = load_settings()
    api_key = settings.get("groq_api_key", "").strip()

    if not api_key:
        logger.error("No Groq API key configured.")
        return [""] * len(texts), list(range(len(texts)))

    model_name = settings.get("groq_model", DEFAULT_GROQ_MODEL)
    all_translated: List[str] = [""] * len(texts)
    failed_indices: List[int] = []

    # Step 1: Pre-flight Story Context Analysis
    logger.info("Analyzing full video story synopsis & character dynamics (Step 1)...")
    story_context = analyze_story_context(texts, api_key, model_name=model_name)
    logger.info(f"Story Context ready: {story_context[:100]}...")

    # Step 2: Batch Translation
    total_chunks = (len(texts) + batch_size - 1) // batch_size
    logger.info(f"Starting Groq translation for {len(texts)} lines in {total_chunks} chunks using {model_name}...")

    for chunk_idx, i in enumerate(range(0, len(texts), batch_size)):
        chunk = texts[i:i + batch_size]
        chunk_durations = durations[i:i + batch_size] if durations else None

        # Build sliding window of up to 4 preceding translated lines for seamless cross-chunk context
        prev_pairs: List[Tuple[str, str]] = []
        if i > 0:
            start_prev = max(0, i - 4)
            for p_idx in range(start_prev, i):
                if all_translated[p_idx]:
                    prev_pairs.append((texts[p_idx], all_translated[p_idx]))

        chunk_res = groq_translate_chunk(
            chunk,
            api_key,
            model_name=model_name,
            source_code=source_code,
            target_code=target_code,
            story_context=story_context,
            durations=chunk_durations,
            prev_context_pairs=prev_pairs
        )

        if chunk_res is not None:
            for offset, trans in enumerate(chunk_res):
                idx = i + offset
                all_translated[idx] = trans
        else:
            logger.warning(f"Groq chunk {chunk_idx + 1}/{total_chunks} failed. Splitting into smaller sub-chunks (15 lines) to recover...")
            sub_size = 15
            for sub_i in range(0, len(chunk), sub_size):
                sub_chunk = chunk[sub_i:sub_i + sub_size]
                sub_durs = chunk_durations[sub_i:sub_i + sub_size] if chunk_durations else None
                sub_prev: List[Tuple[str, str]] = []
                abs_sub_start = i + sub_i
                if abs_sub_start > 0:
                    for p_idx in range(max(0, abs_sub_start - 3), abs_sub_start):
                        if all_translated[p_idx]:
                            sub_prev.append((texts[p_idx], all_translated[p_idx]))
                time.sleep(2.5)
                sub_res = groq_translate_chunk(
                    sub_chunk,
                    api_key,
                    model_name=model_name,
                    source_code=source_code,
                    target_code=target_code,
                    story_context=story_context,
                    durations=sub_durs,
                    prev_context_pairs=sub_prev
                )
                if sub_res is not None:
                    for offset, trans in enumerate(sub_res):
                        idx = i + sub_i + offset
                        all_translated[idx] = trans
                else:
                    for offset in range(len(sub_chunk)):
                        idx = i + sub_i + offset
                        failed_indices.append(idx)

        if progress_callback:
            progress_callback(chunk_idx + 1, total_chunks)

        # Safe pacing delay to stay safely under Groq's 6,000 TPM limit
        time.sleep(2.0)

    return all_translated, failed_indices
