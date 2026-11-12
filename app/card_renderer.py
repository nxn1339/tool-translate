import os
import subprocess
import shutil
import logging
from typing import Dict, Any, Optional
from PIL import Image

logger = logging.getLogger(__name__)

# Search paths for Chromium-based browsers on Windows
BROWSER_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]


def get_browser_executable() -> Optional[str]:
    """Finds an installed Chrome or Edge executable on Windows."""
    for path in BROWSER_CANDIDATES:
        if os.path.isfile(path):
            return path
    which_chrome = shutil.which("chrome")
    if which_chrome:
        return which_chrome
    which_edge = shutil.which("msedge")
    if which_edge:
        return which_edge
    return None


def crop_transparent_borders(image_path: str, padding: int = 16) -> bool:
    """Crops transparent borders around an image with optional padding."""
    try:
        with Image.open(image_path) as im:
            if im.mode != "RGBA":
                im = im.convert("RGBA")
            bbox = im.getbbox()
            if bbox:
                left = max(0, bbox[0] - padding)
                upper = max(0, bbox[1] - padding)
                right = min(im.width, bbox[2] + padding)
                lower = min(im.height, bbox[3] + padding)
                cropped = im.crop((left, upper, right, lower))
                cropped.save(image_path, "PNG")
                return True
    except Exception as e:
        logger.warning(f"Error cropping transparent borders for {image_path}: {e}")
    return False


