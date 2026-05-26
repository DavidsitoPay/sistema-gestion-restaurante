from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "Sistema Gestión Restaurante"
    SECRET_KEY: str = "supersecretkey-change-in-production-please"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 horas

    DATABASE_URL: str = "mysql+pymysql://root:root@localhost:3306/restaurante_db"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
