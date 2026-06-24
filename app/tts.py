import os
import asyncio
import logging
import subprocess
from typing import List, Dict, Any
from app.downloader import get_ffmpeg_path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Voice presets utilizing Microsoft Edge TTS neural voices
VOICE_PRESETS = {
    "tiktok_girl": {
        "voice": "vi-VN-HoaiMyNeural",
        "rate": "+20%",   # Faster rate for lively TikTok style
        "pitch": "+4Hz",  # Slightly higher pitch for energetic feel
        "name": "Cô gái hoạt ngôn (TikTok style)"
    },
    "gentle_girl": {
        "voice": "vi-VN-HoaiMyNeural",
        "rate": "+0%",
        "pitch": "+0Hz",
        "name": "Cô gái nhẹ nhàng (Truyền cảm)"
    },
    "warm_man": {
        "voice": "vi-VN-NamMinhNeural",
        "rate": "+0%",
        "pitch": "+0Hz",
        "name": "Giọng nam trầm ấm (Thuyết minh)"
    },
    "fast_man": {
        "voice": "vi-VN-NamMinhNeural",
        "rate": "+18%",
        "pitch": "-1Hz",
        "name": "Giọng nam nhanh (Năng động)"
    }
}

async def generate_single_tts(text: str, voice_preset: Dict[str, Any], output_path: str):
    """
    Generates a single TTS audio file using edge-tts.
    Includes retry logic and text sanitization to handle NoAudioReceived errors.
    """
    import edge_tts
    import re

    # Sanitize text: remove special characters that may cause issues
    sanitized_text = text.strip()
    # Remove zero-width characters and other invisible unicode
    sanitized_text = re.sub(r'[\u200b-\u200f\u2028-\u202f\u2060-\u206f\ufeff]', '', sanitized_text)
    # Replace multiple spaces/newlines with single space
    sanitized_text = re.sub(r'\s+', ' ', sanitized_text).strip()

    if not sanitized_text:
        logger.warning(f"Empty text after sanitization, skipping TTS generation for: {output_path}")
        # Create a short silent audio file as placeholder
        ffmpeg_path = get_ffmpeg_path()
        if ffmpeg_path:
            import subprocess as sp
            sp.run([ffmpeg_path, "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", "0.1", output_path],
                   stdout=sp.DEVNULL, stderr=sp.DEVNULL)
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
            return  # Success
        except Exception as e:
            logger.warning(f"TTS attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(1)  # Wait before retry
            else:
                logger.error(f"TTS failed after {max_retries} attempts for text: '{sanitized_text[:50]}...'")
                # Create a short silent audio file as fallback
                ffmpeg_path = get_ffmpeg_path()
                if ffmpeg_path:
                    import subprocess as sp
                    sp.run([ffmpeg_path, "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", "0.5", output_path],
                           stdout=sp.DEVNULL, stderr=sp.DEVNULL)
                    logger.info(f"Created silent placeholder for failed segment: {output_path}")
                else:
                    raise

def get_audio_duration(file_path: str) -> float:
    """
    Uses ffprobe (from ffmpeg) to get the duration of an audio file in seconds.
    """
    ffmpeg_path = get_ffmpeg_path()
    if not ffmpeg_path:
        # Fallback if ffmpeg is missing
        return 0.0
        
    ffprobe_path = ffmpeg_path.replace("ffmpeg.exe", "ffprobe.exe")
    if not os.path.exists(ffprobe_path):
        ffprobe_path = ffmpeg_path.replace("ffmpeg", "ffprobe")
        if not os.path.exists(ffprobe_path) and shutil.which("ffprobe"):
            ffprobe_path = shutil.which("ffprobe")
        else:
            # If still not found, try running ffprobe from PATH or fallback to running ffmpeg
            ffprobe_path = "ffprobe"

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
        # Secondary fallback using ffmpeg to query
        return 0.0

def adjust_audio_speed(input_path: str, output_path: str, speed_ratio: float):
    """
    Adjusts the speed of an audio file using ffmpeg's atempo filter.
    speed_ratio: > 1.0 speeds up, < 1.0 slows down.
    """
    ffmpeg_path = get_ffmpeg_path()
    if not ffmpeg_path:
        raise FileNotFoundError("ffmpeg executable not found.")
        
    # ffmpeg's atempo filter must be between 0.5 and 2.0.
    # If we need larger speed adjustments, we chain them.
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

def generate_tts_for_segments(segments: List[Dict[str, Any]], voice_key: str, temp_dir: str) -> List[Dict[str, Any]]:
    """
    Generates TTS files for each segment and returns updated segments with local file paths.
    - segments: List of translation segments
    - voice_key: The key in VOICE_PRESETS (e.g., 'tiktok_girl')
    - temp_dir: Directory to save generated audio files
    """
    preset = VOICE_PRESETS.get(voice_key, VOICE_PRESETS["tiktok_girl"])
    logger.info(f"Generating TTS for {len(segments)} segments using preset: {preset['name']}")
    
    updated_segments = []
    
    for i, seg in enumerate(segments):
        translation = seg["translation"].strip()
        start = seg["start"]
        end = seg["end"]
        duration = end - start
        
        if not translation:
            continue
            
        temp_file = os.path.join(temp_dir, f"seg_{i}_raw.mp3")
        final_file = os.path.join(temp_dir, f"seg_{i}_aligned.wav")
        
        # 1. Generate raw TTS audio
        logger.info(f"Generating TTS for segment {i}: '{translation}'")
        asyncio.run(generate_single_tts(translation, preset, temp_file))
        
        # 2. Check duration
        tts_duration = get_audio_duration(temp_file)
        logger.info(f"Segment {i} original duration: {duration:.2f}s, TTS duration: {tts_duration:.2f}s")
        
        # 3. Adjust speed if necessary (especially if TTS is longer than video window)
        # We allow a small tolerance (e.g. 0.2s)
        if tts_duration > duration > 0.1:
            speed_ratio = tts_duration / duration
            # Limit maximum speed up to 1.6x so it's still readable
            if speed_ratio > 1.6:
                speed_ratio = 1.6
            logger.info(f"Speeding up segment {i} by {speed_ratio:.2f}x to fit timeline.")
            try:
                adjust_audio_speed(temp_file, final_file, speed_ratio)
            except Exception as e:
                logger.error(f"Failed to adjust speed for segment {i}: {e}. Using raw file.")
                # Fallback: convert mp3 to wav directly without speed adjustment
                ffmpeg_path = get_ffmpeg_path()
                if ffmpeg_path:
                    subprocess.run([ffmpeg_path, "-y", "-i", temp_file, final_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    final_file = temp_file
        else:
            # Just convert raw MP3 to WAV for final merging
            ffmpeg_path = get_ffmpeg_path()
            if ffmpeg_path:
                subprocess.run([ffmpeg_path, "-y", "-i", temp_file, final_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                final_file = temp_file
                
        # Save file path and final duration in the segment info
        actual_duration = get_audio_duration(final_file) if os.path.exists(final_file) else tts_duration
        updated_segments.append({
            **seg,
            "audio_path": final_file,
            "actual_duration": actual_duration
        })
        
    return updated_segments
