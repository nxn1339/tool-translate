"""
Gemini Contextual AI Translation Engine for Subtitles & Dubbing.
Produces natural, dialogue-ready, dramatic Vietnamese translations with correct
pronouns, Sino-Vietnamese names, and dubbing rhythm.
"""

import os
import re
import json
import logging
import urllib.request
import urllib.parse
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "data", "settings.json")
ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")

DEFAULT_GEMINI_MODEL = "gemini-3.5-flash"
FALLBACK_GEMINI_MODELS = ["gemini-flash-latest", "gemini-3.8-flash"]


def load_settings() -> Dict[str, Any]:
    settings = {
        "translation_engine": "groq",
        "groq_api_key": "",
        "groq_model": "llama-3.3-70b-versatile",
        "gemini_api_key": "",
        "gemini_model": DEFAULT_GEMINI_MODEL
    }
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                settings.update(json.load(f))
        except Exception as e:
            logger.warning(f"Failed to read settings from {SETTINGS_PATH}: {e}")

    if settings.get("groq_model") == "qwen/qwen3.8-27b":
        settings["groq_model"] = "llama-3.3-70b-versatile"

    # Fallback to environment variables or .env
    if not settings.get("groq_api_key"):
        env_groq = os.environ.get("GROQ_API_KEY", "")
        if env_groq:
            settings["groq_api_key"] = env_groq

    if not settings.get("gemini_api_key"):
        env_key = os.environ.get("GEMINI_API_KEY", "")
        if not env_key and os.path.exists(ENV_PATH):
            try:
                with open(ENV_PATH, "r", encoding="utf-8") as ef:
                    for line in ef:
                        if line.startswith("GEMINI_API_KEY="):
                            env_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                        elif line.startswith("GROQ_API_KEY=") and not settings.get("groq_api_key"):
                            settings["groq_api_key"] = line.split("=", 1)[1].strip().strip('"').strip("'")
            except Exception:
                pass
        if env_key:
            settings["gemini_api_key"] = env_key

    return settings


def save_settings(new_settings: Dict[str, Any]) -> Dict[str, Any]:
    curr = load_settings()
    curr.update(new_settings)
    os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(curr, f, ensure_ascii=False, indent=2)

    # Also sync keys to .env
    env_lines = []
    gemini_k = curr.get("gemini_api_key", "")
    groq_k = curr.get("groq_api_key", "")
    if gemini_k:
        env_lines.append(f"GEMINI_API_KEY={gemini_k}\n")
    if groq_k:
        env_lines.append(f"GROQ_API_KEY={groq_k}\n")
    if env_lines:
        try:
            with open(ENV_PATH, "w", encoding="utf-8") as ef:
                ef.writelines(env_lines)
        except Exception:
            pass

    return curr


