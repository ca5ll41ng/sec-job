@echo off
chcp 65001 >nul
title 安全面试刷题
cd /d %~dp0backend
echo.
echo   安全面试刷题服务启动中...
echo   本机访问:   http://127.0.0.1:8000
echo   手机访问:   http://(本机IP):8000  （需同一局域网）
echo   按 Ctrl+C 停止服务
echo.
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
pause
