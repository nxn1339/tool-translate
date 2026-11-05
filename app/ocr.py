import os
import re
import logging
import numpy as np
from collections import Counter
from typing import List, Dict, Any, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global cache for RapidOCR engine
_cached_ocr_engine = None

# Common studio/watermark suffixes in Bilibili/Douyin animations & recaps
WATERMARK_PATTERN = re.compile(
    r'^[\u4e00-\u9fffA-Za-z0-9]{1,6}(?:动画|动漫|剧场|影视|解说|出品|制作|工作室|字幕组|汉化组|原创|漫画)$'
)


def get_ocr_engine():
    """
    Initializes and returns cached RapidOCR instance with GPU DirectML acceleration,
    optimized detector resolution, and classification bypass for ultra-fast subtitle scanning.
    """
    global _cached_ocr_engine
    if _cached_ocr_engine is not None:
        return _cached_ocr_engine

    try:
        from rapidocr_onnxruntime import RapidOCR
    except ImportError:
        raise ImportError(
            "Thư viện RapidOCR chưa được cài đặt. "
            "Vui lòng cài đặt bằng lệnh: pip install rapidocr-onnxruntime onnxruntime-directml opencv-python-headless"
        )

    try:
        import onnxruntime as ort
        available_ep = ort.get_available_providers()
        use_dml = "DmlExecutionProvider" in available_ep
        use_cuda = "CUDAExecutionProvider" in available_ep
        logger.info(f"Khởi tạo RapidOCR (DirectML={use_dml}, CUDA={use_cuda})...")
        _cached_ocr_engine = RapidOCR(
            use_dml=use_dml,
            use_cuda=use_cuda,
            use_cls=False,
            det_limit_type="max",
            det_limit_side_len=960
        )
        logger.info(f"RapidOCR khởi tạo thành công với tăng tốc phần cứng (GPU DML: {use_dml}).")
    except Exception as e_init:
        logger.warning(f"Cảnh báo khởi tạo RapidOCR với GPU ({e_init}), fallback cấu hình an toàn...")
        _cached_ocr_engine = RapidOCR(use_cls=False)

    return _cached_ocr_engine


def has_meaningful_chinese(text: str) -> bool:
    """
    Checks if a string contains at least one Chinese character.
    Filters out stray OCR noise like 'A', '1', '_', '-', etc.
    """
    if not text:
        return False
    return bool(re.search(r'[\u4e00-\u9fff]', text))


def clean_ocr_line(text: str) -> str:
    """
    Cleans raw OCR text from a single frame:
    - Strips stray brackets, quotes, underscores, leading/trailing noise
    - Removes embedded watermark tokens if separated by spaces
    """
    if not text:
        return ""
    t = text.strip()
    # Remove common OCR border artifacts
    t = re.sub(r'^[|_—\-~·•*]+|[|_—\-~·•*]+$', '', t).strip()

    # If multiple space-separated tokens exist, drop tokens that match studio watermark patterns
    parts = [p.strip() for p in t.split() if p.strip()]
    if len(parts) > 1:
        filtered_parts = [p for p in parts if not WATERMARK_PATTERN.match(p)]
        if filtered_parts:
            parts = filtered_parts
    t = " ".join(parts).strip()
    return t


def select_main_subtitle_from_ocr_result(
    result: List[Any],
    crop_w: int,
    crop_h: int
) -> Tuple[str, float]:
    """
    Given RapidOCR result [[box, text, score], ...], filters out small corner watermarks
    and low-confidence noise, returning (cleaned_text, average_score).
    """
    if not result:
        return "", 0.0

    candidates = []
    for item in result:
        if not item or len(item) < 3:
            continue
        box, raw_txt, score = item[0], item[1], float(item[2])
        if not raw_txt or score < 0.45:
            continue
        txt = clean_ocr_line(str(raw_txt))
        if not has_meaningful_chinese(txt):
            continue

        # Compute bounding box geometry
        try:
            xs = [pt[0] for pt in box]
            ys = [pt[1] for pt in box]
            bh = max(1.0, max(ys) - min(ys))
            bw = max(1.0, max(xs) - min(xs))
            cx = (min(xs) + max(xs)) / 2.0
            cy = (min(ys) + max(ys)) / 2.0
        except Exception:
            bh, bw, cx, cy = 20.0, 100.0, crop_w / 2.0, crop_h / 2.0

        candidates.append({
            "text": txt,
            "score": score,
            "bh": bh,
            "bw": bw,
            "cx": cx,
            "cy": cy
        })

    if not candidates:
        return "", 0.0

    # Filter out boxes that are significantly smaller in font height than the main subtitle line
    max_bh = max(c["bh"] for c in candidates)
    main_candidates = [
        c for c in candidates
        if c["bh"] >= max_bh * 0.65 and not (len(candidates) > 1 and WATERMARK_PATTERN.match(c["text"]))
    ]
    if not main_candidates:
        main_candidates = candidates

    # Sort left-to-right / top-to-bottom
    main_candidates.sort(key=lambda c: (round(c["cy"] / max(10.0, max_bh * 0.5)), c["cx"]))
    combined_text = clean_ocr_line(" ".join(c["text"] for c in main_candidates))
    avg_score = sum(c["score"] for c in main_candidates) / len(main_candidates)
    return combined_text, avg_score


