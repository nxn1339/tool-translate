@echo off
title AI Video Dubber

rem ==================== Setup ====================
if not exist "%~dp0ffmpeg\ffmpeg.exe" (
    echo [Setup] ffmpeg not found, invoking setup script...
    powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup_ffmpeg.ps1"
) else (
    echo [Setup] ffmpeg already present.
)
rem Add project ffmpeg folder to PATH so Whisper can find it
set "PATH=%~dp0ffmpeg;%PATH%"

rem ==================== Launch Application ====================
echo ====================================================
echo          AI Video Dubber - Web Local App
echo ====================================================
echo.

echo [Launch] Checking Python...
where python <nul 2>&1
if %errorlevel% neq 0 (
    echo [Error] Python is not installed or not added to your system PATH.
    echo Please install Python 3.8+ first before running this application.
    pause
    exit /b 1
)

echo [Launch] Starting run.py script...
python "%~dp0run.py"

if %errorlevel% neq 0 (
    echo.
    echo [Error] An error occurred while running the application.
    pause
)
