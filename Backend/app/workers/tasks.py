"""
Celery tasks — heavy AI workloads and scheduled background jobs.

All tasks import application modules lazily to avoid circular imports and to
keep the Celery worker startup lightweight.

Queue routing is handled centrally by task_routes in celery_app.py.
"""

from __future__ import annotations

import asyncio
import uuid
from celery import shared_task  # noqa: F401

from app.core.enums import GoalStatus, NotificationType, PlanStatus
from app.core.logging import get_logger
from app.workers.celery_app import celery  # noqa: F401 — ensures tasks are registered

logger = get_logger(__name__)


def _acquire_task_lock(key: str, ttl_seconds: int) -> str | None:
    from app.database.redis import get_redis

    token = uuid.uuid4().hex
    acquired = get_redis().set(f"task_lock:{key}", token, nx=True, ex=ttl_seconds)
    return token if acquired else None


def _release_task_lock(key: str, token: str | None) -> None:
    if not token:
        return
    from app.database.redis import get_redis

    script = """
    if redis.call('GET', KEYS[1]) == ARGV[1] then
        return redis.call('DEL', KEYS[1])
    end
    return 0
    """
    try:
        get_redis().eval(script, 1, f"task_lock:{key}", token)
    except Exception as exc:
        logger.warning("Could not release task lock %s: %s", key, exc)


# ── AI Tasks (queue: ai_tasks via task_routes in celery_app.py) ───────────────

@celery.task(
    name="app.workers.tasks.task_generate_quiz",
    bind=True,
    max_retries=2,
    default_retry_delay=30,
)
def task_generate_quiz(
    self,
    student_id: int,
    subject_id: int,
    topic: str,
    difficulty: str,
    total_questions: int,
    study_plan_id: int | None = None,
) -> dict:
    """
    Asynchronously generate an AI quiz via RAG.
    The caller receives a Celery task ID and polls for the result.
    """
    from app.database.mongodb import make_mongodb_db
    from app.database.mysql import SessionLocal
    from app.services.quiz_service import generate_and_save_quiz

    logger.info(
        "task_generate_quiz: student=%d subject=%d topic='%s'",
        student_id, subject_id, topic,
    )

    async def _run(db):
        # Fresh Motor client created inside asyncio.run() so it is always bound
        # to the current event loop, not a previously closed one.
        mongo_client, db_mongo = make_mongodb_db()
        try:
            return await generate_and_save_quiz(
                db=db,
                db_mongo=db_mongo,
                student_id=student_id,
                subject_id=subject_id,
                topic=topic,
                difficulty=difficulty,
                total_questions=total_questions,
                study_plan_id=study_plan_id,
            )
        finally:
            mongo_client.close()

    try:
        with SessionLocal() as db:
            quiz = asyncio.run(_run(db))
        return {"quiz_id": quiz.id, "title": quiz.title}
    except Exception as exc:
        logger.error("task_generate_quiz failed: %s", exc)
        raise self.retry(exc=exc)


@celery.task(
    name="app.workers.tasks.task_update_analytics",
    bind=True,
    max_retries=3,
    default_retry_delay=10,
)
def task_update_analytics(
    self,
    student_id: int,
    subject_id: int,
    quiz_id: int,
    score: float,
) -> None:
    """
    Recalculate LearningAnalytic after a quiz submission and trigger
    AI-generated study recommendations when the score is below threshold.
    """
    from app.database.mysql import SessionLocal
    from app.services.analytic_service import update_student_analytics_and_recommend

    logger.info(
        "task_update_analytics: student=%d subject=%d quiz=%d score=%.1f",
        student_id, subject_id, quiz_id, score,
    )
    try:
        with SessionLocal() as db:
            asyncio.run(
                update_student_analytics_and_recommend(
                    db=db,
                    student_id=student_id,
                    subject_id=subject_id,
                    quiz_id=quiz_id,
                    score=score,
                )
            )
    except Exception as exc:
        logger.error("task_update_analytics failed: %s", exc)
        raise self.retry(exc=exc)


@celery.task(
    name="app.workers.tasks.task_generate_attempt_assessment",
    bind=True,
    max_retries=3,
    default_retry_delay=20,
)
def task_generate_attempt_assessment(self, attempt_id: int) -> None:
    """Generate an attempt assessment using authoritative database data."""
    from app.database.mysql import SessionLocal
    from app.models.quiz_attempt import QuizAttempt
    from app.services.quiz.attempts import process_ai_quiz_assessment_background

    lock_key = f"attempt_assessment:{attempt_id}"
    lock_token = _acquire_task_lock(lock_key, 900)
    if not lock_token:
        return
    try:
        with SessionLocal() as db:
            attempt = db.query(QuizAttempt).filter(QuizAttempt.id == attempt_id).first()
            if not attempt or not attempt.quiz or attempt.ai_assessment is not None:
                return
            process_ai_quiz_assessment_background(
                attempt.id,
                attempt.quiz.title or "Đề thi",
                attempt.quiz.questions or [],
                attempt.answers or [],
                float(attempt.score),
                attempt.correct_count,
                attempt.wrong_count,
            )
    except Exception as exc:
        raise self.retry(exc=exc)
    finally:
        _release_task_lock(lock_key, lock_token)


@celery.task(
    name="app.workers.tasks.task_generate_single_plan_material",
    bind=True,
    max_retries=0,
    soft_time_limit=150,
    time_limit=180,
)
def task_generate_single_plan_material(self, plan_id: int) -> None:
    from app.services.unified.materials import generate_single_plan_material_bg

    asyncio.run(generate_single_plan_material_bg(plan_id))


