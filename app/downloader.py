import os
import re
import time
import shutil
import logging
import yt_dlp

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_ffmpeg_path():
    """
    Get the path to the ffmpeg executable.
    Checks system path first, then checks local bin directory.
    """
    ffmpeg_sys = shutil.which("ffmpeg")
    if ffmpeg_sys:
        return ffmpeg_sys
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for folder in ("bin", "ffmpeg"):
        local_ffmpeg = os.path.join(base_dir, folder, "ffmpeg.exe")
        if os.path.exists(local_ffmpeg):
            return local_ffmpeg

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
    
    with open(cookie_file_path, "w", encoding="utf-8") as f:
        f.write("# Netscape HTTP Cookie File\n")
        f.write("# This file is generated automatically\n")
        for key, val in cookies.items():
            f.write(f".bilibili.com\tTRUE\t/\tTRUE\t2147483647\t{key}\t{val}\n")
            
    return cookie_file_path


def download_bilibili_video(
    url: str,
    output_video_path: str,
    output_audio_path: str,
    progress_callback=None,
    bilibili_cookie: str = None,
    log_callback=None
):
    """
    Downloads Bilibili video and audio separately or together.
    - url: The Bilibili video URL
    - output_video_path: Path to save the downloaded mp4 video file
    - output_audio_path: Path to save the extracted wav/mp3 audio file
    - progress_callback: A function to call with progress updates: progress_callback(pct, msg=None)
    - bilibili_cookie: Optional manually provided Cookie string
    - log_callback: A function to call with progress logs: log_callback(msg, level="INFO")
    """
    # Clean and normalize Bilibili URL:
    if "bilibili.com" in url:
        url = re.sub(r'bilibili\.com/[a-z]{2}(?:-[a-z]{2,4})?/video/', 'bilibili.com/video/', url)
        p_match = re.search(r'[?&](p=\d+)', url)
        clean_base = url.split('?')[0].rstrip('/')
        url = f"{clean_base}?{p_match.group(1)}" if p_match else clean_base

    ffmpeg_path = get_ffmpeg_path()
    if not ffmpeg_path:
        logger.warning("ffmpeg was not found. Download might fail if merge is required.")
        if log_callback:
            log_callback("Không tìm thấy FFmpeg trong hệ thống, việc ghép video có thể thất bại.", level="WARN")

    # State tracker for smooth multi-stream progress (Video: 5-75%, Audio: 75-90%, FFmpeg: 90-100%)
    tracker = {
        "stream_index": 0,
        "last_filename": None,
        "last_log_time": 0.0,
        "last_raw_pct": 0.0
    }

    def safe_clean_str(val):
        if not val:
            return ""
        return re.sub(r'\x1b\[[0-9;]*m', '', str(val)).strip()

    # Custom progress hook for yt-dlp
    def ytdl_hook(d):
        if d.get('status') == 'downloading':
            current_fn = d.get('filename') or ""
            if tracker["last_filename"] and current_fn != tracker["last_filename"]:
                tracker["stream_index"] += 1
                if log_callback:
                    log_callback(f"Bắt đầu tải luồng media thứ {tracker['stream_index'] + 1}: {os.path.basename(current_fn)}", level="INFO")
            tracker["last_filename"] = current_fn

            raw_pct = None
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded = d.get('downloaded_bytes')
            if downloaded and total_bytes and total_bytes > 0:
                raw_pct = (downloaded / total_bytes) * 100.0
            else:
                percent_str = safe_clean_str(d.get('_percent_str', ''))
                m = re.search(r'(\d+(?:\.\d+)?)%', percent_str)
                if m:
                    try:
                        raw_pct = float(m.group(1))
                    except ValueError:
                        raw_pct = None

            if raw_pct is None:
                raw_pct = tracker["last_raw_pct"]
            else:
                tracker["last_raw_pct"] = raw_pct

            raw_pct = max(0.0, min(100.0, raw_pct))

            stream_idx = tracker["stream_index"]
            if stream_idx == 0:
                # Video stream: map to 5% -> 75%
                overall_pct = 5.0 + (raw_pct * 0.70)
                stream_label = "luồng video"
            else:
                # Audio or secondary stream: map to 75% -> 90%
                overall_pct = 75.0 + (raw_pct * 0.15)
                stream_label = "luồng âm thanh"

            overall_pct = min(90.0, overall_pct)

            speed_str = safe_clean_str(d.get('_speed_str', '')) or "N/A"
            eta_str = safe_clean_str(d.get('_eta_str', '')) or "N/A"
            down_str = safe_clean_str(d.get('_downloaded_bytes_str', ''))
            tot_str = safe_clean_str(d.get('_total_bytes_str', '') or d.get('_total_bytes_estimate_str', ''))

            msg = f"Đang tải {stream_label}... ({raw_pct:.1f}%)"
            if progress_callback:
                try:
                    progress_callback(overall_pct, msg=msg)
                except TypeError:
                    progress_callback(overall_pct)

            now = time.time()
            if log_callback and (now - tracker["last_log_time"] >= 1.0 or raw_pct >= 99.8):
                tracker["last_log_time"] = now
                size_str = f" | {down_str} / {tot_str}" if (down_str and tot_str) else ""
                log_callback(f"[Download] {raw_pct:.1f}%{size_str} | Tốc độ: {speed_str} | Còn lại: {eta_str}", level="INFO")

        elif d.get('status') == 'finished':
            fn = os.path.basename(d.get('filename', 'media'))
            if log_callback:
                log_callback(f"Đã tải xong luồng: {fn}", level="SUCCESS")

    class YtDlpCustomLogger:
        def __init__(self, callback):
            self.callback = callback
        def debug(self, msg):
            m = safe_clean_str(msg)
            if not m or m.startswith('[download]'):
                return
            if self.callback:
                self.callback(f"[yt-dlp] {m}", level="INFO")
        def info(self, msg):
            m = safe_clean_str(msg)
            if not m:
                return
            if self.callback:
                self.callback(f"[yt-dlp] {m}", level="INFO")
        def warning(self, msg):
            m = safe_clean_str(msg)
            if not m:
                return
            if self.callback:
                self.callback(f"[Cảnh báo] {m}", level="WARN")
        def error(self, msg):
            m = safe_clean_str(msg)
            if not m:
                return
            if self.callback:
                self.callback(f"[Lỗi] {m}", level="ERROR")

    # Options for downloading video
    ydl_opts_video = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': output_video_path,
        'merge_output_format': 'mp4',
        'progress_hooks': [ytdl_hook],
        'logger': YtDlpCustomLogger(log_callback) if log_callback else None,
        'nocheckcertificate': True,
        'quiet': False if log_callback else True,
        'socket_timeout': 60,
        'retries': 10,
        'fragment_retries': 10,
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
            if log_callback:
                log_callback("Đã áp dụng cookie xác thực tài khoản Bilibili.", level="SUCCESS")
        except Exception as e:
            logger.error(f"Failed to create temp cookie file: {e}")
            if log_callback:
                log_callback(f"Lỗi khởi tạo cookie tạm: {e}", level="WARN")

    if ffmpeg_path:
        ydl_opts_video['ffmpeg_location'] = ffmpeg_path

    logger.info(f"Starting video download from: {url}")
    if log_callback:
        log_callback(f"Bắt đầu kết nối tải video từ URL: {url}", level="INFO")
    if progress_callback:
        try:
            progress_callback(5.0, msg="Đang kết nối đến máy chủ video...")
        except TypeError:
            progress_callback(5.0)

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
    if log_callback:
        log_callback("Đã tải xong toàn bộ các luồng media. Đang chuẩn bị bóc tách âm thanh 16kHz WAV...", level="INFO")
    if progress_callback:
        try:
            progress_callback(90.0, msg="Đang chuẩn bị trích xuất âm thanh...")
        except TypeError:
            progress_callback(90.0)

    # Now extract the audio to output_audio_path using ffmpeg
    if ffmpeg_path and os.path.exists(output_video_path):
        import subprocess
        if log_callback:
            log_callback(f"[FFmpeg] Đang trích xuất âm thanh 16kHz mono sang {os.path.basename(output_audio_path)}...", level="INFO")
        if progress_callback:
            try:
                progress_callback(94.0, msg="FFmpeg: Đang trích xuất âm thanh 16kHz WAV...")
            except TypeError:
                progress_callback(94.0)

        cmd = [
            ffmpeg_path,
            '-y',
            '-i', output_video_path,
            '-vn',
            '-acodec', 'pcm_s16le',
            '-ar', '16000',
            '-ac', '1',
            output_audio_path
        ]
        logger.info(f"Running ffmpeg command to extract audio: {' '.join(cmd)}")
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        logger.info("Audio extraction completed successfully.")
        if log_callback:
            log_callback("[FFmpeg] Trích xuất âm thanh 16kHz WAV hoàn tất!", level="SUCCESS")
        if progress_callback:
            try:
                progress_callback(99.0, msg="Đang hoàn tất nạp video vào Studio...")
            except TypeError:
                progress_callback(99.0)
    else:
        raise FileNotFoundError("Could not extract audio because video file or ffmpeg was not found.")
