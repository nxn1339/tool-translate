import os
import uuid
import shutil
import logging
import json
import hashlib
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, BackgroundTasks, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.downloader import download_bilibili_video
from app.translator import (
    translate_video_audio,
    batch_translate_texts,
    preprocess_chinese_segments,
    export_segments_to_srt_string,
    import_srt_to_segments
)
from app.tts import generate_tts_for_segments
from app.merger import merge_audio_segments_to_video, generate_preview_audio_track

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Video Dubber Studio")


@app.on_event("startup")
def startup_event():
    import asyncio
    import sys

    # Silence ProactorBasePipeTransport connection lost logs on Windows
    if sys.platform == "win32":
        try:
            loop = asyncio.get_event_loop()
            old_handler = loop.get_exception_handler()

            def custom_exception_handler(loop, context):
                exception = context.get("exception")
                if (
                    isinstance(exception, ConnectionResetError)
                    or "ConnectionResetError" in str(exception)
                    or "_call_connection_lost" in context.get("message", "")
                ):
                    return
                if old_handler:
                    old_handler(loop, context)
                else:
                    loop.default_exception_handler(context)

            loop.set_exception_handler(custom_exception_handler)
            logger.info("Custom asyncio exception handler set to suppress WinError 10054 logs.")
        except Exception as e:
            logger.warning(f"Could not set custom asyncio exception handler: {e}")

    cleanup_old_tasks(max_age_hours=24)


# Define base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMP_DIR = os.path.join(BASE_DIR, "app", "temp")
STATIC_DIR = os.path.join(BASE_DIR, "app", "static")
PROJECTS_DIR = os.path.join(BASE_DIR, "app", "projects")

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(PROJECTS_DIR, exist_ok=True)


def get_project_dir(project_id: str, create: bool = True) -> str:
    """
    Returns the persistent project directory in PROJECTS_DIR.
    Migrates legacy projects from TEMP_DIR if present.
    """
    p_dir = os.path.join(PROJECTS_DIR, project_id)
    if not os.path.exists(p_dir):
        temp_dir = os.path.join(TEMP_DIR, project_id)
        if os.path.exists(temp_dir):
            try:
                shutil.move(temp_dir, p_dir)
            except Exception:
                return temp_dir
    if create:
        os.makedirs(p_dir, exist_ok=True)
    return p_dir


def get_project_meta_path(project_id: str) -> str:
    return os.path.join(get_project_dir(project_id), "project.json")


def load_project_meta(project_id: str) -> Dict[str, Any]:
    project_dir = get_project_dir(project_id, create=False)
    meta_path = os.path.join(project_dir, "project.json")
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Error reading project.json for {project_id}: {e}")

    from datetime import datetime
    now_iso = datetime.now().isoformat()
    return {
        "id": project_id,
        "name": f"Dự án {datetime.now().strftime('%d/%m %H:%M')}",
        "created_at": now_iso,
        "updated_at": now_iso,
        "current_step": 1,
        "completed_steps": [],
        "video_url": "",
        "bilibili_cookie": None,
        "mode": "ocr",
        "mask_box": {"x": 10, "y": 78, "w": 80, "h": 14, "enabled": True, "style": "blur"},
        "sub_box": {"x": 10, "y": 78, "w": 80, "h": 14},
        "sub_styling": {
            "font_size": 48,
            "font_name": "Nunito",
            "primary_color": "#FFFFFF",
            "outline_color": "#000000",
            "outline_width": 4.0,
            "box_style": "outline",
            "back_color": "#000000",
            "box_opacity": 0.75,
            "bold": True
        },
        "voice": "capcut_cogaithoatngon",
        "bg_volume": 0.15,
        "tts_volume": 1.0,
        "logo_box": {
            "enabled": False,
            "x": 80.0,
            "y": 5.0,
            "w": 15.0,
            "h": 10.0,
            "opacity": 1.0,
            "keep_aspect": True,
            "filename": None,
            "image_path": None
        },
        "status": "draft"
    }