def generate_avatar_svg(name: str, size: int = 76) -> str:
    """Generates an aesthetic inline SVG gradient circle with the author's initial."""
    initial = (name.strip()[0] if name and name.strip() else 'U').upper()
    palette = [
        ("#6366f1", "#a855f7"), # Indigo to Purple
        ("#ec4899", "#f43f5e"), # Pink to Rose
        ("#06b6d4", "#3b82f6"), # Cyan to Blue
        ("#10b981", "#059669"), # Emerald
        ("#f59e0b", "#d97706"), # Amber
    ]
    c1, c2 = palette[abs(hash(name)) % len(palette)]
    grad_id = f"av_grad_{abs(hash(name)) % 1000}"
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="{grad_id}" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="{c1}"/>
                <stop offset="100%" stop-color="{c2}"/>
            </linearGradient>
        </defs>
        <circle cx="{size/2}" cy="{size/2}" r="{size/2}" fill="url(#{grad_id})"/>
        <text x="{size/2}" y="{size*0.64}" text-anchor="middle" fill="#ffffff" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-weight="800" font-size="{int(size*0.48)}">{initial}</text>
    </svg>"""


def truncate_card_display_text(text: str, max_chars: int = 500) -> str:
    """
    Limits text length on the visible card image so it stays within vertical bounds.
    Voice AI still reads the full story.
    """
    text = text.strip()
    if len(text) <= max_chars:
        return text
    cutoff = text[:max_chars].rfind(" ")
    if cutoff == -1 or cutoff < 280:
        cutoff = max_chars
    return text[:cutoff] + "... [Xem tiếp câu chuyện trong video]"


def build_threads_post_html(data: Dict[str, Any], dark_mode: bool = True) -> str:
    """Generates pixel-perfect HTML/CSS for a Threads post card."""
    bg_color = "#121212" if dark_mode else "#ffffff"
    text_color = "#f3f5f7" if dark_mode else "#000000"
    sub_color = "#777777" if dark_mode else "#999999"
    border_color = "rgba(255, 255, 255, 0.12)" if dark_mode else "rgba(0, 0, 0, 0.08)"
    icon_fill = "#f3f5f7" if dark_mode else "#111111"

    author = data.get("author", {})
    name = author.get("name", "Người dùng Threads")
    handle = author.get("handle", "threads_user")
    time_ago = data.get("time_ago", "2 giờ")
    raw_content = data.get("content", "")
    content = truncate_card_display_text(raw_content, 500).replace("\n", "<br>")
    likes = data.get("likes", "1.2K")
    replies = data.get("replies", "148")
    avatar_svg = generate_avatar_svg(name, 76)

    # Threads Verified Badge SVG
    verified_badge = """
    <svg width="18" height="18" viewBox="0 0 24 24" fill="#0095f6" style="vertical-align: middle; margin-left: 4px;">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
    </svg>
    """ if author.get("is_verified") else ""

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html, body {{
        background: transparent !important;
        overflow: hidden !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        display: inline-block;
        padding: 30px;
    }}
    ::-webkit-scrollbar {{
        display: none !important;
        width: 0 !important;
        height: 0 !important;
    }}
    .card {{
        width: 920px;
        background-color: {bg_color};
        color: {text_color};
        border-radius: 36px;
        padding: 40px;
        border: 1px solid {border_color};
        box-shadow: 0 24px 60px rgba(0,0,0,0.5);
    }}
    .header {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 24px;
    }}
    .author-info {{
        display: flex;
        align-items: center;
        gap: 20px;
    }}
    .avatar-wrap {{
        width: 76px;
        height: 76px;
        border-radius: 50%;
        overflow: hidden;
        flex-shrink: 0;
    }}
    .names {{
        display: flex;
        flex-direction: column;
        gap: 4px;
    }}
    .display-name {{
        font-size: 32px;
        font-weight: 700;
        line-height: 1.2;
        display: flex;
        align-items: center;
    }}
    .handle-time {{
        font-size: 22px;
        color: {sub_color};
    }}
    .threads-logo {{
        width: 44px;
        height: 44px;
        fill: {text_color};
    }}
    .content {{
        font-size: 34px;
        line-height: 1.48;
        font-weight: 400;
        word-break: break-word;
        margin-bottom: 32px;
        letter-spacing: -0.2px;
    }}
    .actions {{
        display: flex;
        align-items: center;
        gap: 32px;
        margin-top: 12px;
        padding-top: 24px;
        border-top: 1px solid {border_color};
    }}
    .action-btn {{
        display: flex;
        align-items: center;
        gap: 10px;
        color: {sub_color};
        font-size: 24px;
        font-weight: 600;
    }}
    .action-btn svg {{
        width: 30px;
        height: 30px;
        stroke: {icon_fill};
        fill: none;
        stroke-width: 2.2;
    }}
</style>
</head>
<body>
    <div class="card">
        <div class="header">
            <div class="author-info">
                <div class="avatar-wrap">{avatar_svg}</div>
                <div class="names">
                    <span class="display-name">{name}{verified_badge}</span>
                    <span class="handle-time">@{handle} · {time_ago}</span>
                </div>
            </div>
            <!-- Threads Official Glyph SVG -->
            <svg class="threads-logo" viewBox="0 0 192 192">
                <path d="M141.537 88.9883C140.71 88.5919 139.87 88.2104 139.019 87.8451C137.537 60.5382 122.616 44.905 97.5619 44.745C97.4101 44.7441 97.2583 44.7441 97.1065 44.745C75.2974 44.745 57.5756 59.8378 54.1205 81.3323C49.9982 106.974 65.5791 129.213 90.0416 132.748C90.3129 132.787 90.5849 132.823 90.8576 132.855C104.996 134.52 118.847 130.407 127.973 121.849L128.016 121.808C129.585 120.317 129.626 117.847 128.114 116.305C126.611 114.773 124.161 114.746 122.625 116.241C115.342 123.067 104.092 126.248 92.4278 124.873C74.0734 122.221 61.9429 104.945 65.2505 84.3725C68.043 66.9945 82.3556 54.8966 97.1065 54.8966C97.2272 54.8957 97.3486 54.8957 97.4693 54.8966C116.892 55.0204 127.818 66.9737 128.986 88.083C119.57 86.8398 107.591 86.6806 94.6738 88.8519C69.6053 93.0654 54.8995 106.331 56.4026 122.463C57.876 138.272 73.0805 147.886 91.1378 147.886C108.975 147.886 123.639 139.73 129.704 128.329C134.464 135.214 141.246 139.792 150.158 140.231C164.766 140.952 174.004 130.569 174.577 116.223C175.185 100.99 164.912 87.8942 141.537 88.9883ZM93.1872 138.006C78.4316 138.006 67.2023 130.82 66.2737 120.865C65.3059 110.49 75.3184 101.442 96.229 97.9272C106.634 96.1784 116.744 96.3478 125.105 97.6826C122.569 126.969 108.799 138.006 93.1872 138.006Z"/>
            </svg>
        </div>
        <div class="content">{content}</div>
        <div class="actions">
            <div class="action-btn">
                <svg viewBox="0 0 24 24"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>
                <span>{likes}</span>
            </div>
            <div class="action-btn">
                <svg viewBox="0 0 24 24"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg>
                <span>{replies}</span>
            </div>
            <div class="action-btn">
                <svg viewBox="0 0 24 24"><polyline points="17 1 21 5 17 9"></polyline><path d="M3 11V9a4 4 0 0 1 4-4h14"></path><polyline points="7 23 3 19 7 15"></polyline><path d="M21 13v2a4 4 0 0 1-4 4H3"></path></svg>
            </div>
        </div>
    </div>
</body>
</html>"""


