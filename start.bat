@echo off
title ClipVidio AI Launcher

:: Change directory safely to current script folder
cd /d "%~dp0"

echo ================================================================
echo             ClipVidio AI -- Pre-flight Check dan Launch
echo ================================================================
echo.

:: ------------------------------------------------------------------
:: 1. Check Node.js and NPM Installation
:: ------------------------------------------------------------------
echo [1/5] Memeriksa Node.js dan NPM...
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ================================================================
    echo [ERROR] Node.js TIDAK DITEMUKAN di sistem Anda
    echo ================================================================
    echo ClipVidio AI membutuhkan Node.js versi 18 atau lebih baru.
    echo Silakan install melalui:
    echo   - Website : https://nodejs.org/
    echo   - Terminal: winget install OpenJS.NodeJS
    echo.
    pause
    exit /b 1
)

where npm >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ================================================================
    echo [ERROR] NPM tidak ditemukan di sistem PATH
    echo ================================================================
    echo Pastikan opsi Add to PATH tercentang saat instalasi Node.js.
    echo.
    pause
    exit /b 1
)
echo       [OK] Node.js dan NPM terdeteksi.

:: ------------------------------------------------------------------
:: 2. Check Node.js Dependencies (node_modules)
:: ------------------------------------------------------------------
echo [2/5] Memeriksa library Frontend...
if not exist "%~dp0node_modules" (
    echo.
    echo [INFO] Folder node_modules belum ada.
    echo        Memulai instalasi library Frontend otomatis via npm install...
    echo.
    call npm install
    if %errorlevel% neq 0 (
        echo.
        echo ================================================================
        echo [ERROR] Gagal menginstall library Frontend via npm install
        echo ================================================================
        echo Periksa koneksi internet Anda atau coba jalankan: npm install
        echo.
        pause
        exit /b 1
    )
    echo       [OK] Library Frontend berhasil diinstall.
) else (
    echo       [OK] Folder node_modules ditemukan.
)

:: ------------------------------------------------------------------
:: 3. Check Python Installation
:: ------------------------------------------------------------------
echo [3/5] Memeriksa Python...
set "PY_CMD="
where python >nul 2>&1
if %errorlevel% equ 0 (
    set "PY_CMD=python"
) else (
    where py >nul 2>&1
    if %errorlevel% equ 0 (
        set "PY_CMD=py"
    )
)

if "%PY_CMD%"=="" (
    echo.
    echo ================================================================
    echo [ERROR] Python 3 TIDAK DITEMUKAN di sistem Anda
    echo ================================================================
    echo Backend ClipVidio AI membutuhkan Python versi 3.10 atau lebih baru.
    echo Silakan install melalui:
    echo   - Website : https://www.python.org/downloads/
    echo   - Catatan : Centang opsi Add Python to PATH saat install
    echo   - Terminal: winget install Python.Python.3.11
    echo.
    pause
    exit /b 1
)
echo       [OK] Python terdeteksi: %PY_CMD%

:: ------------------------------------------------------------------
:: 4. Check dan Setup Python Virtual Environment dan Dependencies
:: ------------------------------------------------------------------
echo [4/5] Memeriksa Python Virtual Environment dan Library Backend...

set "VENV_PY="
if exist "%~dp0.venv\Scripts\python.exe" (
    set "VENV_PY=%~dp0.venv\Scripts\python.exe"
    echo       [OK] Virtual environment lokal .venv ditemukan.
) else if exist "%~dp0venv\Scripts\python.exe" (
    set "VENV_PY=%~dp0venv\Scripts\python.exe"
    echo       [OK] Virtual environment lokal venv ditemukan.
) else (
    echo [INFO] Virtual environment Python belum dibuat.
    echo        Membuat virtual environment otomatis di .venv...
    %PY_CMD% -m venv "%~dp0.venv"
    if %errorlevel% neq 0 (
        echo [WARNING] Gagal membuat venv otomatis. Menggunakan Python sistem.
        set "VENV_PY=%PY_CMD%"
    ) else (
        set "VENV_PY=%~dp0.venv\Scripts\python.exe"
        echo       [OK] Virtual environment berhasil dibuat.
    )
)

set "REQ_FILE=%~dp0backend\requirements.txt"
if not exist "%REQ_FILE%" (
    set "REQ_FILE=%~dp0requirements.txt"
)

:: Test whether core backend packages (fastapi, uvicorn) exist
"%VENV_PY%" -c "import fastapi, uvicorn" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [INFO] Dependensi Python backend belum lengkap.
    echo        Menginstall library backend dari %REQ_FILE%...
    echo.
    "%VENV_PY%" -m pip install -r "%REQ_FILE%"
    if %errorlevel% neq 0 (
        echo.
        echo ================================================================
        echo [ERROR] Gagal menginstall dependensi backend Python
        echo ================================================================
        echo Silakan coba jalankan manual: pip install -r backend/requirements.txt
        echo.
        pause
        exit /b 1
    )
    echo       [OK] Dependensi Python berhasil diinstall.
) else (
    echo       [OK] Dependensi Python terverifikasi: fastapi dan uvicorn siap.
)

:: ------------------------------------------------------------------
:: 5. Check Media Processing Tools (FFmpeg dan yt-dlp)
:: ------------------------------------------------------------------
echo [5/5] Memeriksa utilitas media FFmpeg dan yt-dlp...
where ffmpeg >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ----------------------------------------------------------------
    echo [PERINGATAN] FFmpeg TIDAK DITEMUKAN di sistem PATH.
    echo Rendering server-side mungkin gagal tanpa FFmpeg.
    echo Anda dapat menginstallnya via PowerShell: winget install Gyan.FFmpeg
    echo ----------------------------------------------------------------
    echo.
) else (
    echo       [OK] FFmpeg terdeteksi.
)

where yt-dlp >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ----------------------------------------------------------------
    echo [PERINGATAN] yt-dlp TIDAK DITEMUKAN di sistem PATH.
    echo Pengunduhan video YouTube membutuhkan yt-dlp.
    echo Anda dapat menginstallnya via PowerShell: winget install yt-dlp.yt-dlp
    echo ----------------------------------------------------------------
    echo.
) else (
    echo       [OK] yt-dlp terdeteksi.
)

:: ------------------------------------------------------------------
:: 6. Launch Application
:: ------------------------------------------------------------------
echo.
echo ================================================================
echo   Seluruh pemeriksaan selesai. Menjalankan ClipVidio AI...
echo   Frontend : http://localhost:5173
echo   Backend  : http://localhost:8000
echo ================================================================
echo.

title ClipVidio AI Server Running
call npm run dev

echo.
echo ================================================================
echo Aplikasi telah berhenti.
echo ================================================================
pause