def text_similarity(str1: str, str2: str) -> float:
    """
    Computes character-based similarity between two strings (0.0 to 1.0).
    """
    s1 = "".join(str1.split()).strip()
    s2 = "".join(str2.split()).strip()
    if not s1 and not s2:
        return 1.0
    if not s1 or not s2:
        return 0.0
    if s1 == s2:
        return 1.0

    # Check containment
    if s1 in s2 or s2 in s1:
        return max(0.75, min(len(s1), len(s2)) / max(len(s1), len(s2)))

    # Character multiset overlap (handles repeated characters better than set)
    c1, c2 = Counter(s1), Counter(s2)
    common = sum((c1 & c2).values())
    return 2.0 * common / (len(s1) + len(s2))


def pick_best_segment_text(observations: List[Tuple[str, float]]) -> str:
    """
    Selects the most reliable OCR text from frame observations within a segment
    using frequency voting + confidence weighting (avoiding 1-frame watermark pollution).
    """
    if not observations:
        return ""
    if len(observations) == 1:
        return observations[0][0]

    counts = Counter()
    score_sums = Counter()
    for txt, sc in observations:
        counts[txt] += 1
        score_sums[txt] += sc

    # Score each unique variant: favor variants that appear in multiple frames,
    # with a slight preference for complete Chinese phrases (up to mode length)
    max_count = max(counts.values())
    best_txt = observations[0][0]
    best_rank = -1.0

    for txt, cnt in counts.items():
        avg_sc = score_sums[txt] / cnt
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', txt))
        # Penalize strings with spaces (often multi-box watermark attachment) if a single-block alternative exists
        space_penalty = 0.85 if (" " in txt and len(counts) > 1) else 1.0
        # If only seen once while another variant is seen multiple times, penalize unless it's much higher confidence
        freq_weight = cnt / max_count
        rank = (freq_weight * 0.65 + avg_sc * 0.35) * space_penalty * min(1.15, 0.85 + chinese_chars * 0.03)
        if rank > best_rank:
            best_rank = rank
            best_txt = txt

    return best_txt


