import json
import os
import ssl
import subprocess
import tempfile
import urllib.request
from paths import ytdlp_exe_path

GITHUB_RELEASES_API = "https://api.github.com/repos/yisukm24/dlp-yisk/releases/latest"
LOCAL_VERSION = "1.0.1"
INSTALLER_FILENAME = "dlp_yisk_setup.exe"
INSTALLER_SILENT_ARGS = ["/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART"]


def _create_ssl_context() -> ssl.SSLContext:
    return ssl.create_default_context()


def _parse_version(version_str: str) -> tuple[int, ...]:
    cleaned = version_str.strip().lstrip("vV")
    return tuple(map(int, cleaned.split(".")))


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
    ssl_context = _create_ssl_context()
    req = urllib.request.Request(
        GITHUB_RELEASES_API,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )
    with urllib.request.urlopen(req, timeout=10, context=ssl_context) as response:
        info_release = json.loads(response.read().decode('utf-8'))

    remote_version = info_release.get("tag_name", current_version).strip().lstrip('vV')
    installer_url = ""
    assets = info_release.get("assets", [])
    if isinstance(assets, list):
        for asset in assets:
            name = asset.get("name", "").lower()
            if name == INSTALLER_FILENAME:
                installer_url = asset.get("browser_download_url", "")
                break
        if not installer_url:
            for asset in assets:
                name = asset.get("name", "").lower()
                if name.endswith(".exe"):
                    installer_url = asset.get("browser_download_url", "")
                    break

    has_update = False
    if installer_url:
        try:
            has_update = _parse_version(remote_version) > _parse_version(current_version)
        except Exception:
            has_update = remote_version > current_version

    return has_update, remote_version, installer_url


def download_and_run_updater(installer_url: str) -> None:
    setup_path = os.path.join(tempfile.gettempdir(), INSTALLER_FILENAME)
    ssl_context = _create_ssl_context()
    req_installer = urllib.request.Request(
        installer_url,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )
    with urllib.request.urlopen(req_installer, timeout=30, context=ssl_context) as response, open(setup_path, 'wb') as out_file:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            out_file.write(chunk)

    if not os.path.exists(setup_path) or os.path.getsize(setup_path) == 0:
        raise RuntimeError("Downloaded installer is empty or missing.")

    subprocess.Popen(
        [setup_path, *INSTALLER_SILENT_ARGS],
        shell=False,
        close_fds=True,
    )
