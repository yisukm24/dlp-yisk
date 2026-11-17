import os
import sys
import datetime
import multiprocessing

from PySide6.QtCore import Qt, QThread, Signal, QTimer, QEvent, QPointF, QSize
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QPen, QBrush, QPolygonF
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QProgressBar,
    QPlainTextEdit,
    QMessageBox,
    QDialog,
    QFrame,
    QListView,
    QStyle,
    QStyleOptionComboBox,
)

from paths import (
    app_icon_path,
    config_file_path,
)
from config import load_config, save_config, update_config_value
from audio import sound_alert, check_and_play_event_melody
from downloader import (
    build_ytdlp_command,
    run_download_subprocess,
    get_target_dir_for_option,
)
from updater import (
    LOCAL_VERSION,
    update_ytdlp_binary as run_ytdlp_updater,
    check_latest_release,
    download_and_run_updater,
)

LANGUAGES = {
    "EN": {
        "title": "DLP-YISK DOWNLOADER",
        "subtitle": "Developed for yisukm",
        "url_label": "Content URL",
        "action_label": "Action Type",
        "console_label": "Console Output",
        "btn_run": "Download",
        "btn_downloading": "DOWNLOADING...",
        "btn_folder": "OPEN DOWNLOADS",
        "err_valid": "Please enter a valid link.",
        "err_chars": "Dangerous or invalid characters detected in URL.",
        "err_format": "Please select an Action Type before downloading.",
        "err_length": "The URL exceeds the maximum safe length.",
        "config_title": "Configuration",
        "config_info": "Hello! Enter your birthdate:",
        "config_day": "Day:",
        "config_month": "Month:",
        "config_btn": "Save",
        "config_err": "Could not save configuration: ",
        "months_list": [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December",
        ],
        "msg_success": "\n[✓] Completed successfully!",
        "msg_warn": "\n[!] Finished with warning code: ",
        "msg_crit": "\n[!] Critical system error: ",
        "options": [
            "Quality Video (MKV)",
            "Quality Video (MP4)",
            "Quality Audio (MP3)",
            "Quality Audio (FLAC)",
            "Download Video Playlist (MKV)",
            "Download Video Playlist (MP4)",
            "Download Audio Playlist (MP3)",
            "Download Audio Playlist (FLAC)",
            "View Available Source Formats (-F)",
        ],
        "logs": [
            "[+] Downloading mkv video...",
            "[+] Downloading mp4 video...",
            "[+] Extracting MP3 audio...",
            "[+] Extracting FLAC quality...",
            "[+] Processing MKV video playlist...",
            "[+] Processing MP4 video playlist...",
            "[+] Processing MP3 audio playlist...",
            "[+] Processing FLAC audio playlist...",
            "[+] Analyzing source formats...",
        ],
        "msg_update": "[+] Checking for yt-dlp updates...",
        "err_update": "\n[!] Update error: ",
        "placeholder": "Enter the content link here...",
        "action_placeholder": "Select an action...",
        "app_update_title": "Update Available",
        "app_update_prompt": "A new version ({version}) is available.\nDo you want to update now?",
        "app_update_downloading": "[+] Downloading application update package...",
        "app_update_failed": "[!] Update failed: ",
    },
    "ES": {
        "title": "DLP-YISK DOWNLOADER",
        "subtitle": "Desarrollado por yisukm",
        "url_label": "URL del Contenido",
        "action_label": "Tipo de Acción",
        "console_label": "Salida de Consola",
        "btn_run": "Descargar",
        "btn_downloading": "DESCARGANDO...",
        "btn_folder": "ABRIR DESCARGAS",
        "err_valid": "Por favor introduce un enlace válido.",
        "err_length": "La URL supera el tamaño límite seguro.",
        "err_chars": "Caracteres peligrosos/inválidos en la URL.",
        "err_format": "Por favor selecciona un Tipo de Acción antes de descargar.",
        "config_title": "Configuración",
        "config_info": "¡Hola! Introduce tu fecha de nacimiento:",
        "config_day": "Día:",
        "config_month": "Mes:",
        "config_btn": "Guardar",
        "config_err": "No se pudo guardar la configuración: ",
        "months_list": [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
        ],
        "msg_success": "\n[✓] ¡Completado exitosamente!",
        "msg_warn": "\n[!] Finalizó con código de advertencia: ",
        "msg_crit": "\n[!] Error crítico del sistema: ",
        "options": [
            "Video Calidad (MKV)",
            "Video Calidad (MP4)",
            "Audio Calidad (MP3)",
            "Audio Calidad (FLAC)",
            "Descargar Playlist - Video (MKV)",
            "Descargar Playlist - Video (MP4)",
            "Descargar Playlist - Audio (MP3)",
            "Descargar Playlist - Audio (FLAC)",
            "Ver Formatos Disponibles (-F)",
        ],
        "logs": [
            "[+] Descargando mkv video...",
            "[+] Descargando mp4 video...",
            "[+] Extrayendo audio MP3...",
            "[+] Extrayendo audio FLAC...",
            "[+] Procesando Playlist de videos MKV...",
            "[+] Procesando Playlist de videos MP4...",
            "[+] Procesando Playlist de audios MP3...",
            "[+] Procesando Playlist de audios FLAC...",
            "[+] Analizando formatos de origen...",
        ],
        "msg_update": "[+] Comprobando actualizaciones de yt-dlp...",
        "err_update": "\n[!] Error al intentar actualizar: ",
        "placeholder": "Introduce el enlace del contenido aquí...",
        "action_placeholder": "Selecciona una acción...",
        "app_update_title": "Actualización Disponible",
        "app_update_prompt": "Hay una nueva versión ({version}) disponible.\n¿Deseas actualizar ahora?",
        "app_update_downloading": "[+] Descargando paquete de actualización...",
        "app_update_failed": "[!] Error de actualización: ",
    },
    "KO": {
        "title": "DLP-YISK 다운로더",
        "subtitle": "yisukm 제작",
        "url_label": "콘텐츠 URL",
        "action_label": "작업 유형",
        "console_label": "콘솔 출력",
        "btn_run": "다운로드",
        "btn_downloading": "다운로드 중...",
        "btn_folder": "다운로드 폴더 열기",
        "err_valid": "올바른 링크를 입력해 주세요.",
        "err_length": "URL이 안전 제한 길이를 초과했습니다.",
        "err_chars": "URL에서 위험하거나 잘못된 문자가 감지되었습니다.",
        "err_format": "다운로드하기 전에 작업 유형을 선택해 주세요.",
        "config_title": "설정",
        "config_info": "안녕하세요! 생년월일을 입력해 주세요:",
        "config_day": "일:",
        "config_month": "월:",
        "config_btn": "저장",
        "config_err": "설정을 저장할 수 없습니다: ",
        "months_list": [
            "1월", "2월", "3월", "4월", "5월", "6월",
            "7월", "8월", "9월", "10월", "11월", "12월",
        ],
        "msg_success": "\n[✓] 성공적으로 완료되었습니다!",
        "msg_warn": "\n[!] 경고 코드와 함께 종료됨: ",
        "msg_crit": "\n[!] 심각한 시스템 오류: ",
        "options": [
            "고화질 비디오 (MKV)",
            "고화질 비디오 (MP4)",
            "고음질 오디오 (MP3)",
            "고음질 오디오 (FLAC)",
            "재생목록 비디오 다운로드 (MKV)",
            "재생목록 비디오 다운로드 (MP4)",
            "재생목록 오디오 다운로드 (MP3)",
            "재생목록 오디오 다운로드 (FLAC)",
            "사용 가능한 소스 형식 보기 (-F)",
        ],
        "logs": [
            "[+] MKV 비디오 다운로드 중...",
            "[+] MP4 비디오 다운로드 중...",
            "[+] MP3 오디오 추출 중...",
            "[+] FLAC 음질 추출 중...",
            "[+] MKV 비디오 재생목록 처리 중...",
            "[+] MP4 비디오 재생목록 처리 중...",
            "[+] MP3 오디오 재생목록 처리 중...",
            "[+] FLAC 오디오 재생목록 처리 중...",
            "[+] 소스 형식 분석 중...",
        ],
        "msg_update": "[+] yt-dlp 업데이트 확인 중...",
        "err_update": "\n[!] 업데이트 오류: ",
        "placeholder": "여기에 콘텐츠 링크를 입력하세요...",
        "action_placeholder": "작업 선택...",
        "app_update_title": "업데이트 가능",
        "app_update_prompt": "새 버전({version})이 있습니다.\n지금 업데이트하시겠습니까?",
        "app_update_downloading": "[+] 업데이트 패키지를 다운로드하는 중...",
        "app_update_failed": "[!] 업데이트 실패: ",
    },
}


