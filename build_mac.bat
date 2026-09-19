:; # macOS / Linux bash execution section
:; echo "======================================================="
:; echo "           SoundMaster macOS Builder"
:; echo "======================================================="
:; echo "[1/3] Checking requirements and PyInstaller..."
:; python3 -m pip install -r requirements.txt pyinstaller
:; echo "[2/3] Generating application icon (ICNS)..."
:; python3 generate_icon.py
:; python3 -c "from PIL import Image; img = Image.open('soundmaster.png'); img.save('soundmaster.icns', format='ICNS')"
:; echo "[3/3] Building standalone macOS binary and App bundle..."
:; python3 -m PyInstaller --noconfirm --clean --onefile --name "SoundMaster" --icon "soundmaster.icns" main.py
:; python3 -m PyInstaller --noconfirm --clean --windowed --name "SoundMasterApp" --icon "soundmaster.icns" main.py
:; echo ""
:; echo "======================================================="
:; echo "[SUCCESS] Build complete! Outputs created in dist/"
:; echo "======================================================="
:; exit 0

@echo off
rem Windows execution section if someone double clicks build_mac.bat on Windows
echo =======================================================
echo           SoundMaster macOS Builder
echo =======================================================
echo.
echo [NOTE] macOS binaries (.app and Mach-O binaries) must be compiled
echo on a macOS system because PyInstaller builds native binaries for
echo the operating system it runs on.
echo.
echo If you have macOS, you can run this file directly in terminal:
echo   bash build_mac.bat
echo   (or ./build_mac.command)
echo.
pause
