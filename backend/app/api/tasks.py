from fastapi import APIRouter
from app.tasks.example_tasks import example_task, send_notification
from app.api.schemas.task import TaskResponse

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/example", response_model=TaskResponse)
async def trigger_example_task(message: str):
    """
    Триггерит пример задачи TaskIQ
    """
    task = await example_task.kiq(message)
    return TaskResponse(task_id=task.task_id, message="Task queued")


@router.post("/notify", response_model=TaskResponse)
async def trigger_notification(user_id: int, message: str):
    """
    Триггерит задачу отправки уведомления
    """
    task = await send_notification.kiq(user_id, message)
    return TaskResponse(task_id=task.task_id, message="Notification task queued")


