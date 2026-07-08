"""
APScheduler — lightweight in-process scheduler.

Used as a fallback when Celery Beat is not running (e.g., local development).
For production, prefer Celery Beat (configured in celery_app.py).

Start alongside the FastAPI app via lifespan if ENABLE_SCHEDULER=true.
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.logging import get_logger

logger = get_logger(__name__)

_scheduler: AsyncIOScheduler | None = None


async def _run_daily_reminders() -> None:
    from app.workers.tasks import task_send_daily_reminders
    task_send_daily_reminders.delay()


async def _run_deadline_check() -> None:
    from app.workers.tasks import task_check_approaching_deadlines
    task_check_approaching_deadlines.delay()


def get_scheduler() -> AsyncIOScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler(timezone="Asia/Ho_Chi_Minh")

        # Daily reminder — every day at 08:00 VN time
        _scheduler.add_job(
            _run_daily_reminders,
            CronTrigger(hour=8, minute=0, timezone="Asia/Ho_Chi_Minh"),
            id="daily_reminders",
            replace_existing=True,
        )

        # Deadline check — every day at 07:00 VN time
        _scheduler.add_job(
            _run_deadline_check,
            CronTrigger(hour=7, minute=0, timezone="Asia/Ho_Chi_Minh"),
            id="deadline_check",
            replace_existing=True,
        )

    return _scheduler


def start_scheduler() -> None:
    scheduler = get_scheduler()
    if not scheduler.running:
        scheduler.start()
        logger.info("APScheduler started with %d jobs.", len(scheduler.get_jobs()))


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("APScheduler stopped.")
        _scheduler = None
