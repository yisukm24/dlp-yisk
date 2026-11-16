# dlp-yisk

> A modern, high-performance desktop application built with **PySide6 (Qt)** to download videos, audio, and playlists seamlessly using **yt-dlp** and **ffmpeg**.

---

## Features

- **Multi-Format Downloads**:
  - High-Quality Video in **MKV** or **MP4**.
  - High-Quality Audio extraction in **MP3** (320kbps) or **FLAC** (lossless).
  - Full **Playlist** batch downloading for both video and audio formats.
  - Source Format Viewer (`-F` flag) to inspect available streams before downloading.
- **Robust Anti-Bot Evasion**:
  - Pre-configured browser impersonation (`chrome:windows`), custom referers, DNT headers, fragment retries, and embedded `deno` JS runtime solver for maximum reliability.
- **Multilingual Support**:
  - Native internationalization for **English (EN)**, **Spanish (ES)**, and **Korean (KO)**.
- **Non-Blocking UI Architecture**:
  - Multi-threaded execution (`QThread`) ensures the interface never freezes during heavy downloads, format analysis, audio alerts, or binary updates.
- **Real-Time Download Tracking**:
  - Live progress bar, real-time speed monitoring (e.g., `12.5Mb/s`), and interactive console log output.
- **Convenience & User Experience**:
  - **Always on Top (`topmost`)**: Pin the application window over other windows.
  - **Automatic Folders**: Organized output directories (`videos`, `audios`, `playlists`).
  - **Audio Alerts & Melodies**: Completion sound alerts and festive melodies for Christmas and user birthdays.
- **Self-Updating**:
  - One-click binary updater for `yt-dlp.exe` (`-U`).
  - Automatic app update checking via **GitHub Releases API** with silent background installation.

---

## Architecture

| Module | Description |
| :--- | :--- |
| `src/paths.py` | Handles environment resolution for dev/frozen modes (`IS_FROZEN`), persistent data stored in `%LOCALAPPDATA%\dlp_yisk\data`, and download locations. |
| `src/config.py` | Manages persistent user preferences in `config.json` (language, birthday, window pinning). |
| `src/audio.py` | Controls completion chime alerts and seasonal melodies using Windows `winsound`. |
| `src/downloader.py` | Assembles `yt-dlp` commands with anti-blocking arguments and executes subprocesses with stdout regex parsing. |
| `src/updater.py` | Handles `yt-dlp` binary updates and checks GitHub Releases for application updates. |
| `src/Interface.py` | Main PySide6 Qt GUI, worker threads (`QThread`), language switching, and event management. |

### Included Binaries (`assets/bin/`)
- `yt-dlp.exe`: Underlying media extraction engine.
- `ffmpeg.exe` & `ffprobe.exe`: Audio conversion, stream merging, and thumbnail embedding.
- `deno.exe`: JavaScript engine used by yt-dlp to execute complex YouTube challenges.

---

## Mmmmmmmmm

### Prerequisites
- **Windows 10 / 11** (64-bit)
- **Python 3.10+** (if running from source)

### Running from Source

1. **Clone the repository**:
   ```cmd
   git clone https://github.com/yisukm24/dlp-yisk.git
   cd dlp-yisk
   ```

2. **Install dependencies**:
   ```cmd
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```cmd
   python src/Interface.py
   ```
---

## Configuration File (`config.json`)

The configuration file is automatically created at `%LOCALAPPDATA%\dlp_yisk\data\config.json`:

---

## License & Credits

Developed by **yisukm**. Built with [PySide6](https://www.qt.io/qt-for-python), [yt-dlp](https://github.com/yt-dlp/yt-dlp), and [ffmpeg](https://ffmpeg.org/).
