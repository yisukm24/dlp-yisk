import os
import threading
import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import multiprocessing

from paths import (
    app_icon_path,
    config_file_path,
    script_root,
)
from config import load_config, save_config, update_config_value
from audio import sound_alert, check_and_play_event_melody
from downloader import (
    build_ytdlp_command,
    run_download_subprocess,
    get_target_dir_for_option,
)
from updater import (
    update_ytdlp_binary as run_ytdlp_updater,
    check_latest_release,
    download_and_run_updater,
)

LANGUAGES = {
    "EN": {
        "title": "YT-DLP DOWNLOADER",
        "subtitle": "Developed for yisukm",
        "url_label": "Content URL",
        "action_label": "Action Type",
        "console_label": "Console Output",
        "btn_run": "Download",
        "btn_downloading": "DOWNLOADING CONTENT...",
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
        "months_list": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
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
            "View Available Source Formats (-F)"
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
            "[+] Analyzing source formats..."
        ],
        "msg_update": "[+] Checking for application updates...",
        "err_update": "\n[!] Update error: ",
        "placeholder": "Enter the content link here..."
    },
    "ES": {
        "title": "YT-DLP DOWNLOADER",
        "subtitle": "Desarrollado por yisukm",
        "url_label": "URL del Contenido",
        "action_label": "Tipo de Acción",
        "console_label": "Salida de Consola",
        "btn_run": "Descargar",
        "btn_downloading": "DESCARGANDO CONTENIDO...",
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
        "months_list": ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"],
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
            "Ver Formatos Disponibles (-F)"
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
            "[+] Analizando formatos de origen..."
        ],
        "msg_update": "[+] Comprobando actualizaciones de la aplicación...",
        "err_update": "\n[!] Error al intentar actualizar: ",
        "placeholder": "Introduce el enlace del contenido aquí..."
    },
    "KO": {
        "title": "YT-DLP 다운로더",
        "subtitle": "yisukm 제작",
        "url_label": "콘텐츠 URL",
        "action_label": "작업 유형",
        "console_label": "콘솔 출력",
        "btn_run": "다운로드",
        "btn_downloading": "콘텐츠 다운로드 중...",
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
        "months_list": ["1월", "2월", "3월", "4월", "5월", "6월", "7월", "8월", "9월", "10월", "11월", "12월"],
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
            "사용 가능한 소스 형식 보기 (-F)"
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
            "[+] 소스 형식 분석 중..."
        ],
        "msg_update": "[+] 재생목록 업데이트 확인 중...",
        "err_update": "\n[!] 업데이트 오류: ",
        "placeholder": "여기에 콘텐츠 링크를 입력하세요..."
    }
}

