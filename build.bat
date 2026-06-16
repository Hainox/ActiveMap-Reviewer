@echo off
echo === ActiveMap Reviewer - Sborka exe ===
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [OSHIBKA] Python ne nayden. Ustanovite Python 3.8+
    pause
    exit /b 1
)

echo [INFO] Ustanavlivayu PyInstaller...
python -m pip install pyinstaller --quiet

if exist dist\ActiveMapReviewer.exe del /f /q dist\ActiveMapReviewer.exe
if exist build rmdir /s /q build
if exist ActiveMapReviewer.spec del /f /q ActiveMapReviewer.spec

echo [INFO] Sobirayu exe...
echo.

python -m PyInstaller --onefile --noconsole --name ActiveMapReviewer --add-data "reviewer_html.html;." reviewer.py

if errorlevel 1 (
    echo.
    echo [OSHIBKA] Sborka ne udalas. Smotrite vyvod vyshe.
    pause
    exit /b 1
)

if exist build rmdir /s /q build
if exist ActiveMapReviewer.spec del /f /q ActiveMapReviewer.spec

echo.
echo === Gotovo! ===
echo Fayl: dist\ActiveMapReviewer.exe
echo Zapustite dist\ActiveMapReviewer.exe - brauzer otkroetsya sam.
echo.
pause
