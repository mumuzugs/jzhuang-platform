"""
统一响应格式和错误处理
"""
from typing import Optional, Any
from datetime import datetime


class APIResponse:
    """统一API响应格式"""
    
    @staticmethod
    def success(data: Any = None, message: str = "操作成功", code: int = 0) -> dict:
        """成功响应"""
        return {
            "code": code,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def error(message: str, code: int = -1, details: Any = None) -> dict:
        """错误响应"""
        return {
            "code": code,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def paginated(data: list, total: int, page: int = 1, page_size: int = 20) -> dict:
        """分页响应"""
        return {
            "code": 0,
            "message": "查询成功",
            "data": {
                "list": data,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": total,
                    "total_pages": (total + page_size - 1) // page_size
                }
            },
            "timestamp": datetime.now().isoformat()
        }


class ErrorCode:
    """错误码定义"""
    # 通用错误 (1000-1999)
    SUCCESS = 0
    UNKNOWN_ERROR = 1000
    PARAM_ERROR = 1001
    UNAUTHORIZED = 1002
    FORBIDDEN = 1003
    NOT_FOUND = 1004
    INTERNAL_ERROR = 1005
    
    # 认证错误 (2000-2999)
    TOKEN_INVALID = 2001
    TOKEN_EXPIRED = 2002
    PHONE_ERROR = 2003
    CODE_ERROR = 2004
    CODE_EXPIRED = 2005
    USER_NOT_EXIST = 2006
    USER_DISABLED = 2007
    
    # 业务错误 (3000-3999)
    INSPECTION_NOT_FOUND = 3001
    DESIGN_NOT_FOUND = 3002
    ORDER_NOT_FOUND = 3003
    ORDER_PAID = 3004
    PAYMENT_FAILED = 3005
    PERMISSION_DENIED = 3006


class BizException(Exception):
    """业务异常"""
    
    def __init__(self, message: str, code: int = -1, details: Any = None):
        self.message = message
        self.code = code
        self.details = details
        super().__init__(message)
    
    def to_dict(self) -> dict:
        return APIResponse.error(self.message, self.code, self.details)
