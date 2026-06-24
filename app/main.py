import os
import uuid
import shutil
import logging
from typing import Optional
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.downloader import download_bilibili_video
from app.translator import translate_video_audio
from app.tts import generate_tts_for_segments
from app.merger import merge_audio_segments_to_video

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Bilibili Video Translator & Dubber")

# Define base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMP_DIR = os.path.join(BASE_DIR, "app", "temp")
STATIC_DIR = os.path.join(BASE_DIR, "app", "static")

# Create directories if they do not exist
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

# In-memory database to store task statuses
tasks_db = {}

class TranslationRequest(BaseModel):
    url: str
    voice: str = "tiktok_girl"
    source_lang: str = "Chinese"
    bg_volume: float = 0.15
    tts_volume: float = 1.0
    bilibili_cookie: Optional[str] = None

def process_video_pipeline(
    task_id: str,
    url: str,
    voice: str,
    source_lang: str,
    bg_volume: float,
    tts_volume: float,
    bilibili_cookie: Optional[str] = None
):
    """
    Background worker running the complete translation pipeline.
    """
    task_dir = os.path.join(TEMP_DIR, task_id)
    os.makedirs(task_dir, exist_ok=True)
    
    input_video_path = os.path.join(task_dir, "input_video.mp4")
    input_audio_path = os.path.join(task_dir, "input_audio.wav")
    output_video_path = os.path.join(task_dir, "output_dubbed.mp4")
    
    try:
        # Step 1: Downloading Video & Audio
        logger.info(f"[{task_id}] Step 1: Downloading video...")
        tasks_db[task_id] = {
            "status": "downloading",
            "progress": 5,
            "message": "Đang kết nối và tải video từ Bilibili..."
        }
        
        def download_progress(pct):
            # Scale download percentage to represent 0% to 30% of total job progress
            tasks_db[task_id]["progress"] = int(5 + (pct * 0.25))
            tasks_db[task_id]["message"] = f"Đang tải video... ({pct:.1f}%)"

        download_bilibili_video(
            url, 
            input_video_path, 
            input_audio_path, 
            progress_callback=download_progress,
            bilibili_cookie=bilibili_cookie
        )
        
        # Step 2: Speech to Text & Translation
        logger.info(f"[{task_id}] Step 2: Transcribing and translating audio...")
        tasks_db[task_id] = {
            "status": "translating",
            "progress": 35,
            "message": "Đang nhận dạng giọng nói tiếng Trung và dịch sang tiếng Việt..."
        }
        
        segments = translate_video_audio(input_audio_path, source_lang)
        
        if not segments:
            raise ValueError("Không tìm thấy hoặc không nhận dạng được giọng nói nào trong video.")
            
        # Step 3: Text to Speech (TTS)
        logger.info(f"[{task_id}] Step 3: Generating TTS lồng tiếng...")
        tasks_db[task_id] = {
            "status": "tts",
            "progress": 60,
            "message": "Đang khởi tạo giọng đọc lồng tiếng Việt..."
        }
        
        # We can update status within the loop for precise progress
        total_segments = len(segments)
        updated_segments = []
        
        # Import local TTS generation to execute
        from app.tts import generate_tts_for_segments
        
        # Run TTS generation
        updated_segments = generate_tts_for_segments(segments, voice, task_dir)
        
        # Step 4: Merge Audio & Video
        logger.info(f"[{task_id}] Step 4: Merging dubbed audio to original video...")
        tasks_db[task_id] = {
            "status": "merging",
            "progress": 85,
            "message": "Đang ghép giọng lồng tiếng mới vào video gốc..."
        }
        
        merge_audio_segments_to_video(
            original_video_path=input_video_path,
            segments=updated_segments,
            output_video_path=output_video_path,
            bg_volume=bg_volume,
            tts_volume=tts_volume
        )
        
        # Success state
        logger.info(f"[{task_id}] Pipeline completed successfully!")
        tasks_db[task_id] = {
            "status": "completed",
            "progress": 100,
            "message": "Hoàn tất! Video đã sẵn sàng tải về.",
            "video_url": f"/api/download/{task_id}"
        }
        
    except Exception as e:
        logger.error(f"[{task_id}] Pipeline failed: {str(e)}", exc_info=True)
        # Clean up directory on failure if partial files exist
        tasks_db[task_id] = {
            "status": "failed",
            "progress": 100,
            "message": "Có lỗi xảy ra trong quá trình xử lý.",
            "error": str(e)
        }

@app.post("/api/translate")
def start_translation(request: TranslationRequest, background_tasks: BackgroundTasks):
    """
    Starts the video translation pipeline in the background.
    """
    if not request.url:
        raise HTTPException(status_code=400, detail="Bilibili URL is required.")
        
    task_id = str(uuid.uuid4())
    cookie_preview = request.bilibili_cookie[:15] + "..." if request.bilibili_cookie else "None"
    cookie_len = len(request.bilibili_cookie) if request.bilibili_cookie else 0
    logger.info(f"[{task_id}] start_translation endpoint called with bilibili_cookie={cookie_preview} (length={cookie_len})")
    
    tasks_db[task_id] = {
        "status": "pending",
        "progress": 0,
        "message": "Đang chuẩn bị tác vụ..."
    }
    
    background_tasks.add_task(
        process_video_pipeline,
        task_id=task_id,
        url=request.url,
        voice=request.voice,
        source_lang=request.source_lang,
        bg_volume=request.bg_volume,
        tts_volume=request.tts_volume,
        bilibili_cookie=request.bilibili_cookie
    )
    
    return {"task_id": task_id, "status": "pending"}

@app.get("/api/status/{task_id}")
def get_task_status(task_id: str):
    """
    Returns the current status and progress of a translation task.
    """
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found.")
    return tasks_db[task_id]

@app.get("/api/download/{task_id}")
def download_video(task_id: str):
    """
    Downloads the dubbed video.
    """
    video_path = os.path.join(TEMP_DIR, task_id, "output_dubbed.mp4")
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Processed video file not found.")
        
    # Return file as download attachment
    return FileResponse(
        path=video_path,
        media_type="video/mp4",
        filename=f"translated_{task_id[:8]}.mp4"
    )

# Serve the static UI files
# If index.html exists, mount static directory
if os.path.exists(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
