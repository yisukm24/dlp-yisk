import os
import sys

IS_FROZEN = getattr(sys, 'frozen', False)

if IS_FROZEN:
    app_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(sys.executable)))
    script_root = os.path.dirname(os.path.abspath(sys.executable))
    bin_dir = os.path.join(app_dir, "bin")
    app_icon_path = os.path.join(app_dir, "logo.ico")
    
    local_app_data = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
    user_data_dir = os.path.join(local_app_data, "dlp_yisk")
    persistent_core = os.path.join(user_data_dir, "data")
    downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads", "dlp_yisk")
else:
    src_dir = os.path.dirname(os.path.abspath(__file__))
    script_root = os.path.dirname(src_dir)
    app_dir = os.path.join(script_root, "assets")
    bin_dir = os.path.join(app_dir, "bin")
    app_icon_path = os.path.join(app_dir, "logo.ico")
    
    persistent_core = os.path.join(script_root, "data")
    downloads_dir = os.path.join(script_root, "downloads")

core_dir = app_dir

videos_dir = os.path.join(downloads_dir, "videos")
audios_dir = os.path.join(downloads_dir, "audios")
playlists_dir = os.path.join(downloads_dir, "playlists")

ytdlp_exe_path = os.path.join(bin_dir, "yt-dlp.exe")
ffmpeg_exe_path = os.path.join(bin_dir, "ffmpeg.exe")
config_file_path = os.path.join(persistent_core, "config.json")


def ensure_directories():
    os.makedirs(persistent_core, exist_ok=True)
    for d in [downloads_dir, videos_dir, audios_dir, playlists_dir]:
        os.makedirs(d, exist_ok=True)


ensure_directories()
