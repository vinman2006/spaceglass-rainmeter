@echo off
REM ============================================================================
REM SPACEGLASS — WINDOWS 11 INSTALLER WRAPPER (Installer/install.bat)
REM Invokes the PowerShell installer with ExecutionPolicy Bypass for convenience.
REM ============================================================================
setlocal
echo ============================================================================
echo   SPACEGLASS — Desktop Widget System Installer for Windows 11
echo   Your Universe. Your Schedule.
echo ============================================================================
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] SpaceGlass installation encountered an issue. Review the messages above.
    pause
    exit /b %ERRORLEVEL%
)
echo.
pause
