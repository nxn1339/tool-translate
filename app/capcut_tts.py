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
    "capcut_cogaithoatngon": {
        "voice_type": "BV074_streaming",
        "resource_id": "7102355709945188865",
        "name": "CapCut - Cô Gái Hoạt Ngôn (Hot TikTok)",
        "gender": "female",
        "engine": "capcut"
    },
    "capcut_thanhnientutin": {
        "voice_type": "BV075_streaming",
        "resource_id": "7102355803792740865",
        "name": "CapCut - Thanh Niên Tự Tin (Recap Phim)",
        "gender": "male",
        "engine": "capcut"
    },
    "capcut_nhongotngao": {
        "voice_type": "BV421_vivn_streaming",
        "resource_id": "7252594014782755330",
        "name": "CapCut - Nhỏ Ngọt Ngào (Nữ Dễ Thương)",
        "gender": "female",
        "engine": "capcut"
    },
    "capcut_giongbe": {
        "voice_type": "BV074_streaming_dsp",
        "resource_id": "7550087831092251920",
        "name": "CapCut - Giọng Bé (Trẻ Em)",
        "gender": "female",
        "engine": "capcut"
    },
    "capcut_namtram": {
        "voice_type": "multi_male_felipe_uranus_bigtts",
        "resource_id": "7637456729696996628",
        "name": "CapCut - Giọng Nam Trầm (Kể Chuyện)",
        "gender": "male",
        "engine": "capcut"
    },
    "capcut_reviewphim": {
        "voice_type": "multi_female_richgirl_uranus_bigtts",
        "resource_id": "7637460351541447956",
        "name": "CapCut - Review Phim (Truyền Cảm)",
        "gender": "female",
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

