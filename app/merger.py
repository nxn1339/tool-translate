import os
import subprocess
import logging
from typing import List, Dict, Any
from app.downloader import get_ffmpeg_path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_video_has_audio(video_path: str) -> bool:
    """
    Checks if a video file contains an audio stream using ffmpeg.
    """
    ffmpeg_path = get_ffmpeg_path()
    if not ffmpeg_path:
        return True # Default assume yes

    # Use ffmpeg itself to check for audio streams (no ffprobe needed)
    cmd = [
        ffmpeg_path,
        "-i", video_path,
        "-hide_banner"
    ]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # ffmpeg prints stream info to stderr
        return "Audio:" in result.stderr or "audio" in result.stderr.lower()
    except Exception as e:
        logger.error(f"Error checking if video has audio: {e}")
        return True # Fallback to true to attempt mixing

def merge_audio_segments_to_video(
    original_video_path: str,
    segments: List[Dict[str, Any]],
    output_video_path: str,
    bg_volume: float = 0.15,  # Original background music volume (15%)
    tts_volume: float = 1.0,  # Translated TTS voice volume (100%)
):
    """
    Merges all generated audio segments with the original video.
    Aligns each segment to its specific start timestamp and mixes them.
    """
    ffmpeg_path = get_ffmpeg_path()
    if not ffmpeg_path:
        raise FileNotFoundError("ffmpeg executable not found.")

    has_original_audio = check_video_has_audio(original_video_path)
    logger.info(f"Original video has audio: {has_original_audio}")

    # Build the ffmpeg command
    cmd = [ffmpeg_path, "-y"]
    
    # Input 0: Original video
    cmd.extend(["-i", original_video_path])
    
    # Inputs 1 to N: Audio segments
    active_segments = [seg for seg in segments if "audio_path" in seg and os.path.exists(seg["audio_path"])]
    
    if not active_segments:
        logger.warning("No audio segments found to merge. Just copying video.")
        # Just copy original video
        copy_cmd = [ffmpeg_path, "-y", "-i", original_video_path, "-c", "copy", output_video_path]
        subprocess.run(copy_cmd, check=True)
        return

    for seg in active_segments:
        cmd.extend(["-i", seg["audio_path"]])

    # Build complex filter
    filter_parts = []
    
    # 1. Apply adelay to each audio input to place it at the correct timestamp
    # Note: Input 0 is video. Segment i corresponds to input index i + 1.
    for idx, seg in enumerate(active_segments):
        start_ms = int(seg["start"] * 1000)
        if start_ms < 0:
            start_ms = 0
            
        # Use adelay filter. We delay both channels for stereo compatibility (e.g. 1000|1000)
        filter_parts.append(f"[{idx + 1}:a]adelay={start_ms}|{start_ms}[delayed_{idx}];")

    # 2. Mix all delayed TTS segments together
    # IMPORTANT: normalize=0 prevents amix from dividing volume by the number of inputs
    mix_inputs = "".join(f"[delayed_{idx}]" for idx in range(len(active_segments)))
    filter_parts.append(f"{mix_inputs}amix=inputs={len(active_segments)}:duration=longest:dropout_transition=0:normalize=0,volume={tts_volume}[tts_mixed];")

    # 3. Mix with original audio if available, otherwise just use TTS
    if has_original_audio:
        # Scale original background audio volume and mix it with TTS
        filter_parts.append(f"[0:a]volume={bg_volume}[bg_scaled];")
        filter_parts.append(f"[bg_scaled][tts_mixed]amix=inputs=2:duration=first:dropout_transition=2:normalize=0[final_audio]")
        filter_str = "".join(filter_parts)
        
        cmd.extend([
            "-filter_complex", filter_str,
            "-map", "0:v",          # Map original video
            "-map", "[final_audio]", # Map mixed audio
            "-c:v", "copy",         # Stream copy video (no re-encoding, extremely fast!)
            "-c:a", "aac",          # Encode audio to AAC
            "-shortest",            # End when shortest stream ends
            output_video_path
        ])
    else:
        # No original audio, just use the TTS audio
        filter_str = "".join(filter_parts)
        cmd.extend([
            "-filter_complex", filter_str,
            "-map", "0:v",
            "-map", "[tts_mixed]",
            "-c:v", "copy",
            "-c:a", "aac",
            output_video_path
        ])

    logger.info("Running ffmpeg merge command...")
    logger.info(f"Total TTS segments to merge: {len(active_segments)}")
    # Executing the command
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    if result.returncode != 0:
        logger.error(f"ffmpeg merge failed with return code {result.returncode}")
        logger.error(f"ffmpeg stderr: {result.stderr}")
        raise RuntimeError(f"FFmpeg merging failed: {result.stderr}")
        
    logger.info(f"Successfully merged video to {output_video_path}")

