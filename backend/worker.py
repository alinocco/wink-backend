"""
Воркер для обработки задач TaskIQ
Запуск: taskiq worker app.tasks.broker
"""
from app.tasks import broker
from app.tasks.example_tasks import example_task, send_notification  # noqa

if __name__ == "__main__":
    # Это нужно для импорта задач
    pass


