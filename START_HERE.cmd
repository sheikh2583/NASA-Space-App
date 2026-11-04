@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\launch.ps1" %*
set "result=%errorlevel%"
echo.
if not "%result%"=="0" echo Workflow failed. Review the error above and results\logs\.
pause
exit /b %result%
