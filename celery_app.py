from celery import Celery

celery_app = Celery(
    "student_tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1"
)

# 🔹 Вместо autodiscover_tasks — прямой импорт
# Это регистрирует задачи из tasks.py в приложении
import tasks  # noqa: F401