def build_threads_comment_html(comment: Dict[str, Any], dark_mode: bool = True) -> str:
    """Generates pixel-perfect HTML/CSS for a Threads comment card."""
    bg_color = "#181818" if dark_mode else "#f5f5f5"
    text_color = "#f3f5f7" if dark_mode else "#000000"
    sub_color = "#777777" if dark_mode else "#888888"
    border_color = "rgba(255, 255, 255, 0.15)" if dark_mode else "rgba(0, 0, 0, 0.08)"

    author = comment.get("author", {})
    name = author.get("name", "Người bình luận")
    time_ago = comment.get("time_ago", "1 giờ")
    raw_content = comment.get("content", "")
    content = truncate_card_display_text(raw_content, 350).replace("\n", "<br>")
    likes = comment.get("likes", "86")
    avatar_svg = generate_avatar_svg(name, 60)

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html, body {{
        background: transparent !important;
        overflow: hidden !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        display: inline-block;
        padding: 24px;
    }}
    ::-webkit-scrollbar {{
        display: none !important;
        width: 0 !important;
        height: 0 !important;
    }}
    .comment-card {{
        width: 880px;
        background-color: {bg_color};
        color: {text_color};
        border-radius: 28px;
        padding: 28px 32px;
        border: 1px solid {border_color};
        box-shadow: 0 16px 40px rgba(0,0,0,0.45);
        display: flex;
        gap: 20px;
    }}
    .avatar-wrap {{
        width: 60px;
        height: 60px;
        border-radius: 50%;
        overflow: hidden;
        flex-shrink: 0;
    }}
    .body {{
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 8px;
    }}
    .header {{
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}
    .name {{
        font-size: 26px;
        font-weight: 700;
    }}
    .time {{
        font-size: 20px;
        color: {sub_color};
    }}
    .text {{
        font-size: 30px;
        line-height: 1.42;
        word-break: break-word;
        font-weight: 400;
    }}
    .footer {{
        display: flex;
        align-items: center;
        gap: 16px;
        margin-top: 10px;
        color: {sub_color};
        font-size: 20px;
        font-weight: 600;
    }}
    .like-icon {{
        width: 22px;
        height: 22px;
        fill: none;
        stroke: {sub_color};
        stroke-width: 2.2;
    }}
</style>
</head>
<body>
    <div class="comment-card">
        <div class="avatar-wrap">{avatar_svg}</div>
        <div class="body">
            <div class="header">
                <span class="name">{name}</span>
                <span class="time">{time_ago}</span>
            </div>
            <div class="text">{content}</div>
            <div class="footer">
                <svg class="like-icon" viewBox="0 0 24 24"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>
                <span>{likes}</span>
            </div>
        </div>
    </div>
</body>
</html>"""


def build_facebook_post_html(data: Dict[str, Any], dark_mode: bool = True) -> str:
    """Generates pixel-perfect HTML/CSS for a Facebook post card."""
    bg_color = "#242526" if dark_mode else "#ffffff"
    text_color = "#e4e6eb" if dark_mode else "#050505"
    sub_color = "#b0b3b8" if dark_mode else "#65676b"
    border_color = "rgba(255, 255, 255, 0.1)" if dark_mode else "rgba(0, 0, 0, 0.1)"

    author = data.get("author", {})
    name = author.get("name", "Người dùng Facebook")
    time_ago = data.get("time_ago", "Vừa xong")
    raw_content = data.get("content", "")
    content = truncate_card_display_text(raw_content, 500).replace("\n", "<br>")
    likes = data.get("likes", "5.4K")
    comments_count = data.get("replies", "382")
    avatar_svg = generate_avatar_svg(name, 72)

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html, body {{
        background: transparent !important;
        overflow: hidden !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        display: inline-block;
        padding: 30px;
    }}
    ::-webkit-scrollbar {{
        display: none !important;
        width: 0 !important;
        height: 0 !important;
    }}
    .card {{
        width: 920px;
        background-color: {bg_color};
        color: {text_color};
        border-radius: 28px;
        padding: 36px;
        border: 1px solid {border_color};
        box-shadow: 0 20px 50px rgba(0,0,0,0.5);
    }}
    .header {{
        display: flex;
        align-items: center;
        gap: 18px;
        margin-bottom: 24px;
    }}
    .avatar-wrap {{
        width: 72px;
        height: 72px;
        border-radius: 50%;
        overflow: hidden;
        flex-shrink: 0;
    }}
    .meta {{
        display: flex;
        flex-direction: column;
        gap: 4px;
    }}
    .author-name {{
        font-size: 30px;
        font-weight: 700;
    }}
    .post-info {{
        font-size: 22px;
        color: {sub_color};
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    .globe-icon {{
        width: 16px;
        height: 16px;
        fill: {sub_color};
    }}
    .content {{
        font-size: 34px;
        line-height: 1.48;
        word-break: break-word;
        margin-bottom: 28px;
    }}
    .stats {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding-top: 20px;
        border-top: 1px solid {border_color};
        color: {sub_color};
        font-size: 22px;
        font-weight: 500;
    }}
    .reactions {{
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    .react-icon {{
        width: 30px;
        height: 30px;
    }}
</style>
</head>
<body>
    <div class="card">
        <div class="header">
            <div class="avatar-wrap">{avatar_svg}</div>
            <div class="meta">
                <span class="author-name">{name}</span>
                <span class="post-info">
                    {time_ago} ·
                    <svg class="globe-icon" viewBox="0 0 16 16"><path d="M8 0a8 8 0 1 0 0 16A8 8 0 0 0 8 0zm6.5 7.5h-2.1a12.5 12.5 0 0 0-1-4.2 6.5 6.5 0 0 1 3.1 4.2zm-5 0H6.5a11 11 0 0 1 .9-4.8 6.6 6.6 0 0 1 .9 0 11 11 0 0 1 .7 4.8zm-4.9 0H2.5A6.5 6.5 0 0 1 5.6 3.3a12.5 12.5 0 0 0-1 4.2zm0 1c.1 1.5.5 3 1 4.2A6.5 6.5 0 0 1 2.5 8.5h2.1zm1.4 0h3a11 11 0 0 1-.9 4.8 6.6 6.6 0 0 1-.9 0 11 11 0 0 1-.7-4.8zm4.4 0h2.1a6.5 6.5 0 0 1-3.1 4.2 12.5 12.5 0 0 0 1-4.2z"/></svg>
                </span>
            </div>
        </div>
        <div class="content">{content}</div>
        <div class="stats">
            <div class="reactions">
                <svg class="react-icon" viewBox="0 0 36 36"><path fill="#0866FF" d="M18 36c9.941 0 18-8.059 18-18S27.941 0 18 0 0 8.059 0 18s8.059 18 18 18z"/><path fill="#FFF" d="M25.7 16.5c-.2-.7-.7-1.1-1.4-1.2h-3.9c.3-1.6.8-3.6.4-5.2-.4-1.6-1.5-2.1-2.4-2.1-.6 0-1.1.4-1.3.9-.2.5-.2 1.3-.2 2.2 0 1.9-.9 3.5-1.9 4.8l-1.3 1.6v10.5c.9.3 1.9.5 3 .5h7.2c1.4 0 2.5-.9 2.8-2.2l1.3-6.5c.3-1.4-.3-2.7-1.3-3.3zM11 17h2v11.5h-2z"/></svg>
                <span>{likes}</span>
            </div>
            <div>{comments_count} bình luận</div>
        </div>
    </div>
</body>
</html>"""


def build_facebook_comment_html(comment: Dict[str, Any], dark_mode: bool = True) -> str:
    """Generates pixel-perfect HTML/CSS for a Facebook comment card."""
    bubble_bg = "#3a3b3c" if dark_mode else "#f0f2f5"
    text_color = "#e4e6eb" if dark_mode else "#050505"
    sub_color = "#b0b3b8" if dark_mode else "#65676b"

    author = comment.get("author", {})
    name = author.get("name", "Người bình luận")
    time_ago = comment.get("time_ago", "2 giờ")
    raw_content = comment.get("content", "")
    content = truncate_card_display_text(raw_content, 320).replace("\n", "<br>")
    likes = comment.get("likes", "24")
    avatar_svg = generate_avatar_svg(name, 64)

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html, body {{
        background: transparent !important;
        overflow: hidden !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        display: inline-block;
        padding: 20px;
    }}
    ::-webkit-scrollbar {{
        display: none !important;
        width: 0 !important;
        height: 0 !important;
    }}
    .comment-container {{
        width: 880px;
        display: flex;
        gap: 16px;
        align-items: flex-start;
    }}
    .avatar-wrap {{
        width: 64px;
        height: 64px;
        border-radius: 50%;
        overflow: hidden;
        flex-shrink: 0;
    }}
    .bubble-wrapper {{
        flex: 1;
        display: flex;
        flex-direction: column;
    }}
    .bubble {{
        background-color: {bubble_bg};
        color: {text_color};
        border-radius: 24px;
        padding: 20px 24px;
        box-shadow: 0 12px 30px rgba(0,0,0,0.35);
        display: inline-block;
        position: relative;
    }}
    .author-name {{
        font-size: 26px;
        font-weight: 700;
        margin-bottom: 6px;
    }}
    .comment-text {{
        font-size: 30px;
        line-height: 1.4;
        word-break: break-word;
    }}
    .sub-meta {{
        display: flex;
        gap: 20px;
        padding-left: 20px;
        margin-top: 8px;
        font-size: 20px;
        color: {sub_color};
        font-weight: 600;
    }}
</style>
</head>
<body>
    <div class="comment-container">
        <div class="avatar-wrap">{avatar_svg}</div>
        <div class="bubble-wrapper">
            <div class="bubble">
                <div class="author-name">{name}</div>
                <div class="comment-text">{content}</div>
            </div>
            <div class="sub-meta">
                <span>{time_ago}</span>
                <span>Thích · {likes}</span>
                <span>Trả lời</span>
            </div>
        </div>
    </div>
</body>
</html>"""


def render_html_to_png(html_content: str, output_png_path: str, scale: int = 1) -> str:
    """
    Renders an HTML string into a transparent PNG screenshot using headless Chrome or Edge.
    Uses scale=1 to exactly match 1080x1920 video canvas boundaries.
    """
    browser_exe = get_browser_executable()
    if not browser_exe:
        raise RuntimeError("No Chrome or Edge browser found on this system.")

    output_png_path = os.path.abspath(output_png_path)
    os.makedirs(os.path.dirname(output_png_path), exist_ok=True)
    
    temp_html_path = output_png_path + ".temp.html"
    with open(temp_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    html_url = "file:///" + os.path.abspath(temp_html_path).replace("\\", "/")

    cmd = [
        browser_exe,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--hide-scrollbars",
        "--window-size=1280,3000",
        "--default-background-color=00000000",
        f"--force-device-scale-factor={scale}",
        f"--screenshot={output_png_path}",
        html_url
    ]

    try:
        res = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            errors="replace",
            timeout=25
        )
        if res.returncode != 0:
            logger.error(f"Browser screenshot failed: {res.stderr}")
            raise RuntimeError(f"Browser failed to render HTML: {res.stderr}")

        # Crop transparent padding for neat composition
        crop_transparent_borders(output_png_path, padding=16)
        return output_png_path
    finally:
        if os.path.exists(temp_html_path):
            try:
                os.remove(temp_html_path)
            except Exception:
                pass


def render_social_card(data: Dict[str, Any], output_path: str, platform: str = "threads", is_comment: bool = False, dark_mode: bool = True) -> str:
    """
    Convenience wrapper to render either Threads or Facebook Post/Comment card to PNG.
    """
    platform = platform.lower()
    if platform == "facebook":
        html = build_facebook_comment_html(data, dark_mode) if is_comment else build_facebook_post_html(data, dark_mode)
    else:  # Default to Threads
        html = build_threads_comment_html(data, dark_mode) if is_comment else build_threads_post_html(data, dark_mode)

    return render_html_to_png(html, output_path, scale=1)
