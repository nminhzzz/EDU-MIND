"""
Celery application configuration.

Workers are started with:
    celery -A app.workers.celery_app.celery worker --loglevel=info -Q ai_tasks,default

Beat scheduler (periodic tasks):
    celery -A app.workers.celery_app.celery beat --loglevel=info
"""

from celery import Celery

from app.core.config import settings

celery = Celery(
    "ai_learning_platform",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.workers.tasks"],
)

celery.conf.update(
    # Serialisation
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Ho_Chi_Minh",
    enable_utc=True,

    # Reliability
    task_acks_late=True,           # Re-queue task on worker crash
    worker_prefetch_multiplier=1,  # One task at a time per worker (long AI tasks)
    task_reject_on_worker_lost=True,

    # Result expiry (keep results for 1 hour)
    result_expires=3600,

    # Queues
    task_default_queue="default",
    task_routes={
        "app.workers.tasks.task_generate_quiz": {"queue": "ai_tasks"},
        "app.workers.tasks.task_update_analytics": {"queue": "ai_tasks"},
        "app.workers.tasks.task_generate_plan_materials": {"queue": "ai_tasks"},
        "app.workers.tasks.task_send_daily_reminders": {"queue": "default"},
        "app.workers.tasks.task_check_approaching_deadlines": {"queue": "default"},
    },

    # Beat schedule (periodic tasks)
    beat_schedule={
        "send-daily-reminders-8am": {
            "task": "app.workers.tasks.task_send_daily_reminders",
            "schedule": 60 * 60,  # every hour — actual time filter is inside the task
            "options": {"queue": "default"},
        },
        "check-approaching-deadlines": {
            "task": "app.workers.tasks.task_check_approaching_deadlines",
            "schedule": 60 * 60 * 6,  # every 6 hours
            "options": {"queue": "default"},
        },
    },
)
