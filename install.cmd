@echo off
setlocal
echo [INFO] 正在启动 pp-app-store Windows 安装向导...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] 安装执行失败，错误代码: %ERRORLEVEL%
    pause
    exit /b %ERRORLEVEL%
)
endlocal
