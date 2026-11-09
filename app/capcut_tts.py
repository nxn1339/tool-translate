import os
import re
import sys
import asyncio
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Ensure capcut_backend is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CAPCUT_BACKEND_DIR = os.path.join(PROJECT_ROOT, "capcut_backend")
if CAPCUT_BACKEND_DIR not in sys.path and os.path.exists(CAPCUT_BACKEND_DIR):
    sys.path.insert(0, CAPCUT_BACKEND_DIR)

_capcut_client_instance = None


def get_capcut_client():
    global _capcut_client_instance
    if _capcut_client_instance is None:
        try:
            from capcut_tts_api.client import CapCutClient
            _capcut_client_instance = CapCutClient(timeout=30)
            logger.info("Initialized CapCut TTS Client successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize CapCutClient: {e}")
            raise
    return _capcut_client_instance


# Curated Vietnamese CapCut TTS Voices
CAPCUT_VOICES: Dict[str, Dict[str, Any]] = {
    # --- NHÓM GIỌNG NỮ TIKTOK / CAPCUT (ĐỌC TRUYỆN, REVIEW, KỂ CHUYỆN) ---
    "capcut_cogaithoatngon": {
        "voice_type": "BV074_streaming",
        "resource_id": "7102355709945188865",
        "name": "🔥 Cô Gái Hoạt Ngôn (Hot TikTok)",
        "gender": "female",
        "category": "female_hot",
        "engine": "capcut"
    },
    "capcut_nhongotngao": {
        "voice_type": "BV421_vivn_streaming",
        "resource_id": "7252594014782755330",
        "name": "🌸 Nhỏ Ngọt Ngào (Nữ Dễ Thương)",
        "gender": "female",
        "category": "female_sweet",
        "engine": "capcut"
    },
    "capcut_reviewphim": {
        "voice_type": "multi_female_richgirl_uranus_bigtts",
        "resource_id": "7637460351541447956",
        "name": "🎬 Review Phim Mới (Nữ Truyền Cảm)",
        "gender": "female",
        "category": "female_review",
        "engine": "capcut"
    },
    "capcut_reviewphim2": {
        "voice_type": "multi_female_xyf04auto_uranus_bigtts",
        "resource_id": "7637458743197732117",
        "name": "🎬 Review Phim 2 (Nữ Trôi Chảy)",
        "gender": "female",
        "category": "female_review",
        "engine": "capcut"
    },
    "capcut_reviewphim3": {
        "voice_type": "multi_female_daqi_uranus_bigtts",
        "resource_id": "7637451983389019409",
        "name": "🎬 Review Phim 3 (Nữ Trầm Tĩnh)",
        "gender": "female",
        "category": "female_review",
        "engine": "capcut"
    },
    "capcut_reviewphim4": {
        "voice_type": "multi_female_stokie_uranus_bigtts",
        "resource_id": "7637456729696996628",
        "name": "🎬 Review Phim 4 (Nữ Sâu Lắng)",
        "gender": "female",
        "category": "female_review",
        "engine": "capcut"
    },
    "capcut_banmai": {
        "voice_type": "multi_female_yangguangnv_uranus_bigtts",
        "resource_id": "7637456432522218773",
        "name": "☀️ Ban Mai (Trong Trẻo Ấm Áp)",
        "gender": "female",
        "category": "female_story",
        "engine": "capcut"
    },
    "capcut_mai": {
        "voice_type": "BV562_streaming",
        "resource_id": "7483736254694035984",
        "name": "🌿 Mai (Nhẹ Nhàng Trầm Ấm)",
        "gender": "female",
        "category": "female_story",
        "engine": "capcut"
    },
    "capcut_nu_phothong": {
        "voice_type": "vi_female_huong",
        "resource_id": "7264854897953083905",
        "name": "👩 Giọng Nữ Phổ Thông (Tự Nhiên)",
        "gender": "female",
        "category": "female_standard",
        "engine": "capcut"
    },
    "capcut_gaimoilon": {
        "voice_type": "multi_female_peiqi_uranus_bigtts",
        "resource_id": "7637458789033151751",
        "name": "👧 Giọng Gái Mới Lớn (Tươi Trẻ)",
        "gender": "female",
        "category": "female_youth",
        "engine": "capcut"
    },
    "capcut_sunny_idol": {
        "voice_type": "multi_female_kiwi_uranus_bigtts",
        "resource_id": "7637457995882089749",
        "name": "✨ Sunny Idol (Hiện Đại)",
        "gender": "female",
        "category": "female_youth",
        "engine": "capcut"
    },
    "capcut_bantin_nu": {
        "voice_type": "multi_female_sisi_uranus_bigtts",
        "resource_id": "7637455857285860629",
        "name": "📰 Bản Tin Nữ (Dõng Dạc)",
        "gender": "female",
        "category": "female_news",
        "engine": "capcut"
    },
    "capcut_bantin_1": {
        "voice_type": "multi_female_quanweinv_uranus_bigtts",
        "resource_id": "7637458743197732117",
        "name": "📢 Bản Tin 1 (Chuyên Nghiệp)",
        "gender": "female",
        "category": "female_news",
        "engine": "capcut"
    },
    "capcut_giongbe": {
        "voice_type": "BV074_streaming_dsp",
        "resource_id": "7550087831092251920",
        "name": "👶 Giọng Bé (Trẻ Em Đáng Yêu)",
        "gender": "female",
        "category": "female_kid",
        "engine": "capcut"
    },
    "capcut_tianmeijieshuo": {
        "voice_type": "multi_female_tianmeijieshuo_uranus_bigtts",
        "resource_id": "7637460417295469832",
        "name": "🎀 Nữ Dịu Dàng (Truyền Cảm)",
        "gender": "female",
        "category": "female_story",
        "engine": "capcut"
    },

    # --- NHÓM GIỌNG NAM TIKTOK / CAPCUT ---
    "capcut_thanhnientutin": {
        "voice_type": "BV075_streaming",
        "resource_id": "7102355803792740865",
        "name": "⚡ Thanh Niên Tự Tin (Recap Phim)",
        "gender": "male",
        "category": "male_recap",
        "engine": "capcut"
    },
    "capcut_namtram": {
        "voice_type": "multi_male_felipe_uranus_bigtts",
        "resource_id": "7637456729696996628",
        "name": "🎙️ Giọng Nam Trầm (Kể Chuyện Đêm)",
        "gender": "male",
        "category": "male_story",
        "engine": "capcut"
    },
    "capcut_nam_bantin": {
        "voice_type": "multi_female_xinwenjieshuo_uranus_bigtts",
        "resource_id": "7637455039719640327",
        "name": "🎙️ Nam Bản Tin (Thời Sự)",
        "gender": "male",
        "category": "male_news",
        "engine": "capcut"
    },
    "capcut_alex": {
        "voice_type": "BV560_streaming",
        "resource_id": "7483736167565758992",
        "name": "👑 Alex Đại Đế (Mạnh Mẽ)",
        "gender": "male",
        "category": "male_character",
        "engine": "capcut"
    },
    "capcut_kenny": {
        "voice_type": "BV075_streaming_demon_dsp",
        "resource_id": "7569442422665661712",
        "name": "😈 Kenny Đại Đế (Kịch Tính)",
        "gender": "male",
        "category": "male_character",
        "engine": "capcut"
    },
    "capcut_robot": {
        "voice_type": "BV075_streaming_robot_dsp",
        "resource_id": "7538698409633516816",
        "name": "🤖 Robot VN (Điện Tử)",
        "gender": "male",
        "category": "character",
        "engine": "capcut"
    },
    "capcut_vietmeo": {
        "voice_type": "BV075_streaming_vibrato_dsp",
        "resource_id": "7569450639810465040",
        "name": "🌊 Việt Méo (Hiệu Ứng Rung)",
        "gender": "male",
        "category": "character",
        "engine": "capcut"
    }
}


