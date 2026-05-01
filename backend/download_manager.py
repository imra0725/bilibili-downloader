"""Download manager with task tracking and progress callbacks."""
import os
import re
import threading
import time
from typing import Callable, Dict, Optional, Any
from dataclasses import dataclass, field
from .bilibili_api import parse_video_url, get_download_url, download_video, QUALITY_MAP

@dataclass
class DownloadProgress:
    downloaded: int = 0
    total: int = 0
    speed: float = 0.0
    last_time: float = field(default_factory=time.time)
    last_downloaded: int = 0

    @property
    def percent(self) -> int:
        if self.total <= 0:
            return 0
        return min(100, int(self.downloaded * 100 / self.total))

    def update(self, downloaded: int, total: int):
        now = time.time()
        self.downloaded = downloaded
        self.total = total
        elapsed = now - self.last_time
        if elapsed >= 0.5:
            self.speed = (downloaded - self.last_downloaded) / elapsed
            self.last_time = now
            self.last_downloaded = downloaded


def sanitize_filename(name: str) -> str:
    """Remove invalid characters for Windows filenames."""
    name = re.sub(r'[\\/:*?"<>|]', "", name)
    return name.strip()[:120]


class DownloadManager:
    def __init__(self):
        self._tasks: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        self._next_id = 1

    def create_task(self, url: str, quality: int, save_dir: str, page_index: int = 0) -> str:
        task_id = f"task_{self._next_id}"
        self._next_id += 1
        self._tasks[task_id] = {
            "id": task_id,
            "url": url,
            "quality": quality,
            "save_dir": save_dir,
            "page_index": page_index,
            "status": "pending",
            "progress": DownloadProgress(),
            "filename": "",
            "fmt": "",
            "error": None,
            "thread": None,
            "stop_event": threading.Event(),
        }
        return task_id

    def start_task(self, task_id: str, on_update: Optional[Callable] = None):
        task = self._tasks.get(task_id)
        if not task:
            return

        def run():
            try:
                task["status"] = "downloading"
                if on_update:
                    on_update(task_id)

                # Parse video info
                info = parse_video_url(task["url"])
                page = info["pages"][task["page_index"]]
                bvid = info["bvid"]
                cid = page["cid"]
                qn = task["quality"]

                # Get download URL (MP4 or DASH)
                play_data, fmt = get_download_url(bvid, cid, qn)
                task["fmt"] = fmt

                # Determine filename
                quality_desc = QUALITY_MAP.get(qn, f"{qn}P")
                title = sanitize_filename(info["title"])
                part_name = sanitize_filename(page["part"]) if page["part"] else ""
                if len(info["pages"]) > 1 and part_name:
                    base_name = f"{title}_P{page['page']}_{part_name}_{quality_desc}"
                else:
                    base_name = f"{title}_{quality_desc}"

                # DASH files may not end up as .mp4 if ffmpeg unavailable
                ext = ".mp4" if fmt == "mp4" else ".mp4"
                filename = f"{base_name}{ext}"
                save_path = os.path.join(task["save_dir"], filename)

                # Avoid overwrite
                counter = 1
                while os.path.exists(save_path):
                    filename = f"{base_name}_{counter}{ext}"
                    save_path = os.path.join(task["save_dir"], filename)
                    counter += 1

                task["filename"] = filename

                # Download with progress
                def progress_cb(downloaded, total):
                    task["progress"].update(downloaded, total)
                    if on_update:
                        on_update(task_id)
                    if task["stop_event"].is_set():
                        raise InterruptedError("Download cancelled")

                final_path = download_video(play_data, fmt, save_path, progress_cb)
                
                # If download_video returned a different path (e.g. ffmpeg missing, kept .m4s)
                if final_path != save_path and os.path.exists(final_path):
                    actual_name = os.path.basename(final_path)
                    task["filename"] = actual_name

                task["status"] = "completed"
                task["progress"].downloaded = task["progress"].total or task["progress"].downloaded
                if on_update:
                    on_update(task_id)

            except InterruptedError:
                task["status"] = "failed"
                task["error"] = "已取消"
                if on_update:
                    on_update(task_id)
            except Exception as e:
                task["status"] = "failed"
                task["error"] = str(e)
                if on_update:
                    on_update(task_id)

        t = threading.Thread(target=run, daemon=True)
        task["thread"] = t
        t.start()

    def cancel_task(self, task_id: str) -> bool:
        task = self._tasks.get(task_id)
        if not task:
            return False
        task["stop_event"].set()
        return True

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        return self._tasks.get(task_id)

    def list_tasks(self) -> list:
        return list(self._tasks.values())

    def remove_task(self, task_id: str):
        if task_id in self._tasks:
            del self._tasks[task_id]
