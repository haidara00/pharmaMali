@echo off
echo 🚀 PharmaGestion Production Deployment
echo ======================================
echo.

:: Check admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ Please run as Administrator!
    echo 🔒 Right-click → "Run as administrator"
    pause
    exit /b 1
)

echo 📦 Step 1: Checking NSSM...
if not exist "nssm\nssm.exe" (
    echo 📥 Downloading NSSM...
    mkdir nssm 2>nul
    powershell -Command "Invoke-WebRequest -Uri 'https://nssm.cc/ci/nssm-2.24-101-g897c7ad.zip' -OutFile 'nssm.zip'"
    if exist nssm.zip (
        powershell -Command "Expand-Archive -Path 'nssm.zip' -DestinationPath 'nssm-temp' -Force"
        move "nssm-temp\nssm-2.24-101-g897c7ad\win64\nssm.exe" "nssm\nssm64.exe"
        move "nssm-temp\nssm-2.24-101-g897c7ad\win32\nssm.exe" "nssm\nssm.exe"
        rmdir /s /q nssm-temp 2>nul
        del nssm.zip 2>nul
        echo ✅ NSSM downloaded and extracted
    ) else (
        echo ❌ Failed to download NSSM
        echo 📥 Please manually download from: https://nssm.cc/download
        echo 📁 Extract nssm.exe to nssm\ folder
        pause
        exit /b 1
    )
)

echo.
echo 🐍 Step 2: Installing Python dependencies...
pip install -r requirements.txt

echo.
echo 🗃️ Step 3: Setting up database...
python manage.py makemigrations
python manage.py migrate

echo.
echo 📊 Step 4: Creating admin user...
python manage.py createsuperuser --username=admin --email=admin@pharmagestion.ml --noinput 2>nul && (
    echo ⚠️ Default admin created: username=admin, password=admin
    echo 💡 Change password after first login!
) || echo ℹ️ Superuser already exists or creation skipped

echo.
echo 🎨 Step 5: Collecting static files...
python manage.py collectstatic --noinput

echo.
echo 🛠️ Step 6: Installing Windows Service...
call install_service.bat

echo.
echo 🎉 DEPLOYMENT COMPLETE!
echo.
echo 📍 Access: http://localhost:8000
echo 👤 Admin: admin / admin
echo 🛠️ Manage: manage_service.bat
echo.
pause