@echo off
chcp 65001 >nul
echo ╔══════════════════════════════════════════════╗
echo ║     ActiveMap Reviewer — Сборка .exe         ║
echo ╚══════════════════════════════════════════════╝
echo.

:: Проверяем Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден. Установите Python 3.8+ с python.org
    pause
    exit /b 1
)

:: Устанавливаем PyInstaller если нет
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [INFO] Устанавливаю PyInstaller...
    pip install pyinstaller --quiet
)

:: Удаляем старую сборку
if exist dist\ActiveMapReviewer.exe (
    echo [INFO] Удаляю старый exe...
    del /f /q dist\ActiveMapReviewer.exe
)
if exist build (rmdir /s /q build)

echo [INFO] Собираю exe...
echo.

pyinstaller ^
    --onefile ^
    --noconsole ^
    --name ActiveMapReviewer ^
    --add-data "reviewer_html.html;." ^
    reviewer.py

if errorlevel 1 (
    echo.
    echo [ОШИБКА] Сборка не удалась. Проверьте вывод выше.
    pause
    exit /b 1
)

:: Очищаем временные файлы PyInstaller
if exist build (rmdir /s /q build)
if exist ActiveMapReviewer.spec (del /f /q ActiveMapReviewer.spec)

echo.
echo ╔══════════════════════════════════════════════╗
echo ║  Готово! Файл: dist\ActiveMapReviewer.exe    ║
echo ║                                              ║
echo ║  Запустите dist\ActiveMapReviewer.exe        ║
echo ║  Браузер откроется автоматически             ║
echo ╚══════════════════════════════════════════════╝
echo.
pause
