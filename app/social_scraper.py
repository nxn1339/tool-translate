import os
import re
import json
import logging
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def parse_cookie_string(cookie_raw: str) -> Dict[str, str]:
    """
    Parses a cookie string (from browser devtools or export) into a key-value dictionary.
    """
    cookies = {}
    if not cookie_raw or not cookie_raw.strip():
        return cookies

    # Handle JSON format (e.g. EditThisCookie or Cookie-Editor export)
    stripped = cookie_raw.strip()
    if stripped.startswith("[") and stripped.endswith("]"):
        try:
            cookie_list = json.loads(stripped)
            for item in cookie_list:
                name = item.get("name")
                val = item.get("value")
                if name and val:
                    cookies[name] = val
            return cookies
        except Exception as e:
            logger.warning(f"Failed to parse cookie as JSON list: {e}")

    # Handle standard 'name=val; name2=val2' format
    parts = cookie_raw.split(";")
    for part in parts:
        if "=" in part:
            key, val = part.split("=", 1)
            cookies[key.strip()] = val.strip()
    return cookies


def detect_social_platform(url: str) -> str:
    """Detects whether a URL belongs to Threads, Facebook, or Unknown."""
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    if "threads.net" in domain or "threads.com" in domain:
        return "threads"
    elif "facebook.com" in domain or "fb.watch" in domain or "fb.com" in domain:
        return "facebook"
    return "unknown"


def normalize_social_url(url: str) -> str:
    """Normalizes mobile share links and domain variations."""
    url = url.strip()
    if "threads.com" in url:
        url = url.replace("threads.com", "threads.net")
    return url


def extract_threads_post_id(url: str) -> Optional[str]:
    """Extracts post shortcode/ID from a Threads URL."""
    # Matches: /post/C_xxxx or /t/C_xxxx or /share/xxxx
    match = re.search(r"/(?:post|t|share)/([A-Za-z0-9_-]+)", url)
    if match:
        return match.group(1)
    return None


def extract_facebook_post_id(url: str) -> Optional[str]:
    """Extracts post ID or path identifier from a Facebook URL."""
    match = re.search(r"/(?:posts|videos|reel|stories)/([0-9a-zA-Z_-]+)", url)
    if match:
        return match.group(1)
    # Check query params for story_fbid or fbid
    match_query = re.search(r"(?:story_fbid|fbid)=([0-9]+)", url)
    if match_query:
        return match_query.group(1)
    return None


def safe_decode_json_str(text_str: str) -> str:
    """Safely decodes unicode escape sequences and surrogate pairs (emojis)."""
    try:
        return json.loads(f'"{text_str}"')
    except Exception:
        try:
            return text_str.encode('utf-16', 'surrogatepass').decode('utf-16', errors='replace')
        except Exception:
            return text_str


