import os
import re
import subprocess
from paths import bin_dir, ytdlp_exe_path, videos_dir, audios_dir, playlists_dir, downloads_dir

IDENTITY_ARGS = [
    "--referer", "https://google.com",
    "--impersonate", "chrome:windows",
    "--sleep-requests", "0.5",
    "--socket-timeout", "10",
    "--retries", "10",
    "--fragment-retries", "10",
    "--add-header", "DNT:1",
    "--add-header", "Sec-Fetch-Mode:navigate",
    "--ignore-config",
    "--no-cookies",
    "--ffmpeg-location", bin_dir
]

DOWNLOAD_ARGS = IDENTITY_ARGS + [
    "--concurrent-fragments", "10",
    "--part",
    "--clean-info-json",
    "--no-mtime"
]

SPEED_PATTERN = re.compile(r'at\s+([0-9.]+[kMG]b/s)')
PERCENTAGE_PATTERN = re.compile(r'\[download\]\s+([0-9.]+)%')


def get_target_dir_for_option(option_idx: int) -> str:
    if option_idx in (0, 1):
        return videos_dir
    if option_idx in (2, 3):
        return audios_dir
    if option_idx in (4, 5, 6, 7):
        return playlists_dir
    return downloads_dir


def build_ytdlp_command(option_idx: int, url: str) -> list:
    playlist_target = os.path.join(playlists_dir, "%(playlist)s")
    playlist_output = "%(playlist_index)s - %(title)s.%(ext)s"

    profiles = {
        0: DOWNLOAD_ARGS + [
            "-P", videos_dir, "-o", "%(title)s.%(ext)s",
            "-f", "bestvideo+bestaudio/best", "--merge-output-format", "mkv",
            "--embed-thumbnail",
            "--postprocessor-args", "merger+ffmpeg_o:-threads 0 -map_metadata -1 -map_metadata:s:v 0"
        ],
        1: DOWNLOAD_ARGS + [
            "-P", videos_dir, "-o", "%(title)s.%(ext)s",
            "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best", "--merge-output-format", "mp4",
            "--embed-thumbnail",
            "--postprocessor-args", "merger+ffmpeg_o:-threads 0 -map_metadata -1 -map_metadata:s:v 0"
        ],
        2: DOWNLOAD_ARGS + [
            "-P", audios_dir, "-o", "%(title)s.%(ext)s",
            "-f", "ba", "-x", "--audio-format", "mp3", "--audio-quality", "0",
            "--embed-thumbnail",
            "--postprocessor-args", "EmbedThumbnail+ffmpeg_o:-c:v mjpeg -pix_fmt yuvj420p",
            "--postprocessor-args", "ExtractAudio+ffmpeg_o:-threads 0 -map_metadata -1 -map_metadata:s:v 0"
        ],
        3: DOWNLOAD_ARGS + [
            "-P", audios_dir, "-o", "%(title)s.%(ext)s",
            "-f", "ba", "-x", "--audio-format", "flac", "--audio-quality", "0",
            "--embed-thumbnail",
            "--postprocessor-args", "ExtractAudio+ffmpeg_o:-threads 0 -map_metadata -1 -map_metadata:s:v 0"
        ],
        4: DOWNLOAD_ARGS + [
            "-P", playlist_target, "-o", playlist_output,
            "-f", "bestvideo+bestaudio/best", "--merge-output-format", "mkv",
            "--embed-thumbnail",
            "--postprocessor-args", "merger+ffmpeg_o:-threads 0 -map_metadata -1 -map_metadata:s:v 0"
        ],
        5: DOWNLOAD_ARGS + [
            "-P", playlist_target, "-o", playlist_output,
            "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best", "--merge-output-format", "mp4",
            "--embed-thumbnail",
            "--postprocessor-args", "merger+ffmpeg_o:-threads 0 -map_metadata -1 -map_metadata:s:v 0"
        ],
        6: DOWNLOAD_ARGS + [
            "-P", playlist_target, "-o", playlist_output,
            "-f", "ba", "-x", "--audio-format", "mp3", "--audio-quality", "0",
            "--embed-thumbnail",
            "--postprocessor-args", "EmbedThumbnail+ffmpeg_o:-c:v mjpeg -pix_fmt yuvj420p",
            "--postprocessor-args", "ExtractAudio+ffmpeg_o:-threads 0 -map_metadata -1 -map_metadata:s:v 0"
        ],
        7: DOWNLOAD_ARGS + [
            "-P", playlist_target, "-o", playlist_output,
            "-f", "ba", "-x", "--audio-format", "flac", "--audio-quality", "0",
            "--embed-thumbnail",
            "--postprocessor-args", "ExtractAudio+ffmpeg_o:-threads 0 -map_metadata -1 -map_metadata:s:v 0"
        ],
        8: IDENTITY_ARGS + ["-F"]
    }

    specific_args = profiles.get(option_idx, IDENTITY_ARGS + ["-F"])
    return [ytdlp_exe_path] + specific_args + ["--", url]


def run_download_subprocess(cmd: list, log_callback, speed_callback=None, progress_callback=None) -> int:
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        startupinfo=startupinfo,
        errors='replace'
    )

    while True:
        line = process.stdout.readline()
        if not line and process.poll() is not None:
            break
        if line:
            text_line = line.strip()
            text_line = ''.join(c for c in text_line if c.isprintable() or c in '\n\r\t')

            if speed_callback:
                match_v = SPEED_PATTERN.search(text_line)
                if match_v:
                    speed_callback(match_v.group(1))

            if progress_callback:
                match_p = PERCENTAGE_PATTERN.search(text_line)
                if match_p:
                    progress_callback(float(match_p.group(1)))

            if log_callback:
                log_callback(text_line)

    process.wait()
    return process.returncode
