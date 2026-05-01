"""Bilibili video API client with MP4 and DASH support."""
import re
import requests
import subprocess
import shutil
from typing import Dict, Optional, Any, Tuple

# Common headers to mimic a real browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://www.bilibili.com",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Origin": "https://www.bilibili.com",
}

# Quality code mapping
QUALITY_MAP = {
    127: "8K",
    126: "杜比视界",
    125: "HDR",
    120: "4K",
    116: "1080P60",
    112: "1080P+",
    80: "1080P",
    74: "720P60",
    64: "720P",
    32: "480P",
    16: "360P",
    15: "360P",
}


def extract_bvid(url: str) -> Optional[str]:
    """Extract BV ID from various Bilibili URL formats."""
    patterns = [
        r"bilibili\.com/video/([Bb][Vv][a-zA-Z0-9]+)",
        r"b23\.tv/([Bb][Vv][a-zA-Z0-9]+)",
        r"([Bb][Vv][a-zA-Z0-9]{10})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1).upper()
    return None


def get_video_info(bvid: str) -> Dict[str, Any]:
    """Fetch video metadata from Bilibili API."""
    url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
    resp = requests.get(url, headers=HEADERS, timeout=15)
    data = resp.json()
    if data.get("code") != 0:
        raise Exception(data.get("message", "获取视频信息失败"))
    return data["data"]


def _fetch_playurl(bvid: str, cid: int, qn: int, fnval: int) -> Dict[str, Any]:
    """Internal helper to fetch playurl with given params."""
    url = "https://api.bilibili.com/x/player/playurl"
    params = {
        "bvid": bvid,
        "cid": cid,
        "qn": qn,
        "fnval": fnval,
        "fnver": 0,
        "fourk": 1,
    }
    resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
    data = resp.json()
    if data.get("code") != 0:
        raise Exception(data.get("message", f"playurl API错误 (code={data.get('code')})"))
    return data["data"]


def get_download_url(bvid: str, cid: int, qn: int = 80) -> Tuple[Dict[str, Any], str]:
    """
    Get video download info. Returns (play_data, format_type).
    format_type is 'mp4' or 'dash'.
    
    Priority:
    1. Try MP4 format (fnval=0) - single file, easiest
    2. Fallback to DASH (fnval=16) - video+audio separate, needs merge
    """
    # Try MP4 first
    try:
        play_data = _fetch_playurl(bvid, cid, qn, fnval=0)
        if play_data.get("durl") and len(play_data["durl"]) > 0:
            return play_data, "mp4"
    except Exception:
        pass
    
    # Fallback to DASH
    try:
        play_data = _fetch_playurl(bvid, cid, qn, fnval=16)
        if play_data.get("dash") and play_data["dash"].get("video"):
            return play_data, "dash"
    except Exception:
        pass
    
    # If both fail, raise with the MP4 error (more informative)
    play_data = _fetch_playurl(bvid, cid, qn, fnval=0)
    if not play_data.get("durl"):
        raise Exception("该视频无可用下载地址（可能需要登录或版权限制）")
    return play_data, "mp4"


def parse_video_url(url: str) -> Dict[str, Any]:
    """Parse a Bilibili video URL and return structured info."""
    bvid = extract_bvid(url)
    if not bvid:
        raise Exception("无法识别B站视频链接，请检查链接格式\n支持的格式：BV号、完整URL、短链接")

    info = get_video_info(bvid)

    pages = info.get("pages", [])
    pages_data = [
        {
            "cid": p["cid"],
            "page": p["page"],
            "part": p["part"],
            "duration": p["duration"],
        }
        for p in pages
    ]

    # Determine available qualities by calling API with first page
    qualities = []
    seen = set()
    try:
        if pages_data:
            play_data, fmt = get_download_url(bvid, pages_data[0]["cid"], qn=80)
            accept_quality = play_data.get("accept_quality", [])
            
            # Also try higher quality to see what's available
            if not accept_quality:
                try:
                    play_data2, _ = get_download_url(bvid, pages_data[0]["cid"], qn=120)
                    accept_quality = play_data2.get("accept_quality", [80, 64, 32, 16])
                except Exception:
                    accept_quality = [80, 64, 32, 16]
            
            for q in accept_quality:
                if q not in seen:
                    seen.add(q)
                    qualities.append({"qn": q, "desc": QUALITY_MAP.get(q, f"{q}P")})
    except Exception as e:
        print(f"Quality detection warning: {e}")
        qualities = [{"qn": q, "desc": QUALITY_MAP.get(q, f"{q}P")} for q in [80, 64, 32, 16]]

    if not qualities:
        qualities = [{"qn": q, "desc": QUALITY_MAP.get(q, f"{q}P")} for q in [80, 64, 32, 16]]

    return {
        "bvid": bvid,
        "title": info["title"],
        "description": info.get("desc", ""),
        "cover": info.get("pic", ""),
        "owner": {
            "name": info["owner"]["name"],
            "mid": info["owner"]["mid"],
            "face": info["owner"].get("face", ""),
        },
        "duration": info["duration"],
        "pages": pages_data,
        "qualities": qualities,
    }


def _download_stream(url: str, save_path: str, progress_callback=None, total_override: int = 0) -> int:
    """Download a single media stream. Returns downloaded bytes."""
    headers = {**HEADERS, "Referer": "https://www.bilibili.com"}
    resp = requests.get(url, headers=headers, stream=True, timeout=120)
    resp.raise_for_status()

    total = total_override or int(resp.headers.get("content-length", 0))
    downloaded = 0

    with open(save_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=65536):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                if progress_callback and total > 0:
                    progress_callback(downloaded, total)

    return downloaded


def _ffmpeg_available() -> bool:
    """Check if ffmpeg is available in PATH."""
    return shutil.which("ffmpeg") is not None


def _merge_with_ffmpeg(video_path: str, audio_path: str, output_path: str) -> bool:
    """Merge video and audio using ffmpeg. Returns True if output is valid."""
    import subprocess as _sp
    import os as _os
    try:
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", audio_path,
            "-c", "copy",
            "-movflags", "+faststart",
            "-loglevel", "error",
            output_path,
        ]
        result = _sp.run(cmd, stdout=_sp.PIPE, stderr=_sp.PIPE, timeout=300)
        exists = _os.path.exists(output_path)
        size = _os.path.getsize(output_path) if exists else 0
        return result.returncode == 0 and exists and size > 0
    except Exception:
        return False


