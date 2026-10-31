import os
import json
import subprocess
import logging
from typing import List, Dict, Any, Optional, Tuple
from app.downloader import get_ffmpeg_path, get_ffprobe_path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_video_has_audio(video_path: str) -> bool:
    """
    Checks if a video file contains an audio stream using ffmpeg.
    """
    ffmpeg_path = get_ffmpeg_path()
    if not ffmpeg_path:
        return True

    cmd = [
        ffmpeg_path,
        "-i", video_path,
        "-hide_banner"
    ]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return "Audio:" in result.stderr or "audio" in result.stderr.lower()
    except Exception as e:
        logger.error(f"Error checking if video has audio: {e}")
        return True


def get_video_dimensions(video_path: str) -> Tuple[int, int]:
    """
    Returns (width, height) of the video using ffprobe. Defaults to (1920, 1080) on error.
    """
    ffprobe_path = get_ffprobe_path()
    if not ffprobe_path:
        return 1920, 1080

    cmd = [
        ffprobe_path,
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "csv=s=x:p=0",
        video_path
    ]
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        out = res.stdout.strip()
        if "x" in out:
            w_str, h_str = out.split("x", 1)
            return int(w_str), int(h_str)
    except Exception as e:
        logger.warning(f"Could not get video dimensions: {e}. Fallback to 1920x1080.")
    return 1920, 1080


def get_video_duration(video_path: str) -> float:
    """
    Returns duration of the video in seconds using ffprobe.
    """
    ffprobe_path = get_ffprobe_path()
    if not ffprobe_path:
        return 0.0
    cmd = [
        ffprobe_path,
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "csv=p=0",
        video_path
    ]
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return float(res.stdout.strip())
    except Exception as e:
        logger.warning(f"Could not get video duration: {e}")
        return 0.0


def compute_elastic_timeline(
    segments: List[Dict[str, Any]],
    total_video_dur: float = 0.0
) -> List[Dict[str, Any]]:
    """
    Computes non-overlapping, drift-free playback timestamps (`play_start`, `play_end`, `extra_tempo`)
    for each segment in smooth video mode (when Freeze-Frame is disabled):
    1. Borrows up to 0.25s of leading silence before `orig_s` if a clip is longer than its slot.
    2. Allows up to 0.30s of elastic push into the transition gap, strictly bounded so timeline never drifts from video scenes.
    3. If a clip still exceeds its elastic window before the next scene, computes `extra_tempo` (applied via FFmpeg `atempo`)
       so 100% of the words are spoken clearly with ZERO overlap and ZERO word truncation (`atrim`).
    """
    sorted_segs = sorted(segments, key=lambda s: float(s.get("start", 0.0)))
    result: List[Dict[str, Any]] = []
    prev_play_end = 0.0

    for idx, seg in enumerate(sorted_segs):
        s_copy = dict(seg)
        orig_s = float(s_copy.get("start", 0.0))
        orig_e = float(s_copy.get("end", orig_s + 0.5))
        adur = float(s_copy.get("actual_duration", 0.0))
        has_audio = bool(
            s_copy.get("translation", "").strip()
            and s_copy.get("audio_path")
            and os.path.exists(s_copy.get("audio_path", ""))
            and adur > 0.05
        )

        if not has_audio:
            s_copy["play_start"] = round(orig_s, 3)
            s_copy["play_end"] = round(orig_e, 3)
            s_copy["extra_tempo"] = 1.0
            result.append(s_copy)
            continue

        if idx + 1 < len(sorted_segs):
            next_orig_s = float(sorted_segs[idx + 1].get("start", orig_e))
            # Allow borrowing up to 0.25s into the next segment's start if the next segment also has room,
            # but never let start time drift more than 0.35s behind the visual scene
            hard_deadline = next_orig_s + 0.25
        else:
            next_orig_s = max(orig_e + 1.0, total_video_dur) if total_video_dur > 0 else orig_e + 1.5
            hard_deadline = next_orig_s + 0.5

        min_allowed_start = (prev_play_end + 0.03) if prev_play_end > 0 else 0.0
        # Bound play_start so it never drifts more than 0.35s past orig_s
        max_allowed_start = orig_s + 0.35

        overflow = max(0.0, (orig_s + adur) - next_orig_s)
        early_headroom = max(0.0, orig_s - min_allowed_start)
        borrow_early = min(0.25, early_headroom, overflow)

        play_start = max(min_allowed_start, orig_s - borrow_early)
        if play_start > max_allowed_start and min_allowed_start <= max_allowed_start:
            play_start = max_allowed_start

        max_slot_dur = max(0.25, hard_deadline - play_start - 0.03)
        extra_tempo = 1.0
        effective_dur = adur

        if adur > max_slot_dur:
            extra_tempo = min(1.50, round(adur / max_slot_dur, 3))
            if extra_tempo < 1.03:
                extra_tempo = 1.0
            else:
                effective_dur = adur / extra_tempo

        play_end = play_start + effective_dur

        s_copy["play_start"] = round(play_start, 3)
        s_copy["play_end"] = round(play_end, 3)
        s_copy["extra_tempo"] = round(extra_tempo, 3)
        prev_play_end = play_end
        result.append(s_copy)

    # Second pass: synchronize subtitle display end times so two subtitles never overlap on screen
    for idx, s_copy in enumerate(result):
        sub_start = float(s_copy.get("play_start", s_copy.get("start", 0.0)))
        sub_end = max(float(s_copy.get("end", sub_start + 0.5)), float(s_copy.get("play_end", sub_start + 0.5)))
        if idx + 1 < len(result):
            next_sub_start = float(result[idx + 1].get("play_start", result[idx + 1].get("start", sub_end)))
            if sub_end > next_sub_start - 0.02:
                sub_end = max(sub_start + 0.2, next_sub_start - 0.02)
        s_copy["sub_start"] = round(sub_start, 3)
        s_copy["sub_end"] = round(sub_end, 3)

    return result


