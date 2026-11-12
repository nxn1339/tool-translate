import os
import re
import asyncio
import logging
import subprocess
from typing import Dict, Any, List, Optional
from app.downloader import get_ffmpeg_path, get_ffprobe_path
from app.tts import generate_single_tts, VOICE_PRESETS, LEGACY_VOICE_MAP, get_audio_duration

logger = logging.getLogger(__name__)

# Curated voice pools for alternating comments
VOICE_CYCLE_POOL = [
    "capcut_thanhnientutin",
    "capcut_nhongotngao",
    "capcut_namtram",
    "capcut_cogaithoatngon"
]


def resolve_voice_preset(voice_name: Optional[str]) -> Dict[str, Any]:
    """Resolves voice preset configuration by name or alias."""
    if not voice_name:
        voice_name = "capcut_cogaithoatngon"

    resolved_name = LEGACY_VOICE_MAP.get(voice_name, voice_name)
    if resolved_name in VOICE_PRESETS:
        return VOICE_PRESETS[resolved_name]

    # Fallback to first available preset
    if VOICE_PRESETS:
        return next(iter(VOICE_PRESETS.values()))

    # Edge TTS fallback default
    return {
        "engine": "edge_tts",
        "voice": "vi-VN-HoaiMyNeural",
        "rate": "+0%",
        "pitch": "+0Hz"
    }


async def generate_social_audio_timeline(
    post_text: str,
    comments: List[Dict[str, Any]],
    output_dir: str,
    post_voice: str = "capcut_cogaithoatngon",
    pause_between: float = 0.35
) -> Dict[str, Any]:
    """
    Generates TTS for post content and each comment, measures durations,
    and stitches them together into a master audio track with timeline intervals.
    """
    os.makedirs(output_dir, exist_ok=True)
    ffmpeg_path = get_ffmpeg_path()
    if not ffmpeg_path:
        raise RuntimeError("FFmpeg executable not found.")

    segments = []
    current_time = 0.0

    # 1. Generate Post Audio
    post_audio_path = os.path.join(output_dir, "audio_post.mp3")
    post_preset = resolve_voice_preset(post_voice)
    await generate_single_tts(post_text, post_preset, post_audio_path)

    post_dur = get_audio_duration(post_audio_path)
    if post_dur <= 0.1:
        post_dur = 1.0  # Safe fallback

    segments.append({
        "type": "post",
        "audio_path": post_audio_path,
        "start": round(current_time, 2),
        "end": round(current_time + post_dur, 2),
        "duration": round(post_dur, 2)
    })
    current_time += post_dur + pause_between

    # 2. Generate Comments Audio
    for idx, c in enumerate(comments):
        c_text = c.get("content", "").strip()
        if not c_text:
            continue

        c_voice = c.get("voice")
        if not c_voice:
            # Alternate voices for realism
            c_voice = VOICE_CYCLE_POOL[idx % len(VOICE_CYCLE_POOL)]

        c_preset = resolve_voice_preset(c_voice)
        c_audio_path = os.path.join(output_dir, f"audio_comment_{idx+1}.mp3")
        await generate_single_tts(c_text, c_preset, c_audio_path)

        c_dur = get_audio_duration(c_audio_path)
        if c_dur <= 0.1:
            c_dur = 1.0

        segments.append({
            "type": "comment",
            "index": idx,
            "comment_id": c.get("id", f"c_{idx+1}"),
            "audio_path": c_audio_path,
            "start": round(current_time, 2),
            "end": round(current_time + c_dur, 2),
            "duration": round(c_dur, 2)
        })
        current_time += c_dur + pause_between

    # 3. Concatenate all audio segments with silence gap using FFmpeg
    master_audio_path = os.path.join(output_dir, "master_narration.mp3")

    # Build FFmpeg filter_complex for seamless concatenation
    inputs = []
    filter_chains = []
    for i, seg in enumerate(segments):
        inputs.extend(["-i", seg["audio_path"]])
        # Add silent padding after each segment except possibly the last
        filter_chains.append(f"[{i}:a]apad=pad_dur={pause_between}[a{i}]")

    concat_inputs = "".join([f"[a{i}]" for i in range(len(segments))])
    filter_complex = f"{';'.join(filter_chains)};{concat_inputs}concat=n={len(segments)}:v=0:a=1[outa]"

    cmd = [
        ffmpeg_path,
        "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[outa]",
        "-ac", "2",
        "-ar", "44100",
        "-b:a", "192k",
        master_audio_path
    ]

    res = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
        errors="replace"
    )
    if res.returncode != 0:
        logger.error(f"FFmpeg concat failed: {res.stderr}")
        raise RuntimeError(f"Failed to assemble master audio track: {res.stderr}")

    total_duration = get_audio_duration(master_audio_path)

    return {
        "master_audio_path": master_audio_path,
        "total_duration": total_duration or current_time,
        "segments": segments
    }

