"""
中间件
"""
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from src.core.logging import Logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    
    async def dispatch(self, request: Request, call_next):
        # 记录请求开始时间
        start_time = time.time()
        
        # 处理请求
        response = await call_next(request)
        
        # 计算处理时间
        duration_ms = int((time.time() - start_time) * 1000)
        
        # 记录日志
        logger = Logger.api_logger()
        logger.info(
            f"{request.method} {request.url.path} | "
            f"status={response.status_code} | "
            f"duration={duration_ms}ms | "
            f"client={request.client.host if request.client else 'unknown'}"
        )
        
        # 添加处理时间头
        response.headers["X-Process-Time"] = str(duration_ms)
        
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """错误处理中间件"""
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger = Logger.get_logger('error')
            logger.error(f"Unhandled error: {str(e)}", exc_info=True)
            
            return Response(
                content=f'{{"code": -1, "message": "服务器内部错误"}}',
                status_code=500,
                media_type="application/json"
            )


class CORSMiddleware(BaseHTTPMiddleware):
    """CORS中间件"""
    
    def __init__(self, app: ASGIApp, allowed_origins: list = None):
        super().__init__(app)
        self.allowed_origins = allowed_origins or ["*"]
    
    async def dispatch(self, request: Request, call_next):
        # 处理 OPTIONS 预检请求
        if request.method == "OPTIONS":
            return Response(
                status_code=200,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "*",
                    "Access-Control-Allow-Headers": "*",
                }
            )
        
        response = await call_next(request)
        
        # 添加 CORS 头
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """限流中间件（简易版）"""
    
    def __init__(self, app: ASGIApp, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.request_counts = {}
    
    async def dispatch(self, request: Request, call_next):
        # 获取客户端标识
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # 清理过期记录
        self.request_counts = {
            k: v for k, v in self.request_counts.items()
            if current_time - v[0] < self.window_seconds
        }
        
        # 检查限流
        if client_ip in self.request_counts:
            count, start_time = self.request_counts[client_ip]
            if current_time - start_time < self.window_seconds:
                if count >= self.max_requests:
                    return Response(
                        content='{"code": 429, "message": "请求过于频繁"}',
                        status_code=429,
                        media_type="application/json"
                    )
                self.request_counts[client_ip] = (count + 1, start_time)
        else:
            self.request_counts[client_ip] = (1, current_time)
        
        response = await call_next(request)
        return response
