import os
import re
import hashlib
import asyncio
import logging
import subprocess
from typing import List, Dict, Any, Optional
from app.downloader import get_ffmpeg_path, get_ffprobe_path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from app.capcut_tts import CAPCUT_VOICES, generate_capcut_tts

# Voice presets utilizing Microsoft Edge TTS neural voices and CapCut TTS voices
VOICE_PRESETS = {
    "female_hoaimy": {
        "voice": "vi-VN-HoaiMyNeural",
        "rate": "+0%",
        "pitch": "+0Hz",
        "name": "Hoài My (Nữ chuẩn - vi-VN-HoaiMyNeural)",
        "engine": "edge-tts"
    },
    "male_namminh": {
        "voice": "vi-VN-NamMinhNeural",
        "rate": "+0%",
        "pitch": "+0Hz",
        "name": "Nam Minh (Nam chuẩn - vi-VN-NamMinhNeural)",
        "engine": "edge-tts"
    }
}
# Merge CapCut voices into VOICE_PRESETS
VOICE_PRESETS.update(CAPCUT_VOICES)

# Legacy mapping for backwards compatibility
LEGACY_VOICE_MAP = {
    "tiktok_girl": "capcut_cogaithoatngon",
    "cogaithoatngon": "capcut_cogaithoatngon",
    "thanhnientutin": "capcut_thanhnientutin",
    "gentle_girl": "capcut_nhongotngao",
    "warm_man": "capcut_namtram",
    "fast_man": "capcut_thanhnientutin",
    "vi-VN-HoaiMyNeural": "female_hoaimy",
    "vi-VN-NamMinhNeural": "male_namminh"
}