@celery.task(
    name="app.workers.tasks.task_index_study_document",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
)
def task_index_study_document(self, document_id: int) -> None:
    from app.database.mongodb import make_mongodb_db
    from app.database.mysql import SessionLocal
    from app.services.study_document_service import reindex_study_document_rag

    async def _run() -> None:
        mongo_client, db_mongo = make_mongodb_db()
        try:
            with SessionLocal() as db:
                await reindex_study_document_rag(
                    db,
                    db_mongo,
                    document_id=document_id,
                )
        finally:
            mongo_client.close()

    lock_key = f"document_index:{document_id}"
    lock_token = _acquire_task_lock(lock_key, 1200)
    if not lock_token:
        return
    try:
        asyncio.run(_run())
    except Exception as exc:
        raise self.retry(exc=exc)
    finally:
        _release_task_lock(lock_key, lock_token)


# ── Scheduled Tasks (queue: default via task_routes in celery_app.py) ─────────

@celery.task(name="app.workers.tasks.task_dispatch_outbox")
def task_dispatch_outbox() -> dict:
    from app.services.outbox_service import dispatch_pending_outbox_jobs

    return dispatch_pending_outbox_jobs()


@celery.task(name="app.workers.tasks.task_send_daily_reminders")
def task_send_daily_reminders() -> dict:
    """
    Send daily study reminders to students who have tasks scheduled for today.
    Runs every hour; the task internally checks current local time (UTC+7)
    and only sends notifications between 07:00-09:00.
    """
    from datetime import datetime, timezone, timedelta

    # Only send during the 07:00-09:00 window (UTC+7 = UTC+7h)
    now_vn = datetime.now(timezone.utc) + timedelta(hours=7)
    if not (7 <= now_vn.hour < 9):
        return {"status": "skipped", "reason": "outside notification window"}

    from datetime import date
    from app.database.mysql import SessionLocal
    from app.models.study_plan import StudyPlan
    from app.models.study_goal import StudyGoal
    from app.models.notification import Notification

    logger.info("task_send_daily_reminders: sending notifications for %s", date.today())
    sent = 0
    try:
        with SessionLocal() as db:
            today_plans = (
                db.query(StudyPlan)
                .join(StudyGoal, StudyPlan.goal_id == StudyGoal.id)
                .filter(
                    StudyPlan.study_date == date.today(),
                    StudyPlan.status == PlanStatus.TODO,
                    StudyGoal.status == GoalStatus.ACTIVE,
                )
                .all()
            )

            notified_students: set[int] = set()
            for plan in today_plans:
                if plan.student_id in notified_students:
                    continue
                db.add(
                    Notification(
                        user_id=plan.student_id,
                        title="Nhắc nhở học tập hôm nay",
                        content="Bạn có kế hoạch học tập cần hoàn thành hôm nay. Hãy kiểm tra lịch học của bạn!",
                        type=NotificationType.PLAN,
                        is_read=False,
                    )
                )
                notified_students.add(plan.student_id)
                sent += 1

            db.commit()
    except Exception as exc:
        logger.error("task_send_daily_reminders failed: %s", exc)

    logger.info("task_send_daily_reminders: sent %d notifications.", sent)
    return {"status": "ok", "notifications_sent": sent}


@celery.task(name="app.workers.tasks.task_check_approaching_deadlines")
def task_check_approaching_deadlines() -> dict:
    """
    Notify students whose study goal deadline is within 3 days.
    """
    from datetime import date, timedelta
    from app.database.mysql import SessionLocal
    from app.models.notification import Notification
    from app.models.study_goal import StudyGoal
    from app.models.user import User
    from app.services.email_service import send_deadline_reminder_email

    today = date.today()
    warning_date = today + timedelta(days=3)
    sent = 0

    logger.info("task_check_approaching_deadlines: checking deadlines <= %s", warning_date)
    try:
        email_coros = []

        with SessionLocal() as db:
            approaching = (
                db.query(StudyGoal)
                .filter(
                    StudyGoal.status == GoalStatus.ACTIVE,
                    StudyGoal.deadline <= warning_date,
                    StudyGoal.deadline >= today,
                )
                .all()
            )

            for goal in approaching:
                days_left = (goal.deadline - today).days
                db.add(
                    Notification(
                        user_id=goal.student_id,
                        title="Hạn chót lộ trình sắp đến!",
                        content=(
                            f"Lộ trình học tập của bạn còn {days_left} ngày nữa là đến hạn. "
                            "Hãy kiểm tra tiến độ và hoàn thành các nhiệm vụ còn lại!"
                        ),
                        type=NotificationType.PLAN,
                        is_read=False,
                    )
                )

                student = db.query(User).filter(User.id == goal.student_id).first()
                if student:
                    # Collect coroutines — all emails are sent in one asyncio.run()
                    # below to avoid creating/destroying an event loop per email.
                    email_coros.append(
                        send_deadline_reminder_email(
                            student.email,
                            student.full_name or student.email,
                            goal.subject.name if goal.subject else "học tập",
                            days_left,
                        )
                    )

                sent += 1

            db.commit()

        # Single asyncio.run() fires all emails concurrently via gather.
        # return_exceptions=True prevents one failed email from aborting the rest.
        if email_coros:
            asyncio.run(asyncio.gather(*email_coros, return_exceptions=True))

    except Exception as exc:
        logger.error("task_check_approaching_deadlines failed: %s", exc)

    logger.info("task_check_approaching_deadlines: sent %d deadline warnings.", sent)
    return {"status": "ok", "warnings_sent": sent}
