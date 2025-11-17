from taskiq_redis import ListQueueBroker
from app.config import settings

# Инициализация брокера TaskIQ с Redis
broker = ListQueueBroker(url=settings.REDIS_URL)

