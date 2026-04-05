"""
日志模块
"""
import logging
import sys
from datetime import datetime
from typing import Optional


class Logger:
    """统一日志管理"""
    
    _loggers = {}
    
    @classmethod
    def get_logger(cls, name: str, level: int = logging.INFO) -> logging.Logger:
        """获取日志器"""
        if name in cls._loggers:
            return cls._loggers[name]
        
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        # 格式化
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        cls._loggers[name] = logger
        
        return logger
    
    @classmethod
    def api_logger(cls):
        """API日志器"""
        return cls.get_logger('api')
    
    @classmethod
    def auth_logger(cls):
        """认证日志器"""
        return cls.get_logger('auth')
    
    @classmethod
    def payment_logger(cls):
        """支付日志器"""
        return cls.get_logger('payment')
    
    @classmethod
    def ai_logger(cls):
        """AI日志器"""
        return cls.get_logger('ai')


def log_request(endpoint: str, method: str, user_id: Optional[str] = None, 
                params: dict = None, duration_ms: int = 0):
    """记录API请求"""
    logger = Logger.api_logger()
    user_info = f"user={user_id}" if user_id else "anonymous"
    logger.info(f"[API] {method} {endpoint} | {user_info} | {duration_ms}ms")


def log_auth(phone: str, success: bool, reason: str = None):
    """记录认证日志"""
    logger = Logger.auth_logger()
    status = "SUCCESS" if success else "FAILED"
    msg = f"[AUTH] {phone} | {status}"
    if reason:
        msg += f" | {reason}"
    if success:
        logger.info(msg)
    else:
        logger.warning(msg)


def log_payment(order_no: str, action: str, status: str, amount: int = 0):
    """记录支付日志"""
    logger = Logger.payment_logger()
    logger.info(f"[PAYMENT] {action} | order={order_no} | status={status} | amount={amount/100:.2f}元")


def log_ai(feature: str, duration_ms: int, success: bool, 
            accuracy: int = 0, error: str = None):
    """记录AI调用日志"""
    logger = Logger.ai_logger()
    status = "SUCCESS" if success else "FAILED"
    msg = f"[AI] {feature} | {status} | {duration_ms}ms"
    if accuracy:
        msg += f" | accuracy={accuracy}%"
    if error:
        msg += f" | error={error}"
    if success:
        logger.info(msg)
    else:
        logger.warning(msg)
