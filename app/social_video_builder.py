import os
import subprocess
import logging
from typing import Dict, Any, List, Optional
from PIL import Image
from app.downloader import get_ffmpeg_path, get_ffprobe_path
from app.tts import get_audio_duration

logger = logging.getLogger(__name__)


def build_social_short_video(
    post_card_path: str,
    comment_cards: List[Dict[str, Any]],
    master_audio_path: str,
    timeline_segments: List[Dict[str, Any]],
    output_video_path: str,
    background_video_path: Optional[str] = None,
    bgm_path: Optional[str] = None,
    bgm_volume: float = 0.12,
    video_width: int = 1080,
    video_height: int = 1920,
    fps: int = 30
) -> str:
    """
    Renders a vertical 9:16 short video by compositing background video,
    main post card, and sequential comment cards synced with narration.
    """
    ffmpeg_path = get_ffmpeg_path()
    if not ffmpeg_path:
        raise RuntimeError("FFmpeg executable not found.")

    output_video_path = os.path.abspath(output_video_path)
    os.makedirs(os.path.dirname(output_video_path), exist_ok=True)

    total_duration = get_audio_duration(master_audio_path)
    if total_duration <= 0.5:
        total_duration = 10.0

    # Find when post reading finishes and comment reading starts
    post_end_time = 0.0
    for seg in timeline_segments:
        if seg.get("type") == "post":
            post_end_time = seg.get("end", 5.0)
            break

    # 1. Inputs construction
    inputs = []

    # Input 0: Background (video or fallback solid canvas)
    has_bg_video = background_video_path and os.path.isfile(background_video_path)
    if has_bg_video:
        inputs.extend(["-stream_loop", "-1", "-i", background_video_path])
    else:
        # Fallback dark aesthetic gradient background generated via lavfi
        inputs.extend([
            "-f", "lavfi",
            "-i", f"gradients=s={video_width}x{video_height}:c0=0x111827:c1=0x030712:speed=0.5:r={fps}"
        ])

    # Input 1: Post Card PNG
    inputs.extend(["-i", post_card_path])

    # Inputs 2..N: Comment Card PNGs
    comment_input_indices = {}
    next_input_idx = 2
    for c_info in comment_cards:
        c_path = c_info.get("card_path")
        if c_path and os.path.isfile(c_path):
            inputs.extend(["-i", c_path])
            comment_input_indices[c_info.get("comment_id", f"c_{next_input_idx}")] = next_input_idx
            next_input_idx += 1

    # Master Audio Input
    narration_input_idx = next_input_idx
    inputs.extend(["-i", master_audio_path])
    next_input_idx += 1

    # Optional BGM input
    has_bgm = bgm_path and os.path.isfile(bgm_path)
    if has_bgm:
        bgm_input_idx = next_input_idx
        inputs.extend(["-stream_loop", "-1", "-i", bgm_path])
        next_input_idx += 1

    # 2. Filter Complex construction
    filter_chains = []

    # Layer 0: Background scaled and cropped to 1080x1920
    filter_chains.append(
        f"[0:v]scale={video_width}:{video_height}:force_original_aspect_ratio=increase,"
        f"crop={video_width}:{video_height},fps={fps},settb=AVTB[bg]"
    )

    # Calculate post card height to position comment cards perfectly
    post_card_height = 540
    try:
        with Image.open(post_card_path) as p_img:
            post_card_height = p_img.height
    except Exception as e:
        logger.warning(f"Could not read post card height: {e}")

    # Layer 1: Post Card overlay
    # When t < post_end_time: Centered vertically: y=(H-h)/2 - 50
    # When t >= post_end_time: Slid up to upper section: y=130
    post_y_expr = f"if(lt(t,{post_end_time}),(H-h)/2-50,130)"
    filter_chains.append(
        f"[bg][1:v]overlay=x=(W-w)/2:y='{post_y_expr}':eval=frame[v_base]"
    )

    current_v_stream = "v_base"

    # Position comments cleanly beneath the lifted post card
    comment_y = min(130 + post_card_height + 36, 1200)

    # Layer 2..N: Sequential Comment Cards overlay
    for idx, c_info in enumerate(comment_cards):
        c_id = c_info.get("comment_id", f"c_{idx+2}")
        c_in_idx = comment_input_indices.get(c_id)
        if c_in_idx is None:
            continue

        c_start = c_info.get("start", post_end_time)
        c_end = c_info.get("end", total_duration)

        next_v_stream = f"v_com_{idx}"
        filter_chains.append(
            f"[{current_v_stream}][{c_in_idx}:v]overlay="
            f"x=(W-w)/2:y={comment_y}:enable='between(t,{c_start},{c_end})'[{next_v_stream}]"
        )
        current_v_stream = next_v_stream

    # Audio filtering
    if has_bgm:
        # Mix voice narration (1.0) and BGM (0.12)
        filter_chains.append(
            f"[{bgm_input_idx}:a]volume={bgm_volume}[abgm];"
            f"[{narration_input_idx}:a][abgm]amix=inputs=2:duration=first:dropout_transition=2[outa]"
        )
        audio_map = "[outa]"
    else:
        audio_map = f"{narration_input_idx}:a"

    filter_complex_str = ";".join(filter_chains)

    cmd = [
        ffmpeg_path,
        "-y",
        *inputs,
        "-filter_complex", filter_complex_str,
        "-map", f"[{current_v_stream}]",
        "-map", audio_map,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "22",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-t", f"{total_duration + 0.5:.2f}",
        output_video_path
    ]

    logger.info(f"Running video compilation with command: {' '.join(cmd[:12])}...")
    res = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
        errors="replace"
    )
    if res.returncode != 0:
        logger.error(f"FFmpeg compilation error: {res.stderr}")
        raise RuntimeError(f"FFmpeg failed to compose video: {res.stderr}")

    return output_video_path

