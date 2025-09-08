import re
from typing import Optional, Dict, Any
import requests


_YT_ID_PATTERNS = [
    re.compile(r"(?:v=)([\w-]{11})"),
    re.compile(r"youtu\.be/([\w-]{11})"),
    re.compile(r"youtube\.com/shorts/([\w-]{11})"),
]


def extract_youtube_id(url: str) -> Optional[str]:
    if not url:
        return None
    for pat in _YT_ID_PATTERNS:
        m = pat.search(url)
        if m:
            return m.group(1)
    return None


def fetch_youtube_video(api_key: str, video_id: str) -> Optional[Dict[str, Any]]:
    if not api_key or not video_id:
        return None
    endpoint = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "id": video_id,
        "part": "snippet,contentDetails,statistics",
        "key": api_key,
    }
    try:
        r = requests.get(endpoint, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        items = data.get("items") or []
        if not items:
            return None
        item = items[0]
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        content = item.get("contentDetails", {})
        thumbs = (snippet.get("thumbnails") or {})
        # pick a sensible thumbnail
        thumb = (
            (thumbs.get("medium") or {}).get("url")
            or (thumbs.get("high") or {}).get("url")
            or (thumbs.get("default") or {}).get("url")
        )
        return {
            "title": snippet.get("title"),
            "channelTitle": snippet.get("channelTitle"),
            "publishedAt": snippet.get("publishedAt"),
            "thumbnail": thumb,
            "viewCount": int(stats.get("viewCount", 0) or 0),
            "likeCount": int(stats.get("likeCount", 0) or 0),
            "duration": content.get("duration"),
        }
    except Exception:
        return None