def format_timestamp_srt(seconds: float) -> str:
    """
    Converts float seconds to SRT timestamp format: HH:MM:SS,mmm
    """
    if seconds < 0:
        seconds = 0
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    msecs = int(round((seconds - int(seconds)) * 1000))
    if msecs >= 1000:
        msecs = 999
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{msecs:03d}"


def export_srt_file(segments: List[Dict[str, Any]], srt_path: str):
    """
    Generates a standard SubRip (.srt) subtitle file from segments.
    """
    valid_segments = [s for s in segments if s.get("translation") and s["translation"].strip()]
    with open(srt_path, "w", encoding="utf-8") as f:
        for idx, seg in enumerate(valid_segments, 1):
            st = float(seg.get("sub_start", seg.get("start", 0.0)))
            en = float(seg.get("sub_end", seg.get("end", st + 0.5)))
            start_str = format_timestamp_srt(st)
            end_str = format_timestamp_srt(en)
            text = seg.get("translation", "").strip()
            f.write(f"{idx}\n{start_str} --> {end_str}\n{text}\n\n")
    logger.info(f"Exported SRT subtitles to: {srt_path} ({len(valid_segments)} entries)")


def hex_to_ass_color(hex_str: str, alpha_hex: str = "00") -> str:
    """Convert hex #RRGGBB to ASS &HAABBGGRR format (Blue, Green, Red order)."""
    if not hex_str:
        return "&H00FFFFFF"
    clean_hex = hex_str.strip().lstrip("#")
    if len(clean_hex) == 6:
        r, g, b = clean_hex[0:2], clean_hex[2:4], clean_hex[4:6]
        return f"&H{alpha_hex}{b}{g}{r}".upper()
    return "&H00FFFFFF"


def format_timestamp_ass(seconds: float) -> str:
    """Converts float seconds to ASS timestamp format: H:MM:SS.cc"""
    if seconds < 0:
        seconds = 0
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    csecs = int(round((seconds - int(seconds)) * 100))
    if csecs >= 100:
        csecs = 99
    return f"{hrs}:{mins:02d}:{secs:02d}.{csecs:02d}"


