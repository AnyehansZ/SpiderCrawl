@echo off
REM build.bat - Build SpiderCrawl Windows exe

echo ========================================
echo SpiderCrawl - PyInstaller Build Script
echo ========================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.9+
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del *.spec

REM Run PyInstaller
echo Building exe...
pyinstaller --onefile ^
    --windowed ^
    --name "SpiderCrawl" ^
    --icon=icon.ico ^
    --add-data "app:app" ^
    --collect-all requests ^
    --collect-all bs4 ^
    --collect-all lxml ^
    --hidden-import=app.manager ^
    --hidden-import=app.extension_manager ^
    main.py

if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build successful!
echo Exe location: dist\SpiderCrawl.exe
echo ========================================
pause