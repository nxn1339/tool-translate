import os
import uuid
import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, BackgroundTasks, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from app.card_renderer import render_social_card
from app.social_scraper import detect_social_platform, normalize_social_url, parse_threads_html_data, parse_cookie_string
from app.social_tts import generate_social_audio_timeline
from app.social_video_builder import build_social_short_video

logger = logging.getLogger(__name__)

router = APIRouter()

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PROJECTS_DIR = os.path.join(PROJECT_ROOT, "app", "projects")
BACKGROUNDS_DIR = os.path.join(PROJECT_ROOT, "app", "data", "backgrounds")
os.makedirs(PROJECTS_DIR, exist_ok=True)
os.makedirs(BACKGROUNDS_DIR, exist_ok=True)

# In-memory tracking for social video jobs
social_tasks: Dict[str, Dict[str, Any]] = {}


class SocialParseRequest(BaseModel):
    url: str
    cookie_raw: Optional[str] = None
    max_comments: int = 3
    include_op_chain: bool = True


class CommentItem(BaseModel):
    id: Optional[str] = None
    author: Optional[Dict[str, Any]] = None
    content: str
    likes: Optional[str] = "56"
    time_ago: Optional[str] = "1 giờ"
    voice: Optional[str] = None


class SocialGenerateRequest(BaseModel):
    platform: str = "threads"
    author_name: str = "Người dùng"
    author_handle: Optional[str] = "user"
    author_avatar: Optional[str] = None
    time_ago: Optional[str] = "2 giờ"
    post_content: str
    post_likes: Optional[str] = "1.8K"
    post_replies: Optional[str] = "42"
    comments: List[CommentItem] = []
    post_voice: str = "capcut_cogaithoatngon"
    background_video: Optional[str] = None
    bgm_track: Optional[str] = None
    dark_mode: bool = True


@router.post("/parse")
async def parse_social_url(req: SocialParseRequest):
    """
    Parses a Threads or Facebook URL.
    Returns post content, author details, and comments list.
    """
    url = normalize_social_url(req.url)
    platform = detect_social_platform(url)
    if platform == "unknown":
        raise HTTPException(status_code=400, detail="Chỉ hỗ trợ link Threads (threads.net / threads.com) hoặc Facebook.")

    cookies = parse_cookie_string(req.cookie_raw or "")

    # For threads, we try headless dump if browser is present
    parsed_data = None
    try:
        from app.social_scraper import fetch_threads_via_headless_browser
        parsed_data = fetch_threads_via_headless_browser(
            url,
            cookies=cookies,
            max_comments=req.max_comments,
            include_op_chain=req.include_op_chain
        )
    except Exception as e:
        logger.warning(f"Error scraping social url: {e}")

    # Fallback template if scraper is blocked or post is private
    if not parsed_data:
        parsed_data = {
            "platform": platform,
            "author": {
                "name": "Tác Giả Bài Viết",
                "handle": "author_user",
                "avatar": "https://static.cdninstagram.com/rsrc.php/v3/yI/r/VsNE-Bp2f_h.png",
                "is_verified": False
            },
            "content": "Nội dung bài viết chưa tải tự động được do trang yêu cầu đăng nhập. Bạn có thể paste trực tiếp nội dung vào đây.",
            "likes": "1.2K",
            "replies": "3",
            "time_ago": "2 giờ",
            "comments": [
                {
                    "id": "c_1",
                    "author": {"name": "Bình Luận Viên 1", "avatar": ""},
                    "content": "Bình luận đầu tiên về bài viết này...",
                    "likes": "45",
                    "time_ago": "1 giờ"
                },
                {
                    "id": "c_2",
                    "author": {"name": "Bình Luận Viên 2", "avatar": ""},
                    "content": "Bình luận thứ hai, rất đồng quan điểm!",
                    "likes": "30",
                    "time_ago": "30 phút"
                }
            ]
        }

    return parsed_data


@router.get("/backgrounds")
def list_background_videos():
    """Lists available background footage videos in app/data/backgrounds."""
    files = []
    if os.path.exists(BACKGROUNDS_DIR):
        for f in os.listdir(BACKGROUNDS_DIR):
            if f.lower().endswith((".mp4", ".mov", ".mkv", ".webm")):
                files.append(f)
    return {"backgrounds": files}


