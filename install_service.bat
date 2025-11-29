@echo off
setlocal enabledelayedexpansion

echo 🚀 Installing PharmaGestion as Windows Service...
cd /d %~dp0

:: Detect system architecture
if "%PROCESSOR_ARCHITECTURE%"=="AMD64" (
    set NSSM_EXE=nssm64.exe
) else (
    set NSSM_EXE=nssm.exe
)

:: Check if NSSM exists
if not exist "nssm\%NSSM_EXE%" (
    echo ❌ NSSM not found! Please download and place in nssm\ folder
    echo 📥 Download from: https://nssm.cc/download
    pause
    exit /b 1
)

:: Find Python executable
for %%I in (python.exe) do set "PYTHON_EXE=%%~$PATH:I"
if "%PYTHON_EXE%"=="" (
    echo ❌ Python not found in PATH!
    echo 📍 Please install Python or add to PATH
    pause
    exit /b 1
)

echo.
echo 🔍 Detected:
echo    Python: %PYTHON_EXE%
echo    Architecture: %PROCESSOR_ARCHITECTURE%
echo    NSSM: nssm\%NSSM_EXE%

echo.
echo 📦 Creating PharmaGestion service...
"nssm\%NSSM_EXE%" install PharmaGestion "%PYTHON_EXE%" "%~dp0waitress_server.py"

:: Configure service
"nssm\%NSSM_EXE%" set PharmaGestion Description "PharmaGestion - Système de Gestion Pharmaceutique"
"nssm\%NSSM_EXE%" set PharmaGestion DisplayName "PharmaGestion"
"nssm\%NSSM_EXE%" set PharmaGestion Start SERVICE_AUTO_START
"nssm\%NSSM_EXE%" set PharmaGestion AppDirectory "%~dp0"
"nssm\%NSSM_EXE%" set PharmaGestion AppStdout "%~dp0pharmagestion.log"
"nssm\%NSSM_EXE%" set PharmaGestion AppStderr "%~dp0pharmagestion_error.log"
"nssm\%NSSM_EXE%" set PharmaGestion AppRotateFiles 1
"nssm\%NSSM_EXE%" set PharmaGestion AppRotateOnline 1
"nssm\%NSSM_EXE%" set PharmaGestion AppRotateSeconds 86400
"nssm\%NSSM_EXE%" set PharmaGestion AppRotateBytes 1048576

echo.
echo 🏁 Starting PharmaGestion service...
"nssm\%NSSM_EXE%" start PharmaGestion

echo.
echo ✅ PharmaGestion installed successfully!
echo 📍 Access: http://localhost:8000
echo 📋 Logs: pharmagestion.log
echo 🛠️  Manage: services.msc or use manage_service.bat
echo.

timeout /t 3 /nobreak >nul

:: Test if service is running
"nssm\%NSSM_EXE%" status PharmaGestion | find "SERVICE_RUNNING" >nul
if %errorlevel% equ 0 (
    echo 🎉 Service is RUNNING! Opening browser...
    start http://localhost:8000
) else (
    echo ❗ Service installed but not running. Check pharmagestion_error.log
)

pause