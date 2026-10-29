import os
import re
import yt_dlp
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_ffmpeg_path():
    """
    Get the path to the ffmpeg executable.
    Checks system path first, then checks local bin directory.
    """
    # Check if ffmpeg is in system PATH
    import shutil
    ffmpeg_sys = shutil.which("ffmpeg")
    if ffmpeg_sys:
        return ffmpeg_sys
    
    # Check local bin or ffmpeg directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for folder in ("bin", "ffmpeg"):
        local_ffmpeg = os.path.join(base_dir, folder, "ffmpeg.exe")
        if os.path.exists(local_ffmpeg):
            return local_ffmpeg

    # Check WinGet links directory (added for Windows convenience)
    local_appdata = os.environ.get("LOCALAPPDATA")
    if local_appdata:
        winget_ffmpeg = os.path.join(local_appdata, "Microsoft", "WinGet", "Links", "ffmpeg.exe")
        if os.path.exists(winget_ffmpeg):
            return winget_ffmpeg
        
    return None

def get_ffprobe_path():
    """
    Get the path to the ffprobe executable.
    Checks system path first, then checks the same directory as ffmpeg.
    """
    import shutil
    ffprobe_sys = shutil.which("ffprobe")
    if ffprobe_sys:
        return ffprobe_sys
        
    ffmpeg_path = get_ffmpeg_path()
    if ffmpeg_path:
        ffmpeg_dir = os.path.dirname(ffmpeg_path)
        for name in ("ffprobe.exe", "ffprobe.EXE", "ffprobe"):
            candidate = os.path.join(ffmpeg_dir, name)
            if os.path.exists(candidate):
                return candidate

    return "ffprobe"

def _create_temp_cookie_file(cookie_str: str, task_dir: str) -> str:
    """
    Creates a temporary Netscape format cookie file from raw cookie string or SESSDATA.
    Automatically enriches with DedeUserID, buvid3 and buvid4 for seamless Bilibili extraction.
    """
    import urllib.parse
    import uuid
    import random
    import requests

    cookies = {}
    cookie_str = cookie_str.strip()
    
    # Check if it's a simple token or a full cookie string
    if "=" not in cookie_str and len(cookie_str) > 16:
        cookies["SESSDATA"] = cookie_str
    else:
        for part in cookie_str.split(";"):
            part = part.strip()
            if not part:
                continue
            if "=" in part:
                k, v = part.split("=", 1)
                cookies[k.strip()] = v.strip()
                
    # Auto-fetch DedeUserID (Member ID) if missing from cookies
    sessdata = cookies.get("SESSDATA")
    if sessdata and "DedeUserID" not in cookies:
        try:
            r = requests.get(
                "https://api.bilibili.com/x/web-interface/nav",
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Referer": "https://www.bilibili.com/"
                },
                cookies={"SESSDATA": urllib.parse.unquote(sessdata)},
                timeout=5
            )
            if r.status_code == 200:
                mid = r.json().get("data", {}).get("mid")
                if mid:
                    cookies["DedeUserID"] = str(mid)
                    logger.info(f"Automatically retrieved DedeUserID ({mid}) for SESSDATA.")
        except Exception as e:
            logger.warning(f"Could not auto-fetch DedeUserID: {e}")

    # Auto-generate buvid3 and buvid4 if not present in the provided cookies
    # to bypass Bilibili anti-bot HTTP 412 Precondition Failed error
    if "buvid3" not in cookies:
        uid = str(uuid.uuid4()).upper()
        digits = "".join(str(random.randint(0, 9)) for _ in range(5))
        cookies["buvid3"] = f"{uid}{digits}infoc"
        logger.info("Automatically generated buvid3 cookie to prevent Bilibili HTTP 412")

    if "buvid4" not in cookies:
        uid = str(uuid.uuid4()).upper()
        digits = "".join(str(random.randint(0, 9)) for _ in range(5))
        cookies["buvid4"] = f"{uid}{digits}infoc"
        logger.info("Automatically generated buvid4 cookie to prevent Bilibili HTTP 412")

    cookie_file_path = os.path.join(task_dir, "cookies_temp.txt")
    
    # Write in Netscape Cookie File format
    with open(cookie_file_path, "w", encoding="utf-8") as f:
        f.write("# Netscape HTTP Cookie File\n")
        f.write("# This file is generated automatically\n")
        for key, val in cookies.items():
            # domain, include_subdomains, path, is_secure, expiry, name, value
            f.write(f".bilibili.com\tTRUE\t/\tTRUE\t2147483647\t{key}\t{val}\n")
            
    return cookie_file_path

