"""PyWebview API exposed to frontend with detailed logging."""
import os
import subprocess
import platform
from typing import Optional, Dict, Any
from datetime import datetime

from .bilibili_api import parse_video_url, QUALITY_MAP
from .download_manager import DownloadManager, sanitize_filename
from .database import init_db, add_record, update_status, complete_task, get_all_records


def _open_path(path: str) -> bool:
    """Cross-platform open file/folder."""
    try:
        if not os.path.exists(path):
            return False
        system = platform.system()
        if system == 'Windows':
            os.startfile(path)
        elif system == 'Darwin':
            subprocess.call(['open', path])
        else:
            subprocess.call(['xdg-open', path])
        return True
    except Exception:
        return False


class AppAPI:
    def __init__(self):
        self._dm = DownloadManager()
        init_db()

    def parse_video(self, url: str) -> Dict[str, Any]:
        """Parse Bilibili video URL and return metadata."""
        try:
            return parse_video_url(url)
        except Exception as e:
            return {"error": str(e)}

    def download_video(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Start a download task."""
        try:
            url = params.get("url", "")
            quality = params.get("quality", 80)
            save_path = params.get("savePath", "")
            page_index = params.get("pageIndex", 0)

            if not save_path or not os.path.isdir(save_path):
                return {"error": "请选择有效的保存路径"}

            # Parse info first for the record
            info = parse_video_url(url)
            page = info["pages"][page_index]
            bvid = info["bvid"]
            quality_desc = QUALITY_MAP.get(quality, f"{quality}P")

            task_id = self._dm.create_task(url, quality, save_path, page_index)

            # Create initial DB record
            record = {
                "id": task_id,
                "bvid": bvid,
                "title": info["title"],
                "cover": info.get("cover", ""),
                "quality": quality_desc,
                "save_path": save_path,
                "filename": "",
                "status": "pending",
                "progress": 0,
                "speed": "",
                "error": "",
                "created_at": datetime.now().isoformat(),
            }
            add_record(record)

            def on_update(tid: str):
                task = self._dm.get_task(tid)
                if not task:
                    return
                status = task["status"]
                prog = task["progress"]
                speed_str = f"{prog.speed / 1024 / 1024:.1f} MB/s" if prog.speed > 1024 * 1024 else f"{prog.speed / 1024:.1f} KB/s"
                if status == "completed":
                    # Update filename from task
                    if task.get("filename"):
                        # Need to update filename in DB
                        rec = {
                            "id": tid,
                            "bvid": bvid,
                            "title": info["title"],
                            "cover": info.get("cover", ""),
                            "quality": quality_desc,
                            "save_path": save_path,
                            "filename": task["filename"],
                            "status": "completed",
                            "progress": 100,
                            "speed": speed_str,
                            "error": "",
                            "created_at": record["created_at"],
                        }
                        add_record(rec)
                    complete_task(tid)
                elif status == "failed":
                    update_status(tid, "failed", error=task.get("error", ""))
                else:
                    update_status(tid, "downloading", prog.percent, speed_str)

            self._dm.start_task(task_id, on_update)
            return {"task_id": task_id}

        except Exception as e:
            return {"error": str(e)}

    def select_folder(self) -> Optional[str]:
        """Open a folder picker dialog."""
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            root.overrideredirect(True)
            root.attributes('-topmost', True)
            root.lift()
            folder = filedialog.askdirectory(parent=root)
            root.destroy()
            return folder if folder else None
        except Exception:
            return None

    def get_download_history(self) -> list:
        """Return all download records."""
        return get_all_records()

    def cancel_download(self, task_id: str) -> bool:
        """Cancel an active download task."""
        return self._dm.cancel_task(task_id)

    def open_file(self, path: str) -> bool:
        """Open a file with default application."""
        return _open_path(path)

    def open_folder(self, path: str) -> bool:
        """Open a folder in file explorer."""
        return _open_path(path)

    def get_default_download_path(self) -> str:
        """Return the default Downloads folder path."""
        return os.path.join(os.path.expanduser("~"), "Downloads")
