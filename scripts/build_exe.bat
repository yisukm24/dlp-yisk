@echo off
cd /d "%~dp0.."
echo We are finishing it, take a breath...
pyinstaller --clean --onedir --noconsole --name="dlp_yisk" --icon="assets/logo.ico" --add-data "assets/logo.ico;." --add-data "assets/bin;bin" src/Interface.py
echo.
pause