def gemini_translate_chunk(
    chunk_texts: List[str],
    api_key: str,
    model_name: str = DEFAULT_GEMINI_MODEL,
    source_code: str = "zh-CN",
    target_code: str = "vi",
    prev_context_pairs: Optional[List[Tuple[str, str]]] = None
) -> Optional[List[str]]:
    """
    Translates a block of 20-40 dialogue lines with deep narrative context,
    character role preservation, Sino-Vietnamese glossary hints, and subtitle rhythm.
    """
    if not chunk_texts:
        return []

    numbered_lines = "\n".join([f"[{i + 1}] {line}" for i, line in enumerate(chunk_texts)])

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
                f"\nNGỮ CẢNH CÁC CÂU NGAY TRƯỚC ĐÓ (Chỉ đọc để nối mạch câu bị ngắt quãng và giữ nguyên xưng hô, KHÔNG dịch lại):\n"
                f"{prev_lines_str}\n"
            )

    system_instruction = (
        "Bạn là một biên tập viên vietsub và biên kịch lồng tiếng phim truyện (dubbing scriptwriter) hàng đầu.\n"
        f"{chunk_hv_block}"
        f"{prev_ctx_block}"
        "Nhiệm vụ: Dịch danh sách các câu thoại/phụ đề tiếng Trung sang tiếng Việt một cách tự nhiên, giàu cảm xúc, đúng ngữ cảnh đối thoại.\n"
        "Quy tắc bắt buộc:\n"
        "1. XƯNG HÔ ĐÚNG NGỮ CẢNH: Tự động nhận diện bối cảnh để xưng hô nhất quán (Cổ trang/Cung đấu: hoàng thượng - thần thiếp, ta - chàng, nàng - ta; Hiện đại/Hào môn: con - bố/mẹ, anh - em, tôi - anh/cô).\n"
        "2. CHUẨN ÂM HÁN - VIỆT & KHÔNG NHẦM TỪ VỰNG THÔNG THƯỜNG: Mọi tên nhân vật, địa danh, môn phái, danh xưng phải dùng âm Hán - Việt chuẩn (ví dụ: 沈毅 -> Thẩm Nghị, 苏晚晴 -> Tô Vãn Tình, 薛彩衣 -> Tiết Thải Y). Tuyệt đối không dùng Pinyin phương Tây và KHÔNG dịch nhầm từ thông dụng thành tên người (như 任何人 = bất kỳ ai, 明天 = ngày mai, 对方能 = đối phương có thể).\n"
        "3. LIÊN KẾT MẠCH CÂU & CÓ NHỊP ĐIỆU: Nối mạch tự nhiên giữa các dòng phụ đề bị ngắt câu. Lời thoại cô đọng, tự nhiên như lời nói hàng ngày của người Việt, giữ độ dài vừa vặn để đọc lồng tiếng (Voiceover), cấm để sót bất kỳ chữ Hán nào.\n"
        "4. ĐỊNH DẠNG ĐẦU RA: Trả về duy nhất một JSON mảng các chuỗi (JSON array of strings) có số lượng phần tử bằng đúng số lượng câu đầu vào, theo đúng thứ tự. Ví dụ: [\"câu 1\", \"câu 2\", ...]"
    )

    prompt = f"{system_instruction}\n\nDanh sách câu cần dịch:\n{numbered_lines}"

    models_to_try = [model_name] + [m for m in FALLBACK_GEMINI_MODELS if m != model_name]

    for model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.3,
                "responseMimeType": "application/json"
            }
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                if resp.status == 200:
                    res_body = json.loads(resp.read().decode("utf-8"))
                    text_out = res_body["candidates"][0]["content"]["parts"][0]["text"].strip()
                    # Parse JSON array
                    parsed = json.loads(text_out)
                    if isinstance(parsed, list) and len(parsed) == len(chunk_texts):
                        return [str(item).strip() for item in parsed]
                    elif isinstance(parsed, list) and len(parsed) > 0:
                        logger.warning(f"Gemini returned {len(parsed)} items for {len(chunk_texts)} inputs, padding/clipping...")
                        out = []
                        for k in range(len(chunk_texts)):
                            out.append(str(parsed[k]).strip() if k < len(parsed) else "")
                        return out
        except Exception as e:
            logger.warning(f"Gemini translation attempt with {model} failed: {e}")

    return None


def gemini_batch_translate(
    texts: List[str],
    source_code: str = "zh-CN",
    target_code: str = "vi",
    batch_size: int = 35
) -> Optional[List[str]]:
    """
    Translates a list of subtitle texts using Gemini Flash in batches of 30-40 lines.
    Returns None if API key is not configured or fails completely (triggering fallback).
    """
    settings = load_settings()
    api_key = settings.get("gemini_api_key", "").strip()
    if not api_key:
        logger.info("No Gemini API key configured. Skipping Gemini translation.")
        return None

    model_name = settings.get("gemini_model", DEFAULT_GEMINI_MODEL)
    all_translated: List[str] = []

    for i in range(0, len(texts), batch_size):
        chunk = texts[i:i + batch_size]
        prev_pairs: List[Tuple[str, str]] = []
        if i > 0:
            for p_idx in range(max(0, i - 4), i):
                if p_idx < len(all_translated) and all_translated[p_idx]:
                    prev_pairs.append((texts[p_idx], all_translated[p_idx]))
        chunk_res = gemini_translate_chunk(
            chunk,
            api_key,
            model_name=model_name,
            source_code=source_code,
            target_code=target_code,
            prev_context_pairs=prev_pairs
        )
        if chunk_res is not None:
            all_translated.extend(chunk_res)
        else:
            logger.warning(f"Chunk {i // batch_size + 1} failed with Gemini. Leaving {len(chunk)} lines empty for retry.")
            all_translated.extend([""] * len(chunk))

    return all_translated

