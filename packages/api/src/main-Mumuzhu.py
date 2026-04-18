"""
集装修 - FastAPI 应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware as FastAPICORSMiddleware
from contextlib import asynccontextmanager

from .core.config import settings
from src.core.middleware import RequestLoggingMiddleware, ErrorHandlingMiddleware, RateLimitMiddleware
from src.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    print(f"集装修API服务启动 | 版本: {settings.APP_VERSION}")
    yield
    # 关闭时
    print("集装修API服务关闭")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="集装修一站式装修服务平台API - 国内首个AI全链路赋能装修平台",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS配置
app.add_middleware(
    FastAPICORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册中间件
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)

# 注册路由
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "集装修一站式装修服务平台API",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@app.get("/info")
async def info():
    """服务信息"""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENV,
        "debug": settings.DEBUG,
        "features": [
            "AI验房（8类问题识别）",
            "AI设计+预算联动",
            "云监工+进度识别",
            "施工计划管理",
            "支付模块"
        ]
    }
