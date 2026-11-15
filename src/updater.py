import json
import os
import subprocess
import urllib.request
from paths import ytdlp_exe_path, script_root

GITHUB_RELEASES_API = "https://api.github.com/repos/yisukm24/dlp-yisk/releases/latest"
LOCAL_VERSION = "1.0.0"


def update_ytdlp_binary(log_callback) -> int:
    cmd = [ytdlp_exe_path, "-U"]
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        startupinfo=startupinfo,
        errors='replace',
        shell=False
    )

    while True:
        line = process.stdout.readline()
        if not line and process.poll() is not None:
            break
        if line and log_callback:
            log_callback(line.strip())

    process.wait()
    return process.returncode


def check_latest_release(current_version: str = LOCAL_VERSION) -> tuple[bool, str, str]:
    req = urllib.request.Request(
        GITHUB_RELEASES_API,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )
    with urllib.request.urlopen(req, timeout=5) as response:
        info_release = json.loads(response.read().decode('utf-8'))

    remote_version = info_release.get("tag_name", current_version).lstrip('v')
    url_zip = ""
    assets = info_release.get("assets", [])
    if assets and isinstance(assets, list) and len(assets) > 0:
        url_zip = assets[0].get("browser_download_url", "")

    has_update = False
    if url_zip:
        try:
            remote_tuple = tuple(map(int, remote_version.split('.')))
            local_tuple = tuple(map(int, current_version.split('.')))
            has_update = remote_tuple > local_tuple
        except Exception:
            has_update = remote_version > current_version

    return has_update, remote_version, url_zip


def download_and_run_updater(url_zip: str, exe_name: str = "dlp_yisk.exe") -> None:
    temp_zip = os.path.join(script_root, "update_temp.zip")
    req_zip = urllib.request.Request(
        url_zip,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )
    with urllib.request.urlopen(req_zip, timeout=15) as response, open(temp_zip, 'wb') as out_file:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            out_file.write(chunk)

    bat_path = os.path.join(script_root, "updater.bat")
    temp_extract_dir = os.path.join(script_root, "update_extracted_temp")

    script_bat = f"""@echo off
timeout /t 2 /nobreak > nul
if exist "{temp_extract_dir}" rmdir /s /q "{temp_extract_dir}"
powershell -Command "Start-Process powershell -ArgumentList '-Command Expand-Archive -Path \\"'{temp_zip}'\\" -DestinationPath \\"'{temp_extract_dir}'\\" -Force' -Verb RunAs -Wait"
powershell -Command "Start-Process powershell -ArgumentList '-Command Copy-Item -Path \\"'{temp_extract_dir}'\\\\*\\" -Destination \\"'{script_root}'\\" -Recurse -Force' -Verb RunAs -Wait"
if exist "{temp_extract_dir}" rmdir /s /q "{temp_extract_dir}"
if exist "{temp_zip}" del /f /q "{temp_zip}"
cd /d "{script_root}"
start "" "{exe_name}"
del "%~f0"
"""
    with open(bat_path, "w", encoding="utf-8") as bat_file:
        bat_file.write(script_bat)

    subprocess.Popen([bat_path], shell=True)
