from app.tasks import broker


@broker.task
async def example_task(message: str) -> str:
    """
    Пример асинхронной задачи TaskIQ
    """
    print(f"Processing task with message: {message}")
    # Здесь может быть любая асинхронная логика
    return f"Task completed: {message}"


@broker.task
async def send_notification(user_id: int, message: str) -> bool:
    """
    Пример задачи для отправки уведомлений
    """
    print(f"Sending notification to user {user_id}: {message}")
    # Здесь может быть логика отправки email, push-уведомлений и т.д.
    return True

