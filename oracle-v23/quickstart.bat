@echo off
echo ================================================
echo    Oracle v2.3 Deployment System
echo    Quick Start Launcher (Windows)
echo ================================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found. Please install Python 3.7+
    pause
    exit /b 1
)

echo [OK] Python detected
echo.
echo Choose deployment method:
echo   [1] Direct Browser (default)
echo   [2] Python HTTP Server
echo.
set /p choice="Selection [1-2]: "

if "%choice%"=="1" goto browser
if "%choice%"=="2" goto server
if "%choice%"=="" goto browser

echo Invalid selection
pause
exit /b 1

:browser
echo.
echo Opening in browser...
start index.html
goto end

:server
echo.
echo Starting Python server...
python server.py
goto end

:end
pause
