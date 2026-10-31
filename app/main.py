import os
import uuid
import shutil
import logging
import json
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
        "voice": "female_hoaimy",
        "rvc_model": "none",
        "rvc_pitch": 0,
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
    rvc_model: Optional[str] = None
    rvc_pitch: Optional[int] = None
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


class ProjectUpdateSegmentsRequest(BaseModel):
    segments: List[Dict[str, Any]]


class ProjectImportSrtRequest(BaseModel):
    srt_content: str
    target_field: str = "translation"


class ProjectRenderRequest(BaseModel):
    voice: str = "female_hoaimy"
    rvc_model: Optional[str] = "none"
    rvc_pitch: Optional[int] = 0
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
    voice: str = "female_hoaimy"
    rvc_model: Optional[str] = "none"
    rvc_pitch: Optional[int] = 0
    rate: str = "+0%"


# ==========================================
# BACKGROUND WORKERS FOR STUDIO PIPELINE
# ==========================================

def process_project_download_worker(project_id: str, url: str, bilibili_cookie: Optional[str] = None):
    project_dir = get_project_dir(project_id)
    input_video_path = os.path.join(project_dir, "input_video.mp4")
    input_audio_path = os.path.join(project_dir, "input_audio.wav")

    try:
        logger.info(f"[{project_id}] Step 1: Downloading video from {url}...")
        projects_db[project_id] = {
            "status": "downloading",
            "progress": 5,
            "message": "Đang kết nối và tải video..."
        }
        save_project_meta(project_id, {
            "video_url": url,
            "bilibili_cookie": bilibili_cookie,
            "status": "downloading",
            "current_step": 1
        })

        def download_progress(pct):
            projects_db[project_id]["progress"] = int(5 + (pct * 0.90))
            projects_db[project_id]["message"] = f"Đang tải video... ({pct:.1f}%)"

        download_bilibili_video(
            url,
            input_video_path,
            input_audio_path,
            progress_callback=download_progress,
            bilibili_cookie=bilibili_cookie
        )

        projects_db[project_id] = {
            "status": "downloaded",
            "progress": 100,
            "message": "Tải video thành công! Video đã sẵn sàng trên màn hình xem trước.",
            "video_url": f"/api/project/{project_id}/video-raw"
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
        projects_db[project_id] = {
            "status": "download_failed",
            "progress": 100,
            "message": "Tải video thất bại.",
            "error": str(e)
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
        if mode == "ocr":
            logger.info(f"[{project_id}] Step 2: Running OCR...")
            projects_db[project_id] = {
                "status": "transcribing",
                "progress": 15,
                "message": "Đang quét nhận diện chữ phụ đề tiếng Trung (OCR)..."
            }
            from app.ocr import extract_subtitles_from_video

            def ocr_progress(pct):
                projects_db[project_id]["progress"] = int(15 + (pct * 0.55))
                projects_db[project_id]["message"] = f"Đang quét chữ phụ đề video... ({pct:.0f}%)"

            raw_segments = extract_subtitles_from_video(
                input_video_path,
                mask_box or {"x": 10.0, "y": 78.0, "w": 80.0, "h": 14.0},
                sample_rate_fps=3.0,
                progress_callback=ocr_progress
            )
            if not raw_segments:
                raise ValueError("Không phát hiện được chữ phụ đề trong vùng khoanh chọn. Vui lòng kiểm tra lại khung khoanh vùng hoặc chuyển sang chế độ Whisper.")

            projects_db[project_id]["message"] = "Đang dịch chuẩn ngữ cảnh sang tiếng Việt..."
            projects_db[project_id]["progress"] = 75
            raw_texts = [s["text"] for s in raw_segments]
            durations = [max(0.2, float(s["end"]) - float(s["start"])) for s in raw_segments]
            cleaned_zh, _ = preprocess_chinese_segments(raw_texts)
            translations = batch_translate_texts(
                cleaned_zh,
                source_code="zh-CN",
                target_code="vi",
                durations=durations
            )
            segments = []
            for idx, (seg, cz, trans) in enumerate(zip(raw_segments, cleaned_zh, translations)):
                segments.append({
                    "id": idx + 1,
                    "start": round(seg["start"], 2),
                    "end": round(seg["end"], 2),
                    "text": cz,
                    "translation": trans
                })
        else:
            logger.info(f"[{project_id}] Step 2: Running Whisper...")
            projects_db[project_id] = {
                "status": "transcribing",
                "progress": 20,
                "message": "Đang nhận diện giọng nói và dịch tự động bằng Whisper..."
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
                    "translation": seg.get("translation", seg.get("text", ""))
                })

        with open(segments_json_path, "w", encoding="utf-8") as f:
            json.dump(segments, f, ensure_ascii=False, indent=2)

        projects_db[project_id] = {
            "status": "transcribing",
            "progress": 85,
            "message": "Đang khởi tạo giọng đọc AI lồng tiếng xem trước..."
        }
        try:
            meta = load_project_meta(project_id)
            voice = meta.get("voice", "female_hoaimy")
            generate_preview_audio_track(project_dir, segments, voice=voice)
            # Reload segments with populated audio_path & actual_duration
            if os.path.exists(segments_json_path):
                with open(segments_json_path, "r", encoding="utf-8") as f:
                    segments = json.load(f)
            logger.info(f"[{project_id}] Pre-generated preview dubbed audio track successfully.")
        except Exception as e_audio:
            logger.warning(f"[{project_id}] Could not pre-generate preview audio: {e_audio}")

        save_project_meta(project_id, {
            "status": "transcribed",
            "mode": mode,
            "mask_box": mask_box,
            "current_step": 3,
            "completed_steps": [1, 2]
        })

        projects_db[project_id] = {
            "status": "transcribed",
            "progress": 100,
            "message": f"Trích xuất thành công {len(segments)} câu phụ đề & sẵn sàng giọng đọc!",
            "segments": segments
        }
        logger.info(f"[{project_id}] Step 2: Transcribe completed with {len(segments)} segments.")
    except Exception as e:
        logger.error(f"[{project_id}] Transcribe failed: {str(e)}", exc_info=True)
        projects_db[project_id] = {
            "status": "transcribe_failed",
            "progress": 100,
            "message": "Quét phụ đề thất bại.",
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
    rvc_model: str = "none",
    rvc_pitch: int = 0,
    logo_box: Optional[Dict[str, Any]] = None
):
    project_dir = get_project_dir(project_id)
    input_video_path = os.path.join(project_dir, "input_video.mp4")
    output_video_path = os.path.join(project_dir, "output_dubbed.mp4")
    segments_json_path = os.path.join(project_dir, "segments.json")

    if segments is not None and len(segments) > 0:
        with open(segments_json_path, "w", encoding="utf-8") as f:
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
        logger.info(f"[{project_id}] Step 4: Generating TTS for {len(segments)} segments (voice={voice}, rvc={rvc_model}, auto_extend={auto_extend_video})...")
        projects_db[project_id] = {
            "status": "rendering",
            "progress": 25,
            "message": "Đang khởi tạo giọng đọc AI lồng tiếng..."
        }
        updated_segments = generate_tts_for_segments(
            segments,
            voice,
            project_dir,
            auto_extend_video=auto_extend_video,
            rvc_model=rvc_model,
            rvc_pitch=rvc_pitch
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
                meta = get_project_meta(project_id)
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
            else:
                logger.warning(f"[{project_id}] Logo enabled but image file not found. Skipping logo overlay.")
                resolved_logo_box = None

        logger.info(f"[{project_id}] Step 4: Merging audio, sub, logo and video (auto_extend={auto_extend_video}, has_logo={bool(resolved_logo_box)})...")
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

        save_project_meta(project_id, {
            "status": "completed",
            "voice": voice,
            "rvc_model": rvc_model,
            "rvc_pitch": rvc_pitch,
            "bg_volume": bg_volume,
            "tts_volume": tts_volume,
            "mask_box": mask_box,
            "sub_box": sub_box,
            "sub_styling": sub_styling,
            "burn_subtitles": burn_subtitles,
            "logo_box": logo_box or (resolved_logo_box if resolved_logo_box else None),
            "auto_extend_video": auto_extend_video,
            "current_step": 4,
            "completed_steps": [1, 2, 3, 4]
        })

        projects_db[project_id] = {
            "status": "completed",
            "progress": 100,
            "message": "Hoàn tất! Video đã sẵn sàng tải về.",
            "video_url": f"/api/project/{project_id}/video-dubbed",
            "download_url": f"/api/project/{project_id}/download",
            "subtitles_url": f"/api/project/{project_id}/subtitles"
        }
        logger.info(f"[{project_id}] Step 4: Render completed.")
    except Exception as e:
        logger.error(f"[{project_id}] Render failed: {str(e)}", exc_info=True)
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
    preset = VOICE_PRESETS.get(target_key, VOICE_PRESETS["female_hoaimy"]).copy()
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
async def preview_voice(voice: str = "female_hoaimy"):
    """
    Returns an audio sample previewing the selected TTS voice.
    Caches the generated sample audio in temp/previews so future requests are instant.
    """
    from app.tts import generate_single_tts, VOICE_PRESETS, LEGACY_VOICE_MAP

    target_key = LEGACY_VOICE_MAP.get(voice, voice)
    preset = VOICE_PRESETS.get(target_key, VOICE_PRESETS["female_hoaimy"])

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


@app.get("/api/voices")
def api_get_voices():
    """
    Returns the list of all available TTS voices grouped by engine (CapCut TTS & Edge-TTS).
    """
    from app.tts import VOICE_PRESETS
    voices = []
    for key, data in VOICE_PRESETS.items():
        voices.append({
            "id": key,
            "name": data.get("name", key),
            "engine": data.get("engine", "edge-tts"),
            "gender": data.get("gender", "female")
        })
    return {"status": "ok", "voices": voices}


@app.get("/api/rvc-models")
def api_get_rvc_models():
    """
    Returns the list of detected RVC voice models in app/models/rvc and system readiness.
    """
    try:
        from app.rvc_engine import scan_rvc_models, check_rvc_readiness
        models = scan_rvc_models()
        status = check_rvc_readiness()
        return {
            "status": "ok",
            "models": models,
            "system": status
        }
    except Exception as e:
        logger.error(f"Error scanning RVC models: {e}")
        return {
            "status": "error",
            "models": [],
            "system": {"ready": False, "error": str(e)}
        }


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
        "voice": "female_hoaimy",
        "rvc_model": "none",
        "rvc_pitch": 0,
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
        "message": "Đang khởi tạo phiên làm việc..."
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
    return projects_db[project_id]


@app.get("/api/project/{project_id}/video-raw")
def project_stream_raw_video(project_id: str):
    """
    Streams the raw downloaded video so users can scrub and preview it in the interactive canvas.
    """
    video_path = os.path.join(get_project_dir(project_id, create=False), "input_video.mp4")
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video gốc chưa được tải.")
    return FileResponse(path=video_path, media_type="video/mp4", headers={"Accept-Ranges": "bytes"})


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
    Generates it on-the-fly if not already created.
    """
    project_dir = get_project_dir(project_id)
    audio_path = os.path.join(project_dir, "preview_dubbed.mp3")
    if not os.path.exists(audio_path) or os.path.getsize(audio_path) < 1000:
        segments_path = os.path.join(project_dir, "segments.json")
        segments = []
        if os.path.exists(segments_path):
            with open(segments_path, "r", encoding="utf-8") as f:
                segments = json.load(f)
        meta = load_project_meta(project_id)
        voice = meta.get("voice", "female_hoaimy")
        audio_path = generate_preview_audio_track(project_dir, segments, voice=voice)

    return FileResponse(path=audio_path, media_type="audio/mpeg")


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
    voice = (request and request.get("voice")) or meta.get("voice", "female_hoaimy")
    rvc_model = (request and request.get("rvc_model")) or meta.get("rvc_model", "none")
    rvc_pitch = int((request and request.get("rvc_pitch")) or meta.get("rvc_pitch", 0))

    generate_preview_audio_track(
        project_dir,
        segments,
        voice=voice,
        rvc_model=rvc_model,
        rvc_pitch=rvc_pitch
    )
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
        rvc_model=request.rvc_model or "none",
        rvc_pitch=request.rvc_pitch or 0,
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
    return FileResponse(path=video_path, media_type="video/mp4", headers={"Accept-Ranges": "bytes"})


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

    with open(seg_file, "w", encoding="utf-8") as f:
        json.dump(updated_segments, f, ensure_ascii=False, indent=2)

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

    voice = meta.get("voice", "female_hoaimy")
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


# Serve the static UI files
if os.path.exists(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