async def generate_single_tts(text: str, voice_preset: Dict[str, Any], output_path: str):
    """
    Generates a single TTS audio file using CapCut TTS or Edge-TTS.
    Includes retry logic and text sanitization to handle errors.
    """
    sanitized_text = text.strip()
    sanitized_text = re.sub(r'[\u200b-\u200f\u2028-\u202f\u2060-\u206f\ufeff]', '', sanitized_text)
    sanitized_text = re.sub(r'\s+', ' ', sanitized_text).strip()

    if not sanitized_text:
        logger.warning(f"Empty text after sanitization, skipping TTS generation for: {output_path}")
        ffmpeg_path = get_ffmpeg_path()
        if ffmpeg_path:
            subprocess.run(
                [ffmpeg_path, "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", "0.1", output_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        return

    # 1. CapCut TTS Engine
    if voice_preset.get("engine") == "capcut":
        voice_type = voice_preset.get("voice_type", "BV074_streaming")
        resource_id = voice_preset.get("resource_id")
        ok = await generate_capcut_tts(sanitized_text, voice_type, output_path, resource_id=resource_id)
        if ok:
            return
        logger.warning(f"CapCut TTS failed for '{sanitized_text[:30]}', falling back to Edge-TTS Hoài My.")
        voice_preset = VOICE_PRESETS["female_hoaimy"]

    # 2. Edge-TTS Engine
    import edge_tts

    if not sanitized_text:
        logger.warning(f"Empty text after sanitization, skipping TTS generation for: {output_path}")
        ffmpeg_path = get_ffmpeg_path()
        if ffmpeg_path:
            subprocess.run(
                [ffmpeg_path, "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", "0.1", output_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        return

    max_retries = 3
    for attempt in range(max_retries):
        try:
            communicate = edge_tts.Communicate(
                text=sanitized_text,
                voice=voice_preset["voice"],
                rate=voice_preset["rate"],
                pitch=voice_preset["pitch"]
            )
            await communicate.save(output_path)
            return
        except Exception as e:
            logger.warning(f"TTS attempt {attempt + 1}/{max_retries} failed for text '{sanitized_text[:50]}': {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(1)
            else:
                logger.error(f"TTS permanently failed after {max_retries} attempts for text: '{sanitized_text[:50]}...'")
                ffmpeg_path = get_ffmpeg_path()
                if ffmpeg_path:
                    subprocess.run(
                        [ffmpeg_path, "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", "0.5", output_path],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    logger.info(f"Created silent placeholder for failed segment: {output_path}")
                else:
                    raise


def get_audio_duration(file_path: str) -> float:
    """
    Uses ffprobe to get the duration of an audio file in seconds.
    """
    ffprobe_path = get_ffprobe_path()
    if not ffprobe_path or not os.path.exists(file_path):
        return 0.0

    cmd = [
        ffprobe_path,
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        file_path
    ]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return float(result.stdout.strip())
    except Exception as e:
        logger.error(f"Error getting audio duration for {file_path}: {e}")
        return 0.0


def trim_audio_silence(input_path: str, output_path: str):
    """
    Trims silence from the beginning and end of a TTS audio file using ffmpeg silenceremove filter.
    Saves typically 0.25s - 0.4s of dead air per sentence without changing voice pitch or speed.
    """
    ffmpeg_path = get_ffmpeg_path()
    if not ffmpeg_path:
        raise FileNotFoundError("ffmpeg executable not found.")

    silence_filter = (
        "silenceremove=start_periods=1:start_duration=0.02:start_threshold=-45dB:detection=peak,"
        "areverse,"
        "silenceremove=start_periods=1:start_duration=0.02:start_threshold=-45dB:detection=peak,"
        "areverse"
    )
    cmd = [
        ffmpeg_path,
        "-y",
        "-i", input_path,
        "-af", silence_filter,
        output_path
    ]
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except Exception as e:
        logger.warning(f"Silence trimming failed for {input_path}, using input: {e}")
        import shutil
        shutil.copyfile(input_path, output_path)


def adjust_audio_speed(input_path: str, output_path: str, speed_ratio: float):
    """
    Adjusts the speed of an audio file using ffmpeg's atempo filter.
    speed_ratio: > 1.0 speeds up, < 1.0 slows down.
    """
    ffmpeg_path = get_ffmpeg_path()
    if not ffmpeg_path:
        raise FileNotFoundError("ffmpeg executable not found.")

    filters = []
    temp_ratio = speed_ratio

    while temp_ratio > 2.0:
        filters.append("atempo=2.0")
        temp_ratio /= 2.0
    while temp_ratio < 0.5:
        filters.append("atempo=0.5")
        temp_ratio /= 0.5

    filters.append(f"atempo={temp_ratio:.2f}")
    filter_str = ",".join(filters)

    cmd = [
        ffmpeg_path,
        "-y",
        "-i", input_path,
        "-filter:a", filter_str,
        output_path
    ]

    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)


def _compute_raw_tts_hash(text: str, preset: Dict[str, Any], rvc_model: str = "none", rvc_pitch: int = 0) -> str:
    voice_identifier = preset.get("voice_type") or preset.get("voice", "")
    payload = f"{text.strip()}|{voice_identifier}|{preset.get('rate', '+0%')}|{preset.get('pitch', '+0Hz')}|{rvc_model}|{rvc_pitch}"
    return hashlib.md5(payload.encode("utf-8")).hexdigest()[:10]


async def _process_single_segment(
    i: int,
    seg: Dict[str, Any],
    preset: Dict[str, Any],
    temp_dir: str,
    semaphore: asyncio.Semaphore,
    auto_extend_video: bool = False,
    rvc_model: str = "none",
    rvc_pitch: int = 0
) -> Optional[Dict[str, Any]]:
    translation = seg.get("translation", "").strip()
    start = float(seg.get("start", 0.0))
    end = float(seg.get("end", 0.0))
    duration = max(0.1, end - start)

    if not translation:
        return None

    os.makedirs(temp_dir, exist_ok=True)
    raw_hash = _compute_raw_tts_hash(translation, preset, rvc_model, rvc_pitch)

    temp_file = os.path.join(temp_dir, f"seg_{i}_raw.mp3")
    trimmed_file = os.path.join(temp_dir, f"seg_{i}_trimmed.wav")
    rvc_file = os.path.join(temp_dir, f"seg_{i}_rvc.wav")
    final_file = os.path.join(temp_dir, f"seg_{i}_aligned.wav")

    # Check if we can reuse existing trimmed audio for this exact (translation + voice + rvc)
    cached_ok = (
        seg.get("tts_raw_hash") == raw_hash
        and os.path.exists(trimmed_file)
        and os.path.getsize(trimmed_file) > 200
    )

    if not cached_ok:
        async with semaphore:
            await generate_single_tts(translation, preset, temp_file)
        try:
            trim_audio_silence(temp_file, trimmed_file)
        except Exception as e:
            logger.warning(f"Trimming error seg {i}: {e}")
            trimmed_file = temp_file

        # Apply RVC voice conversion if requested
        if rvc_model and rvc_model.lower() not in ("none", "", "false"):
            try:
                from app.rvc_engine import convert_audio_segment_rvc
                success = convert_audio_segment_rvc(
                    input_wav=trimmed_file,
                    output_wav=rvc_file,
                    model_id=rvc_model,
                    f0_pitch=rvc_pitch
                )
                if success and os.path.exists(rvc_file) and os.path.getsize(rvc_file) > 200:
                    trimmed_file = rvc_file
            except Exception as e_rvc:
                logger.warning(f"RVC conversion fallback for seg {i}: {e_rvc}")

    tts_duration = get_audio_duration(trimmed_file)

    # Determine speed ratio:
    # Note: UI sends "auto" or 1.0 by default. Only treat speed as manual override if explicitly != 1.0 (e.g. 0.9, 1.1, 1.2, 1.3)
    raw_speed = seg.get("speed")
    manual_speed = 0.0
    if raw_speed not in (None, "", "auto"):
        try:
            val = float(raw_speed)
            if abs(val - 1.0) > 0.02 and val > 0.4:
                manual_speed = val
        except (ValueError, TypeError):
            manual_speed = 0.0

    if manual_speed > 0.4:
        speed_ratio = manual_speed
    elif not auto_extend_video:
        # Dynamic smart compression: fit naturally into available window before next speech
        target_window = float(seg.get("available_duration") or duration)
        if tts_duration > target_window and target_window > 0.1:
            speed_ratio = round(tts_duration / target_window, 2)
            # Cap at 1.35x so Vietnamese pronunciation stays clear and natural (Elastic Timeline in merger handles any tiny remainder)
            if speed_ratio > 1.35:
                speed_ratio = 1.35
            elif speed_ratio < 1.04:
                speed_ratio = 1.0
        else:
            speed_ratio = 1.0
    else:
        # Auto-extend (Freeze Frame) mode: keep 1.0x pronunciation
        speed_ratio = 1.0

    if abs(speed_ratio - 1.0) > 0.03:
        try:
            adjust_audio_speed(trimmed_file, final_file, speed_ratio)
        except Exception as e:
            logger.error(f"Failed to adjust speed for segment {i}: {e}. Using trimmed file.")
            final_file = trimmed_file
    else:
        final_file = trimmed_file

    actual_duration = get_audio_duration(final_file) if os.path.exists(final_file) else tts_duration
    return {
        **seg,
        "tts_raw_hash": raw_hash,
        "audio_path": final_file,
        "actual_duration": round(actual_duration, 4),
        "speed_ratio": round(speed_ratio, 2)
    }


async def _generate_all_segments(
    segments: List[Dict[str, Any]],
    preset: Dict[str, Any],
    temp_dir: str,
    auto_extend_video: bool = False,
    rvc_model: str = "none",
    rvc_pitch: int = 0
) -> List[Dict[str, Any]]:
    # Pre-calculate available duration for each segment including dead-air silence gap before next subtitle
    for i, s in enumerate(segments):
        st = float(s.get("start", 0.0))
        en = float(s.get("end", 0.0))
        seg_dur = max(0.1, en - st)
        if i + 1 < len(segments):
            next_st = float(segments[i + 1].get("start", en))
            avail = max(seg_dur, next_st - st - 0.04)
        else:
            avail = seg_dur + 1.0
        s["available_duration"] = round(avail, 2)

    semaphore = asyncio.Semaphore(5)
    tasks = [
        _process_single_segment(i, seg, preset, temp_dir, semaphore, auto_extend_video, rvc_model, rvc_pitch)
        for i, seg in enumerate(segments)
    ]
    results = await asyncio.gather(*tasks)
    return [r for r in results if r is not None]


def generate_tts_for_segments(
    segments: List[Dict[str, Any]],
    voice_key: str,
    temp_dir: str,
    auto_extend_video: bool = False,
    rvc_model: str = "none",
    rvc_pitch: int = 0
) -> List[Dict[str, Any]]:
    """
    Generates TTS files in parallel for each segment using asyncio.gather and Semaphore(5).
    Optionally applies RVC voice conversion on active segments.
    Caches raw/trimmed audio by content hash so unchanged segments are instant and edited segments always update.
    """
    target_key = LEGACY_VOICE_MAP.get(voice_key, voice_key)
    preset = VOICE_PRESETS.get(target_key, VOICE_PRESETS["female_hoaimy"])

    # Auto-heal: If segments still contain untranslated Chinese characters, translate them first
    untranslated_indices = []
    untranslated_texts = []
    untranslated_durations = []
    for idx, seg in enumerate(segments):
        trans = seg.get("translation", "").strip()
        if trans and re.search(r'[\u4e00-\u9fff]', trans):
            untranslated_indices.append(idx)
            untranslated_texts.append(trans)
            untranslated_durations.append(max(0.2, float(seg.get("end", 0.0)) - float(seg.get("start", 0.0))))

    if untranslated_texts:
        logger.info(f"Detected {len(untranslated_texts)} segments with untranslated Chinese text. Running batch translation before TTS...")
        try:
            from app.translator import batch_translate_texts
            new_translations = batch_translate_texts(
                untranslated_texts,
                source_code="zh-CN",
                target_code="vi",
                durations=untranslated_durations
            )
            for seg_idx, new_trans in zip(untranslated_indices, new_translations):
                if new_trans and new_trans != segments[seg_idx]["translation"]:
                    segments[seg_idx]["translation"] = new_trans
            logger.info("Successfully translated remaining Chinese segments to Vietnamese.")
        except Exception as e:
            logger.warning(f"Failed to auto-translate Chinese segments before TTS: {e}")

    logger.info(f"Generating parallel TTS for {len(segments)} segments using preset: {preset['name']}")

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                return pool.submit(asyncio.run, _generate_all_segments(segments, preset, temp_dir, auto_extend_video, rvc_model, rvc_pitch)).result()
        else:
            return loop.run_until_complete(_generate_all_segments(segments, preset, temp_dir, auto_extend_video, rvc_model, rvc_pitch))
    except RuntimeError:
        return asyncio.run(_generate_all_segments(segments, preset, temp_dir, auto_extend_video, rvc_model, rvc_pitch))