async def _run_video_generation_task(task_id: str, req: SocialGenerateRequest):
    task = social_tasks[task_id]
    task_dir = os.path.join(PROJECTS_DIR, task_id)
    os.makedirs(task_dir, exist_ok=True)

    try:
        # Step 1: Render Post Card to PNG
        task["status"] = "rendering_cards"
        task["message"] = "Đang tạo hình ảnh thẻ bài viết và bình luận..."
        task["progress"] = 20

        post_data = {
            "author": {
                "name": req.author_name,
                "handle": req.author_handle or "user",
                "avatar": req.author_avatar or "",
            },
            "content": req.post_content,
            "time_ago": req.time_ago or "2 giờ",
            "likes": req.post_likes or "1.5K",
            "replies": req.post_replies or str(len(req.comments))
        }

        post_card_path = os.path.join(task_dir, "card_post.png")
        render_social_card(post_data, post_card_path, platform=req.platform, is_comment=False, dark_mode=req.dark_mode)

        # Render each comment card
        comment_card_items = []
        for idx, c in enumerate(req.comments):
            c_dict = c.model_dump()
            c_id = c_dict.get("id") or f"c_{idx+1}"
            c_card_path = os.path.join(task_dir, f"card_comment_{idx+1}.png")
            render_social_card(c_dict, c_card_path, platform=req.platform, is_comment=True, dark_mode=req.dark_mode)
            comment_card_items.append({
                "comment_id": c_id,
                "card_path": c_card_path,
                "content": c_dict.get("content", ""),
                "voice": c_dict.get("voice")
            })

        # Step 2: Generate Audio with TTS
        task["status"] = "generating_audio"
        task["message"] = "Đang tạo giọng đọc AI cho bài viết và bình luận..."
        task["progress"] = 50

        audio_res = await generate_social_audio_timeline(
            post_text=req.post_content,
            comments=[c.model_dump() for c in req.comments],
            output_dir=task_dir,
            post_voice=req.post_voice
        )

        master_audio_path = audio_res["master_audio_path"]
        segments = audio_res["segments"]

        # Map start/end times to comment cards
        for seg in segments:
            if seg["type"] == "comment":
                idx = seg.get("index", 0)
                if idx < len(comment_card_items):
                    comment_card_items[idx]["start"] = seg["start"]
                    comment_card_items[idx]["end"] = seg["end"]

        # Step 3: Build Final Short Video
        task["status"] = "building_video"
        task["message"] = "Đang dựng và xuất video ngắn (FFmpeg)..."
        task["progress"] = 75

        bg_video_path = None
        if req.background_video:
            candidate = os.path.join(BACKGROUNDS_DIR, req.background_video)
            if os.path.isfile(candidate):
                bg_video_path = candidate

        out_video_path = os.path.join(task_dir, "short_video.mp4")
        build_social_short_video(
            post_card_path=post_card_path,
            comment_cards=comment_card_items,
            master_audio_path=master_audio_path,
            timeline_segments=segments,
            output_video_path=out_video_path,
            background_video_path=bg_video_path
        )

        task["status"] = "completed"
        task["message"] = "Video đã tạo thành công!"
        task["progress"] = 100
        task["video_url"] = f"/api/social/video/{task_id}"

    except Exception as e:
        logger.exception(f"Social video generation failed: {e}")
        task["status"] = "failed"
        task["message"] = f"Lỗi: {str(e)}"


@router.post("/generate")
async def generate_social_video(req: SocialGenerateRequest, background_tasks: BackgroundTasks):
    """Starts video creation in the background and returns task_id."""
    if not req.post_content.strip():
        raise HTTPException(status_code=400, detail="Nội dung bài viết không được để trống.")

    task_id = str(uuid.uuid4())
    social_tasks[task_id] = {
        "status": "pending",
        "progress": 5,
        "message": "Đang khởi tạo tác vụ tạo video..."
    }

    background_tasks.add_task(_run_video_generation_task, task_id, req)
    return {"task_id": task_id, "status": "started"}


@router.get("/status/{task_id}")
def get_social_task_status(task_id: str):
    """Polls progress of a video generation task."""
    task = social_tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task ID không tồn tại.")
    return task


@router.get("/video/{task_id}")
def download_social_video(task_id: str):
    """Serves the generated MP4 video file."""
    video_path = os.path.join(PROJECTS_DIR, task_id, "short_video.mp4")
    if not os.path.isfile(video_path):
        raise HTTPException(status_code=404, detail="Video chưa sẵn sàng hoặc không tồn tại.")
    return FileResponse(video_path, media_type="video/mp4", filename=f"short_{task_id[:8]}.mp4")

