@echo off
chcp 65001 >nul
title 集装修后端服务

echo ========================================
echo   集装修后端启动脚本
echo ========================================
echo.

:: 检查 Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] Python 未安装，请先安装 Python 3.11 或 3.12
    pause
    exit /b 1
)

python --version | findstr "3.11 3.12" >nul
if %errorlevel% neq 0 (
    echo [警告] 建议使用 Python 3.11 或 3.12，当前版本可能有兼容性问题
)

:: 检查依赖
echo [1/4] 检查依赖...
pip show fastapi >nul 2>nul
if %errorlevel% neq 0 (
    echo [警告] 依赖未安装，正在安装...
    pip install -r requirements.txt
)

:: 检查 PostgreSQL
echo [2/4] 检查 PostgreSQL...
powershell -Command "Get-Service -Name '*postgres*' -ErrorAction SilentlyContinue" | findstr "Running" >nul
if %errorlevel% neq 0 (
    echo [警告] PostgreSQL 服务未启动，请确保数据库已启动
)

:: 检查 Redis
echo [3/4] 检查 Redis...
powershell -Command "Get-Service -Name '*redis*' -ErrorAction SilentlyContinue" | findstr "Running" >nul
if %errorlevel% neq 0 (
    echo [警告] Redis 服务未启动，请确保 Redis 已启动
)

:: 设置环境变量
echo [4/4] 启动服务...
set PYTHONPATH=%~dp0

:: 检查 .env 文件
if not exist "%~dp0.env" (
    echo [提示] .env 文件不存在，正在创建...
    copy "%~dp0.env.example" "%~dp0.env"
    echo [提示] 请编辑 .env 文件，填写数据库和 API 配置
    notepad "%~dp0.env"
)

:: 启动 uvicorn
echo.
echo 启动服务: http://localhost:8000
echo 文档地址: http://localhost:8000/docs
echo.
echo 按 Ctrl+C 停止服务
echo.

uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload