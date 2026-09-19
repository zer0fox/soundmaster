@echo off
setlocal
echo =======================================================
echo           SoundMaster Windows Executable Builder
echo =======================================================

echo [1/3] Checking requirements and PyInstaller...
python -m pip install -r requirements.txt pyinstaller

echo [2/3] Generating application icons (ICO and ICNS)...
python generate_icon.py
python -c "from PIL import Image; img = Image.open('soundmaster.png'); img.save('soundmaster.icns', format='ICNS')"

echo [3/3] Building standalone single-file SoundMaster.exe...
python -m PyInstaller --noconfirm --clean --onefile --console --name "SoundMaster" --icon "soundmaster.ico" main.py

echo.
echo =======================================================
if exist "dist\SoundMaster.exe" (
    echo [SUCCESS] SoundMaster.exe has been created in the 'dist' folder!
    echo To use it, simply copy 'dist\SoundMaster.exe' and 'config.json' into any folder.
) else (
    echo [ERROR] Build failed. Please check the logs above.
)
echo =======================================================
pause
