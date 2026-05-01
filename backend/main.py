"""Bilibili Video Downloader - Desktop Entry Point"""
import os
import sys
import webview

# PyInstaller resource path detection
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    BASE_DIR = sys._MEIPASS
else:
    # Running from source
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Ensure backend modules are importable when running from source
if not getattr(sys, 'frozen', False):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    if project_dir not in sys.path:
        sys.path.insert(0, project_dir)

from backend.api import AppAPI

def main():
    # Production mode: load built frontend via http_server
    dist_path = os.path.join(BASE_DIR, "dist", "index.html")
    
    # Check if dist exists
    if not os.path.exists(dist_path):
        print(f"Error: Frontend build not found at {dist_path}")
        print("Please run 'npm run build' first.")
        sys.exit(1)

    # Initialize API
    api = AppAPI()

    # Create window
    window = webview.create_window(
        title='B站视频下载器',
        url=dist_path,
        js_api=api,
        width=900,
        height=700,
        min_size=(700, 500),
        resizable=True,
        text_select=True,
    )

    # Start with http_server=True to serve frontend correctly
    # This avoids file:// protocol restrictions
    webview.start(
        debug=False,
        http_server=True,
    )

if __name__ == '__main__':
    main()
