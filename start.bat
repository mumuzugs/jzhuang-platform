@echo off
chcp 65001 >nul
title 集装修全栈启动

echo ========================================
echo   集装修项目启动（前后端）
echo ========================================
echo.

echo [启动后端]
start "集装修后端" cmd /k "cd /d %~dp0packages\api && call start.bat"

echo [启动前端]
start "集装修前端" cmd /k "cd /d %~dp0packages\web && call start.bat"

echo.
echo 已启动两个窗口：
echo   1. 后端 - http://localhost:8000
echo   2. 前端 - http://localhost:5173
echo.
pause