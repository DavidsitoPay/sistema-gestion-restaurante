from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Sistema Gestión Restaurante"
    SECRET_KEY: str = "supersecretkey-change-in-production-please"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 horas

    # Local: MySQL. Render: PostgreSQL (se sobreescribe con variable de entorno)
    DATABASE_URL: str = "mysql+pymysql://root:root@localhost:3306/restaurante_db"

    class Config:
        env_file = ".env"
        extra = "ignore"

    @property
    def db_url(self) -> str:
        """Render entrega postgres://, SQLAlchemy necesita postgresql://"""
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg2://", 1)
        return url


settings = Settings()
