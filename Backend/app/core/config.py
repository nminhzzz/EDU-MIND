"""
Quy hoạch cấu hình dự án (Settings) sử dụng Pydantic BaseSettings — Giai đoạn 4.
"""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Learning Assistant Platform"
    API_V1_STR: str = "/api/v1"
    
    # Database Connections
    DATABASE_URL: str
    MONGODB_URL: str
    REDIS_URL: str
    
    # Security Configurations
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # Mặc định Access Token 15 phút
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7     # Mặc định Refresh Token 7 ngày
    
    # AI Keys
    GEMINI_API_KEY: str = ""
    NVIDIA_API_KEY: str = ""
    NVIDIA_MODEL: str = "meta/llama-3.1-8b-instruct"
    USE_NVIDIA: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Bỏ qua các biến môi trường thừa không dùng trong code

settings = Settings()
