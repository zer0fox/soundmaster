#!/usr/bin/env bash
cd -- "$(dirname "$0")"

echo "======================================================="
echo "           SoundMaster macOS Builder"
echo "======================================================="

echo "[1/3] Checking requirements and PyInstaller..."
python3 -m pip install -r requirements.txt pyinstaller

echo "[2/3] Generating application icon (ICNS)..."
python3 generate_icon.py
python3 -c "from PIL import Image; img = Image.open('soundmaster.png'); img.save('soundmaster.icns', format='ICNS')"

echo "[3/3] Building standalone macOS binary and App bundle..."
# 1. Standalone single-file CLI executable (place config.json next to it)
python3 -m PyInstaller --noconfirm --clean --onefile --name "SoundMaster" --icon "soundmaster.icns" main.py

# 2. Standalone .app bundle
python3 -m PyInstaller --noconfirm --clean --windowed --name "SoundMasterApp" --icon "soundmaster.icns" main.py

echo ""
echo "======================================================="
echo "[SUCCESS] Build complete!"
echo "Outputs created in dist/:"
echo "  1. dist/SoundMaster (Standalone executable - place next to config.json)"
echo "  2. dist/SoundMasterApp.app (macOS Application bundle)"
echo "======================================================="
read -p "Press Enter to close..."