def sanitize_text(text: str) -> str:
    cleaned = text.strip()
    cleaned = re.sub(r'[\u200b-\u200f\u2028-\u202f\u2060-\u206f\ufeff]', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned


def _sync_generate_capcut_tts(text: str, voice_type: str, output_path: str, resource_id: Optional[str] = None) -> bool:
    client = get_capcut_client()
    sanitized = sanitize_text(text)
    if not sanitized:
        logger.warning(f"Empty text for CapCut TTS, skipping: {output_path}")
        return False

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    res = client.generate_speech(
        texts=sanitized,
        voice=voice_type,
        resource_id=resource_id
    )
    client.download_tts_audio(res, output_path)
    return os.path.exists(output_path) and os.path.getsize(output_path) > 500


async def generate_capcut_tts(
    text: str,
    voice_type: str,
    output_path: str,
    resource_id: Optional[str] = None,
    max_retries: int = 3
) -> bool:
    """
    Asynchronously generates TTS audio via CapCut API with retry handling.
    """
    for attempt in range(max_retries):
        try:
            success = await asyncio.to_thread(
                _sync_generate_capcut_tts,
                text,
                voice_type,
                output_path,
                resource_id
            )
            if success:
                logger.info(f"CapCut TTS successfully generated: '{output_path}' ({os.path.getsize(output_path)} bytes)")
                return True
        except Exception as e:
            logger.warning(f"CapCut TTS attempt {attempt + 1}/{max_retries} failed for '{text[:40]}': {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(1)

    logger.error(f"CapCut TTS failed after {max_retries} attempts for: '{text[:50]}'")
    return False

