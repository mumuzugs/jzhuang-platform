@echo off
chcp 65001 >nul
title 集装修 - 环境检测与启动

echo.
echo  ================================================
echo     集装修一站式装修平台
echo     环境检测与启动脚本
echo  ================================================
echo.

:: ================================================
:: 第一部分：环境检测
:: ================================================
echo [1/6] 检测 Python...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo   [错误] Python 未安装
    echo   请从 https://www.python.org/downloads/ 下载安装 Python 3.11 或 3.12
    pause
    exit /b 1
)
for /f "delims=" %%i in ('python --version 2^>nul') do echo   %%i

echo.
echo [2/6] 检测 Node.js...
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo   [错误] Node.js 未安装
    echo   请从 https://nodejs.org/ 下载安装
    pause
    exit /b 1
)
for /f "delims=" %%i in ('node --version 2^>nul') do echo   %%i

echo.
echo [3/6] 检测 PostgreSQL 服务...
powershell -Command "Get-Service -Name '*postgres*' -ErrorAction SilentlyContinue" | findstr "Running" >nul
if %errorlevel% neq 0 (
    echo   [警告] PostgreSQL 服务未启动
    echo   请手动启动 PostgreSQL 服务后重试
    echo   或者确保 pg_ctl 或 docker 已运行
    echo.
    powershell -Command "Get-Service -Name '*postgres*' -ErrorAction SilentlyContinue"
    pause
    exit /b 1
) else (
    echo   [OK] PostgreSQL 运行中
)

echo.
echo [4/6] 检测 Redis 服务...
powershell -Command "Get-Service -Name '*redis*' -ErrorAction SilentlyContinue" | findstr "Running" >nul
if %errorlevel% neq 0 (
    echo   [警告] Redis 服务未启动
    echo   请手动启动 Redis 服务后重试
    echo.
    powershell -Command "Get-Service -Name '*redis*' -ErrorAction SilentlyContinue"
    pause
    exit /b 1
) else (
    echo   [OK] Redis 运行中
)

:: ================================================
:: 第二部分：后端准备
:: ================================================
echo.
echo [5/6] 后端环境准备...

cd /d "%~dp0packages\api"
set PYTHONPATH=%cd%

if not exist ".env" (
    echo   创建 .env 文件...
    copy ".env.example" ".env" >nul
    echo.
    echo   [重要] 请编辑 .env 文件，填写以下配置：
    echo   - DATABASE_URL：PostgreSQL 连接串
    echo   - REDIS_URL：Redis 连接串
    echo   - JWT_SECRET：JWT 密钥（随机字符串）
    echo   - ZHIPU_API_KEY：智谱 AI API Key
    echo.
    echo   配置文件位置：%cd%\.env
    echo   编辑完成后按任意键继续...
    notepad ".env"
)

echo   检查 Python 依赖...
pip show fastapi >nul 2>nul
if %errorlevel% neq 0 (
    echo   安装依赖中（首次较慢）...
    pip install -r requirements.txt
)

:: ================================================
:: 第三部分：前端准备
:: ================================================
echo.
echo [6/6] 前端环境准备...
cd /d "%~dp0packages\web"

where pnpm >nul 2>nul
if %errorlevel% neq 0 (
    echo   安装 pnpm...
    npm install -g pnpm
)

if not exist "node_modules" (
    echo   安装前端依赖（首次较慢）...
    pnpm install
)

:: ================================================
:: 第四部分：启动服务
:: ================================================
echo.
echo ================================================
echo   环境检测完成，准备启动服务
echo ================================================
echo.
echo   按 Ctrl+C 停止服务
echo.
echo   后端地址：http://localhost:8000
echo   API 文档：  http://localhost:8000/docs
echo   前端地址：  http://localhost:5173
echo.
echo ================================================
echo.

:: 启动后端（在新窗口）
start "集装修后端" cmd /k "cd /d %~dp0packages\api && title 集装修后端 && set PYTHONPATH=%~dp0packages\api && uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload"

:: 等待后端启动
timeout /t 3 /nobreak >nul

:: 启动前端（在新窗口）
start "集装修前端" cmd /k "cd /d %~dp0packages\web && title 集装修前端 && pnpm dev:h5"

echo   服务已启动！
echo.
pause