def your_language(root, on_lang_selected_callback):
    window_lang = tk.Toplevel(root)
    window_lang.title("Language / Idioma / 언어")
    window_lang.geometry("420x150")
    
    apply_dark_title_bar(window_lang)
    
    try:
        if os.path.exists(app_icon_path):
            window_lang.iconbitmap(app_icon_path)
    except:
        pass
        
    window_lang.configure(bg="#0b0c0d")
    window_lang.resizable(False, False)
    window_lang.attributes('-topmost', True) 

    window_lang.transient(root)
    window_lang.grab_set()
    window_lang.protocol("WM_DELETE_WINDOW", lambda: None)

    root.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() // 2) - 210
    y = root.winfo_y() + (root.winfo_height() // 2) - 75
    window_lang.geometry(f"+{x}+{y}")

    lbl_info = tk.Label(window_lang, text="Select your language / Selecciona tu idioma / 언어를 선택하세요:", 
                        bg="#0b0c0d", fg="#ffffff", font=('Segoe UI', 10, 'bold'), justify="center")
    lbl_info.pack(pady=(20, 15))

    frame_btns = tk.Frame(window_lang, bg="#0b0c0d")
    frame_btns.pack(pady=5)

    def set_language(lang):
        data = {"idioma": lang, "bth_day": "", "bth_month": "", "topmost": False}
        if save_config(data):
            window_lang.grab_release()
            window_lang.destroy()
            on_lang_selected_callback(lang)
        else:
            messagebox.showerror("Error", "Could not save language")

    btn_en = tk.Button(frame_btns, text="English (EN)", bg="#8a1a1a", fg="#ffffff", 
                       activebackground="#a32424", activeforeground="#ffffff", 
                       font=('Segoe UI Semibold', 9), bd=0, cursor="hand2", width=12,
                       command=lambda: set_language("EN"))
    btn_en.pack(side="left", padx=8, ipady=5)

    btn_es = tk.Button(frame_btns, text="Español (ES)", bg="#8a1a1a", fg="#ffffff", 
                       activebackground="#a32424", activeforeground="#ffffff", 
                       font=('Segoe UI Semibold', 9), bd=0, cursor="hand2", width=12,
                       command=lambda: set_language("ES"))
    btn_es.pack(side="left", padx=8, ipady=5)

    btn_ko = tk.Button(frame_btns, text="한국어 (KO)", bg="#8a1a1a", fg="#ffffff", 
                       activebackground="#a32424", activeforeground="#ffffff", 
                       font=('Segoe UI Semibold', 9), bd=0, cursor="hand2", width=12,
                       command=lambda: set_language("KO"))
    btn_ko.pack(side="left", padx=8, ipady=5)

def birthdate_(root, actual_language, on_save_callback):
    data = LANGUAGES[actual_language]
    
    birthwind_fecha = tk.Toplevel(root)
    birthwind_fecha.title(data["config_title"])
    birthwind_fecha.geometry("320x180")
    
    apply_dark_title_bar(birthwind_fecha)
    
    try:
        if os.path.exists(app_icon_path):
            birthwind_fecha.iconbitmap(app_icon_path)
    except:
        pass
        
    birthwind_fecha.configure(bg="#0b0c0d")
    birthwind_fecha.resizable(False, False)
    birthwind_fecha.attributes('-topmost', True)
    
    birthwind_fecha.transient(root)
    birthwind_fecha.grab_set()
    birthwind_fecha.protocol("WM_DELETE_WINDOW", lambda: None)

    root.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() // 2) - 160
    y = root.winfo_y() + (root.winfo_height() // 2) - 90
    birthwind_fecha.geometry(f"+{x}+{y}")

    lbl_info = tk.Label(birthwind_fecha, text=data["config_info"], 
                        bg="#0b0c0d", fg="#ffffff", font=('Segoe UI', 9, 'bold'), justify="center")
    lbl_info.pack(pady=(15, 10))

    frame_inputs = tk.Frame(birthwind_fecha, bg="#0b0c0d")
    frame_inputs.pack(pady=5)

    tk.Label(frame_inputs, text=data["config_day"], bg="#0b0c0d", fg="#a0a5aa", font=('Segoe UI', 9)).grid(row=0, column=0, padx=5)
    
    combo_border_day = tk.Frame(frame_inputs, bg="#3a3d40", bd=1)
    combo_border_day.grid(row=0, column=1, padx=5)
    combo_day = ttk.Combobox(combo_border_day, values=[str(i).zfill(2) for i in range(1, 32)], width=5, state="readonly", style='Custom.TCombobox')
    combo_day.pack()
    combo_day.current(0)

    tk.Label(frame_inputs, text=data["config_month"], bg="#0b0c0d", fg="#a0a5aa", font=('Segoe UI', 9)).grid(row=0, column=2, padx=5)
    
    combo_border_month = tk.Frame(frame_inputs, bg="#3a3d40", bd=1)
    combo_border_month.grid(row=0, column=3, padx=5)
    
    months_list = data["months_list"]
    combo_month = ttk.Combobox(combo_border_month, values=months_list, width=12, state="readonly", style='Custom.TCombobox')
    combo_month.pack()
    combo_month.current(0)

    def date_b_():
        month_selected = combo_month.get()
        indexed_month = months_list.index(month_selected) + 1
        numeric_month = str(indexed_month).zfill(2)
        
        cfg_data = load_config()
        cfg_data["bth_day"] = combo_day.get()
        cfg_data["bth_month"] = numeric_month
        
        if save_config(cfg_data):
            birthwind_fecha.grab_release()
            birthwind_fecha.destroy()
            threading.Thread(target=on_save_callback, daemon=True).start()
        else:
            messagebox.showerror("Error", f"{data['config_err']}save failed")

    btn_safe = tk.Button(birthwind_fecha, text=data["config_btn"], bg="#8a1a1a", fg="#ffffff", 
         activebackground="#a32424", activeforeground="#ffffff", 
          font=('Segoe UI Semibold', 9), bd=0, cursor="hand2", width=12, command=date_b_)
    btn_safe.pack(pady=15)

def load_app_config(root, app):
    if not os.path.exists(config_file_path):
        your_language(root, lambda lang: (
            app.switch_language(lang),
            birthdate_(root, lang, lambda: load_app_config(root, app))
        ))
        return

    try:
        data = load_config()
        saved_language = data.get("idioma", "EN")
        saved_topmost = data.get("topmost", False)
        
        app.switch_language(saved_language)
        app.set_topmost(saved_topmost)
        
        day_txt = data.get("bth_day", "")
        month_txt = data.get("bth_month", "")
        
        if not day_txt or not month_txt:
            birthdate_(root, saved_language, lambda: load_app_config(root, app))
            return
            
        birth_d = int(day_txt)
        birth_m = int(month_txt)
        threading.Thread(target=check_and_play_event_melody, args=(birth_d, birth_m), daemon=True).start()
    except Exception:
        pass

def apply_dark_title_bar(window):
    try:
        import ctypes
        window.update()
        
        try:
            hwnd = int(window.wm_frame(), 16)
        except:
            hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
            if hwnd == 0:
                hwnd = window.winfo_id()
        
        dark_mode = ctypes.c_int(1)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(dark_mode), ctypes.sizeof(dark_mode))
        ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 26, ctypes.byref(dark_mode), ctypes.sizeof(dark_mode))
        
        window.update()
    except Exception:
        pass

