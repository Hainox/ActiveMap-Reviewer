@echo off
chcp 65001 >nul
echo === ActiveMap Reviewer — Сборка exe ===
echo.

:: ── Найти Python с PyInstaller ───────────────────────────────────────────────
set PYEXE=
python -m PyInstaller --version >nul 2>&1
if not errorlevel 1 set PYEXE=python

if "%PYEXE%"=="" (
    C:\Python314\python.exe -m PyInstaller --version >nul 2>&1
    if not errorlevel 1 set PYEXE=C:\Python314\python.exe
)

if "%PYEXE%"=="" (
    echo [ОШИБКА] PyInstaller не найден. Установите:
    echo   python -m pip install pyinstaller
    pause & exit /b 1
)
echo [INFO] Используется: %PYEXE%

:: ── Остановить работающий процесс ─────────────────────────────────────────────
taskkill /F /IM ActiveMapReviewer.exe >nul 2>&1
timeout /t 2 /nobreak >nul

:: ── Очистить старые файлы ─────────────────────────────────────────────────────
if exist dist\_tmp     rmdir /s /q dist\_tmp
if exist dist\ActiveMapReviewer.exe del /f /q dist\ActiveMapReviewer.exe
if exist build         rmdir /s /q build
if exist ActiveMapReviewer.spec del /f /q ActiveMapReviewer.spec

:: ── Сборка во временную папку ─────────────────────────────────────────────────
echo [INFO] Собираю exe...
echo.
%PYEXE% -m PyInstaller --onefile --noconsole --name ActiveMapReviewer --add-data "reviewer_html.html;." --distpath dist\_tmp reviewer.py

if errorlevel 1 (
    echo.
    echo [ОШИБКА] Сборка не удалась. Смотрите вывод выше.
    pause & exit /b 1
)

:: ── Переместить результат в dist\ ─────────────────────────────────────────────
move /Y dist\_tmp\ActiveMapReviewer.exe dist\ActiveMapReviewer.exe >nul
if errorlevel 1 (
    echo.
    echo [ОШИБКА] Не удалось переместить exe — возможно, файл занят другим процессом.
    echo Собранный файл остался в dist\_tmp\ActiveMapReviewer.exe
    pause & exit /b 1
)
rmdir /s /q dist\_tmp

:: ── Очистить мусор сборки ─────────────────────────────────────────────────────
if exist build         rmdir /s /q build
if exist ActiveMapReviewer.spec del /f /q ActiveMapReviewer.spec

echo.
echo === Готово! ===
echo Файл: dist\ActiveMapReviewer.exe
for %%F in (dist\ActiveMapReviewer.exe) do echo Размер: %%~zF байт
echo.
echo Запустите dist\ActiveMapReviewer.exe — браузер откроется автоматически.
echo.
pause