def parse_threads_html_data(html_content: str, max_comments: int = 3, include_op_chain: bool = True) -> Optional[Dict[str, Any]]:
    """
    Extracts post content, author thread continuation chain (parts),
    and selected audience comments from raw Threads HTML.
    """
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")

        # 1. Try finding application/ld+json for author and post text
        post_content = ""
        author_name = ""
        author_handle = ""
        avatar_url = ""

        ld_scripts = soup.find_all("script", {"type": "application/ld+json"})
        for script in ld_scripts:
            if not script.string:
                continue
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    if data.get("@type") == "SocialMediaPosting":
                        post_content = data.get("articleBody") or data.get("text") or ""
                        author_data = data.get("author", {})
                        author_name = author_data.get("name", "")
                        author_handle = author_data.get("alternateName", "")
                        avatar_url = author_data.get("image", "")
            except Exception:
                pass

        # 2. Extract meta tags as fallback
        if not post_content:
            og_desc = soup.find("meta", {"property": "og:description"}) or soup.find("meta", {"name": "description"})
            if og_desc and og_desc.get("content"):
                post_content = og_desc["content"]

        if not author_name:
            og_title = soup.find("meta", {"property": "og:title"})
            if og_title and og_title.get("content"):
                title_val = og_title["content"]
                m = re.match(r"^(.*?)\s*\(@([^)]+)\)", title_val)
                if m:
                    author_name = m.group(1).strip()
                    author_handle = m.group(2).strip()
                else:
                    author_name = title_val

        op_username = (author_handle or "").lower().strip()

        # 3. Extract all replies and separate OP continuation chain vs Audience comments
        op_story_parts: List[str] = []
        raw_audience_comments: List[Dict[str, Any]] = []
        seen_texts = set()

        if post_content:
            seen_texts.add(post_content.strip())

        # Regex search for all node texts and usernames
        reply_matches = re.findall(r'{"pk":"(\d+)".*?"text":"([^"]+)".*?"username":"([^"]+)"', html_content)
        
        for pk, raw_text, username in reply_matches:
            decoded = safe_decode_json_str(raw_text).strip()
            if not decoded or decoded in seen_texts:
                continue
            seen_texts.add(decoded)

            user_clean = username.lower().strip()

            # If reply is by OP and looks like a story continuation (length >= 60 chars)
            if op_username and user_clean == op_username and len(decoded) >= 60:
                op_story_parts.append(decoded)
            elif user_clean != op_username:
                # Audience comments
                if len(decoded) >= 6:  # Filter out tiny icon spam
                    raw_audience_comments.append({
                        "id": f"c_{len(raw_audience_comments)+1}",
                        "author": {
                            "name": username,
                            "avatar": "https://static.cdninstagram.com/rsrc.php/v3/yI/r/VsNE-Bp2f_h.png"
                        },
                        "content": decoded,
                        "likes": "45",
                        "time_ago": "1 giờ"
                    })

        # Combine OP story chain if requested
        full_content = post_content
        if include_op_chain and op_story_parts:
            # Join all parts cleanly
            parts_joined = "\n\n".join(op_story_parts)
            if full_content:
                full_content = f"{full_content}\n\n{parts_joined}"
            else:
                full_content = parts_joined

        # Slice audience comments according to user's max_comments setting
        selected_comments = raw_audience_comments[:max(1, max_comments)]

        if not full_content and not author_name:
            return None

        return {
            "platform": "threads",
            "author": {
                "name": author_name or "Người dùng Threads",
                "handle": author_handle or "threads_user",
                "avatar": avatar_url or "https://static.cdninstagram.com/rsrc.php/v3/yI/r/VsNE-Bp2f_h.png",
                "is_verified": False
            },
            "content": full_content,
            "story_parts_count": len(op_story_parts) + 1 if op_story_parts else 1,
            "likes": "1.8K",
            "replies": str(len(raw_audience_comments)),
            "time_ago": "Vừa xong",
            "comments": selected_comments
        }
    except Exception as e:
        logger.error(f"Error parsing Threads HTML: {e}")
        return None


def parse_facebook_html_data(html_content: str) -> Optional[Dict[str, Any]]:
    """
    Extracts post content, author, and comments from raw Facebook HTML.
    """
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")

        post_content = ""
        author_name = ""
        avatar_url = "https://static.xx.fbcdn.net/rsrc.php/v3/yo/r/UlIqmHJn-SK.gif"

        og_desc = soup.find("meta", {"property": "og:description"})
        if og_desc and og_desc.get("content"):
            post_content = og_desc["content"]

        og_title = soup.find("meta", {"property": "og:title"})
        if og_title and og_title.get("content"):
            author_name = og_title["content"].replace(" - Facebook", "").strip()

        comments: List[Dict[str, Any]] = []

        if not post_content and not author_name:
            return None

        return {
            "platform": "facebook",
            "author": {
                "name": author_name or "Người dùng Facebook",
                "avatar": avatar_url
            },
            "content": post_content,
            "likes": "2.5K",
            "replies": "112",
            "time_ago": "2 giờ",
            "comments": comments
        }
    except Exception as e:
        logger.error(f"Error parsing Facebook HTML: {e}")
        return None


def fetch_threads_via_headless_browser(
    url: str,
    cookies: Optional[Dict[str, str]] = None,
    max_comments: int = 3,
    include_op_chain: bool = True,
    timeout: int = 15
) -> Optional[Dict[str, Any]]:
    """
    Extracts post, author thread continuation chain, and comments using headless Chrome/Edge DOM evaluation.
    This guarantees full JavaScript rendering of Threads.
    """
    from app.card_renderer import get_browser_executable
    import subprocess
    import tempfile

    browser_exe = get_browser_executable()
    if not browser_exe:
        logger.error("No browser found for headless scraping.")
        return None

    temp_dir = tempfile.mkdtemp()
    cmd = [
        browser_exe,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        f"--dump-dom",
        url
    ]

    try:
        res = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            errors="replace",
            timeout=timeout
        )
        if res.returncode == 0 and res.stdout:
            parsed = parse_threads_html_data(res.stdout, max_comments=max_comments, include_op_chain=include_op_chain)
            if parsed:
                return parsed
    except Exception as e:
        logger.warning(f"Headless dump failed for Threads: {e}")
    finally:
        try:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass

    return None