class YisukmDownloaderScript:
    def __init__(self, root):
        self.root = root
        self.root.title("YT-DLP - v1.0.0")
        self.root.geometry("640x510")
        apply_dark_title_bar(self.root)
        try:
            if os.path.exists(app_icon_path):
                self.root.iconbitmap(app_icon_path)
        except:
            pass

        self.root.configure(bg="#0b0c0d")
        self.root.resizable(False, False)
        
        self.current_lang = "EN"
        self.is_topmost = False
        
        self.style = ttk.Style()
        self.style.theme_use('default')
        
        root.option_add('*TCombobox*Listbox.background', '#161719')
        root.option_add('*TCombobox*Listbox.foreground', '#ffffff')
        root.option_add('*TCombobox*Listbox.selectBackground', '#8a1a1a')
        root.option_add('*TCombobox*Listbox.selectForeground', '#ffffff')
        root.option_add('*TCombobox*Listbox.font', ('Segoe UI', 10))
        root.option_add('*TCombobox*Listbox.borderWidth', 0)
        root.option_add('*TCombobox*Listbox.highlightThickness', 0)
        
        self.style.configure('.', background='#0b0c0d', foreground='#ffffff')
        self.style.configure('TLabel', background='#0b0c0d', foreground='#ffffff', font=('Segoe UI', 10, 'semibold'))
        
        self.style.configure('Custom.TCombobox', fieldbackground='#111214', background='#111214', foreground='#ffffff', font=('Segoe UI', 10), borderwidth=0, arrowcolor='#ffffff', relief='flat')
        self.style.map('Custom.TCombobox', 
            fieldbackground=[('readonly', '#111214')],
            foreground=[('readonly', '#ffffff')],
            background=[('readonly', '#111214')],
            arrowcolor=[('readonly', '#ffffff')]
        )
        
        self.style.configure("Custom.Horizontal.TProgressbar", troughcolor='#161719', background="#af6f25", thickness=4, borderwidth=0)

        header_frame = tk.Frame(root, bg="#0b0c0d")
        header_frame.pack(fill="x", padx=25, pady=(20, 5))
        
        self.lbl_title = tk.Label(header_frame, text="", bg="#0b0c0d", fg="#8a1a1a", font=('Segoe UI', 14, 'bold'))
        self.lbl_title.pack(side="left", anchor="w")
        
        self.lbl_subtitle = tk.Label(header_frame, text="", bg="#0b0c0d", fg="#4f5256", font=('Segoe UI', 9, 'italic'))
        self.lbl_subtitle.pack(side="right", anchor="e", pady=(4, 0))
        
        divider = tk.Frame(root, bg="#3a3d40", height=1)
        divider.pack(fill="x", padx=25, pady=(0, 15))

        lang_frame = tk.Frame(root, bg="#0b0c0d")   
        lang_frame.pack(anchor="e", padx=25, pady=(0, 5))
        
        self.btn_lang_en = tk.Button(lang_frame, text="EN", bg="#161719", fg="#ffffff", font=('Segoe UI', 7, 'bold'), bd=0, relief="flat", width=4, cursor="hand2", command=lambda: self.switch_language("EN"))
        self.btn_lang_en.pack(side="left", padx=2)
        self.btn_lang_en.bind("<Enter>", lambda e: self.btn_lang_en.configure(bg="#222428"))
        self.btn_lang_en.bind("<Leave>", lambda e: self.btn_lang_en.configure(bg="#161719" if self.current_lang != "EN" else "#8a1a1a"))
        
        self.btn_lang_es = tk.Button(lang_frame, text="ES", bg="#161719", fg="#ffffff", font=('Segoe UI', 7, 'bold'), bd=0, relief="flat", width=4, cursor="hand2", command=lambda: self.switch_language("ES"))
        self.btn_lang_es.pack(side="left", padx=2)
        self.btn_lang_es.bind("<Enter>", lambda e: self.btn_lang_es.configure(bg="#222428"))
        self.btn_lang_es.bind("<Leave>", lambda e: self.btn_lang_es.configure(bg="#161719" if self.current_lang != "ES" else "#8a1a1a"))

        self.btn_lang_ko = tk.Button(lang_frame, text="KO", bg="#161719", fg="#ffffff", font=('Segoe UI', 7, 'bold'), bd=0, relief="flat", width=4, cursor="hand2", command=lambda: self.switch_language("KO"))
        self.btn_lang_ko.pack(side="left", padx=2)
        self.btn_lang_ko.bind("<Enter>", lambda e: self.btn_lang_ko.configure(bg="#222428"))
        self.btn_lang_ko.bind("<Leave>", lambda e: self.btn_lang_ko.configure(bg="#161719" if self.current_lang != "KO" else "#8a1a1a"))

        self.btn_update_ytdlp = tk.Button(lang_frame, text="⚙", bg="#763F00", fg="#FFFFFF", font=('Segoe UI', 9), bd=0, relief="flat", width=4, cursor="hand2", command=self.update_ytdlp_binary)
        self.btn_update_ytdlp.pack(side="left", padx=(10, 1))
        self.btn_update_ytdlp.bind("<Enter>", lambda e: self.btn_update_ytdlp.configure(bg="#763F00"))
        self.btn_update_ytdlp.bind("<Leave>", lambda e: self.btn_update_ytdlp.configure(bg="#763F00"))

        self.btn_pin = tk.Button(lang_frame, text="⚓", bg="#161719", fg="#ffffff", font=('Segoe UI Symbol', 9), anchor="center", padx=0, bd=0, relief="flat", width=4, cursor="hand2", command=self.toggle_topmost)
        self.btn_pin.pack(side="left", padx=(2, 0))
        self.btn_pin.bind("<Enter>", lambda e: self.btn_pin.configure(bg="#222428" if not self.is_topmost else "#a32424"))
        self.btn_pin.bind("<Leave>", lambda e: self.btn_pin.configure(bg="#8a1a1a" if self.is_topmost else "#161719"))

        input_frame = tk.Frame(root, bg="#0b0c0d")
        input_frame.pack(fill="x", padx=25, pady=5)
        
        self.lbl_url = tk.Label(input_frame, text="", bg="#0b0c0d", fg="#b2b5b8", font=('Segoe UI', 10, 'bold'))
        self.lbl_url.pack(anchor="w", pady=2)
        
        url_row = tk.Frame(input_frame, bg="#0b0c0d")
        url_row.pack(fill="x", pady=5)

        self.entry_url = tk.Entry(url_row, bg="#111214", fg="#ffffff", insertbackground="#ffffff", highlightbackground="#3a3d40", highlightcolor="#8a1a1a", highlightthickness=1, bd=0, font=('Consolas', 11))
        self.entry_url.pack(side="left", fill="x", expand=True, ipady=8)
        self.root.focus_set()
        self.entry_url.bind("<Return>", lambda event: self.start_download_thread())

        def on_focus_in(event):
            placeholder_actual = LANGUAGES[self.current_lang]["placeholder"]
            if self.entry_url.get() == placeholder_actual:
                self.entry_url.delete(0, tk.END)
                self.entry_url.configure(fg="#ffffff")
                
        def on_focus_out(event):
            placeholder_actual = LANGUAGES[self.current_lang]["placeholder"]
            if not self.entry_url.get().strip():
                self.entry_url.insert(0, placeholder_actual)
                self.entry_url.configure(fg="#4f5256")
                
        self.entry_url.bind("<FocusIn>", on_focus_in)
        self.entry_url.bind("<FocusOut>", on_focus_out)

        self.btn_run = tk.Button(url_row, text="", bg="#8a1a1a", fg="#ffffff", activebackground="#a32424", activeforeground="#ffffff", font=('Segoe UI Semibold', 9, 'bold'), bd=0, relief="flat", cursor="hand2", width=12, command=self.start_download_thread)
        self.btn_run.pack(side="right", padx=(12, 0), ipady=7)
        self.btn_run.bind("<Enter>", lambda e: self.btn_run.configure(bg="#a32424") if self.btn_run["state"] == "normal" else None)
        self.btn_run.bind("<Leave>", lambda e: self.btn_run.configure(bg="#8a1a1a") if self.btn_run["state"] == "normal" else None)

        options_frame = tk.Frame(root, bg="#0b0c0d")
        options_frame.pack(fill="x", padx=25, pady=10)
        
        self.lbl_action = tk.Label(options_frame, text="", bg="#0b0c0d", fg="#b2b5b8", font=('Segoe UI', 10, 'bold'))
        self.lbl_action.pack(side="left", padx=(0, 10))
        
        combo_border = tk.Frame(options_frame, bg="#3a3d40", bd=1)
        combo_border.pack(side="left", fill="x", expand=True)

        self.combo_options = ttk.Combobox(combo_border, state="readonly", width=45, style='Custom.TCombobox')
        self.combo_options.pack(fill="x", expand=True)
        
        self.combo_options.bind("<Delete>", lambda event: (self.combo_options.configure(state="normal"), self.combo_options.delete(0, tk.END), self.combo_options.configure(state="readonly"), self.style.map('Custom.TCombobox', fieldbackground=[('readonly', '#111214')]), self.combo_options.configure(style='Custom.TCombobox')))
        self.combo_options.bind("<BackSpace>", lambda event: (self.combo_options.configure(state="normal"), self.combo_options.delete(0, tk.END), self.combo_options.configure(state="readonly"), self.style.map('Custom.TCombobox', fieldbackground=[('readonly', '#111214')]), self.combo_options.configure(style='Custom.TCombobox')))
        self.combo_options.bind("<<ComboboxSelected>>", lambda event: (self.combo_options.selection_clear(), self.style.map('Custom.TCombobox', fieldbackground=[('readonly', '#8a1a1a')]), self.combo_options.configure(style='Custom.TCombobox'), self.root.focus()))

        console_frame = tk.Frame(root, bg="#0b0c0d")
        console_frame.pack(fill="both", expand=True, padx=25, pady=5)
        
        self.lbl_console = tk.Label(console_frame, text="", bg="#0b0c0d", fg="#b2b5b8", font=('Segoe UI', 10, 'bold'))
        self.lbl_console.pack(anchor="w", pady=2)

        self.progress_bar = ttk.Progressbar(console_frame, orient="horizontal", mode="determinate", style="Custom.Horizontal.TProgressbar")
        self.progress_bar.pack(fill="x", pady=(0, 10))
        
        self.txt_console = tk.Text(console_frame, bg="#070809", fg="#efbd61", insertbackground="#efbd61", font=('Consolas', 9), highlightbackground="#111214", highlightthickness=1, bd=0, relief="flat", state="disabled", height=8)
        self.txt_console.pack(fill="both", expand=True)
        
        self.btn_folder = tk.Button(root, text="", bg="#111214", fg="#ffffff", activebackground="#1c1d21", activeforeground="#ffffff", font=('Segoe UI', 10, 'bold'), bd=0, relief="flat", cursor="hand2", command=self.open_downloads_folder)
        self.btn_folder.pack(fill="x", padx=25, pady=20, ipady=10)
        self.btn_folder.bind("<Enter>", lambda e: self.btn_folder.configure(bg="#1c1d21"))
        self.btn_folder.bind("<Leave>", lambda e: self.btn_folder.configure(bg="#111214"))

        self.update_ui_texts()

        timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        init_banner = f"✦  yiskm-downloader  ->  v1.0.0\n----------------------------------------\n[session] {timestamp_str}\n"
        self.log(init_banner.strip())

    def switch_language(self, lang):
        self.current_lang = lang
        if os.path.exists(config_file_path):
            update_config_value("idioma", lang)

        for btn, l_code in [(self.btn_lang_en, "EN"), (self.btn_lang_es, "ES"), (self.btn_lang_ko, "KO")]:
            if l_code == lang:
                btn.configure(bg="#8a1a1a", fg="#ffffff")
            else:
                btn.configure(bg="#161719", fg="#ffffff")

        self.update_ui_texts()

    def set_topmost(self, state):
        self.is_topmost = bool(state)
        self.root.attributes('-topmost', self.is_topmost)
        if self.is_topmost:
            self.btn_pin.configure(bg="#8a1a1a")
        else:
            self.btn_pin.configure(bg="#161719")

    def toggle_topmost(self):
        self.set_topmost(not self.is_topmost)
        if os.path.exists(config_file_path):
            update_config_value("topmost", self.is_topmost)

    def update_ui_texts(self):
        data = LANGUAGES[self.current_lang]
        self.lbl_title.configure(text=data["title"])
        self.lbl_subtitle.configure(text=data["subtitle"])
        self.lbl_url.configure(text=data["url_label"])
        self.lbl_action.configure(text=data["action_label"])
        self.lbl_console.configure(text=data["console_label"])
        
        current_idx = self.combo_options.current()
        self.combo_options['values'] = data["options"]
        if current_idx >= 0:
            self.combo_options.current(current_idx)
        else:
            self.combo_options.set("")
            
        if self.btn_run["state"] == "normal":
            self.btn_run.configure(text=data["btn_run"])
        else:
            self.btn_run.configure(text="..." if self.current_lang == "EN" else "...")
            
        if self.current_lang == "ES":
            self.btn_folder.configure(text="ABRIR DESCARGAS")
        elif self.current_lang == "KO":
            self.btn_folder.configure(text="다운로드 폴더 열기")
        else:
            self.btn_folder.configure(text="OPEN DOWNLOADS")    

        text_url = self.entry_url.get()
        es_placeholder = any(text_url == LANGUAGES[lang]["placeholder"] or not text_url.strip() for lang in LANGUAGES)
        
        if es_placeholder:
            self.entry_url.delete(0, tk.END)
            self.entry_url.insert(0, data["placeholder"])
            self.entry_url.configure(fg="#4f5256")


    def log(self, text):
        self.txt_console.configure(state="normal")
        self.txt_console.insert(tk.END, text + "\n")
        if float(self.txt_console.index('end-1c')) > 500.0:
            self.txt_console.delete('1.0', '2.0')  
        self.txt_console.see(tk.END)
        self.txt_console.configure(state="disabled")


    def clear_log(self):
        self.txt_console.configure(state="normal")
        self.txt_console.delete('1.0', tk.END)
        self.txt_console.configure(state="disabled")

    def start_download_thread(self):
        data = LANGUAGES[self.current_lang]
        
        if not self.combo_options.get().strip():
            messagebox.showerror("Error", data["err_format"], parent=self.root)
            return
            
        url = self.entry_url.get()
        if url == data["placeholder"] or not url.strip():
            messagebox.showerror("Error", data["err_valid"], parent=self.root)
            return

        clean_url = url.strip()
            
        self.btn_run.configure(state="disabled", bg="#333333", text="...")
        self.clear_log()
        thread = threading.Thread(target=self.execute_ytdlp, args=(clean_url,))
        thread.daemon = True
        thread.start()

    def execute_ytdlp(self, url):
        idx = self.combo_options.current()
        data = LANGUAGES[self.current_lang]
        self.log(data["logs"][idx])

        cmd = build_ytdlp_command(idx, url)

        try:
            self.root.after(0, lambda: self.progress_bar.configure(value=0))
            returncode = run_download_subprocess(
                cmd,
                log_callback=lambda t: self.root.after(0, lambda msg=t: self.log(msg)),
                speed_callback=lambda v: self.root.after(0, lambda spd=v: self.root.title(f"YT-DLP [Speed: {spd}]")),
                progress_callback=lambda p: self.root.after(0, lambda pct=p: self.progress_bar.configure(value=pct)),
            )

            self.root.after(0, lambda: self.root.title("YT-DLP"))
            if returncode == 0:
                self.root.after(0, lambda: self.progress_bar.configure(value=100))
                self.log(data["msg_success"])
                sound_alert()
            else:
                self.log(f"{data['msg_warn']}{returncode}")
        except Exception as e:
            self.log(f"{data['msg_crit']}{str(e)}")
        self.root.after(0, self.reset_button)

    def reset_button(self):
        data = LANGUAGES[self.current_lang]
        self.btn_run.configure(state="normal", bg="#8b0000", text=data["btn_run"])

    def open_downloads_folder(self):
        idx = self.combo_options.current()
        target_dir = get_target_dir_for_option(idx)
        os.makedirs(target_dir, exist_ok=True)
        os.startfile(target_dir)

    def update_ytdlp_binary(self):
        def run_update():
            data = LANGUAGES[self.current_lang]
            self.root.after(0, self.clear_log)
            self.root.after(0, lambda: self.log(data["msg_update"]))
            try:
                returncode = run_ytdlp_updater(
                    log_callback=lambda msg: self.root.after(0, lambda m=msg: self.log(m))
                )
                if returncode == 0:
                    sound_alert()
            except Exception as e:
                self.log(f"{data['err_update']}{str(e)}")

        thread = threading.Thread(target=run_update, daemon=True)
        thread.start()

    def check_app_updates(self):
        def run_check():
            try:
                has_update, remote_version, installer_url = check_latest_release()
                if has_update and installer_url:
                    self.root.after(0, lambda: self.prompt_app_update(remote_version, installer_url))
            except Exception:
                pass

        thread = threading.Thread(target=run_check, daemon=True)
        thread.start()

    def prompt_app_update(self, remote_version, installer_url):
        ans = messagebox.askyesno("Update Available", f"A new version ({remote_version}) is available.\nDo you want to update now?", parent=self.root)
        if ans:
            self.clear_log()
            self.log("[+] Downloading application update package...")

            def close_for_update():
                self.root.quit()
                self.root.destroy()

            def run_download():
                try:
                    download_and_run_updater(installer_url)
                    self.root.after(0, close_for_update)
                except Exception as e:
                    self.root.after(0, lambda err=str(e): self.log(f"[!] Update failed: {err}"))

            threading.Thread(target=run_download, daemon=True).start()

if __name__ == "__main__":
    multiprocessing.freeze_support()
    root = tk.Tk()
    app = YisukmDownloaderScript(root)
    apply_dark_title_bar(root)
    root.after(1500, app.check_app_updates)
    root.after(100, lambda: load_app_config(root, app))
    root.mainloop()