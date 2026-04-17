"""
应用配置
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用信息
    APP_NAME: str = "集装修"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENV: str = "production"
    
    # 数据库配置
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/jzhuang"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: str = ""
    
    # JWT配置
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 10080
    
    # AI服务配置
    ZHIPU_API_KEY: str = ""
    ZHIPU_VISION_MODEL: str = "glm-4v-flash"
    ALIYUN_ACCESS_KEY_ID: str = ""
    ALIYUN_ACCESS_KEY_SECRET: str = ""
    TENCENT_SECRET_ID: str = ""
    TENCENT_SECRET_KEY: str = ""
    
    # 微信支付配置
    WECHAT_MCH_ID: str = ""
    WECHAT_API_KEY: str = ""
    WECHAT_APP_ID: str = ""
    
    # Sentry配置
    SENTRY_DSN: str = ""
    
    # CORS配置
    CORS_ALLOW_ORIGINS: str = "*"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


settings = get_settings()
