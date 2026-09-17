@echo off
cd /d "%~dp0"

:: Check if dependencies are installed
python -c "import keyboard, pycaw, comtypes" 2>nul
if %errorlevel% neq 0 (
    echo [SoundMaster] Installing required dependencies...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install dependencies. Please ensure Python and pip are installed.
        pause
        exit /b %errorlevel%
    )
    echo [SoundMaster] Dependencies installed successfully!
    echo.
)

python main.py
pause