def download_bilibili_video(url: str, output_video_path: str, output_audio_path: str, progress_callback=None, bilibili_cookie: str = None):
    """
    Downloads Bilibili video and audio separately or together.
    - url: The Bilibili video URL
    - output_video_path: Path to save the downloaded mp4 video file
    - output_audio_path: Path to save the extracted wav/mp3 audio file
    - progress_callback: A function to call with progress updates
    - bilibili_cookie: Optional manually provided Cookie string
    """
    # Clean and normalize Bilibili URL:
    # 1. Remove language prefixes like /vi/, /en/, /id/, /th/, etc. that break yt-dlp's Bilibili extractor
    # 2. Strip tracking parameters like ?spm_id_from=... but retain ?p= if present
    if "bilibili.com" in url:
        url = re.sub(r'bilibili\.com/[a-z]{2}(?:-[a-z]{2,4})?/video/', 'bilibili.com/video/', url)
        p_match = re.search(r'[?&](p=\d+)', url)
        clean_base = url.split('?')[0].rstrip('/')
        url = f"{clean_base}?{p_match.group(1)}" if p_match else clean_base

    ffmpeg_path = get_ffmpeg_path()
    if not ffmpeg_path:
        logger.warning("ffmpeg was not found. Download might fail if merge is required.")

    # Custom progress hook for yt-dlp
    def ytdl_hook(d):
        if d['status'] == 'downloading':
            percent_str = d.get('_percent_str', '0%').strip()
            # Clean ANSI escape sequences from percent_str if any
            clean_percent = ''.join(c for c in percent_str if c.isdigit() or c == '.')
            if clean_percent and progress_callback:
                try:
                    progress_callback(float(clean_percent))
                except ValueError:
                    pass
        elif d['status'] == 'finished':
            if progress_callback:
                progress_callback(100.0)

    # Options for downloading video
    ydl_opts_video = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': output_video_path,
        'merge_output_format': 'mp4',
        'progress_hooks': [ytdl_hook],
        'nocheckcertificate': True,
        'quiet': True,
        'socket_timeout': 60,       # Increase timeout from 20s to 60s for slow connections
        'retries': 10,              # Retry 10 times on transient network errors
        'fragment_retries': 10,     # Retry 10 times for chunk/fragment download failures
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Referer': 'https://www.bilibili.com/',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,vi;q=0.7',
        },
    }

    temp_cookie_path = None
    if bilibili_cookie and bilibili_cookie.strip():
        task_dir = os.path.dirname(output_video_path)
        try:
            temp_cookie_path = _create_temp_cookie_file(bilibili_cookie, task_dir)
            ydl_opts_video['cookiefile'] = temp_cookie_path
            logger.info(f"Using manually provided cookie file: {temp_cookie_path}")
        except Exception as e:
            logger.error(f"Failed to create temp cookie file: {e}")

    if ffmpeg_path:
        ydl_opts_video['ffmpeg_location'] = ffmpeg_path

    logger.info(f"Starting video download from: {url}")
    if progress_callback:
        progress_callback(0.0)

    try:
        try:
            with yt_dlp.YoutubeDL(ydl_opts_video) as ydl:
                ydl.download([url])
        except Exception as e:
            err_str = str(e)
            if "412" in err_str or "Precondition Failed" in err_str or "Unable to extract initial state" in err_str:
                raise ValueError(
                    "Bilibili chặn tải video từ địa chỉ IP này (Lỗi HTTP 412 / Cần xác thực). "
                    "Vui lòng mở mục 'Cookie Bilibili (Tùy chọn)' ở Bước 1 và dán mã SESSDATA "
                    "từ tài khoản Bilibili của bạn trên trình duyệt để tiếp tục tải."
                )
            if "unusual and will be skipped" in err_str or "extension ('html')" in err_str:
                raise ValueError(
                    "Không thể bóc tách luồng video từ link này (Lỗi nhận diện trang HTML). "
                    "Vui lòng kiểm tra lại đường link video chuẩn (dạng https://www.bilibili.com/video/BV...)."
                )
            raise e
    finally:
        # Clean up temporary cookie file if created
        if temp_cookie_path and os.path.exists(temp_cookie_path):
            try:
                os.remove(temp_cookie_path)
                logger.info("Cleaned up temporary cookie file.")
            except OSError:
                pass

    logger.info("Video download completed. Extracting audio...")

    # Now extract the audio to output_audio_path using ffmpeg
    if ffmpeg_path and os.path.exists(output_video_path):
        import subprocess
        # Extract audio as WAV (16kHz, mono, suitable for Speech-To-Text)
        cmd = [
            ffmpeg_path,
            '-y',  # Overwrite output file if it exists
            '-i', output_video_path,
            '-vn',  # Disable video recording
            '-acodec', 'pcm_s16le',
            '-ar', '16000',
            '-ac', '1',
            output_audio_path
        ]
        logger.info(f"Running ffmpeg command to extract audio: {' '.join(cmd)}")
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        logger.info("Audio extraction completed successfully.")
    else:
        raise FileNotFoundError("Could not extract audio because video file or ffmpeg was not found.")
