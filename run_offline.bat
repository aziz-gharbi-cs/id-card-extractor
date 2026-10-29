@echo off
title "ID Card and Passport Extractor"
cd /d "%~dp0"
echo Starting ID Card and Passport Extractor offline...
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
set GRADIO_ANALYTICS_ENABLED=False

if exist "C:\Users\azizg\AppData\Local\Programs\Python\Python313\python.exe" (
    "C:\Users\azizg\AppData\Local\Programs\Python\Python313\python.exe" gradio_app.py
) else (
    python gradio_app.py
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] The application exited with an error.
)
pause