DARK_QSS = """
QMainWindow, QDialog {
    background-color: #000000;
    color: #ffffff;
    font-family: "Segoe UI", sans-serif;
}

QWidget {
    color: #ffffff;
    font-family: "Segoe UI", sans-serif;
}

QLabel#TitleLabel {
    color: #b91c1c;
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 0.5px;
}

QLabel#SubtitleLabel {
    color: #525252;
    font-size: 11px;
    font-style: italic;
}

QLabel#SectionLabel {
    color: #a3a3a3;
    font-size: 12px;
    font-weight: 600;
}

QLabel#DialogLabel {
    color: #e5e5e5;
    font-size: 12px;
    font-weight: 600;
}

QLabel#FieldLabel {
    color: #a3a3a3;
    font-size: 12px;
}

QFrame#Divider {
    background-color: #1a1a1a;
    max-height: 1px;
    min-height: 1px;
}

QLineEdit {
    background-color: #0a0a0a;
    color: #ffffff;
    border: 1px solid #1f1f1f;
    border-radius: 4px;
    padding: 8px 12px;
    font-family: "Consolas", monospace;
    font-size: 13px;
    selection-background-color: #8a1a1a;
}

QLineEdit:focus {
    border: 1px solid #8a1a1a;
}

QPushButton {
    background-color: #121212;
    color: #d4d4d4;
    border: 1px solid #242424;
    border-radius: 4px;
    padding: 6px 12px;
    font-size: 12px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #1a1a1a;
    border-color: #2e2e2e;
}

QPushButton:pressed {
    background-color: #0a0a0a;
}

QPushButton#LangButton {
    background-color: #121212;
    color: #a3a3a3;
    border: 1px solid #242424;
    border-radius: 2px;
    font-size: 9px;
    font-weight: 700;
    padding: 0px;
}

QPushButton#LangButton:hover {
    background-color: #1a1a1a;
    border-color: #2e2e2e;
    color: #d4d4d4;
}

QPushButton#LangButton[active="true"] {
    background-color: #8a1a1a;
    border: none;
    color: #ffffff;
}

QPushButton#LangButton[active="true"]:hover {
    background-color: #a32020;
}

QPushButton#UpdateBinButton {
    background-color: #9a3412;
    border: none;
    border-radius: 2px;
    color: #ffffff;
    padding: 0px;
}

QPushButton#UpdateBinButton:hover {
    background-color: #b45309;
}

QPushButton#UpdateBinButton:pressed {
    background-color: #7c2d12;
}

QPushButton#PinButton {
    background-color: #121212;
    color: #a3a3a3;
    border: 1px solid #242424;
    border-radius: 2px;
    padding: 0px;
}

QPushButton#PinButton:hover {
    background-color: #1a1a1a;
    border-color: #2e2e2e;
}

QPushButton#PinButton[active="true"] {
    background-color: #8a1a1a;
    border: none;
    color: #ffffff;
}

QPushButton#PinButton[active="true"]:hover {
    background-color: #a32020;
}

QPushButton#PrimaryButton {
    background-color: #8a1a1a;
    border: none;
    color: #ffffff;
    font-size: 12px;
    font-weight: 700;
    padding: 9px 18px;
    border-radius: 6px;
}

QPushButton#PrimaryButton:hover {
    background-color: #a32020;
}

QPushButton#PrimaryButton:pressed {
    background-color: #6e1414;
}

QPushButton#PrimaryButton:disabled {
    background-color: #1f1f1f;
    color: #525252;
}

QPushButton#FolderButton {
    background-color: #121212;
    border: 1px solid #242424;
    color: #d4d4d4;
    font-size: 12px;
    font-weight: 700;
    padding: 11px 16px;
    border-radius: 6px;
}

QPushButton#FolderButton:hover {
    background-color: #1a1a1a;
    border-color: #2e2e2e;
    color: #ffffff;
}

QPushButton#FolderButton:pressed {
    background-color: #0a0a0a;
}

QComboBox {
    background-color: #0a0a0a;
    color: #ffffff;
    border: 1px solid #1f1f1f;
    border-radius: 4px;
    padding: 7px 12px;
    font-size: 12px;
}

QComboBox:hover {
    border-color: #2e2e2e;
}

QComboBox[selected="true"] {
    background-color: #0a0a0a;
    border: 1px solid #8a1a1a;
}

QComboBox[selected="true"]:hover {
    border-color: #a32020;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 26px;
    border-left: 1px solid #1f1f1f;
    border-top-right-radius: 4px;
    border-bottom-right-radius: 4px;
}

QComboBox::down-arrow {
    image: none;
    width: 0px;
    height: 0px;
    border: none;
}

QComboBox QAbstractItemView {
    background-color: #0a0a0a;
    color: #ffffff;
    border: 1px solid #1f1f1f;
    border-radius: 4px;
    max-height: 200px;
    selection-background-color: #8a1a1a;
    selection-color: #ffffff;
    outline: 0;
    padding: 4px;
}

QComboBox QAbstractItemView QScrollBar:vertical {
    background: #0a0a0a;
    width: 6px;
    border-radius: 3px;
}

QComboBox QAbstractItemView QScrollBar::handle:vertical {
    background: #242424;
    min-height: 20px;
    border-radius: 3px;
}

QComboBox QAbstractItemView QScrollBar::handle:vertical:hover {
    background: #3a3a3a;
}

QComboBox QAbstractItemView QScrollBar::add-line:vertical,
QComboBox QAbstractItemView QScrollBar::sub-line:vertical {
    height: 0px;
}

QProgressBar {
    background-color: #121212;
    border: none;
    border-radius: 3px;
    min-height: 6px;
    max-height: 6px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #c2410c;
    border-radius: 3px;
}

QPlainTextEdit#ConsoleOutput {
    background-color: #0a0a0a;
    color: #efbd61;
    border: 1px solid #1f1f1f;
    border-radius: 4px;
    padding: 8px;
    font-family: "Consolas", monospace;
    font-size: 12px;
    selection-background-color: #8a1a1a;
    selection-color: #ffffff;
}

QScrollBar:vertical {
    background: #000000;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #1f1f1f;
    min-height: 24px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #2e2e2e;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""


def apply_dark_title_bar(widget: QWidget) -> None:
    try:
        import ctypes
        hwnd = int(widget.winId())
        dark_mode = ctypes.c_int(1)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, 20, ctypes.byref(dark_mode), ctypes.sizeof(dark_mode)
        )
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, 26, ctypes.byref(dark_mode), ctypes.sizeof(dark_mode)
        )
    except Exception:
        pass


def create_gear_icon(color: str = "#ffffff", size: int = 14) -> QIcon:
    dpr = 2
    pm = QPixmap(size * dpr, size * dpr)
    pm.setDevicePixelRatio(dpr)
    pm.fill(Qt.transparent)

    painter = QPainter(pm)
    painter.setRenderHint(QPainter.Antialiasing, True)

    c = QColor(color)
    center = size / 2.0

    painter.setPen(Qt.NoPen)
    painter.setBrush(QBrush(c))
    painter.save()
    painter.translate(center, center)
    for _ in range(8):
        painter.drawRoundedRect(-1.1, -6.1, 2.2, 2.4, 0.5, 0.5)
        painter.rotate(45.0)
    painter.restore()

    painter.drawEllipse(QPointF(center, center), 4.4, 4.4)

    painter.setCompositionMode(QPainter.CompositionMode_Clear)
    painter.drawEllipse(QPointF(center, center), 1.9, 1.9)

    painter.end()
    return QIcon(pm)


def create_pin_icon(color: str = "#a3a3a3", size: int = 14) -> QIcon:
    dpr = 2
    pm = QPixmap(size * dpr, size * dpr)
    pm.setDevicePixelRatio(dpr)
    pm.fill(Qt.transparent)

    painter = QPainter(pm)
    painter.setRenderHint(QPainter.Antialiasing, True)

    c = QColor(color)
    painter.setPen(Qt.NoPen)
    painter.setBrush(QBrush(c))

    painter.drawRoundedRect(4.5, 1.5, 5.0, 2.0, 0.6, 0.6)
    painter.drawRect(5.6, 3.5, 2.8, 3.3)
    collar = QPolygonF([
        QPointF(3.2, 6.8),
        QPointF(10.8, 6.8),
        QPointF(11.3, 8.2),
        QPointF(2.7, 8.2),
    ])
    painter.drawPolygon(collar)

    pen = QPen(c, 1.5, Qt.SolidLine, Qt.RoundCap)
    painter.setPen(pen)
    painter.drawLine(QPointF(7.0, 8.2), QPointF(7.0, 12.6))

    painter.end()
    return QIcon(pm)


class VectorComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setView(QListView(self))

    def paintEvent(self, event):
        super().paintEvent(event)

        opt = QStyleOptionComboBox()
        self.initStyleOption(opt)
        arrow_rect = self.style().subControlRect(
            QStyle.CC_ComboBox, opt, QStyle.SC_ComboBoxArrow, self
        )
        if not arrow_rect.isValid():
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor("#a3a3a3")))

        cx = arrow_rect.center().x()
        cy = arrow_rect.center().y()
        half_w = 4.0
        half_h = 2.2
        triangle = QPolygonF([
            QPointF(cx - half_w, cy - half_h),
            QPointF(cx + half_w, cy - half_h),
            QPointF(cx, cy + half_h + 0.5),
        ])
        painter.drawPolygon(triangle)
        painter.end()


class DownloadWorker(QThread):
    progress_updated = Signal(float)
    speed_updated = Signal(str)
    log_received = Signal(str)
    finished = Signal(int)

    def __init__(self, cmd: list, parent=None):
        super().__init__(parent)
        self.cmd = cmd

    def run(self):
        try:
            returncode = run_download_subprocess(
                self.cmd,
                log_callback=self.log_received.emit,
                speed_callback=self.speed_updated.emit,
                progress_callback=self.progress_updated.emit,
            )
            self.finished.emit(returncode)
        except Exception as e:
            self.log_received.emit(f"CRITICAL_ERROR::{e}")
            self.finished.emit(-1)


class YtDlpUpdateWorker(QThread):
    log_received = Signal(str)
    update_finished = Signal(int)
    error_occurred = Signal(str)

    def run(self):
        try:
            returncode = run_ytdlp_updater(log_callback=self.log_received.emit)
            self.update_finished.emit(returncode)
        except Exception as e:
            self.error_occurred.emit(str(e))


class AppUpdateCheckWorker(QThread):
    update_available = Signal(str, str)

    def run(self):
        try:
            has_update, remote_version, installer_url = check_latest_release()
            if has_update and installer_url:
                self.update_available.emit(remote_version, installer_url)
        except Exception:
            pass


class AppUpdateDownloadWorker(QThread):
    download_finished = Signal()
    error_occurred = Signal(str)

    def __init__(self, installer_url: str, parent=None):
        super().__init__(parent)
        self.installer_url = installer_url

    def run(self):
        try:
            download_and_run_updater(self.installer_url)
            self.download_finished.emit()
        except Exception as e:
            self.error_occurred.emit(str(e))


class EventMelodyWorker(QThread):
    def __init__(self, birth_d: int, birth_m: int, parent=None):
        super().__init__(parent)
        self.birth_d = birth_d
        self.birth_m = birth_m

    def run(self):
        check_and_play_event_melody(self.birth_d, self.birth_m)


class SoundAlertWorker(QThread):
    def run(self):
        sound_alert()


class LanguageDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_lang = "EN"
        self._completed = False

        self.setWindowTitle("Language / Idioma / 언어")
        self.setFixedSize(430, 150)
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        self.setModal(True)

        if os.path.exists(app_icon_path):
            self.setWindowIcon(QIcon(app_icon_path))

        apply_dark_title_bar(self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        lbl_info = QLabel("Select your language / Selecciona tu idioma / 언어를 선택하세요:")
        lbl_info.setObjectName("DialogLabel")
        lbl_info.setAlignment(Qt.AlignCenter)
        lbl_info.setWordWrap(True)
        layout.addWidget(lbl_info)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        for label, code in [("English (EN)", "EN"), ("Español (ES)", "ES"), ("한국어 (KO)", "KO")]:
            btn = QPushButton(label)
            btn.setObjectName("PrimaryButton")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _=False, c=code: self._choose(c))
            btn_row.addWidget(btn)

        layout.addLayout(btn_row)

    def _choose(self, lang: str):
        data = {"idioma": lang, "bth_day": "", "bth_month": "", "topmost": False}
        if save_config(data):
            self.selected_lang = lang
            self._completed = True
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Could not save language")

    def closeEvent(self, event):
        if not self._completed:
            event.ignore()
        else:
            super().closeEvent(event)


class BirthdateDialog(QDialog):
    def __init__(self, lang: str, parent=None):
        super().__init__(parent)
        self.lang = lang
        self._completed = False
        data = LANGUAGES[lang]

        self.setWindowTitle(data["config_title"])
        self.setFixedSize(360, 180)
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        self.setModal(True)

        if os.path.exists(app_icon_path):
            self.setWindowIcon(QIcon(app_icon_path))

        apply_dark_title_bar(self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(14)

        lbl_info = QLabel(data["config_info"])
        lbl_info.setObjectName("DialogLabel")
        lbl_info.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_info)

        inputs_row = QHBoxLayout()
        inputs_row.setSpacing(8)

        lbl_day = QLabel(data["config_day"])
        lbl_day.setObjectName("FieldLabel")
        inputs_row.addWidget(lbl_day)

        self.combo_day = VectorComboBox()
        self.combo_day.setMaxVisibleItems(10)
        self.combo_day.addItems([str(i).zfill(2) for i in range(1, 32)])
        self.combo_day.setFixedWidth(68)
        inputs_row.addWidget(self.combo_day)

        lbl_month = QLabel(data["config_month"])
        lbl_month.setObjectName("FieldLabel")
        inputs_row.addWidget(lbl_month)

        self.months_list = data["months_list"]
        self.combo_month = VectorComboBox()
        self.combo_month.setMaxVisibleItems(10)
        self.combo_month.addItems(self.months_list)
        self.combo_month.setMinimumWidth(130)
        inputs_row.addWidget(self.combo_month)

        layout.addLayout(inputs_row)

        btn_save = QPushButton(data["config_btn"])
        btn_save.setObjectName("PrimaryButton")
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.setFixedWidth(130)
        btn_save.clicked.connect(self._save)

        btn_container = QHBoxLayout()
        btn_container.addStretch()
        btn_container.addWidget(btn_save)
        btn_container.addStretch()
        layout.addLayout(btn_container)

    def _save(self):
        data = LANGUAGES[self.lang]
        indexed_month = self.combo_month.currentIndex() + 1
        numeric_month = str(indexed_month).zfill(2)

        cfg_data = load_config()
        cfg_data["bth_day"] = self.combo_day.currentText()
        cfg_data["bth_month"] = numeric_month

        if save_config(cfg_data):
            self._completed = True
            self.accept()
        else:
            QMessageBox.critical(self, "Error", f"{data['config_err']}save failed")

    def closeEvent(self, event):
        if not self._completed:
            event.ignore()
        else:
            super().closeEvent(event)

class YisukmDownloaderWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_lang = "EN"
        self.is_topmost = False
        self.is_downloading = False
        self.download_worker = None
        self.ytdlp_update_worker = None
        self.app_update_check_worker = None
        self.app_update_download_worker = None
        self.melody_worker = None
        self.sound_worker = None

        self.setWindowTitle(f"dlp-yisk - v{LOCAL_VERSION}")
        self.setFixedSize(650, 520)

        if os.path.exists(app_icon_path):
            self.setWindowIcon(QIcon(app_icon_path))

        apply_dark_title_bar(self)
        self._build_ui()
        self.update_ui_texts()

        timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        init_banner = (
            f"✦  yiskm-downloader  ->  v{LOCAL_VERSION}\n"
            f"----------------------------------------\n"
            f"[session] {timestamp_str}"
        )
        self.log(init_banner)

        QTimer.singleShot(100, self.load_app_config)
        QTimer.singleShot(1500, self.check_app_updates)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(12)

        header_layout = QHBoxLayout()
        self.lbl_title = QLabel()
        self.lbl_title.setObjectName("TitleLabel")
        header_layout.addWidget(self.lbl_title)
        header_layout.addStretch()

        self.lbl_subtitle = QLabel()
        self.lbl_subtitle.setObjectName("SubtitleLabel")
        header_layout.addWidget(self.lbl_subtitle)
        main_layout.addLayout(header_layout)

        divider = QFrame()
        divider.setObjectName("Divider")
        divider.setFrameShape(QFrame.HLine)
        main_layout.addWidget(divider)

        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(6)
        toolbar_layout.addStretch()

        self.btn_lang_en = self._make_lang_button("EN")
        self.btn_lang_es = self._make_lang_button("ES")
        self.btn_lang_ko = self._make_lang_button("KO")
        toolbar_layout.addWidget(self.btn_lang_en)
        toolbar_layout.addWidget(self.btn_lang_es)
        toolbar_layout.addWidget(self.btn_lang_ko)

        toolbar_layout.addSpacing(8)

        self.btn_update_ytdlp = QPushButton()
        self.btn_update_ytdlp.setObjectName("UpdateBinButton")
        self.btn_update_ytdlp.setFixedSize(25, 22)
        self.btn_update_ytdlp.setIcon(create_gear_icon("#ffffff", 12))
        self.btn_update_ytdlp.setIconSize(QSize(12, 12))
        self.btn_update_ytdlp.setCursor(Qt.PointingHandCursor)
        self.btn_update_ytdlp.setToolTip("Update yt-dlp")
        self.btn_update_ytdlp.clicked.connect(self.update_ytdlp_binary)
        toolbar_layout.addWidget(self.btn_update_ytdlp)

        self._pin_icon_inactive = create_pin_icon("#a3a3a3", 12)
        self._pin_icon_active = create_pin_icon("#ffffff", 12)

        self.btn_pin = QPushButton()
        self.btn_pin.setObjectName("PinButton")
        self.btn_pin.setFixedSize(25, 22)
        self.btn_pin.setIcon(self._pin_icon_inactive)
        self.btn_pin.setIconSize(QSize(12, 12))
        self.btn_pin.setCursor(Qt.PointingHandCursor)
        self.btn_pin.setProperty("active", "false")
        self.btn_pin.clicked.connect(self.toggle_topmost)
        toolbar_layout.addWidget(self.btn_pin)

        main_layout.addLayout(toolbar_layout)

        self.lbl_url = QLabel()
        self.lbl_url.setObjectName("SectionLabel")
        main_layout.addWidget(self.lbl_url)

        url_row = QHBoxLayout()
        url_row.setSpacing(12)

        self.entry_url = QLineEdit()
        self.entry_url.returnPressed.connect(self.start_download_thread)
        url_row.addWidget(self.entry_url, 1)

        self.btn_run = QPushButton()
        self.btn_run.setObjectName("PrimaryButton")
        self.btn_run.setCursor(Qt.PointingHandCursor)
        self.btn_run.setMinimumWidth(120)
        self.btn_run.clicked.connect(self.start_download_thread)
        url_row.addWidget(self.btn_run)

        main_layout.addLayout(url_row)

        options_row = QHBoxLayout()
        options_row.setSpacing(12)

        self.lbl_action = QLabel()
        self.lbl_action.setObjectName("SectionLabel")
        options_row.addWidget(self.lbl_action)

        self.combo_options = VectorComboBox()
        self.combo_options.setProperty("selected", "false")
        self.combo_options.currentIndexChanged.connect(self._on_option_changed)
        self.combo_options.installEventFilter(self)
        options_row.addWidget(self.combo_options, 1)

        main_layout.addLayout(options_row)

        self.lbl_console = QLabel()
        self.lbl_console.setObjectName("SectionLabel")
        main_layout.addWidget(self.lbl_console)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        main_layout.addWidget(self.progress_bar)

        self.txt_console = QPlainTextEdit()
        self.txt_console.setObjectName("ConsoleOutput")
        self.txt_console.setReadOnly(True)
        self.txt_console.setMaximumBlockCount(500)
        main_layout.addWidget(self.txt_console, 1)

        self.btn_folder = QPushButton()
        self.btn_folder.setObjectName("FolderButton")
        self.btn_folder.setCursor(Qt.PointingHandCursor)
        self.btn_folder.clicked.connect(self.open_downloads_folder)
        main_layout.addWidget(self.btn_folder)

    def _make_lang_button(self, code: str) -> QPushButton:
        btn = QPushButton(code)
        btn.setObjectName("LangButton")
        btn.setFixedSize(34, 22)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setProperty("active", "false")
        btn.clicked.connect(lambda _=False, c=code: self.switch_language(c))
        return btn

    def _refresh_widget_style(self, widget: QWidget):
        widget.style().unpolish(widget)
        widget.style().polish(widget)

    def eventFilter(self, obj, event):
        if obj is self.combo_options and event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
                self.combo_options.setCurrentIndex(-1)
                return True
        return super().eventFilter(obj, event)

    def _on_option_changed(self, index: int):
        is_selected = "true" if index >= 0 else "false"
        self.combo_options.setProperty("selected", is_selected)
        self._refresh_widget_style(self.combo_options)

    def switch_language(self, lang: str):
        if lang not in LANGUAGES:
            return
        self.current_lang = lang
        if os.path.exists(config_file_path):
            update_config_value("idioma", lang)

        for btn, code in [(self.btn_lang_en, "EN"), (self.btn_lang_es, "ES"), (self.btn_lang_ko, "KO")]:
            btn.setProperty("active", "true" if code == lang else "false")
            self._refresh_widget_style(btn)

        self.update_ui_texts()

    def set_topmost(self, state: bool):
        self.is_topmost = bool(state)
        self.setWindowFlag(Qt.WindowStaysOnTopHint, self.is_topmost)
        self.show()
        apply_dark_title_bar(self)

        self.btn_pin.setProperty("active", "true" if self.is_topmost else "false")
        self.btn_pin.setIcon(self._pin_icon_active if self.is_topmost else self._pin_icon_inactive)
        self._refresh_widget_style(self.btn_pin)

    def toggle_topmost(self):
        self.set_topmost(not self.is_topmost)
        if os.path.exists(config_file_path):
            update_config_value("topmost", self.is_topmost)

    def update_ui_texts(self):
        data = LANGUAGES[self.current_lang]
        self.lbl_title.setText(data["title"])
        self.lbl_subtitle.setText(data["subtitle"])
        self.lbl_url.setText(data["url_label"])
        self.lbl_action.setText(data["action_label"])
        self.lbl_console.setText(data["console_label"])
        self.entry_url.setPlaceholderText(data["placeholder"])
        self.btn_folder.setText(data["btn_folder"])

        current_idx = self.combo_options.currentIndex()
        self.combo_options.blockSignals(True)
        self.combo_options.clear()
        self.combo_options.addItems(data["options"])
        self.combo_options.setPlaceholderText(data["action_placeholder"])
        self.combo_options.setCurrentIndex(current_idx if current_idx >= 0 else -1)
        self.combo_options.blockSignals(False)
        self._on_option_changed(self.combo_options.currentIndex())

        if not self.is_downloading:
            self.btn_run.setText(data["btn_run"])
        else:
            self.btn_run.setText("...")

    def log(self, text: str):
        self.txt_console.appendPlainText(text)
        scrollbar = self.txt_console.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear_log(self):
        self.txt_console.clear()

    def _play_sound_alert(self):
        self.sound_worker = SoundAlertWorker(self)
        self.sound_worker.start()

    def load_app_config(self):
        if not os.path.exists(config_file_path):
            lang_dlg = LanguageDialog(self)
            if lang_dlg.exec() == QDialog.Accepted:
                self.switch_language(lang_dlg.selected_lang)
                bth_dlg = BirthdateDialog(lang_dlg.selected_lang, self)
                if bth_dlg.exec() == QDialog.Accepted:
                    self.load_app_config()
            return

        try:
            data = load_config()
            saved_language = data.get("idioma", "EN")
            saved_topmost = data.get("topmost", False)

            self.switch_language(saved_language)
            self.set_topmost(saved_topmost)

            day_txt = data.get("bth_day", "")
            month_txt = data.get("bth_month", "")

            if not day_txt or not month_txt:
                bth_dlg = BirthdateDialog(saved_language, self)
                if bth_dlg.exec() == QDialog.Accepted:
                    self.load_app_config()
                return

            birth_d = int(day_txt)
            birth_m = int(month_txt)
            self.melody_worker = EventMelodyWorker(birth_d, birth_m, self)
            self.melody_worker.start()
        except Exception:
            pass

    def start_download_thread(self):
        if self.is_downloading:
            return

        data = LANGUAGES[self.current_lang]
        idx = self.combo_options.currentIndex()
        if idx < 0:
            QMessageBox.critical(self, "Error", data["err_format"])
            return

        clean_url = self.entry_url.text().strip()
        if not clean_url:
            QMessageBox.critical(self, "Error", data["err_valid"])
            return

        self.is_downloading = True
        self.btn_run.setEnabled(False)
        self.btn_run.setText("...")
        self.progress_bar.setValue(0)
        self.clear_log()
        self.log(data["logs"][idx])

        cmd = build_ytdlp_command(idx, clean_url)
        self.download_worker = DownloadWorker(cmd, self)
        self.download_worker.log_received.connect(self._on_worker_log)
        self.download_worker.speed_updated.connect(self._on_worker_speed)
        self.download_worker.progress_updated.connect(self._on_worker_progress)
        self.download_worker.finished.connect(self._on_download_finished)
        self.download_worker.start()

    def _on_worker_log(self, msg: str):
        data = LANGUAGES[self.current_lang]
        if msg.startswith("CRITICAL_ERROR::"):
            err = msg.split("CRITICAL_ERROR::", 1)[1]
            self.log(f"{data['msg_crit']}{err}")
        else:
            self.log(msg)

    def _on_worker_speed(self, speed: str):
        self.setWindowTitle(f"DLP-YISK [Speed: {speed}]")
        
    def _on_worker_progress(self, pct: float):
        self.progress_bar.setValue(int(round(pct)))

    def _on_download_finished(self, returncode: int):
        data = LANGUAGES[self.current_lang]
        self.setWindowTitle(f"DLP-YISK - v{LOCAL_VERSION}")

        if returncode == 0:
            self.progress_bar.setValue(100)
            self.log(data["msg_success"])
            self._play_sound_alert()
        elif returncode > 0:
            self.log(f"{data['msg_warn']}{returncode}")

        self.is_downloading = False
        self.btn_run.setEnabled(True)
        self.btn_run.setText(data["btn_run"])

    def open_downloads_folder(self):
        idx = self.combo_options.currentIndex()
        target_dir = get_target_dir_for_option(idx)
        os.makedirs(target_dir, exist_ok=True)
        os.startfile(target_dir)

    def update_ytdlp_binary(self):
        if self.ytdlp_update_worker and self.ytdlp_update_worker.isRunning():
            return

        data = LANGUAGES[self.current_lang]
        self.clear_log()
        self.log(data["msg_update"])

        self.ytdlp_update_worker = YtDlpUpdateWorker(self)
        self.ytdlp_update_worker.log_received.connect(self.log)
        self.ytdlp_update_worker.update_finished.connect(self._on_ytdlp_update_finished)
        self.ytdlp_update_worker.error_occurred.connect(
            lambda err: self.log(f"{LANGUAGES[self.current_lang]['err_update']}{err}")
        )
        self.ytdlp_update_worker.start()

    def _on_ytdlp_update_finished(self, returncode: int):
        if returncode == 0:
            self._play_sound_alert()

    def check_app_updates(self):
        self.app_update_check_worker = AppUpdateCheckWorker(self)
        self.app_update_check_worker.update_available.connect(self.prompt_app_update)
        self.app_update_check_worker.start()

    def prompt_app_update(self, remote_version: str, installer_url: str):
        data = LANGUAGES[self.current_lang]
        ans = QMessageBox.question(
            self,
            data["app_update_title"],
            data["app_update_prompt"].format(version=remote_version),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )
        if ans == QMessageBox.Yes:
            self.clear_log()
            self.log(data["app_update_downloading"])

            self.app_update_download_worker = AppUpdateDownloadWorker(installer_url, self)
            self.app_update_download_worker.download_finished.connect(QApplication.quit)
            self.app_update_download_worker.error_occurred.connect(
                lambda err: self.log(f"{LANGUAGES[self.current_lang]['app_update_failed']}{err}")
            )
            self.app_update_download_worker.start()


def main():
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(DARK_QSS)

    window = YisukmDownloaderWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()