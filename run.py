import os
import sys
import subprocess
import webbrowser
import time
import threading

# Add current directory to python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def setup_ffmpeg():
    """
    Downloads and configures FFmpeg automatically on Windows if not available in system path.
    """
    import shutil
    if shutil.which("ffmpeg"):
        print("[System Check] FFmpeg is already installed in the system PATH.")
        return

    # Check local bin directory
    bin_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin")
    ffmpeg_exe = os.path.join(bin_dir, "ffmpeg.exe")
    ffprobe_exe = os.path.join(bin_dir, "ffprobe.exe")

    if os.path.exists(ffmpeg_exe) and os.path.exists(ffprobe_exe):
        print("[System Check] FFmpeg is already configured in the local bin/ folder.")
        return

    # Check WinGet installation path
    local_appdata = os.environ.get("LOCALAPPDATA")
    if local_appdata:
        winget_ffmpeg = os.path.join(local_appdata, "Microsoft", "WinGet", "Links", "ffmpeg.exe")
        winget_ffprobe = os.path.join(local_appdata, "Microsoft", "WinGet", "Links", "ffprobe.exe")
        if os.path.exists(winget_ffmpeg) and os.path.exists(winget_ffprobe):
            print("[System Check] FFmpeg is already installed via WinGet.")
            return

    print("[Setup] FFmpeg was not found on your system.")
    print("[Setup] Automatically downloading FFmpeg Release Essentials for Windows (approx. 35MB)...")
    
    import urllib.request
    import zipfile
    
    url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    temp_zip = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffmpeg_temp.zip")
    
    os.makedirs(bin_dir, exist_ok=True)
    
    try:
        def progress_callback(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(100.0, downloaded * 100 / total_size)
                sys.stdout.write(f"\rDownloading: {percent:.1f}%")
            else:
                sys.stdout.write(f"\rDownloaded: {downloaded / (1024*1024):.1f} MB")
            sys.stdout.flush()

        urllib.request.urlretrieve(url, temp_zip, progress_callback)
        sys.stdout.write("\nDownload completed! Extracting FFmpeg binaries...\n")
        sys.stdout.flush()
        
        # Extract only the executables to target folder
        with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
            for member in zip_ref.namelist():
                filename = os.path.basename(member)
                if filename == "ffmpeg.exe":
                    with zip_ref.open(member) as source, open(ffmpeg_exe, "wb") as target:
                        shutil.copyfileobj(source, target)
                    print("- Extracted ffmpeg.exe")
                elif filename == "ffprobe.exe":
                    with zip_ref.open(member) as source, open(ffprobe_exe, "wb") as target:
                        shutil.copyfileobj(source, target)
                    print("- Extracted ffprobe.exe")
                    
        print("[Setup] Local FFmpeg setup completed successfully!")
    except Exception as e:
        print(f"\n[Error] Failed to configure FFmpeg: {e}")
        print("[Warning] Video mixing may fail. Please install FFmpeg manually on your Windows machine.")
    finally:
        if os.path.exists(temp_zip):
            try:
                os.remove(temp_zip)
            except OSError:
                pass

def install_dependencies():
    """
    Checks and installs requirements.txt dependencies automatically.
    """
    print("[Setup] Checking python dependencies...")
    req_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements.txt")
    if not os.path.exists(req_file):
        print("[Warning] requirements.txt not found. Skipping auto-installation.")
        return
        
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_file])
        print("[Setup] Python dependencies checked and updated.")
    except Exception as e:
        print(f"[Error] Failed to automatically install dependencies: {e}")
        print("[Warning] Please install them manually via: pip install -r requirements.txt")

import socket

PORT = 8080

def find_free_port():
    """
    Finds a free port on the system.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(('localhost', 8080))
        return 8080
    except OSError:
        # Port 8080 is taken, find any free port
        s.bind(('', 0))
        return s.getsockname()[1]
    finally:
        s.close()

def open_browser():
    """
    Delay opening the browser by 2.5 seconds to let the server start up.
    """
    time.sleep(2.5)
    print(f"[System] Opening application in your web browser at http://localhost:{PORT} ...")
    webbrowser.open(f"http://localhost:{PORT}")

def main():
    global PORT
    print("====================================================")
    print("        AI Video Dubber - Start Script              ")
    print("====================================================")
    
    # 1. Setup local FFmpeg
    setup_ffmpeg()
    
    # 2. Check & Install python packages
    install_dependencies()
    
    # 3. Find a free port
    PORT = find_free_port()
    
    # 4. Open browser on background thread
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # 5. Run FastAPI Server via Uvicorn
    print(f"[System] Starting server on port {PORT}...")
    import uvicorn
    uvicorn.run("app.main:app", host="localhost", port=PORT, reload=False)

if __name__ == "__main__":
    main()
