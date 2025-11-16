from fastapi import FastAPI
from app.config import settings
from app.api import tasks, scenarios, shots, styles
from app.database import Base
from app.api.schemas.common import MessageResponse, HealthResponse

# Примечание: Создание таблиц через Base.metadata.create_all не поддерживается
# для асинхронных движков. Используйте Alembic миграции для создания таблиц.

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG
)

# Подключение роутеров
app.include_router(tasks.router)
app.include_router(scenarios.router)
app.include_router(shots.router)
app.include_router(styles.router)


@app.get("/", response_model=MessageResponse)
async def root():
    return MessageResponse(message="Welcome to FastAPI TaskIQ App")


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="healthy")

