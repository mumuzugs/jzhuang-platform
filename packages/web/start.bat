@echo off
chcp 65001 >nul
title 集装修前端

echo ========================================
echo   集装修前端启动脚本
echo ========================================
echo.

:: 检查 Node.js
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] Node.js 未安装
    echo 请从 https://nodejs.org/ 下载安装
    pause
    exit /b 1
)

echo [Node.js 版本]
node --version
echo.

:: 检查 pnpm
where pnpm >nul 2>nul
if %errorlevel% neq 0 (
    echo [提示] pnpm 未安装，正在安装...
    npm install -g pnpm
)

:: 安装依赖
echo [1/2] 安装依赖...
if not exist "node_modules" (
    pnpm install
) else (
    echo 依赖已安装，跳过
)

:: 启动开发服务器
echo [2/2] 启动开发服务器...
echo.
echo 访问地址: http://localhost:5173
echo 文档地址: http://localhost:5173/docs (如适用)
echo.
echo 按 Ctrl+C 停止服务
echo.

pnpm dev:h5