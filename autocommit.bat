@echo off
setlocal enabledelayedexpansion

title Auto Git Committer
echo Starting auto-commit script...

REM Ждем 1 минуту после загрузки ПК
echo Waiting 60 seconds after system startup...
timeout /t 60 /nobreak >nul

REM Создаем папку logs если её нет
if not exist "logs" (
    echo Creating logs directory...
    mkdir logs
)

REM Создаем файл логов с текущей датой и временем
echo PC started at: %date% %time% >> logs\system.log
echo Log entry created at: %date% %time% >> logs\system.log
echo Log file updated: logs\system.log

REM Переходим в корневую папку скрипта
cd /d "%~dp0"
echo Current directory: %cd%

REM Проверяем наличие .git папки
if not exist ".git" (
    echo ERROR: .git folder not found!
    echo Script will exit in 10 seconds...
    timeout /t 10 /nobreak >nul
    exit /b 1
)

REM Выполняем git коммит
echo Performing git operations...
git add .
if !errorlevel! neq 0 (
    echo ERROR: git add failed!
    pause
    exit /b 1
)

git commit -m "Auto-commit: System log update %date% %time%"
if !errorlevel! neq 0 (
    echo WARNING: git commit failed or no changes to commit
) else (
    echo Git commit completed successfully!
)

echo.
echo Script execution finished!
echo Press any key to close...
pause >nul