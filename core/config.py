import os
from typing import List, Union

from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- 基础配置 ---
    PROJECT_NAME: str = "CampusTaskAPI"
    API_V1_STR: str = "/api/v1"

    # --- 安全与加密配置 ---
    # 建议在 .env 中设置真正的密钥：openssl rand -hex 32
    SECRET_KEY: str = "super-secret-key-for-development-only"
    ALGORITHM: str = "HS256"
    # Token 过期时间（分钟）
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 默认 7 天

    # --- 数据库配置 (MySQL) ---
    MYSQL_SERVER: str = "localhost"
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "yourpassword"
    MYSQL_DB: str = "campus_task_db"
    MYSQL_PORT: str = "3306"

    # 构造 SQLAlchemy 数据库连接字符串
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_SERVER}:{self.MYSQL_PORT}/{self.MYSQL_DB}?charset=utf8mb4"

    # --- 跨域配置 (CORS) ---
    # 允许访问后端的来源列表
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # --- 静态文件配置 ---
    UPLOAD_DIR: str = "uploads"
    AVATAR_DIR: str = os.path.join(UPLOAD_DIR, "avatars")
    ATTACHMENT_DIR: str = os.path.join(UPLOAD_DIR, "attachments")

    # 读取 .env 文件配置
    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env")


# 实例化配置对象，供其他模块直接导入
settings = Settings()