def save_project_meta(project_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    from datetime import datetime
    meta = load_project_meta(project_id)
    meta.update(updates)
    meta["updated_at"] = datetime.now().isoformat()
    meta_path = get_project_meta_path(project_id)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    return meta


def cleanup_old_tasks(max_age_hours: int = 24):
    """
    Cleans up temporary files in TEMP_DIR older than max_age_hours.
    Note: PROJECTS_DIR is persistent and is never deleted automatically.
    """
    import time
    try:
        now = time.time()
        if os.path.exists(TEMP_DIR):
            for item in os.listdir(TEMP_DIR):
                if item == "previews":
                    continue
                item_path = os.path.join(TEMP_DIR, item)
                if os.path.isdir(item_path):
                    if now - os.path.getmtime(item_path) > max_age_hours * 3600:
                        shutil.rmtree(item_path, ignore_errors=True)
                        logger.info(f"Cleaned up expired temp directory: {item}")
    except Exception as e:
        logger.warning(f"Error during temp directory cleanup: {e}")


# In-memory cache of live project job progress
projects_db: Dict[str, Dict[str, Any]] = {}


def get_project_logs_path(project_id: str) -> str:
    return os.path.join(get_project_dir(project_id, create=False), "project_logs.json")


def get_project_logs(project_id: str) -> List[str]:
    if project_id in projects_db and projects_db[project_id].get("logs"):
        return projects_db[project_id]["logs"]
    logs_path = get_project_logs_path(project_id)
    if os.path.exists(logs_path):
        try:
            with open(logs_path, "r", encoding="utf-8") as f:
                logs = json.load(f)
                if isinstance(logs, list):
                    if project_id not in projects_db:
                        projects_db[project_id] = {}
                    projects_db[project_id]["logs"] = logs
                    return logs
        except Exception as e:
            logger.warning(f"Error reading project_logs.json for {project_id}: {e}")
    return []


def append_project_log(project_id: str, message: str, level: str = "INFO"):
    from datetime import datetime
    now_str = datetime.now().strftime("%H:%M:%S")
    clean_line = f"[{now_str}] [{level}] {message}"
    if project_id not in projects_db:
        projects_db[project_id] = {"logs": []}
    if "logs" not in projects_db[project_id]:
        projects_db[project_id]["logs"] = get_project_logs(project_id)
    projects_db[project_id]["logs"].append(clean_line)
    if len(projects_db[project_id]["logs"]) > 300:
        projects_db[project_id]["logs"] = projects_db[project_id]["logs"][-300:]

    try:
        p_dir = get_project_dir(project_id, create=False)
        if os.path.exists(p_dir):
            logs_path = os.path.join(p_dir, "project_logs.json")
            with open(logs_path, "w", encoding="utf-8") as f:
                json.dump(projects_db[project_id]["logs"], f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.debug(f"Failed to persist logs to disk for {project_id}: {e}")



class ProjectCreateRequest(BaseModel):
    name: Optional[str] = None
    video_url: Optional[str] = None


class ProjectUpdateRequest(BaseModel):
    name: Optional[str] = None
    current_step: Optional[int] = None
    completed_steps: Optional[List[int]] = None
    video_url: Optional[str] = None
    bilibili_cookie: Optional[str] = None
    mode: Optional[str] = None
    mask_box: Optional[Dict[str, Any]] = None
    sub_box: Optional[Dict[str, Any]] = None
    sub_styling: Optional[Dict[str, Any]] = None
    voice: Optional[str] = None
    bg_volume: Optional[float] = None
    tts_volume: Optional[float] = None
    auto_extend_video: Optional[bool] = None
    logo_box: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class ProjectDownloadRequest(BaseModel):
    url: str
    bilibili_cookie: Optional[str] = None
    project_id: Optional[str] = None


class ProjectTranscribeRequest(BaseModel):
    mode: str = "ocr"  # "ocr" or "whisper"
    mask_box: Optional[Dict[str, Any]] = None
    source_lang: str = "Chinese"


AUDIO_META_KEYS = ("tts_error", "tts_raw_hash", "audio_path", "actual_duration", "speed_ratio")


def purge_project_audio(project_dir: str) -> int:
    """Deletes every generated TTS/preview audio file of a project so no stale voice can be mixed in."""
    removed = 0
    if not os.path.isdir(project_dir):
        return removed
    for fname in os.listdir(project_dir):
        is_seg_audio = fname.startswith(("seg_", "_temp_")) and fname.endswith((".wav", ".mp3"))
        if is_seg_audio or fname in ("preview_dubbed.mp3", "dubbed_voice_track.wav"):
            try:
                os.remove(os.path.join(project_dir, fname))
                removed += 1
            except Exception:
                pass
    return removed


def strip_audio_meta(segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Removes audio references/cache keys from segments (in place) so TTS is regenerated from scratch."""
    for s in segments:
        for k in AUDIO_META_KEYS:
            s.pop(k, None)
    return segments


class ProjectUpdateSegmentsRequest(BaseModel):
    segments: List[Dict[str, Any]]


class ProjectGenerateTTSRequest(BaseModel):
    voice: Optional[str] = "capcut_cogaithoatngon"
    failed_only: Optional[bool] = False
    use_original: Optional[bool] = False


class ProjectImportSrtRequest(BaseModel):
    srt_content: str
    target_field: str = "translation"


class ProjectTranslateRequest(BaseModel):
    engine: Optional[str] = "groq"
    custom_srt: Optional[str] = None
    failed_only: Optional[bool] = False


class SettingsUpdateRequest(BaseModel):
    translation_engine: Optional[str] = None
    groq_api_key: Optional[str] = None
    groq_model: Optional[str] = None
    gemini_api_key: Optional[str] = None
    gemini_model: Optional[str] = None


class ProjectRenderRequest(BaseModel):
    voice: str = "capcut_cogaithoatngon"
    bg_volume: float = 0.15
    tts_volume: float = 1.0
    mask_box: Optional[Dict[str, Any]] = None
    sub_box: Optional[Dict[str, Any]] = None
    sub_styling: Optional[Dict[str, Any]] = None
    burn_subtitles: bool = True
    segments: Optional[List[Dict[str, Any]]] = None
    auto_extend_video: bool = False
    logo_box: Optional[Dict[str, Any]] = None


class TTSFreeRequest(BaseModel):
    text: str
    voice: str = "capcut_cogaithoatngon"
    rate: str = "+0%"


class TTSPreviewRequest(BaseModel):
    voice: Optional[str] = "capcut_cogaithoatngon"
    text: Optional[str] = None


# ==========================================
# BACKGROUND WORKERS FOR STUDIO PIPELINE
# ==========================================

def process_project_download_worker(project_id: str, url: str, bilibili_cookie: Optional[str] = None):
    project_dir = get_project_dir(project_id)
    input_video_path = os.path.join(project_dir, "input_video.mp4")
    input_audio_path = os.path.join(project_dir, "input_audio.wav")

    try:
        logger.info(f"[{project_id}] Step 1: Downloading video from {url}...")
        existing_logs = projects_db.get(project_id, {}).get("logs", [])
        projects_db[project_id] = {
            "status": "downloading",
            "progress": 5,
            "message": "Đang kết nối và tải video...",
            "logs": existing_logs
        }
        append_project_log(project_id, f"Bắt đầu tác vụ tải video từ URL: {url}", level="INFO")
        save_project_meta(project_id, {
            "video_url": url,
            "bilibili_cookie": bilibili_cookie,
            "status": "downloading",
            "current_step": 1
        })

        def download_progress(pct, msg=None):
            val = min(99, max(0, int(round(pct))))
            projects_db[project_id]["progress"] = val
            if msg:
                projects_db[project_id]["message"] = msg
            else:
                projects_db[project_id]["message"] = f"Đang tải video... ({val}%)"

        def download_log(msg, level="INFO"):
            append_project_log(project_id, msg, level=level)

        download_bilibili_video(
            url,
            input_video_path,
            input_audio_path,
            progress_callback=download_progress,
            bilibili_cookie=bilibili_cookie,
            log_callback=download_log
        )

        append_project_log(project_id, "Tải và trích xuất video hoàn tất! Sẵn sàng trên Studio.", level="SUCCESS")
        current_logs = projects_db.get(project_id, {}).get("logs", [])
        projects_db[project_id] = {
            "status": "downloaded",
            "progress": 100,
            "message": "Tải video thành công! Video đã sẵn sàng trên màn hình xem trước.",
            "video_url": f"/api/project/{project_id}/video-raw",
            "logs": current_logs
        }
        save_project_meta(project_id, {
            "status": "downloaded",
            "video_url": url,
            "bilibili_cookie": bilibili_cookie,
            "current_step": 2,
            "completed_steps": [1]
        })
        logger.info(f"[{project_id}] Step 1: Download completed.")
    except Exception as e:
        logger.error(f"[{project_id}] Download failed: {str(e)}", exc_info=True)
        append_project_log(project_id, f"Tải video thất bại: {str(e)}", level="ERROR")
        current_logs = projects_db.get(project_id, {}).get("logs", [])
        projects_db[project_id] = {
            "status": "download_failed",
            "progress": 100,
            "message": "Tải video thất bại.",
            "error": str(e),
            "logs": current_logs
        }
        save_project_meta(project_id, {
            "status": "download_failed"
        })


def process_project_transcribe_worker(
    project_id: str,
    mode: str = "ocr",
    mask_box: Optional[Dict[str, Any]] = None,
    source_lang: str = "Chinese"
):
    project_dir = get_project_dir(project_id)
    input_video_path = os.path.join(project_dir, "input_video.mp4")
    input_audio_path = os.path.join(project_dir, "input_audio.wav")
    segments_json_path = os.path.join(project_dir, "segments.json")

    if not os.path.exists(input_video_path):
        projects_db[project_id] = {
            "status": "transcribe_failed",
            "progress": 100,
            "message": "Chưa tải video gốc.",
            "error": "Input video not found."
        }
        return

    try:
        # Clean up stale audio files from any previous scan to prevent orphaned segments
        for fname in os.listdir(project_dir):
            if (fname.startswith("seg_") and fname.endswith((".wav", ".mp3"))) or fname in ("preview_dubbed.mp3", "dubbed_voice_track.wav"):
                try:
                    os.remove(os.path.join(project_dir, fname))
                except Exception:
                    pass

        if mode == "ocr":
            logger.info(f"[{project_id}] Step 2: Running OCR...")
            existing_logs = projects_db.get(project_id, {}).get("logs", [])
            projects_db[project_id] = {
                "status": "transcribing",
                "progress": 15,
                "message": "Đang quét nhận diện chữ phụ đề video (OCR)...",
                "logs": existing_logs
            }
            append_project_log(project_id, "Bắt đầu quét phụ đề tiếng Trung (OCR)...", level="INFO")
            from app.ocr import extract_subtitles_from_video

            def ocr_progress(pct):
                projects_db[project_id]["progress"] = int(15 + (pct * 0.80))
                projects_db[project_id]["message"] = f"Đang quét chữ phụ đề video... ({pct:.0f}%)"

            raw_segments = extract_subtitles_from_video(
                input_video_path,
                mask_box or {"x": 10.0, "y": 78.0, "w": 80.0, "h": 14.0},
                sample_rate_fps=2.0,
                progress_callback=ocr_progress
            )
            if not raw_segments:
                raise ValueError("Không phát hiện được chữ phụ đề trong vùng khoanh chọn. Vui lòng kiểm tra lại khung khoanh vùng hoặc chuyển sang chế độ Whisper.")

            raw_texts = [s["text"] for s in raw_segments]
            cleaned_zh, _ = preprocess_chinese_segments(raw_texts)
            segments = []
            for idx, (seg, cz) in enumerate(zip(raw_segments, cleaned_zh)):
                segments.append({
                    "id": idx + 1,
                    "start": round(seg["start"], 2),
                    "end": round(seg["end"], 2),
                    "text": cz,
                    "translation": ""
                })
        else:
            logger.info(f"[{project_id}] Step 2: Running Whisper...")
            projects_db[project_id] = {
                "status": "transcribing",
                "progress": 20,
                "message": "Đang nhận diện giọng nói bằng Whisper..."
            }
            raw_segments = translate_video_audio(input_audio_path, source_lang)
            if not raw_segments:
                raise ValueError("Không tìm thấy hoặc không nhận dạng được giọng nói nào trong video.")
            segments = []
            for idx, seg in enumerate(raw_segments):
                segments.append({
                    "id": idx + 1,
                    "start": round(seg.get("start", 0.0), 2),
                    "end": round(seg.get("end", 0.0), 2),
                    "text": seg.get("text", ""),
                    "translation": ""
                })

        with open(segments_json_path, "w", encoding="utf-8") as f:
            json.dump(segments, f, ensure_ascii=False, indent=2)

        orig_segments_json_path = os.path.join(project_dir, "segments_original.json")
        with open(orig_segments_json_path, "w", encoding="utf-8") as of:
            json.dump(segments, of, ensure_ascii=False, indent=2)

        orig_segments_json_path = os.path.join(project_dir, "segments_original.json")
        with open(orig_segments_json_path, "w", encoding="utf-8") as f:
            json.dump(segments, f, ensure_ascii=False, indent=2)

        save_project_meta(project_id, {
            "status": "transcribed",
            "mode": mode,
            "mask_box": mask_box,
            "current_step": 3,
            "completed_steps": [1, 2]
        })

        append_project_log(project_id, f"Trích xuất thành công {len(segments)} câu phụ đề gốc! Chuyển sang Bước 3 để dịch hoặc nạp file SRT.", level="SUCCESS")
        existing_logs = projects_db.get(project_id, {}).get("logs", [])
        projects_db[project_id] = {
            "status": "transcribed",
            "progress": 100,
            "message": f"Trích xuất thành công {len(segments)} câu phụ đề gốc!",
            "segments": segments,
            "logs": existing_logs
        }
        logger.info(f"[{project_id}] Step 2: OCR/Transcribe completed with {len(segments)} segments.")
    except Exception as e:
        logger.error(f"[{project_id}] Transcribe failed: {str(e)}", exc_info=True)
        projects_db[project_id] = {
            "status": "transcribe_failed",
            "progress": 100,
            "message": "Quét phụ đề thất bại.",
            "error": str(e)
        }


def process_project_translate_worker(
    project_id: str,
    engine: str = "groq",
    custom_srt: Optional[str] = None,
    failed_only: bool = False
):
    """
    Step 3: Translates segments using Groq AI / Gemini AI / Google Translate, OR applies custom imported SRT.
    Supports failed_only=True to only retry segments that failed or are missing translations.
    """
    project_dir = get_project_dir(project_id)
    segments_json_path = os.path.join(project_dir, "segments.json")
    if not os.path.exists(segments_json_path):
        projects_db[project_id] = {
            "status": "translate_failed",
            "progress": 100,
            "message": "Chưa có dữ liệu phụ đề gốc từ Bước 2.",
            "error": "segments.json not found"
        }
        return

    try:
        with open(segments_json_path, "r", encoding="utf-8") as f:
            segments = json.load(f)

        if not segments:
            raise ValueError("Danh sách phụ đề rỗng. Vui lòng quét phụ đề ở Bước 2 trước.")

        existing_logs = projects_db.get(project_id, {}).get("logs", [])
        action_name = "Dịch lại các câu lỗi" if failed_only else "Dịch phụ đề"
        projects_db[project_id] = {
            "status": "translating",
            "progress": 20,
            "message": f"Đang tiến hành {action_name.lower()}...",
            "logs": existing_logs
        }

        if not failed_only:
            # Full re-translation: wipe previous voice files so old audio can never be mixed with new text
            purged = purge_project_audio(project_dir)
            strip_audio_meta(segments)
            if purged:
                append_project_log(project_id, f"Đã xóa {purged} file âm thanh cũ trước khi tạo lại bản dịch.", level="INFO")

        if custom_srt and custom_srt.strip():
            append_project_log(project_id, "Đang khớp file/nội dung SRT tiếng Việt từ bên ngoài...", level="INFO")
            from app.translator import import_srt_to_segments
            updated_segments = import_srt_to_segments(
                custom_srt.strip(),
                existing_segments=segments,
                target_field="translation"
            )
            segments = updated_segments
            for s in segments:
                s.pop("translation_error", None)
            append_project_log(project_id, f"Khớp thành công {len(segments)} câu phụ đề từ SRT ngoài!", level="SUCCESS")
        else:
            if engine in ("groq", "gemini", "google"):
                from app.gemini_translator import save_settings
                save_settings({"translation_engine": engine})

            from app.translator import preprocess_chinese_segments, batch_translate_texts
            from app.hanviet import detect_untranslated_foreign_chars

            if failed_only:
                # Clear stale error flags on segments that have no source text
                for s in segments:
                    if not (s.get("text") or "").strip():
                        s.pop("translation_error", None)
                        s.pop("untranslated_warning", None)
                        s.pop("untranslated_chars", None)

                target_indices = [
                    idx for idx, s in enumerate(segments)
                    if (s.get("text") or "").strip() and (
                        s.get("translation_error")
                        or not (s.get("translation") or "").strip()
                        or bool(detect_untranslated_foreign_chars(s.get("translation") or ""))
                    )
                ]
                if not target_indices:
                    append_project_log(project_id, "Không có câu lỗi hoặc sót tiếng Trung nào cần dịch lại. Toàn bộ phụ đề đã hợp lệ!", level="INFO")
                    with open(segments_json_path, "w", encoding="utf-8") as f:
                        json.dump(segments, f, ensure_ascii=False, indent=2)
                    projects_db[project_id]["status"] = "translated"
                    projects_db[project_id]["progress"] = 100
                    projects_db[project_id]["message"] = "Không có câu lỗi nào cần dịch lại."
                    projects_db[project_id]["segments"] = segments
                    projects_db[project_id]["failed_trans_count"] = 0
                    return

                append_project_log(project_id, f"Bắt đầu dịch lại {len(target_indices)} câu bị lỗi/sót tiếng Trung bằng AI ({engine.upper()})...", level="INFO")
                projects_db[project_id]["message"] = f"Đang dịch lại {len(target_indices)} câu lỗi bằng {engine.upper()}..."
                projects_db[project_id]["progress"] = 40

                target_raw_texts = [segments[idx].get("text", "") for idx in target_indices]
                target_durations = [max(0.2, float(segments[idx].get("end", 0.0)) - float(segments[idx].get("start", 0.0))) for idx in target_indices]
                cleaned_zh, _ = preprocess_chinese_segments(target_raw_texts)
                translations = batch_translate_texts(
                    cleaned_zh,
                    source_code="zh-CN",
                    target_code="vi",
                    durations=target_durations
                )

                recovered_count = 0
                for idx, trans in zip(target_indices, translations):
                    if trans and trans.strip():
                        clean_tr = trans.strip()
                        segments[idx]["translation"] = clean_tr
                        segments[idx].pop("translation_error", None)
                        segments[idx].pop("tts_raw_hash", None)
                        foreign_left = detect_untranslated_foreign_chars(clean_tr)
                        if foreign_left:
                            segments[idx]["untranslated_warning"] = True
                            segments[idx]["untranslated_chars"] = "".join(foreign_left)
                        else:
                            segments[idx].pop("untranslated_warning", None)
                            segments[idx].pop("untranslated_chars", None)
                            recovered_count += 1
                    else:
                        segments[idx]["translation_error"] = True

                append_project_log(project_id, f"Dịch lại hoàn tất: Phục hồi sạch {recovered_count}/{len(target_indices)} câu!", level="SUCCESS" if recovered_count == len(target_indices) else "WARNING")
            else:
                append_project_log(project_id, f"Bắt đầu dịch tự động {len(segments)} câu bằng AI ({engine.upper()})...", level="INFO")
                projects_db[project_id]["message"] = f"Đang dịch chuẩn ngữ cảnh bằng {engine.upper()}..."
                projects_db[project_id]["progress"] = 40

                raw_texts = [s.get("text", "") for s in segments]
                durations = [max(0.2, float(s.get("end", 0.0)) - float(s.get("start", 0.0))) for s in segments]
                cleaned_zh, _ = preprocess_chinese_segments(raw_texts)
                translations = batch_translate_texts(
                    cleaned_zh,
                    source_code="zh-CN",
                    target_code="vi",
                    durations=durations
                )
                for idx, (seg, trans) in enumerate(zip(segments, translations)):
                    if not (seg.get("text") or "").strip():
                        seg.pop("translation_error", None)
                        seg.pop("untranslated_warning", None)
                        seg.pop("untranslated_chars", None)
                        continue
                    if trans and trans.strip():
                        clean_tr = trans.strip()
                        seg["translation"] = clean_tr
                        seg.pop("translation_error", None)
                        foreign_left = detect_untranslated_foreign_chars(clean_tr)
                        if foreign_left:
                            seg["untranslated_warning"] = True
                            seg["untranslated_chars"] = "".join(foreign_left)
                        else:
                            seg.pop("untranslated_warning", None)
                            seg.pop("untranslated_chars", None)
                    else:
                        seg["translation"] = ""
                        seg["translation_error"] = True
                    seg.pop("tts_raw_hash", None)

                success_count = sum(1 for s in segments if (s.get("text") or "").strip() and s.get("translation", "").strip() and not s.get("translation_error") and not s.get("untranslated_warning"))
                append_project_log(project_id, f"Dịch tự động hoàn tất: {success_count}/{len(segments)} câu thành công!", level="SUCCESS" if success_count == len(segments) else "WARNING")

        failed_trans_count = sum(
            1 for s in segments
            if (s.get("text") or "").strip() and (
                s.get("translation_error")
                or not (s.get("translation") or "").strip()
                or bool(detect_untranslated_foreign_chars(s.get("translation") or ""))
            )
        )
        projects_db[project_id]["failed_trans_count"] = failed_trans_count

        with open(segments_json_path, "w", encoding="utf-8") as f:
            json.dump(segments, f, ensure_ascii=False, indent=2)

        orig_segments_json_path = os.path.join(project_dir, "segments_original.json")
        with open(orig_segments_json_path, "w", encoding="utf-8") as of:
            json.dump(segments, of, ensure_ascii=False, indent=2)

        # Pre-generate preview dubbed audio track only on full translation (skip blocking TTS on failed_only retry)
        if not failed_only:
            projects_db[project_id]["progress"] = 80
            projects_db[project_id]["message"] = "Đang khởi tạo giọng đọc lồng tiếng xem trước..."
            try:
                meta = load_project_meta(project_id)
                voice = meta.get("voice", "capcut_cogaithoatngon")
                from app.merger import generate_preview_audio_track
                generate_preview_audio_track(project_dir, segments, voice=voice)
                if os.path.exists(segments_json_path):
                    with open(segments_json_path, "r", encoding="utf-8") as f:
                        segments = json.load(f)
                logger.info(f"[{project_id}] Pre-generated preview dubbed audio track successfully.")
            except Exception as e_audio:
                logger.warning(f"[{project_id}] Could not pre-generate preview audio: {e_audio}")

        save_project_meta(project_id, {
            "status": "translated",
            "current_step": 4,
            "completed_steps": [1, 2, 3]
        })

        if failed_trans_count > 0:
            finish_msg = f"Đã dịch xong. Còn {failed_trans_count} câu chưa dịch được. Bạn có thể bấm 'Dịch lại câu lỗi' để thử lại."
            append_project_log(project_id, f"[Cảnh báo] Còn {failed_trans_count} câu chưa có bản dịch hoàn chỉnh.", level="WARNING")
        else:
            finish_msg = f"Dịch và khớp thành công {len(segments)} câu phụ đề!"
            append_project_log(project_id, f"Dịch & tạo giọng đọc xem trước thành công cho toàn bộ {len(segments)} câu!", level="SUCCESS")

        existing_logs = projects_db.get(project_id, {}).get("logs", [])
        projects_db[project_id] = {
            "status": "translated",
            "progress": 100,
            "message": finish_msg,
            "segments": segments,
            "failed_trans_count": failed_trans_count,
            "logs": existing_logs
        }
        logger.info(f"[{project_id}] Step 3: Translate completed with {len(segments)} segments ({failed_trans_count} failed).")
    except Exception as e:
        logger.error(f"[{project_id}] Translate failed: {str(e)}", exc_info=True)
        projects_db[project_id] = {
            "status": "translate_failed",
            "progress": 100,
            "message": "Dịch phụ đề thất bại.",
            "error": str(e)
        }


def process_project_render_worker(
    project_id: str,
    voice: str,
    bg_volume: float,
    tts_volume: float,
    mask_box: Optional[Dict[str, Any]],
    sub_box: Optional[Dict[str, Any]],
    sub_styling: Optional[Dict[str, Any]],
    burn_subtitles: bool,
    segments: Optional[List[Dict[str, Any]]] = None,
    auto_extend_video: bool = False,
    logo_box: Optional[Dict[str, Any]] = None
):
    project_dir = get_project_dir(project_id)
    input_video_path = os.path.join(project_dir, "input_video.mp4")
    output_video_path = os.path.join(project_dir, "output_dubbed.mp4")
    segments_json_path = os.path.join(project_dir, "segments.json")

    if segments is not None and len(segments) > 0:
        with open(segments_json_path, "w", encoding="utf-8") as f:
            json.dump(segments, f, ensure_ascii=False, indent=2)

        orig_segments_json_path = os.path.join(project_dir, "segments_original.json")
        with open(orig_segments_json_path, "w", encoding="utf-8") as of:
            json.dump(segments, of, ensure_ascii=False, indent=2)

        orig_segments_json_path = os.path.join(project_dir, "segments_original.json")
        with open(orig_segments_json_path, "w", encoding="utf-8") as f:
            json.dump(segments, f, ensure_ascii=False, indent=2)
    elif os.path.exists(segments_json_path):
        with open(segments_json_path, "r", encoding="utf-8") as f:
            segments = json.load(f)
    else:
        projects_db[project_id] = {
            "status": "render_failed",
            "progress": 100,
            "message": "Không tìm thấy danh sách phụ đề.",
            "error": "No segments available."
        }
        return

    try:
        append_project_log(project_id, f"[INFO] [Xuất Video] Bắt đầu xuất video hoàn chỉnh (Giọng: {voice}, Auto-extend: {auto_extend_video})...")
        logger.info(f"[{project_id}] Step 5: Generating TTS for {len(segments)} segments (voice={voice}, auto_extend={auto_extend_video})...")
        projects_db[project_id] = {
            "status": "rendering",
            "progress": 25,
            "message": "Đang khởi tạo giọng đọc AI lồng tiếng..."
        }
        append_project_log(project_id, f"[INFO] [Xuất Video] Kiểm tra và đồng bộ {len(segments)} câu thoại...")
        updated_segments = generate_tts_for_segments(
            segments,
            voice,
            project_dir,
            auto_extend_video=auto_extend_video
        )
        try:
            with open(segments_json_path, "w", encoding="utf-8") as f:
                json.dump(updated_segments, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

        # Resolve logo_box image_path if enabled
        resolved_logo_box = None
        if logo_box and logo_box.get("enabled"):
            resolved_logo_box = dict(logo_box)
            img_p = resolved_logo_box.get("image_path")
            if not img_p or not os.path.exists(img_p):
                meta = load_project_meta(project_id)
                meta_logo = meta.get("logo_box", {})
                img_p = meta_logo.get("image_path")
                if not img_p or not os.path.exists(img_p):
                    for ext in (".png", ".jpg", ".jpeg", ".webp", ".svg", ".bmp"):
                        cand = os.path.join(project_dir, f"logo{ext}")
                        if os.path.exists(cand):
                            img_p = cand
                            break
            if img_p and os.path.exists(img_p):
                resolved_logo_box["image_path"] = img_p
                if not resolved_logo_box.get("filename"):
                    resolved_logo_box["filename"] = os.path.basename(img_p)
                append_project_log(project_id, f"[INFO] [Xuất Video] Đã tìm thấy file logo watermark: {os.path.basename(img_p)}")
            else:
                logger.warning(f"[{project_id}] Logo enabled but image file not found. Skipping logo overlay.")
                append_project_log(project_id, "[CẢNH BÁO] [Xuất Video] Bật chèn logo nhưng không tìm thấy file ảnh logo. Bỏ qua chèn logo.")
                resolved_logo_box = None

        logger.info(f"[{project_id}] Step 5: Merging audio, sub, logo and video (auto_extend={auto_extend_video}, has_logo={bool(resolved_logo_box)})...")
        append_project_log(project_id, "[INFO] [Xuất Video] Đang ghép phụ đề, giọng đọc lồng tiếng và logo vào video bằng FFmpeg...")
        projects_db[project_id] = {
            "status": "rendering",
            "progress": 65,
            "message": "Đang ghép lồng tiếng, logo và xử lý phụ đề video..."
        }
        merge_audio_segments_to_video(
            original_video_path=input_video_path,
            segments=updated_segments,
            output_video_path=output_video_path,
            bg_volume=bg_volume,
            tts_volume=tts_volume,
            mask_box=mask_box,
            sub_box=sub_box,
            burn_subtitles=burn_subtitles,
            sub_styling=sub_styling,
            auto_extend_video=auto_extend_video,
            logo_box=resolved_logo_box
        )

        saved_logo_box = resolved_logo_box if resolved_logo_box else logo_box
        if saved_logo_box and not saved_logo_box.get("image_path"):
            meta_existing_logo = load_project_meta(project_id).get("logo_box") or {}
            if meta_existing_logo.get("image_path"):
                saved_logo_box = {
                    **meta_existing_logo,
                    **saved_logo_box,
                    "image_path": meta_existing_logo.get("image_path"),
                    "filename": saved_logo_box.get("filename") or meta_existing_logo.get("filename")
                }

        save_project_meta(project_id, {
            "status": "completed",
            "voice": voice,
            "bg_volume": bg_volume,
            "tts_volume": tts_volume,
            "mask_box": mask_box,
            "sub_box": sub_box,
            "sub_styling": sub_styling,
            "burn_subtitles": burn_subtitles,
            "logo_box": saved_logo_box,
            "auto_extend_video": auto_extend_video,
            "current_step": 6,
            "completed_steps": [1, 2, 3, 4, 5, 6]
        })

        projects_db[project_id] = {
            "status": "completed",
            "progress": 100,
            "message": "Hoàn tất! Video đã sẵn sàng tải về.",
            "video_url": f"/api/project/{project_id}/video-dubbed",
            "download_url": f"/api/project/{project_id}/download",
            "subtitles_url": f"/api/project/{project_id}/subtitles"
        }
        append_project_log(project_id, "[SUCCESS] [Xuất Video] Đã xuất video hoàn tất thành công! Video đã sẵn sàng tải về.")
        logger.info(f"[{project_id}] Step 5: Render completed.")
    except Exception as e:
        logger.error(f"[{project_id}] Render failed: {str(e)}", exc_info=True)
        append_project_log(project_id, f"[LỖI] [Xuất Video] Thất bại: {str(e)}")
        projects_db[project_id] = {
            "status": "render_failed",
            "progress": 100,
            "message": "Xuất video thất bại.",
            "error": str(e)
        }


# ==========================================
# TTS STUDIO & VOICE PREVIEW ENDPOINTS
# ==========================================

@app.post("/api/tts-free")
async def generate_free_tts(request: TTSFreeRequest):
    """
    Generates speech audio on-the-fly for free text input (TTS Studio & Clip Preview).
    """
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Văn bản không được để trống.")

    from app.tts import generate_single_tts, VOICE_PRESETS, LEGACY_VOICE_MAP
    target_key = LEGACY_VOICE_MAP.get(request.voice, request.voice)
    preset = VOICE_PRESETS.get(target_key, VOICE_PRESETS.get("capcut_cogaithoatngon", {})).copy()
    if request.rate:
        preset["rate"] = request.rate

    free_tts_dir = os.path.join(TEMP_DIR, "free_tts")
    os.makedirs(free_tts_dir, exist_ok=True)
    temp_audio = os.path.join(free_tts_dir, f"tts_{uuid.uuid4().hex[:8]}.mp3")

    await generate_single_tts(request.text, preset, temp_audio)
    return FileResponse(
        path=temp_audio,
        media_type="audio/mpeg",
        filename="speech.mp3"
    )


@app.get("/api/preview-voice")
async def preview_voice(voice: str = "capcut_cogaithoatngon"):
    """
    Returns an audio sample previewing the selected TTS voice.
    Caches the generated sample audio in temp/previews so future requests are instant.
    """
    from app.tts import generate_single_tts, VOICE_PRESETS, LEGACY_VOICE_MAP

    target_key = LEGACY_VOICE_MAP.get(voice, voice)
    preset = VOICE_PRESETS.get(target_key, VOICE_PRESETS.get("capcut_cogaithoatngon"))

    preview_dir = os.path.join(TEMP_DIR, "previews")
    os.makedirs(preview_dir, exist_ok=True)
    file_path = os.path.join(preview_dir, f"preview_{target_key}.mp3")

    sample_text = {
        "female_hoaimy": "Xin chào, tôi là Hoài My. Đây là bản nghe thử giọng đọc lồng tiếng của tôi.",
        "male_namminh": "Xin chào, tôi là Nam Minh. Đây là bản nghe thử giọng đọc lồng tiếng của tôi.",
        "capcut_cogaithoatngon": "Xin chào các bạn, tôi là cô gái hoạt ngôn trên CapCut. Chào mừng các bạn đến với kênh của mình!",
        "capcut_thanhnientutin": "Chào anh em, hôm nay chúng ta cùng recap bộ phim siêu kịch tính này nhé!",
        "capcut_nhongotngao": "Xin chào, em là Nhỏ Ngọt Ngào, chúc cả nhà một ngày thật nhiều niềm vui nha!",
        "capcut_giongbe": "Dạ con chào cô chú, con là giọng em bé siêu dễ thương đây ạ!",
        "capcut_namtram": "Xin chào quý vị và các bạn, đây là câu chuyện kỳ bí hôm nay tôi muốn gửi đến các bạn.",
        "capcut_reviewphim": "Chào mừng các bạn đã quay trở lại với chuyên mục review phim chiếu rạp hôm nay."
    }.get(target_key, "Xin chào, đây là bản nghe thử giọng đọc lồng tiếng.")

    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        await generate_single_tts(sample_text, preset, file_path)

    return FileResponse(
        path=file_path,
        media_type="audio/mpeg",
        filename=f"preview_{target_key}.mp3"
    )


@app.post("/api/tts-preview")
@app.get("/api/tts-preview")
async def api_tts_preview(
    request: Optional[TTSPreviewRequest] = None,
    voice: Optional[str] = None,
    text: Optional[str] = None
):
    """
    Endpoint for previewing TTS voice with custom or default sample text.
    Handles both POST (JSON body) and GET (query params) seamlessly.
    """
    from app.tts import generate_single_tts, VOICE_PRESETS, LEGACY_VOICE_MAP

    v = (request and request.voice) or voice or "capcut_cogaithoatngon"
    t = (request and request.text) or text or ""

    target_key = LEGACY_VOICE_MAP.get(v, v)
    preset = VOICE_PRESETS.get(target_key, VOICE_PRESETS.get("capcut_cogaithoatngon"))

    preview_dir = os.path.join(TEMP_DIR, "previews")
    os.makedirs(preview_dir, exist_ok=True)

    sample_text = t.strip()
    if not sample_text:
        sample_text = {
            "female_hoaimy": "Xin chào, tôi là Hoài My. Đây là bản nghe thử giọng đọc lồng tiếng của tôi.",
            "male_namminh": "Xin chào, tôi là Nam Minh. Đây là bản nghe thử giọng đọc lồng tiếng của tôi.",
            "capcut_cogaithoatngon": "Xin chào các bạn, tôi là cô gái hoạt ngôn trên CapCut. Chào mừng các bạn đến với kênh của mình!",
            "capcut_thanhnientutin": "Chào anh em, hôm nay chúng ta cùng recap bộ phim siêu kịch tính này nhé!",
            "capcut_nhongotngao": "Xin chào, em là Nhỏ Ngọt Ngào, chúc cả nhà một ngày thật nhiều niềm vui nha!",
            "capcut_giongbe": "Dạ con chào cô chú, con là giọng em bé siêu dễ thương đây ạ!",
            "capcut_namtram": "Xin chào quý vị và các bạn, đây là câu chuyện kỳ bí hôm nay tôi muốn gửi đến các bạn.",
            "capcut_reviewphim": "Chào mừng các bạn đã quay trở lại với chuyên mục review phim chiếu rạp hôm nay."
        }.get(target_key, "Xin chào, đây là giọng đọc thử nghiệm kịch bản của Siêu Tool.")

    text_hash = hashlib.md5(sample_text.encode("utf-8")).hexdigest()[:8]
    file_path = os.path.join(preview_dir, f"preview_{target_key}_{text_hash}.mp3")

    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        await generate_single_tts(sample_text, preset, file_path)

    return FileResponse(
        path=file_path,
        media_type="audio/mpeg",
        filename=f"preview_{target_key}.mp3"
    )


@app.get("/api/voices")
def api_get_voices():
    """
    Returns the list of all available TTS voices (100% CapCut / TikTok voices).
    """
    from app.tts import VOICE_PRESETS
    voices = []
    for key, data in VOICE_PRESETS.items():
        voices.append({
            "id": key,
            "name": data.get("name", key),
            "engine": data.get("engine", "capcut"),
            "gender": data.get("gender", "female"),
            "category": data.get("category", "general")
        })
    return {"status": "ok", "voices": voices}


@app.get("/api/rvc-models")
def api_get_rvc_models():
    """
    Returns empty list since RVC is deprecated/removed.
    """
    return {
        "status": "ok",
        "models": [],
        "system": {"ready": False}
    }


# ==========================================
# STORY TTS STUDIO APIS
# ==========================================

class StoryExtractRequest(BaseModel):
    url: str

class StoryRewriteRequest(BaseModel):
    text: str
    style: Optional[str] = "storytelling"
    custom_instruction: Optional[str] = ""

class StorySynthesizeRequest(BaseModel):
    text: str
    voice: Optional[str] = "capcut_cogaithoatngon"
    pause_ms: Optional[int] = 350


@app.get("/api/story-tts/voices")
def api_get_story_tts_voices():
    """
    Returns available TikTok voices grouped by category for Story TTS Studio.
    """
    from app.capcut_tts import CAPCUT_VOICES
    female_voices = []
    male_voices = []
    for k, v in CAPCUT_VOICES.items():
        entry = {
            "id": k,
            "name": v.get("name", k),
            "gender": v.get("gender", "female"),
            "category": v.get("category", "general")
        }
        if v.get("gender") == "female":
            female_voices.append(entry)
        else:
            male_voices.append(entry)
    return {
        "status": "ok",
        "female_voices": female_voices,
        "male_voices": male_voices
    }


@app.post("/api/story-tts/extract-youtube")
def api_story_extract_youtube(req: StoryExtractRequest):
    """
    Extracts transcript / captions from YouTube URL via yt-dlp.
    """
    from app.story_tts import extract_youtube_transcript
    res = extract_youtube_transcript(req.url)
    return res


@app.post("/api/story-tts/rewrite")
def api_story_rewrite(req: StoryRewriteRequest):
    """
    Rewrites story content using Groq / Gemini with custom storytelling styles.
    """
    from app.story_tts import rewrite_story_content
    res = rewrite_story_content(req.text, style=req.style, custom_instruction=req.custom_instruction)
    return res


@app.post("/api/story-tts/synthesize")
async def api_story_synthesize(req: StorySynthesizeRequest):
    """
    Synthesizes story text into MP3 + synchronized SRT subtitle.
    """
    from app.story_tts import synthesize_story_session
    res = await synthesize_story_session(req.text, voice_key=req.voice, pause_ms=req.pause_ms)
    return res


@app.get("/api/story-tts/download/{task_id}/audio")
def api_story_download_audio(task_id: str):
    """
    Downloads synthesized story MP3 file.
    """
    from app.story_tts import STORY_TEMP_DIR
    mp3_path = os.path.join(STORY_TEMP_DIR, task_id, "final_story.mp3")
    if not os.path.exists(mp3_path):
        raise HTTPException(status_code=404, detail="Không tìm thấy file âm thanh.")
    return FileResponse(mp3_path, media_type="audio/mpeg", filename=f"{task_id}.mp3")


@app.get("/api/story-tts/download/{task_id}/srt")
def api_story_download_srt(task_id: str):
    """
    Downloads synchronized story SRT file.
    """
    from app.story_tts import STORY_TEMP_DIR
    srt_path = os.path.join(STORY_TEMP_DIR, task_id, "final_story.srt")
    if not os.path.exists(srt_path):
        raise HTTPException(status_code=404, detail="Không tìm thấy file phụ đề.")
    return FileResponse(srt_path, media_type="application/x-subrip", filename=f"{task_id}.srt")


# ==========================================
# STEP-BY-STEP PROJECT APIS (STUDIO WORKFLOW)
# ==========================================

@app.get("/api/projects")
def list_projects():
    """
    Returns list of all saved projects sorted by updated_at descending.
    """
    projects = []
    if not os.path.exists(PROJECTS_DIR):
        return []

    for item in os.listdir(PROJECTS_DIR):
        item_path = os.path.join(PROJECTS_DIR, item)
        if os.path.isdir(item_path):
            meta = load_project_meta(item)
            segments_file = os.path.join(item_path, "segments.json")
            video_file = os.path.join(item_path, "input_video.mp4")
            output_file = os.path.join(item_path, "output_dubbed.mp4")

            seg_count = 0
            if os.path.exists(segments_file):
                try:
                    with open(segments_file, "r", encoding="utf-8") as f:
                        seg_count = len(json.load(f))
                except Exception:
                    pass

            meta["segments_count"] = seg_count
            meta["has_raw_video"] = os.path.exists(video_file)
            meta["has_dubbed_video"] = os.path.exists(output_file)
            projects.append(meta)

    projects.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    return projects


@app.post("/api/projects")
def create_project(request: Optional[ProjectCreateRequest] = None):
    """
    Creates a new empty project.
    """
    from datetime import datetime
    project_id = str(uuid.uuid4())
    get_project_dir(project_id)
    name = (request.name.strip() if request and request.name and request.name.strip() else None)
    if not name:
        name = f"Dự án {datetime.now().strftime('%d/%m %H:%M')}"

    meta = {
        "id": project_id,
        "name": name,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "current_step": 1,
        "completed_steps": [],
        "video_url": request.video_url if request and request.video_url else "",
        "bilibili_cookie": None,
        "mode": "ocr",
        "mask_box": {"x": 10, "y": 78, "w": 80, "h": 14, "enabled": True, "style": "blur"},
        "sub_box": {"x": 10, "y": 78, "w": 80, "h": 14},
        "sub_styling": {
            "font_size": 48,
            "font_name": "Nunito",
            "primary_color": "#FFFFFF",
            "outline_color": "#000000",
            "outline_width": 4.0,
            "box_style": "outline",
            "back_color": "#000000",
            "box_opacity": 0.75,
            "bold": True
        },
        "voice": "capcut_cogaithoatngon",
        "bg_volume": 0.15,
        "tts_volume": 1.0,
        "logo_box": {
            "enabled": False,
            "x": 80.0,
            "y": 5.0,
            "w": 15.0,
            "h": 10.0,
            "opacity": 1.0,
            "keep_aspect": True,
            "filename": None,
            "image_path": None
        },
        "status": "draft"
    }
    save_project_meta(project_id, meta)
    return meta


@app.get("/api/projects/{project_id}")
def get_project_detail(project_id: str):
    """
    Returns full metadata and segments of a specific project.
    """
    p_dir = get_project_dir(project_id, create=False)
    if not os.path.exists(p_dir):
        raise HTTPException(status_code=404, detail="Dự án không tồn tại.")

    meta = load_project_meta(project_id)
    segments_path = os.path.join(p_dir, "segments.json")
    segments = []
    if os.path.exists(segments_path):
        try:
            with open(segments_path, "r", encoding="utf-8") as f:
                segments = json.load(f)
        except Exception:
            pass

    meta["segments"] = segments
    meta["has_raw_video"] = os.path.exists(os.path.join(p_dir, "input_video.mp4"))
    meta["has_dubbed_video"] = os.path.exists(os.path.join(p_dir, "output_dubbed.mp4"))
    return meta


@app.patch("/api/projects/{project_id}")
def update_project_meta(project_id: str, request: ProjectUpdateRequest):
    """
    Updates metadata (name, settings, boxes, styling, etc.) for a project.
    """
    p_dir = get_project_dir(project_id, create=False)
    if not os.path.exists(p_dir):
        raise HTTPException(status_code=404, detail="Dự án không tồn tại.")

    if hasattr(request, "model_dump"):
        update_data = {k: v for k, v in request.model_dump(exclude_unset=True).items() if v is not None}
    else:
        update_data = {k: v for k, v in request.dict(exclude_unset=True).items() if v is not None}

    if "logo_box" in update_data and isinstance(update_data["logo_box"], dict):
        existing_meta = load_project_meta(project_id)
        existing_logo = existing_meta.get("logo_box") or {}
        merged_logo = {**existing_logo, **update_data["logo_box"]}
        if not merged_logo.get("image_path") and existing_logo.get("image_path"):
            merged_logo["image_path"] = existing_logo["image_path"]
        if not merged_logo.get("filename") and existing_logo.get("filename"):
            merged_logo["filename"] = existing_logo["filename"]
        update_data["logo_box"] = merged_logo

    meta = save_project_meta(project_id, update_data)
    return meta


@app.delete("/api/projects/{project_id}")
def delete_project_endpoint(project_id: str):
    """
    Deletes a project directory and all associated files.
    """
    p_dir = get_project_dir(project_id, create=False)
    if os.path.exists(p_dir):
        shutil.rmtree(p_dir, ignore_errors=True)
    if project_id in projects_db:
        del projects_db[project_id]
    return {"status": "ok", "message": "Đã xóa dự án thành công."}


@app.post("/api/project/download")
def project_start_download(request: ProjectDownloadRequest, background_tasks: BackgroundTasks):
    """
    Step 1: Downloads the source video into a dedicated project session.
    """
    if not request.url or not request.url.strip():
        raise HTTPException(status_code=400, detail="Vui lòng nhập link video.")

    project_id = request.project_id if request.project_id else str(uuid.uuid4())
    get_project_dir(project_id)

    meta = load_project_meta(project_id)
    meta.update({
        "video_url": request.url.strip(),
        "bilibili_cookie": request.bilibili_cookie,
        "status": "downloading",
        "current_step": 1
    })
    save_project_meta(project_id, meta)

    projects_db[project_id] = {
        "status": "pending",
        "progress": 0,
        "message": "Đang khởi tạo phiên làm việc...",
        "logs": []
    }
    background_tasks.add_task(
        process_project_download_worker,
        project_id=project_id,
        url=request.url.strip(),
        bilibili_cookie=request.bilibili_cookie
    )
    return {"project_id": project_id, "status": "pending", "project": meta}


@app.get("/api/project/{project_id}/status")
def project_get_status(project_id: str):
    """
    Retrieves the status and progress of the project session.
    Automatically recovers state from disk if server was restarted.
    """
    if project_id not in projects_db:
        project_dir = get_project_dir(project_id, create=False)
        if os.path.exists(project_dir):
            output_video = os.path.join(project_dir, "output_dubbed.mp4")
            segments_json = os.path.join(project_dir, "segments.json")
            input_video = os.path.join(project_dir, "input_video.mp4")
            meta = load_project_meta(project_id)

            if os.path.exists(output_video):
                projects_db[project_id] = {
                    "status": "completed",
                    "progress": 100,
                    "message": "Hoàn tất! Video đã sẵn sàng tải về.",
                    "video_url": f"/api/project/{project_id}/video-dubbed",
                    "download_url": f"/api/project/{project_id}/download",
                    "subtitles_url": f"/api/project/{project_id}/subtitles",
                    "project": meta
                }
            elif os.path.exists(segments_json):
                try:
                    with open(segments_json, "r", encoding="utf-8") as f:
                        segs = json.load(f)
                except Exception:
                    segs = []
                projects_db[project_id] = {
                    "status": "transcribed",
                    "progress": 100,
                    "message": f"Trích xuất thành công {len(segs)} câu phụ đề!",
                    "segments": segs,
                    "project": meta
                }
            elif os.path.exists(input_video):
                projects_db[project_id] = {
                    "status": "downloaded",
                    "progress": 100,
                    "message": "Tải video gốc thành công!",
                    "video_url": f"/api/project/{project_id}/video-raw",
                    "project": meta
                }
            else:
                projects_db[project_id] = {
                    "status": meta.get("status", "draft"),
                    "progress": 0,
                    "message": "Dự án mới.",
                    "project": meta
                }
        else:
            raise HTTPException(status_code=404, detail="Phiên làm việc không tồn tại.")
    res = dict(projects_db[project_id])
    res["logs"] = get_project_logs(project_id)
    return res


@app.get("/api/project/{project_id}/video-raw")
def project_stream_raw_video(project_id: str):
    """
    Streams the raw downloaded video so users can scrub and preview it in the interactive canvas.
    """
    video_path = os.path.join(get_project_dir(project_id, create=False), "input_video.mp4")
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video gốc chưa được tải.")
    return FileResponse(
        path=video_path,
        media_type="video/mp4",
        headers={
            "Accept-Ranges": "bytes",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )


@app.post("/api/project/{project_id}/transcribe")
def project_start_transcribe(project_id: str, request: ProjectTranscribeRequest, background_tasks: BackgroundTasks):
    """
    Step 2: Runs OCR or Whisper to extract and translate subtitles.
    """
    video_path = os.path.join(get_project_dir(project_id, create=False), "input_video.mp4")
    if not os.path.exists(video_path):
        raise HTTPException(status_code=400, detail="Chưa tải video gốc cho phiên này.")

    projects_db[project_id] = {
        "status": "transcribing",
        "progress": 5,
        "message": "Đang chuẩn bị quét phụ đề..."
    }
    background_tasks.add_task(
        process_project_transcribe_worker,
        project_id=project_id,
        mode=request.mode,
        mask_box=request.mask_box,
        source_lang=request.source_lang
    )
    return {"project_id": project_id, "status": "transcribing"}


@app.post("/api/project/{project_id}/translate")
def project_start_translate(project_id: str, request: ProjectTranslateRequest, background_tasks: BackgroundTasks):
    """
    Step 3: Translates subtitle segments using Groq AI / Gemini AI / Google Translate, OR applies custom imported SRT.
    """
    segments_path = os.path.join(get_project_dir(project_id, create=False), "segments.json")
    if not os.path.exists(segments_path):
        raise HTTPException(status_code=400, detail="Chưa có dữ liệu phụ đề từ Bước 2 để dịch.")

    action_label = "dịch lại các câu lỗi" if request.failed_only else "dịch phụ đề"
    projects_db[project_id] = {
        "status": "translating",
        "progress": 5,
        "message": f"Đang chuẩn bị {action_label}..."
    }
    background_tasks.add_task(
        process_project_translate_worker,
        project_id=project_id,
        engine=request.engine or "groq",
        custom_srt=request.custom_srt,
        failed_only=bool(request.failed_only)
    )
    return {"project_id": project_id, "status": "translating"}


@app.get("/api/project/{project_id}/segments")
def project_get_segments(project_id: str):
    """
    Returns the extracted and translated subtitle segments for review.
    """
    segments_path = os.path.join(get_project_dir(project_id, create=False), "segments.json")
    if os.path.exists(segments_path):
        with open(segments_path, "r", encoding="utf-8") as f:
            return json.load(f)
    if project_id in projects_db and "segments" in projects_db[project_id]:
        return projects_db[project_id]["segments"]
    return []


@app.put("/api/project/{project_id}/segments")
def project_update_segments(project_id: str, request: ProjectUpdateSegmentsRequest):
    """
    Updates subtitle segments after user edits/corrections on the UI.
    Preserves existing tts_raw_hash / audio_path metadata if text has not changed.
    """
    project_dir = get_project_dir(project_id)
    segments_path = os.path.join(project_dir, "segments.json")

    old_map: Dict[int, Dict[str, Any]] = {}
    if os.path.exists(segments_path):
        try:
            with open(segments_path, "r", encoding="utf-8") as f:
                old_list = json.load(f)
                for idx, item in enumerate(old_list):
                    old_map[idx] = item
        except Exception:
            pass

    merged_segments = []
    for idx, new_seg in enumerate(request.segments):
        prev = old_map.get(idx, {})
        if (
            prev
            and prev.get("translation", "").strip() == new_seg.get("translation", "").strip()
            and prev.get("tts_raw_hash")
        ):
            merged = {**prev, **new_seg, "tts_raw_hash": prev["tts_raw_hash"]}
        else:
            merged = dict(new_seg)
            merged.pop("tts_raw_hash", None)
        merged_segments.append(merged)

    with open(segments_path, "w", encoding="utf-8") as f:
        json.dump(merged_segments, f, ensure_ascii=False, indent=2)
    if project_id in projects_db:
        projects_db[project_id]["segments"] = merged_segments
    save_project_meta(project_id, {
        "status": "editing_subtitles",
        "current_step": 3,
        "completed_steps": [1, 2]
    })
    return {"status": "ok", "count": len(merged_segments)}


@app.get("/api/project/{project_id}/preview-audio")
def project_get_preview_audio(project_id: str):
    """
    Returns the synchronized Vietnamese dubbing audio track for the video preview player.
    Mixes existing cached audio segments rapidly via NumPy (0.05s) if available.
    Never blocks synchronously on external network TTS calls.
    """
    project_dir = get_project_dir(project_id)
    audio_path = os.path.join(project_dir, "preview_dubbed.mp3")
    if os.path.exists(audio_path) and os.path.getsize(audio_path) >= 1000:
        return FileResponse(path=audio_path, media_type="audio/mpeg")

    segments_path = os.path.join(project_dir, "segments.json")
    if os.path.exists(segments_path):
        try:
            with open(segments_path, "r", encoding="utf-8") as f:
                segments = json.load(f)
            active_segs = [s for s in segments if s.get("audio_path") and os.path.exists(s["audio_path"])]
            if active_segs:
                from app.merger import compute_elastic_timeline, mix_timeline_audio_fast
                aligned = compute_elastic_timeline(active_segs)
                audio_path = mix_timeline_audio_fast(project_dir, aligned, audio_path)
                if os.path.exists(audio_path) and os.path.getsize(audio_path) >= 1000:
                    return FileResponse(path=audio_path, media_type="audio/mpeg")
        except Exception as e:
            logger.warning(f"Failed fast audio mix: {e}")

    raise HTTPException(status_code=404, detail="Chưa có file âm thanh lồng tiếng. Vui lòng bấm 'Tạo giọng đọc'.")


@app.post("/api/project/{project_id}/generate-tts")
def project_generate_tts(project_id: str, request: ProjectGenerateTTSRequest, background_tasks: BackgroundTasks):
    """
    Step 3: Explicit trigger to generate TTS for the chosen voice with real-time per-sentence logging.
    """
    project_dir = get_project_dir(project_id)
    segments_path = os.path.join(project_dir, "segments.json")
    if not os.path.exists(segments_path):
        raise HTTPException(status_code=400, detail="Chưa có phụ đề để tạo giọng đọc.")

    with open(segments_path, "r", encoding="utf-8") as f:
        segments = json.load(f)

    if not segments:
        raise HTTPException(status_code=400, detail="Danh sách phụ đề rỗng.")

    voice = request.voice or "capcut_cogaithoatngon"
    failed_only = bool(request.failed_only)
    use_original = bool(request.use_original) if not failed_only else False
    action_text = "tạo lại các câu lỗi" if failed_only else "tạo giọng đọc"

    # Reset to Step 2 original text snapshot & clean stale audio files when requested
    orig_segments_path = os.path.join(project_dir, "segments_original.json")
    if use_original and os.path.exists(orig_segments_path):
        try:
            with open(orig_segments_path, "r", encoding="utf-8") as of:
                orig_data = json.load(of)
            if orig_data:
                # Remove stale audio files to ensure clean regeneration
                for fname in os.listdir(project_dir):
                    if (fname.startswith("seg_") and fname.endswith((".wav", ".mp3"))) or fname in ("preview_dubbed.mp3", "dubbed_voice_track.wav"):
                        try:
                            os.remove(os.path.join(project_dir, fname))
                        except Exception:
                            pass

                # Reset segments cleanly
                clean_segments = []
                for idx, s in enumerate(orig_data):
                    s_clean = {k: v for k, v in s.items() if k not in ("tts_error", "tts_raw_hash", "audio_path", "actual_duration", "speed_ratio")}
                    s_clean["id"] = idx + 1
                    # Preserve existing translation if original had none
                    if not s_clean.get("translation") and idx < len(segments) and segments[idx].get("translation"):
                        s_clean["translation"] = segments[idx]["translation"]
                    clean_segments.append(s_clean)

                segments = clean_segments
                with open(segments_path, "w", encoding="utf-8") as sf:
                    json.dump(segments, sf, ensure_ascii=False, indent=2)

                append_project_log(project_id, f"[Tạo Giọng] Đã khôi phục {len(segments)} câu gốc và dọn sạch file âm thanh cũ.", level="INFO")
        except Exception as e_rst:
            logger.warning(f"Failed to reset to original segments: {e_rst}")

    if not failed_only:
        # Full regeneration: delete all previous voice files and their references first
        purged = purge_project_audio(project_dir)
        strip_audio_meta(segments)
        with open(segments_path, "w", encoding="utf-8") as sf:
            json.dump(segments, sf, ensure_ascii=False, indent=2)
        append_project_log(project_id, f"[Tạo Giọng] Đã xóa {purged} file âm thanh cũ, tạo lại từ đầu.", level="INFO")

    save_project_meta(project_id, {
        "voice": voice,
        "current_step": 4
    })

    projects_db[project_id] = {
        **projects_db.get(project_id, {}),
        "status": "generating_tts",
        "progress": 0,
        "message": f"Bắt đầu {action_text} ({voice})...",
        "logs": get_project_logs(project_id)
    }

    def _run_tts_bg():
        try:
            append_project_log(project_id, f"[Tạo Giọng] Bắt đầu {action_text} cho {len(segments)} câu (Giọng: {voice})...")
            
            def _progress_cb(done, total, text):
                pct = int(done / max(1, total) * 100)
                if done % 15 == 0 or done == total or done == 1:
                    short_t = text[:35] + ("..." if len(text) > 35 else "")
                    append_project_log(project_id, f"[Tạo Giọng] [{done}/{total}] ({pct}%): '{short_t}'")
                if project_id in projects_db:
                    projects_db[project_id]["progress"] = pct
                    projects_db[project_id]["message"] = f"Đang {action_text} AI ({done}/{total} câu)..."

            generate_preview_audio_track(
                project_dir,
                segments,
                voice=voice,
                progress_callback=_progress_cb,
                failed_only=failed_only
            )

            # Check segments result to count any remaining errors
            failed_count = 0
            if os.path.exists(segments_path):
                try:
                    with open(segments_path, "r", encoding="utf-8") as sf:
                        curr_segs = json.load(sf)
                        failed_count = sum(
                            1 for s in curr_segs
                            if s.get("translation", "").strip() and (
                                s.get("tts_error")
                                or not s.get("audio_path")
                                or not os.path.exists(s.get("audio_path") or "")
                            )
                        )
                except Exception:
                    pass

            if failed_count > 0:
                append_project_log(project_id, f"[Tạo Giọng] Hoàn tất nhưng còn {failed_count} câu chưa tạo được giọng đọc.", level="WARNING")
                msg = f"Đã xử lý xong. Còn {failed_count} câu chưa tạo được tiếng."
            else:
                append_project_log(project_id, f"[Tạo Giọng] Hoàn tất tạo giọng đọc thành công cho toàn bộ {len(segments)} câu!", level="SUCCESS")
                msg = "Đã tạo giọng đọc thành công!"

            if project_id in projects_db:
                projects_db[project_id]["status"] = "tts_ready"
                projects_db[project_id]["progress"] = 100
                projects_db[project_id]["failed_count"] = failed_count
                projects_db[project_id]["message"] = msg
                projects_db[project_id]["preview_audio_url"] = f"/api/project/{project_id}/preview-audio"
        except Exception as e:
            logger.error(f"TTS generation error for {project_id}: {e}")
            append_project_log(project_id, f"[Tạo Giọng] Lỗi khi tạo giọng đọc: {e}", level="ERROR")
            if project_id in projects_db:
                projects_db[project_id]["status"] = "error"
                projects_db[project_id]["message"] = f"Lỗi tạo giọng đọc: {e}"

    background_tasks.add_task(_run_tts_bg)
    return {"status": "started", "project_id": project_id, "voice": voice}


@app.post("/api/project/{project_id}/reset-to-original")
def project_reset_to_original(project_id: str):
    """
    Manually reset segments back to Step 2 original OCR/Whisper output.
    """
    project_dir = get_project_dir(project_id)
    orig_segments_path = os.path.join(project_dir, "segments_original.json")
    segments_path = os.path.join(project_dir, "segments.json")
    if not os.path.exists(orig_segments_path):
        raise HTTPException(status_code=404, detail="Không tìm thấy bản quét gốc Bước 2.")

    with open(orig_segments_path, "r", encoding="utf-8") as of:
        orig_data = json.load(of)

    for fname in os.listdir(project_dir):
        if (fname.startswith("seg_") and fname.endswith((".wav", ".mp3"))) or fname in ("preview_dubbed.mp3", "dubbed_voice_track.wav"):
            try:
                os.remove(os.path.join(project_dir, fname))
            except Exception:
                pass

    segments = []
    for idx, s in enumerate(orig_data):
        s_clean = {k: v for k, v in s.items() if k not in ("tts_error", "tts_raw_hash", "audio_path", "actual_duration", "speed_ratio")}
        s_clean["id"] = idx + 1
        segments.append(s_clean)

    with open(segments_path, "w", encoding="utf-8") as sf:
        json.dump(segments, sf, ensure_ascii=False, indent=2)

    append_project_log(project_id, f"[Khôi phục] Đã khôi phục hoàn toàn {len(segments)} câu gốc từ Bước 2.", level="SUCCESS")
    return {"status": "ok", "segments": segments}


@app.post("/api/project/{project_id}/preview-audio")
def project_generate_preview_audio(project_id: str, request: Optional[Dict[str, Any]] = None):
    """
    Forces generating or refreshing the preview dubbed audio track from current segments.
    """
    project_dir = get_project_dir(project_id)
    segments_path = os.path.join(project_dir, "segments.json")
    segments = []
    if os.path.exists(segments_path):
        with open(segments_path, "r", encoding="utf-8") as f:
            segments = json.load(f)
    meta = load_project_meta(project_id)
    voice = (request and request.get("voice")) or meta.get("voice", "capcut_cogaithoatngon")

    append_project_log(project_id, f"[Lồng tiếng] Bắt đầu tổng hợp âm thanh lồng tiếng xem trước ({len(segments)} câu, giọng: {voice})...")
    generate_preview_audio_track(
        project_dir,
        segments,
        voice=voice
    )
    append_project_log(project_id, f"[Lồng tiếng] Đã tạo xong âm thanh lồng tiếng xem trước!", level="SUCCESS")
    return {"status": "ok", "url": f"/api/project/{project_id}/preview-audio"}


@app.post("/api/project/{project_id}/render")
def project_start_render(project_id: str, request: ProjectRenderRequest, background_tasks: BackgroundTasks):
    """
    Step 4: Renders the final dubbed and subbed video using reviewed subtitles.
    """
    video_path = os.path.join(get_project_dir(project_id, create=False), "input_video.mp4")
    if not os.path.exists(video_path):
        raise HTTPException(status_code=400, detail="Chưa có video gốc.")

    projects_db[project_id] = {
        "status": "rendering",
        "progress": 5,
        "message": "Đang chuẩn bị render video..."
    }
    background_tasks.add_task(
        process_project_render_worker,
        project_id=project_id,
        voice=request.voice,
        bg_volume=request.bg_volume,
        tts_volume=request.tts_volume,
        mask_box=request.mask_box,
        sub_box=request.sub_box,
        sub_styling=request.sub_styling,
        burn_subtitles=request.burn_subtitles,
        segments=request.segments,
        auto_extend_video=request.auto_extend_video,
        logo_box=request.logo_box
    )
    return {"project_id": project_id, "status": "rendering"}


@app.get("/api/project/{project_id}/video-dubbed")
def project_stream_dubbed_video(project_id: str):
    """
    Streams the finished dubbed video for inline playback.
    """
    video_path = os.path.join(get_project_dir(project_id, create=False), "output_dubbed.mp4")
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video thành phẩm chưa được tạo.")
    return FileResponse(
        path=video_path,
        media_type="video/mp4",
        headers={
            "Accept-Ranges": "bytes",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )


@app.get("/api/project/{project_id}/download")
def project_download_video(project_id: str):
    """
    Downloads the finished dubbed video as an attachment.
    """
    video_path = os.path.join(get_project_dir(project_id, create=False), "output_dubbed.mp4")
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="File video chưa sẵn sàng.")
    return FileResponse(path=video_path, media_type="video/mp4", filename=f"translated_{project_id[:8]}.mp4")


@app.get("/api/project/{project_id}/subtitles")
def project_download_subtitles(project_id: str, lang: str = "vi"):
    """
    Downloads the SubRip (.srt) subtitle file for the project (supports lang=zh, vi, dual).
    """
    p_dir = get_project_dir(project_id, create=False)
    if not os.path.exists(p_dir):
        raise HTTPException(status_code=404, detail="Dự án không tồn tại.")

    seg_file = os.path.join(p_dir, "segments.json")
    segments = []
    if os.path.exists(seg_file):
        try:
            with open(seg_file, "r", encoding="utf-8") as f:
                segments = json.load(f)
        except Exception:
            pass
    if not segments and project_id in projects_db:
        segments = projects_db[project_id].get("segments", [])

    if not segments:
        srt_path = os.path.join(p_dir, "subtitles.srt")
        if os.path.exists(srt_path):
            return FileResponse(path=srt_path, media_type="text/plain; charset=utf-8", filename=f"subtitles_{project_id[:8]}.srt")
        raise HTTPException(status_code=404, detail="Chưa có dữ liệu phụ đề để xuất file .srt.")

    lang_norm = lang.lower().strip() if lang else "vi"
    if lang_norm not in ("zh", "vi", "dual"):
        lang_norm = "vi"

    srt_text = export_segments_to_srt_string(segments, lang=lang_norm)
    filename = f"subtitles_{lang_norm}_{project_id[:8]}.srt"
    return Response(
        content=srt_text.encode("utf-8"),
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@app.post("/api/project/{project_id}/clear-translations")
def project_clear_translations(project_id: str):
    """
    Step 3 cleanup: wipes every Vietnamese translation (and the voice files that depend on it).
    """
    p_dir = get_project_dir(project_id, create=False)
    if not os.path.exists(p_dir):
        raise HTTPException(status_code=404, detail="Dự án không tồn tại.")

    def _clear(path: str) -> List[Dict[str, Any]]:
        data: List[Dict[str, Any]] = []
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = []
        for s in data:
            s["translation"] = ""
            for k in ("translation_error", "untranslated_warning", "untranslated_chars"):
                s.pop(k, None)
        strip_audio_meta(data)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return data

    removed = purge_project_audio(p_dir)
    segments = _clear(os.path.join(p_dir, "segments.json"))
    orig_path = os.path.join(p_dir, "segments_original.json")
    if os.path.exists(orig_path):
        _clear(orig_path)

    if project_id in projects_db:
        projects_db[project_id]["segments"] = segments
    save_project_meta(project_id, {
        "status": "editing_subtitles",
        "current_step": 3,
        "completed_steps": [1, 2]
    })
    return {"status": "ok", "count": len(segments), "removed_audio_files": removed, "segments": segments}


@app.post("/api/project/{project_id}/clear-audio")
def project_clear_audio(project_id: str):
    """
    Step 4 cleanup: deletes every generated voice file, preview track and cache reference.
    Translations are kept.
    """
    p_dir = get_project_dir(project_id, create=False)
    if not os.path.exists(p_dir):
        raise HTTPException(status_code=404, detail="Dự án không tồn tại.")

    removed = purge_project_audio(p_dir)
    seg_file = os.path.join(p_dir, "segments.json")
    segments: List[Dict[str, Any]] = []
    if os.path.exists(seg_file):
        try:
            with open(seg_file, "r", encoding="utf-8") as f:
                segments = json.load(f)
        except Exception:
            segments = []
        strip_audio_meta(segments)
        with open(seg_file, "w", encoding="utf-8") as f:
            json.dump(segments, f, ensure_ascii=False, indent=2)

    if project_id in projects_db:
        projects_db[project_id]["segments"] = segments
    return {"status": "ok", "removed_audio_files": removed, "segments": segments}


@app.post("/api/project/{project_id}/import-srt")
def project_import_subtitles_srt(project_id: str, request: ProjectImportSrtRequest):
    """
    Imports an external .SRT file (or pasted translated lines) into the project's segments,
    preserving original Chinese text and timestamps while updating Vietnamese translation.
    """
    p_dir = get_project_dir(project_id, create=False)
    if not os.path.exists(p_dir):
        raise HTTPException(status_code=404, detail="Dự án không tồn tại.")

    if not request.srt_content or not request.srt_content.strip():
        raise HTTPException(status_code=400, detail="Nội dung file SRT hoặc bản dịch đang để trống.")

    seg_file = os.path.join(p_dir, "segments.json")
    existing_segments: List[Dict[str, Any]] = []
    if os.path.exists(seg_file):
        try:
            with open(seg_file, "r", encoding="utf-8") as f:
                existing_segments = json.load(f)
        except Exception:
            pass

    target_field = "text" if request.target_field == "text" else "translation"
    updated_segments = import_srt_to_segments(
        request.srt_content,
        existing_segments=existing_segments,
        target_field=target_field
    )

    if not updated_segments:
        raise HTTPException(status_code=400, detail="Không đọc được câu phụ đề nào từ dữ liệu SRT gửi lên.")

    if target_field == "translation":
        # New translation invalidates every previously generated voice file
        purge_project_audio(p_dir)
        strip_audio_meta(updated_segments)

    with open(seg_file, "w", encoding="utf-8") as f:
        json.dump(updated_segments, f, ensure_ascii=False, indent=2)

    # Keep the "original" snapshot in sync so Reset does not discard the imported translation
    with open(os.path.join(p_dir, "segments_original.json"), "w", encoding="utf-8") as of:
        json.dump(updated_segments, of, ensure_ascii=False, indent=2)

    if project_id in projects_db:
        projects_db[project_id]["segments"] = updated_segments

    save_project_meta(project_id, {
        "status": "editing_subtitles",
        "current_step": 3,
        "completed_steps": [1, 2]
    })

    return {
        "status": "ok",
        "count": len(updated_segments),
        "segments": updated_segments,
        "message": f"Đã gắn thành công {len(updated_segments)} câu từ SRT vào dự án!"
    }



@app.get("/api/project/{project_id}/download-audio")
def project_download_audio_dubbed(project_id: str):
    """
    Downloads only the Vietnamese translated voiceover audio track (MP3),
    synchronized with the timeline, WITHOUT original video audio/background.
    Always ensures latest segment edits and voice selection are compiled.
    """
    project_dir = get_project_dir(project_id, create=False)
    if not os.path.exists(project_dir):
        raise HTTPException(status_code=404, detail="Dự án không tồn tại.")

    meta = load_project_meta(project_id)
    segments = []
    seg_file = os.path.join(project_dir, "segments.json")
    if os.path.exists(seg_file):
        try:
            with open(seg_file, "r", encoding="utf-8") as f:
                segments = json.load(f)
        except Exception:
            pass
    if not segments:
        segments = meta.get("segments", [])

    voice = meta.get("voice", "capcut_cogaithoatngon")
    preview_audio_path = generate_preview_audio_track(project_dir, segments, voice)

    if not os.path.exists(preview_audio_path):
        raise HTTPException(status_code=404, detail="Không thể tạo file âm thanh lời dịch.")

    return FileResponse(
        path=preview_audio_path,
        media_type="audio/mpeg",
        filename=f"audio_dich_tieng_viet_{project_id[:8]}.mp3"
    )


@app.post("/api/project/{project_id}/logo")
async def project_upload_logo(project_id: str, file: UploadFile = File(...)):
    """
    Uploads a watermark / logo image (PNG, JPG, WEBP, SVG) for the project.
    """
    project_dir = get_project_dir(project_id)
    orig_name = file.filename or "logo.png"
    ext = os.path.splitext(orig_name)[1].lower()
    if ext not in (".png", ".jpg", ".jpeg", ".webp", ".svg", ".bmp"):
        raise HTTPException(
            status_code=400,
            detail="Định dạng ảnh không được hỗ trợ. Vui lòng tải lên PNG, JPG, WEBP hoặc SVG."
        )

    dest_path = os.path.join(project_dir, f"logo{ext}")
    with open(dest_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    meta = load_project_meta(project_id)
    logo_box = meta.get("logo_box") or {
        "x": 80.0,
        "y": 5.0,
        "w": 15.0,
        "h": 10.0,
        "opacity": 1.0,
        "keep_aspect": True
    }
    logo_box.update({
        "enabled": True,
        "image_path": dest_path,
        "filename": orig_name,
        "logo_url": f"/api/project/{project_id}/logo"
    })
    save_project_meta(project_id, {"logo_box": logo_box})

    return {
        "status": "ok",
        "logo_url": f"/api/project/{project_id}/logo",
        "filename": orig_name,
        "logo_box": logo_box
    }


@app.get("/api/project/{project_id}/logo")
def project_get_logo(project_id: str):
    """
    Streams the project's uploaded logo image.
    """
    project_dir = get_project_dir(project_id, create=False)
    if not os.path.exists(project_dir):
        raise HTTPException(status_code=404, detail="Dự án không tồn tại.")

    meta = load_project_meta(project_id)
    logo_box = meta.get("logo_box", {})
    image_path = logo_box.get("image_path")

    if not image_path or not os.path.exists(image_path):
        for ext in (".png", ".jpg", ".jpeg", ".webp", ".svg", ".bmp"):
            cand = os.path.join(project_dir, f"logo{ext}")
            if os.path.exists(cand):
                image_path = cand
                break

    if not image_path or not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Chưa có logo được tải lên cho dự án này.")

    ext = os.path.splitext(image_path)[1].lower()
    mime_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".svg": "image/svg+xml",
        ".bmp": "image/bmp"
    }
    media_type = mime_types.get(ext, "image/png")
    return FileResponse(path=image_path, media_type=media_type)


@app.get("/api/settings")
def get_app_settings():
    """
    Returns current translation engine and API keys status for Groq and Gemini.
    """
    from app.gemini_translator import load_settings
    s = load_settings()
    gem_key = s.get("gemini_api_key", "")
    masked_gem_key = (gem_key[:8] + "..." + gem_key[-6:]) if len(gem_key) > 14 else ("******" if gem_key else "")
    groq_key = s.get("groq_api_key", "")
    masked_groq_key = (groq_key[:8] + "..." + groq_key[-6:]) if len(groq_key) > 14 else ("******" if groq_key else "")
    return {
        "translation_engine": s.get("translation_engine", "groq"),
        "groq_api_key_masked": masked_groq_key,
        "has_groq_key": bool(groq_key),
        "groq_model": s.get("groq_model", "llama-3.3-70b-versatile"),
        "gemini_api_key_masked": masked_gem_key,
        "has_gemini_key": bool(gem_key),
        "gemini_model": s.get("gemini_model", "gemini-3.5-flash")
    }


@app.post("/api/settings")
def update_app_settings(req: SettingsUpdateRequest):
    """
    Updates translation settings (engine, api key, model).
    """
    from app.gemini_translator import save_settings
    updates = {}
    if req.translation_engine is not None:
        updates["translation_engine"] = req.translation_engine
    if req.groq_api_key is not None:
        raw_groq = req.groq_api_key.strip()
        if raw_groq and "..." not in raw_groq:
            updates["groq_api_key"] = raw_groq
    if req.groq_model is not None:
        updates["groq_model"] = req.groq_model.strip()
    if req.gemini_api_key is not None:
        raw_k = req.gemini_api_key.strip()
        if raw_k and "..." not in raw_k:
            updates["gemini_api_key"] = raw_k
    if req.gemini_model is not None:
        updates["gemini_model"] = req.gemini_model.strip()

    saved = save_settings(updates)
    gem_key = saved.get("gemini_api_key", "")
    masked_gem_key = (gem_key[:8] + "..." + gem_key[-6:]) if len(gem_key) > 14 else ("******" if gem_key else "")
    groq_key = saved.get("groq_api_key", "")
    masked_groq_key = (groq_key[:8] + "..." + groq_key[-6:]) if len(groq_key) > 14 else ("******" if groq_key else "")
    return {
        "status": "ok",
        "translation_engine": saved.get("translation_engine", "groq"),
        "groq_api_key_masked": masked_groq_key,
        "has_groq_key": bool(groq_key),
        "groq_model": saved.get("groq_model", "llama-3.3-70b-versatile"),
        "gemini_api_key_masked": masked_gem_key,
        "has_gemini_key": bool(gem_key),
        "gemini_model": saved.get("gemini_model", "gemini-3.5-flash")
    }


# Include Social Video Generator router
from app.social_router import router as social_router
app.include_router(social_router, prefix="/api/social", tags=["social"])

# Serve the static UI files
if os.path.exists(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
