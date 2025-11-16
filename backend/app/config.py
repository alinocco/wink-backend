from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    # Database (async)
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/dbname"
    
    @field_validator('DATABASE_URL')
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Автоматически конвертирует postgresql:// в postgresql+asyncpg:// для async драйвера"""
        if v.startswith('postgresql://') and not v.startswith('postgresql+asyncpg://'):
            # Заменяем postgresql:// на postgresql+asyncpg://
            v = v.replace('postgresql://', 'postgresql+asyncpg://', 1)
        return v
    
    # Database URL для Alembic (sync версия)
    @property
    def DATABASE_URL_SYNC(self) -> str:
        """Возвращает синхронную версию URL для Alembic"""
        return self.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # App
    APP_NAME: str = "FastAPI TaskIQ App"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