def export_ass_file(
    segments: List[Dict[str, Any]],
    ass_path: str,
    video_w: int,
    video_h: int,
    sub_box: Optional[Dict[str, Any]] = None,
    sub_styling: Optional[Dict[str, Any]] = None
):
    """
    Generates a pixel-perfect Advanced SubStation Alpha (.ass) file
    with explicit PlayResX and PlayResY matching video dimensions.
    """
    valid_segments = [s for s in segments if s.get("translation") and s["translation"].strip()]
    styling = sub_styling or {}
    raw_font = styling.get("font_name", "Nunito")
    if "nunito" in raw_font.lower():
        font_name = "Nunito ExtraBold"
    else:
        font_name = raw_font

    raw_size = styling.get("font_size", 48)
    base_font_size = int(raw_size) if raw_size else 48
    scale = max(0.3, float(video_h) / 720.0)
    font_size = max(16, int(round(base_font_size * scale)))

    primary_color_hex = styling.get("primary_color", "#FFFFFF")
    outline_color_hex = styling.get("outline_color", "#000000")
    base_outline_width = float(styling.get("outline_width", 3.0))
    outline_width = max(1.2, round(min(2.4, base_outline_width) * scale, 1))

    box_style = styling.get("box_style", "outline")
    box_color_hex = styling.get("back_color", "#000000")
    box_opacity = float(styling.get("box_opacity", 0.75))
    bold_flag = -1 if styling.get("bold", True) else 0
    shadow_val = max(1.0, round(1.6 * scale, 1))

    primary_ass = hex_to_ass_color(primary_color_hex, "00")
    outline_ass = hex_to_ass_color(outline_color_hex, "00")

    sx_pct = float(sub_box.get("x", 10.0)) if sub_box else 10.0
    sy_pct = float(sub_box.get("y", 78.0)) if sub_box else 78.0
    sw_pct = float(sub_box.get("w", 80.0)) if sub_box else 80.0
    sh_pct = float(sub_box.get("h", 14.0)) if sub_box else 14.0

    cx = int((sx_pct + sw_pct / 2.0) * video_w / 100.0)
    cy = int((sy_pct + sh_pct / 2.0) * video_h / 100.0)
    margin_l = max(10, int(sx_pct * video_w / 100.0))
    margin_r = max(10, int((100.0 - sx_pct - sw_pct) * video_w / 100.0))
    alignment = 5  # Mid-Center

    if box_style == "box":
        border_style = 3
        alpha_int = int((1.0 - box_opacity) * 255)
        alpha_hex = f"{max(0, min(255, alpha_int)):02X}"
        box_ass = hex_to_ass_color(box_color_hex, alpha_hex)
        border_color = box_ass
        back_color = "&HFF000000"
        outline_val = max(4.0, outline_width)
        shadow_val = 0
    else:
        border_style = 1
        border_color = outline_ass
        back_color = hex_to_ass_color("#000000", "80")
        outline_val = outline_width

    ass_header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {video_w}
PlayResY: {video_h}
ScaledBorderAndShadow: yes
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font_name},{font_size},{primary_ass},&H000000FF,{border_color},{back_color},{bold_flag},0,0,0,100,100,0,0,{border_style},{outline_val},{shadow_val},{alignment},{margin_l},{margin_r},0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ass_header)
        for seg in valid_segments:
            st = float(seg.get("sub_start", seg.get("start", 0.0)))
            en = float(seg.get("sub_end", seg.get("end", st + 0.5)))
            start_str = format_timestamp_ass(st)
            end_str = format_timestamp_ass(en)
            text = seg.get("translation", "").strip()
            text = text.replace("\r\n", "\\N").replace("\n", "\\N")
            pos_tag = f"{{\\an5\\pos({cx},{cy})\\blur2.5}}"
            f.write(f"Dialogue: 0,{start_str},{end_str},Default,,{margin_l},{margin_r},0,,{pos_tag}{text}\n")

    logger.info(f"Exported ASS subtitles to: {ass_path} ({len(valid_segments)} entries, PlayRes={video_w}x{video_h}, Fontsize={font_size}, Center=({cx},{cy}))")


