from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    """全局配置 - 自动读取.env环境变量"""

    # 数据库模式
    DB_TYPE: str = "sqlite"
    SQLITE_PATH: str = "./data.db"

    # MySQL / RDS
    RDS_HOST: Optional[str] = None
    RDS_PORT: int = 3306
    RDS_USER: Optional[str] = None
    RDS_PWD: Optional[str] = None
    RDS_DB: Optional[str] = None

    # JWT
    JWT_SECRET_KEY: str = "change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440

    # 初始管理员
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "Admin123!"

    # OSS（预留）
    OSS_ENABLED: bool = False
    OSS_ENDPOINT: Optional[str] = None
    OSS_BUCKET: Optional[str] = None
    OSS_ACCESS_KEY_ID: Optional[str] = None
    OSS_ACCESS_KEY_SECRET: Optional[str] = None

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173"

    # 路径
    LOG_DIR: str = "./logs"
    EXCEL_STORAGE_DIR: str = "./reports"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

# 创建必要目录
os.makedirs(settings.LOG_DIR, exist_ok=True)
os.makedirs(settings.EXCEL_STORAGE_DIR, exist_ok=True)

# CORS 白名单列表
CORS_ORIGIN_LIST: List[str] = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