def download_video(
    play_data: Dict[str, Any],
    fmt: str,
    save_path: str,
    progress_callback=None
) -> str:
    """
    Download video based on play_data and format.
    
    For MP4: single file download.
    For DASH: download video+audio, merge with ffmpeg if available.
    
    Returns final file path.
    """
    import os
    
    if fmt == "mp4":
        durl_list = play_data.get("durl", [])
        if not durl_list:
            raise Exception("MP4下载地址为空")
        
        media_url = durl_list[0]["url"]
        _download_stream(media_url, save_path, progress_callback)
        return save_path
    
    elif fmt == "dash":
        dash = play_data.get("dash", {})
        videos = dash.get("video", [])
        audios = dash.get("audio", [])
        
        if not videos:
            raise Exception("DASH视频流为空")
        
        # Select best video (first one is typically highest quality in the list)
        video_url = videos[0].get("baseUrl") or videos[0].get("base_url")
        audio_url = audios[0].get("baseUrl") or audios[0].get("base_url") if audios else None
        
        if not video_url:
            raise Exception("无法获取DASH视频流地址")
        
        base, ext = os.path.splitext(save_path)
        
        # Download video stream
        video_temp = f"{base}_video.m4s"
        video_size = videos[0].get("size", 0) or videos[0].get("bandwidth", 0) * dash.get("duration", 1) / 8
        
        def video_progress(dl, total):
            if progress_callback:
                # Video is ~85% of total work
                progress_callback(int(dl * 0.85), int(total * 0.85))
        
        _download_stream(video_url, video_temp, video_progress, int(video_size))
        
            # Download audio stream if available
        if audio_url:
            audio_temp = f"{base}_audio.m4s"
            audio_size = audios[0].get("size", 0) or audios[0].get("bandwidth", 0) * dash.get("duration", 1) / 8
            
            def audio_progress(dl, total):
                if progress_callback:
                    # Audio is ~15% of total work, video part done
                    progress_callback(int(video_size * 0.85 + dl * 0.15), int(video_size * 0.85 + total * 0.15))
            
            _download_stream(audio_url, audio_temp, audio_progress, int(audio_size))
            
            # Try merge with ffmpeg
            if _ffmpeg_available():
                merged = _merge_with_ffmpeg(video_temp, audio_temp, save_path)
                if merged:
                    os.remove(video_temp)
                    os.remove(audio_temp)
                    return save_path
                else:
                    # ffmpeg failed but may have created a partial file - clean it up
                    if os.path.exists(save_path):
                        try:
                            os.remove(save_path)
                        except Exception:
                            pass
                    # Rename video file to .mp4 (m4s is playable but missing audio)
                    video_fallback = save_path
                    shutil.move(video_temp, video_fallback)
                    return video_fallback
            else:
                # No ffmpeg, keep separate files
                # Rename video file to .mp4 (m4s is playable but missing audio)
                if os.path.exists(save_path):
                    try:
                        os.remove(save_path)
                    except Exception:
                        pass
                video_fallback = save_path
                shutil.move(video_temp, video_fallback)
                return video_fallback
        else:
            # No audio stream, just return video
            shutil.move(video_temp, save_path)
            return save_path
    
    else:
        raise Exception(f"不支持的格式: {fmt}")