def merge_audio_segments_to_video(
    original_video_path: str,
    segments: List[Dict[str, Any]],
    output_video_path: str,
    bg_volume: float = 0.15,
    tts_volume: float = 1.0,
    mask_box: Optional[Dict[str, Any]] = None,
    sub_box: Optional[Dict[str, Any]] = None,
    burn_subtitles: bool = True,
    sub_styling: Optional[Dict[str, Any]] = None,
    auto_extend_video: bool = False,
    logo_box: Optional[Dict[str, Any]] = None
):
    """
    Merges generated audio segments with the original video,
    using either Elastic Timeline Sync (smooth video, 0% word loss, 0% overlap)
    or Freeze-Frame Auto-Extend, applying video masking, burning subtitles (Hardsub),
    and overlaying customizable logo/watermark.
    """
    ffmpeg_path = get_ffmpeg_path()
    if not ffmpeg_path:
        raise FileNotFoundError("ffmpeg executable not found.")

    has_original_audio = check_video_has_audio(original_video_path)
    video_w, video_h = get_video_dimensions(original_video_path)
    total_video_dur = get_video_duration(original_video_path)
    logger.info(
        f"Video specs: {video_w}x{video_h}, total_duration={total_video_dur:.2f}s, "
        f"Has original audio: {has_original_audio}, Auto-extend: {auto_extend_video}"
    )

    from app.tts import get_audio_duration
    for seg in segments:
        if "audio_path" in seg and os.path.exists(seg["audio_path"]) and not seg.get("actual_duration"):
            seg["actual_duration"] = get_audio_duration(seg["audio_path"])

    sorted_segments = sorted(segments, key=lambda s: float(s.get("start", 0.0)))
    active_segments = [
        s for s in sorted_segments
        if s.get("translation") and s.get("translation").strip() and s.get("audio_path") and os.path.exists(s["audio_path"])
    ]

    needs_extension = auto_extend_video and any(
        float(s.get("actual_duration", 0.0)) > (float(s.get("end", 0.0)) - float(s.get("start", 0.0)))
        for s in active_segments
    )

    timeline_segments: List[Dict[str, Any]] = []
    slices: List[Dict[str, float]] = []

    if needs_extension and total_video_dur > 0:
        logger.info("Auto-Extend Video: Constructing extended slices and synchronized timeline...")
        cur_orig_t = 0.0
        cur_new_t = 0.0

        for s in sorted_segments:
            orig_s = float(s.get("start", 0.0))
            orig_e = float(s.get("end", 0.0))
            orig_dur = max(0.05, orig_e - orig_s)

            if orig_s > cur_orig_t + 0.04:
                gap = orig_s - cur_orig_t
                slices.append({"start": cur_orig_t, "end": orig_s, "pad": 0.0})
                cur_new_t += gap
                cur_orig_t = orig_s
            elif orig_s < cur_orig_t:
                orig_s = cur_orig_t
                orig_e = max(orig_s + 0.1, orig_e)
                orig_dur = orig_e - orig_s

            adur = float(s.get("actual_duration", 0.0))
            has_audio = bool(s.get("translation", "").strip() and s.get("audio_path") and os.path.exists(s.get("audio_path", "")))
            pad = 0.0
            if has_audio and adur > orig_dur:
                pad = adur - orig_dur + 0.12

            new_dur = orig_dur + pad
            new_seg = dict(s)
            new_seg["start"] = round(cur_new_t, 3)
            new_seg["end"] = round(cur_new_t + new_dur, 3)
            new_seg["play_start"] = new_seg["start"]
            new_seg["play_end"] = new_seg["end"]
            new_seg["sub_start"] = new_seg["start"]
            new_seg["sub_end"] = new_seg["end"]
            timeline_segments.append(new_seg)

            slices.append({"start": orig_s, "end": orig_e, "pad": round(pad, 3)})
            cur_orig_t = orig_e
            cur_new_t += new_dur

        if total_video_dur > cur_orig_t + 0.05:
            slices.append({"start": cur_orig_t, "end": total_video_dur, "pad": 0.0})

        logger.info(f"Built {len(slices)} video slices. Output video duration expanded from {total_video_dur:.2f}s to {cur_new_t:.2f}s.")
    else:
        # Smooth mode: apply Elastic Timeline alignment so clips never overlap or get cut off mid-word
        timeline_segments = compute_elastic_timeline(sorted_segments, total_video_dur=total_video_dur)

    task_dir = os.path.dirname(output_video_path)
    srt_path = os.path.join(task_dir, "subtitles.srt")
    export_srt_file(timeline_segments, srt_path)

    ass_path = os.path.join(task_dir, "subtitles.ass")
    export_ass_file(timeline_segments, ass_path, video_w, video_h, sub_box, sub_styling)

    active_timeline_segments = [
        s for s in timeline_segments
        if s.get("translation") and s.get("translation").strip() and s.get("audio_path") and os.path.exists(s["audio_path"])
    ]

    has_mask = bool(mask_box and mask_box.get("enabled", False))
    has_logo = bool(
        logo_box
        and logo_box.get("enabled", False)
        and logo_box.get("image_path")
        and os.path.exists(logo_box["image_path"])
    )
    need_video_filter = has_mask or burn_subtitles or (needs_extension and bool(slices)) or has_logo

    cmd = [ffmpeg_path, "-y", "-i", original_video_path]
    for seg in active_timeline_segments:
        cmd.extend(["-i", seg["audio_path"]])

    logo_input_idx = None
    if has_logo:
        logo_input_idx = 1 + len(active_timeline_segments)
        cmd.extend(["-i", logo_box["image_path"]])

    filter_parts = []

    if needs_extension and slices:
        v_labels = []
        a_labels = []
        for idx, sl in enumerate(slices):
            st = sl["start"]
            en = sl["end"]
            pad = sl["pad"]

            v_filter = f"[0:v]trim=start={st:.3f}:end={en:.3f},setpts=PTS-STARTPTS"
            if pad > 0:
                v_filter += f",tpad=stop_mode=clone:stop_duration={pad:.3f}"
            v_lbl = f"v_sl_{idx}"
            filter_parts.append(f"{v_filter}[{v_lbl}];")
            v_labels.append(f"[{v_lbl}]")

            if has_original_audio:
                a_filter = f"[0:a]atrim=start={st:.3f}:end={en:.3f},asetpts=PTS-STARTPTS"
                if pad > 0:
                    a_filter += f",apad=pad_dur={pad:.3f}"
                a_lbl = f"a_sl_{idx}"
                filter_parts.append(f"{a_filter}[{a_lbl}];")
                a_labels.append(f"[{a_lbl}]")

        if has_original_audio:
            concat_ins = "".join(f"{v}{a}" for v, a in zip(v_labels, a_labels))
            filter_parts.append(f"{concat_ins}concat=n={len(slices)}:v=1:a=1[v_concat][a_concat];")
            current_audio_label = "a_concat"
        else:
            concat_ins = "".join(v_labels)
            filter_parts.append(f"{concat_ins}concat=n={len(slices)}:v=1:a=0[v_concat];")
            current_audio_label = None

        current_video_label = "v_concat"
    else:
        current_video_label = "0:v"
        current_audio_label = "0:a" if has_original_audio else None

    # --- 1. Video Filters: Masking (Blur) & Hardsub ---
    if has_mask:
        x_pct = max(0.0, min(100.0, float(mask_box.get("x", 10.0))))
        y_pct = max(0.0, min(100.0, float(mask_box.get("y", 80.0))))
        w_pct = max(5.0, min(100.0, float(mask_box.get("w", 80.0))))
        h_pct = max(3.0, min(100.0, float(mask_box.get("h", 12.0))))

        mx = int(x_pct * video_w / 100.0)
        my = int(y_pct * video_h / 100.0)
        mw = max(10, int(w_pct * video_w / 100.0))
        mh = max(10, int(h_pct * video_h / 100.0))
        style = mask_box.get("style", "blur")

        if style == "solid":
            filter_parts.append(f"[{current_video_label}]drawbox=x={mx}:y={my}:w={mw}:h={mh}:color=black@0.85:t=fill[v_masked];")
            current_video_label = "v_masked"
        else:
            filter_parts.append(
                f"[{current_video_label}]split[v_main][v_crop];"
                f"[v_crop]crop=w={mw}:h={mh}:x={mx}:y={my},boxblur=15:5[v_blur];"
                f"[v_main][v_blur]overlay=x={mx}:y={my}[v_masked];"
            )
            current_video_label = "v_masked"

    if burn_subtitles and os.path.exists(ass_path) and os.path.getsize(ass_path) > 0:
        try:
            rel_ass = os.path.relpath(ass_path, os.getcwd()).replace("\\", "/")
        except Exception:
            rel_ass = ass_path.replace("\\", "/")

        fonts_dir = os.path.join(os.path.dirname(__file__), "fonts")
        if os.path.exists(fonts_dir) and any(f.endswith((".ttf", ".otf")) for f in os.listdir(fonts_dir)):
            try:
                rel_fonts = os.path.relpath(fonts_dir, os.getcwd()).replace("\\", "/")
            except Exception:
                rel_fonts = fonts_dir.replace("\\", "/")
            sub_filter = f"subtitles={rel_ass}:fontsdir={rel_fonts}"
        else:
            sub_filter = f"subtitles={rel_ass}"
        filter_parts.append(f"[{current_video_label}]{sub_filter}[v_subbed];")
        current_video_label = "v_subbed"

    # --- 1.3 Video Filters: Logo / Watermark Overlay ---
    if has_logo and logo_input_idx is not None:
        lx_pct = max(0.0, min(100.0, float(logo_box.get("x", 80.0))))
        ly_pct = max(0.0, min(100.0, float(logo_box.get("y", 5.0))))
        lw_pct = max(2.0, min(100.0, float(logo_box.get("w", 15.0))))
        l_opacity = max(0.05, min(1.0, float(logo_box.get("opacity", 1.0))))
        l_keep_aspect = bool(logo_box.get("keep_aspect", True))

        target_lw = max(16, int(round((lw_pct / 100.0) * video_w)))
        pos_x = max(0, min(max(0, video_w - 10), int(round((lx_pct / 100.0) * video_w))))
        pos_y = max(0, min(max(0, video_h - 10), int(round((ly_pct / 100.0) * video_h))))

        if l_keep_aspect:
            scale_filter = f"scale={target_lw}:-1"
        else:
            lh_pct = max(2.0, min(100.0, float(logo_box.get("h", 10.0))))
            target_lh = max(16, int(round((lh_pct / 100.0) * video_h)))
            scale_filter = f"scale={target_lw}:{target_lh}"

        logo_chain = f"[{logo_input_idx}:v]{scale_filter}"
        if l_opacity < 0.99:
            logo_chain += f",format=rgba,colorchannelmixer=aa={l_opacity:.2f}"
        logo_chain += "[v_logo_prepared];"
        filter_parts.append(logo_chain)

        filter_parts.append(
            f"[{current_video_label}][v_logo_prepared]overlay=x={pos_x}:y={pos_y}[v_logo_out];"
        )
        current_video_label = "v_logo_out"

    # --- 2. Audio Filters: Non-overlapping Elastic Delay & Background Mixing ---
    if active_timeline_segments:
        for idx, seg in enumerate(active_timeline_segments):
            start_sec = float(seg.get("play_start", seg.get("start", 0.0)))
            start_ms = max(0, int(round(start_sec * 1000)))
            extra_tempo = float(seg.get("extra_tempo", 1.0))
            tempo_chain = f"atempo={min(2.0, extra_tempo):.3f}," if extra_tempo > 1.02 else ""
            filter_parts.append(f"[{idx + 1}:a]{tempo_chain}adelay={start_ms}|{start_ms}[delayed_{idx}];")

        mix_inputs = "".join(f"[delayed_{idx}]" for idx in range(len(active_timeline_segments)))
        filter_parts.append(
            f"{mix_inputs}amix=inputs={len(active_timeline_segments)}:duration=longest:dropout_transition=0:normalize=0,"
            f"volume={tts_volume}[tts_mixed];"
        )

        if current_audio_label:
            filter_parts.append(f"[{current_audio_label}]volume={bg_volume}[bg_scaled];")
            filter_parts.append(
                f"[bg_scaled][tts_mixed]amix=inputs=2:duration=first:dropout_transition=2:normalize=0[final_audio]"
            )
    else:
        if current_audio_label:
            filter_parts.append(f"[{current_audio_label}]volume=1.0[final_audio]")

    filter_str = "".join(filter_parts)
    filter_script_path = os.path.join(task_dir, "filter_script.txt")
    with open(filter_script_path, "w", encoding="utf-8") as f:
        f.write(filter_str)

    # Compatible with FFmpeg 4.x - 9.x+
    cmd.extend(["-filter_complex", filter_str])

    if need_video_filter:
        cmd.extend(["-map", f"[{current_video_label}]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "22"])
    else:
        cmd.extend(["-map", "0:v", "-c:v", "copy"])

    if active_timeline_segments:
        audio_label = "[final_audio]" if current_audio_label else "[tts_mixed]"
        cmd.extend(["-map", audio_label, "-c:a", "aac", "-b:a", "192k"])
    else:
        if current_audio_label:
            cmd.extend(["-map", "[final_audio]", "-c:a", "aac"])
        else:
            cmd.extend(["-an"])

    if not needs_extension:
        cmd.extend(["-shortest"])

    cmd.append(output_video_path)

    logger.info(f"Running master FFmpeg command (need_video_filter={need_video_filter}, needs_extension={needs_extension})...")
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        logger.error(f"FFmpeg execution failed (code {result.returncode}): {result.stderr}")
        raise RuntimeError(f"FFmpeg merging error: {result.stderr}")

    logger.info(f"Video merged successfully: {output_video_path}")


def generate_preview_audio_track(
    project_dir: str,
    segments: List[Dict[str, Any]],
    voice: str = "female_hoaimy",
    rvc_model: str = "none",
    rvc_pitch: int = 0
) -> str:
    """
    Mixes all TTS segment audio files into a single preview audio track
    synchronized with the original video timeline (using Elastic Timeline to prevent overlap).
    Automatically regenerates TTS for any edited segment via content hash.
    """
    from app.tts import generate_tts_for_segments

    ffmpeg = get_ffmpeg_path()
    if not ffmpeg:
        raise FileNotFoundError("ffmpeg not found.")

    output_preview_mp3 = os.path.join(project_dir, "preview_dubbed.mp3")

    if segments:
        logger.info(f"Ensuring up-to-date TTS for preview audio track ({len(segments)} segments, voice={voice}, rvc={rvc_model})...")
        segments = generate_tts_for_segments(
            segments,
            voice,
            project_dir,
            auto_extend_video=False,
            rvc_model=rvc_model,
            rvc_pitch=rvc_pitch
        )
        seg_json = os.path.join(project_dir, "segments.json")
        try:
            with open(seg_json, "w", encoding="utf-8") as f:
                json.dump(segments, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    aligned_segments = compute_elastic_timeline(segments)
    active_segs = [
        s for s in aligned_segments
        if s.get("translation") and s["translation"].strip() and s.get("audio_path") and os.path.exists(s["audio_path"])
    ]

    if not active_segs:
        subprocess.run(
            [ffmpeg, "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", "1.0", output_preview_mp3],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        return output_preview_mp3

    cmd = [ffmpeg, "-y"]
    for s in active_segs:
        cmd.extend(["-i", s["audio_path"]])

    filter_parts = []
    for idx, s in enumerate(active_segs):
        st_sec = float(s.get("play_start", s.get("start", 0.0)))
        st_ms = max(0, int(round(st_sec * 1000)))
        extra_tempo = float(s.get("extra_tempo", 1.0))
        tempo_chain = f"atempo={min(2.0, extra_tempo):.3f}," if extra_tempo > 1.02 else ""
        filter_parts.append(f"[{idx}:a]{tempo_chain}adelay={st_ms}|{st_ms}[a{idx}];")

    mix_str = "".join(f"[a{idx}]" for idx in range(len(active_segs)))
    filter_parts.append(f"{mix_str}amix=inputs={len(active_segs)}:duration=longest:dropout_transition=0:normalize=0[outa]")

    filter_str = "".join(filter_parts)
    preview_filter_path = os.path.join(project_dir, "preview_filter_script.txt")
    with open(preview_filter_path, "w", encoding="utf-8") as f:
        f.write(filter_str)

    cmd.extend([
        "-filter_complex", filter_str,
        "-map", "[outa]",
        "-c:a", "libmp3lame",
        "-b:a", "128k",
        output_preview_mp3
    ])
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    logger.info(f"Generated preview dubbed audio: {output_preview_mp3} ({len(active_segs)} clips)")
    return output_preview_mp3
