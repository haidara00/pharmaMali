@echo off
setlocal enabledelayedexpansion

cd /d %~dp0

:: Detect architecture and NSSM
if "%PROCESSOR_ARCHITECTURE%"=="AMD64" (
    set NSSM_EXE=nssm64.exe
) else (
    set NSSM_EXE=nssm.exe
)

if not exist "nssm\%NSSM_EXE%" (
    echo ❌ NSSM not found in nssm\ folder
    pause
    exit /b 1
)

echo.
echo 🛠️ PharmaGestion Service Manager
echo ================================
echo 1. Start Service
echo 2. Stop Service  
echo 3. Restart Service
echo 4. Service Status
echo 5. View Logs
echo 6. Open in Browser
echo 7. Open Service Manager
echo 8. Uninstall Service
echo.
set /p choice="Choose option [1-8]: "

if "%choice%"=="1" (
    "nssm\%NSSM_EXE%" start PharmaGestion
    echo ✅ Service started
) else if "%choice%"=="2" (
    "nssm\%NSSM_EXE%" stop PharmaGestion
    echo ✅ Service stopped
) else if "%choice%"=="3" (
    "nssm\%NSSM_EXE%" stop PharmaGestion
    timeout /t 2 /nobreak >nul
    "nssm\%NSSM_EXE%" start PharmaGestion
    echo ✅ Service restarted
) else if "%choice%"=="4" (
    "nssm\%NSSM_EXE%" status PharmaGestion
) else if "%choice%"=="5" (
    if exist pharmagestion.log (
        notepad pharmagestion.log
    ) else (
        echo No log file found
    )
) else if "%choice%"=="6" (
    start http://localhost:8000
    echo 🌐 Browser opened
) else if "%choice%"=="7" (
    services.msc
    echo 🔧 Service Manager opened
) else if "%choice%"=="8" (
    echo ❗ This will remove PharmaGestion service
    set /p confirm="Are you sure? (y/N): "
    if /i "!confirm!"=="y" (
        "nssm\%NSSM_EXE%" stop PharmaGestion
        timeout /t 2 /nobreak >nul
        "nssm\%NSSM_EXE%" remove PharmaGestion confirm
        echo ✅ Service uninstalled
    )
) else (
    echo ❌ Invalid choice
)

echo.
pause