def post_filter_watermarks_and_noise(segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Removes standalone watermark segments (e.g. '梦天动画' at 0.0s) and strips repeated
    watermark substrings from adjacent subtitle segments.
    """
    if not segments:
        return []

    # 1. Identify potential watermark tokens:
    # - Short segments (<= 0.8s) matching WATERMARK_PATTERN
    # - Or short segments whose exact text is embedded inside another longer segment
    watermark_tokens = set()
    all_texts = [s["text"] for s in segments]

    for s in segments:
        txt = s["text"].strip()
        dur = float(s["end"]) - float(s["start"])
        if WATERMARK_PATTERN.match(txt) and dur <= 1.2:
            watermark_tokens.add(txt)
        elif 2 <= len(txt) <= 5 and dur <= 0.6:
            # Check if this short text appears as prefix/suffix inside another longer segment
            embedded_count = sum(1 for other in all_texts if other != txt and txt in other)
            if embedded_count >= 1:
                watermark_tokens.add(txt)

    cleaned_segments = []
    for s in segments:
        txt = s["text"].strip()
        # Strip known watermark tokens from longer sentences
        for wm in watermark_tokens:
            if txt != wm and wm in txt:
                txt = txt.replace(wm, "").strip()

        txt = clean_ocr_line(txt)
        if not has_meaningful_chinese(txt):
            continue

        # Skip standalone watermark segments
        if txt in watermark_tokens and (float(s["end"]) - float(s["start"]) <= 1.2):
            logger.info(f"Đã lọc bỏ watermark/logo: '{txt}' ({s['start']}s - {s['end']}s)")
            continue

        # Skip 1-character transient flashes (<= 0.5s)
        chinese_len = len(re.findall(r'[\u4e00-\u9fff]', txt))
        if chinese_len <= 1 and (float(s["end"]) - float(s["start"]) <= 0.5):
            continue

        cleaned_segments.append({
            **s,
            "text": txt
        })

    return cleaned_segments


def extract_subtitles_from_video(
    video_path: str,
    mask_box: Dict[str, Any],
    sample_rate_fps: float = 2.0,
    progress_callback=None
) -> List[Dict[str, Any]]:
    """
    Scans video frames inside mask_box coordinates using GPU-accelerated RapidOCR,
    with hardware-accelerated skip decoding, binary text mask caching, and timeline grouping.
    - mask_box: {"x": float %, "y": float %, "w": float %, "h": float %}
    """
    try:
        import cv2
    except ImportError:
        raise ImportError(
            "Thư viện OpenCV chưa được cài đặt. "
            "Vui lòng cài đặt bằng lệnh: pip install opencv-python-headless"
        )

    ocr = get_ocr_engine()

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Không thể mở file video: {video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    video_fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    logger.info(f"Video info: {video_width}x{video_height}, FPS: {video_fps}, Total frames: {total_frames}")

    # Calculate pixel crop box from percentages
    x_pct = max(0.0, min(100.0, float(mask_box.get("x", 10.0))))
    y_pct = max(0.0, min(100.0, float(mask_box.get("y", 80.0))))
    w_pct = max(5.0, min(100.0, float(mask_box.get("w", 80.0))))
    h_pct = max(3.0, min(100.0, float(mask_box.get("h", 12.0))))

    x1 = int(x_pct * video_width / 100.0)
    y1 = int(y_pct * video_height / 100.0)
    x2 = min(video_width, int((x_pct + w_pct) * video_width / 100.0))
    y2 = min(video_height, int((y_pct + h_pct) * video_height / 100.0))
    crop_w = max(1, x2 - x1)
    crop_h = max(1, y2 - y1)

    logger.info(f"Crop coordinates: X1={x1}, Y1={y1}, X2={x2}, Y2={y2}")

    frame_step = max(1, int(round(video_fps / sample_rate_fps)))
    effective_fps = video_fps / frame_step
    frame_dur = 1.0 / effective_fps
    raw_detections: List[Tuple[float, str, float]] = []

    frame_idx = 0
    prev_binary = None
    prev_text = ""
    prev_score = 0.0

    while True:
        # Fast grab: Skip software decompression for un-sampled frames
        if frame_idx % frame_step != 0:
            if not cap.grab():
                break
            frame_idx += 1
            continue

        ret, frame = cap.read()
        if not ret:
            break

        timestamp = frame_idx / video_fps
        cropped = frame[y1:y2, x1:x2]

        if cropped.size > 0:
            # 1. Fast binary text-mask activity check (< 0.05ms)
            gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
            _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
            white_ratio = float(np.mean(binary == 255))

            if white_ratio < 0.005:
                # Blank subtitle region (no bright text pixels)
                prev_binary = binary
                prev_text = ""
                prev_score = 0.0
            elif prev_binary is not None and prev_text:
                # Check binary difference vs previous frame
                diff_pct = float(np.mean(prev_binary != binary)) * 100.0
                if diff_pct < 4.2:
                    # Cache hit: Subtitle text is identical, skip deep learning model
                    raw_detections.append((timestamp, prev_text, prev_score))
                else:
                    # Cache miss: Subtitle changed -> run RapidOCR
                    result, _ = ocr(cropped)
                    text, avg_score = select_main_subtitle_from_ocr_result(result, crop_w, crop_h)
                    if text:
                        raw_detections.append((timestamp, text, avg_score))
                        prev_text = text
                        prev_score = avg_score
                    else:
                        prev_text = ""
                        prev_score = 0.0
                    prev_binary = binary
            else:
                # First text frame -> run RapidOCR
                result, _ = ocr(cropped)
                text, avg_score = select_main_subtitle_from_ocr_result(result, crop_w, crop_h)
                if text:
                    raw_detections.append((timestamp, text, avg_score))
                    prev_text = text
                    prev_score = avg_score
                else:
                    prev_text = ""
                    prev_score = 0.0
                prev_binary = binary

        if progress_callback and total_frames > 0:
            pct = min(100.0, (frame_idx / total_frames) * 100)
            progress_callback(pct)

        frame_idx += 1

    cap.release()
    logger.info(f"Quét xong. Tìm thấy {len(raw_detections)} frame có phụ đề hợp lệ.")

    if not raw_detections:
        return []

    # Group consecutive frames into distinct subtitle segments
    segments = []
    current_start = raw_detections[0][0]
    current_end = raw_detections[0][0] + frame_dur
    current_obs: List[Tuple[str, float]] = [(raw_detections[0][1], raw_detections[0][2])]

    for timestamp, text, score in raw_detections[1:]:
        time_gap = timestamp - current_end
        rep_text = pick_best_segment_text(current_obs)
        similarity = text_similarity(rep_text, text)

        if similarity >= 0.68 and time_gap <= 0.65:
            current_end = timestamp + frame_dur
            current_obs.append((text, score))
        else:
            if (current_end - current_start) >= 0.35:
                segments.append({
                    "start": round(current_start, 2),
                    "end": round(min(current_end, timestamp), 2),
                    "text": pick_best_segment_text(current_obs)
                })
            current_start = timestamp
            current_end = timestamp + frame_dur
            current_obs = [(text, score)]

    if (current_end - current_start) >= 0.35:
        segments.append({
            "start": round(current_start, 2),
            "end": round(current_end, 2),
            "text": pick_best_segment_text(current_obs)
        })

    segments = post_filter_watermarks_and_noise(segments)
    logger.info(f"Gom cụm và lọc sạch thành công {len(segments)} đoạn phụ đề.")
    return segments
