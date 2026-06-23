import asyncio
from datetime import date, datetime
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.deps import get_db, get_current_student
from app.models.user import User
from app.models.study_goal import StudyGoal
from app.models.study_plan import StudyPlan
from app.models.quiz import Quiz
from app.models.quiz_attempt import QuizAttempt
from app.models.learning_analytic import LearningAnalytic
from app.models.notification import Notification

router = APIRouter()


async def generate_progress_events(student_id: int, db: Session):
    while True:
        try:
            active_goals = db.query(StudyGoal).filter(
                StudyGoal.student_id == student_id,
                StudyGoal.status == "active"
            ).count()

            today = date.today()
            today_plans = db.query(StudyPlan).filter(
                StudyPlan.student_id == student_id,
                StudyPlan.study_date == today
            ).all()
            today_total = len(today_plans)
            today_done = sum(1 for p in today_plans if p.status == "done")
            today_doing = sum(1 for p in today_plans if p.status == "doing")

            total_plans_all = db.query(StudyPlan).filter(
                StudyPlan.student_id == student_id
            ).count()
            done_plans_all = db.query(StudyPlan).filter(
                StudyPlan.student_id == student_id,
                StudyPlan.status == "done"
            ).count()

            total_attempts = db.query(QuizAttempt).filter(
                QuizAttempt.student_id == student_id
            ).count()
            avg_score = db.query(func.avg(QuizAttempt.score)).filter(
                QuizAttempt.student_id == student_id
            ).scalar() or 0.0

            unread_notifications = db.query(Notification).filter(
                Notification.user_id == student_id,
                Notification.is_read == False
            ).count()

            next_plan = db.query(StudyPlan).filter(
                StudyPlan.student_id == student_id,
                StudyPlan.study_date >= today,
                StudyPlan.status == "todo"
            ).order_by(StudyPlan.study_date, StudyPlan.start_time).first()

            weak_areas = db.query(LearningAnalytic).filter(
                LearningAnalytic.student_id == student_id
            ).all()
            weak_summary = []
            for wa in weak_areas:
                if wa.weak_topics:
                    weak_topics_list = [t.get("topic", str(t)) if isinstance(t, dict) else str(t) for t in wa.weak_topics]
                    weak_summary.extend(weak_topics_list[:2])

            progress_pct = 0
            if total_plans_all > 0:
                progress_pct = round(done_plans_all / total_plans_all * 100)

            event_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "active_goals": active_goals,
                "today": {
                    "total_tasks": today_total,
                    "done": today_done,
                    "doing": today_doing,
                    "remaining": today_total - today_done - today_doing,
                },
                "overall": {
                    "progress_pct": progress_pct,
                    "done_plans": done_plans_all,
                    "total_plans": total_plans_all,
                },
                "quizzes": {
                    "total_attempts": total_attempts,
                    "avg_score": round(float(avg_score), 1),
                },
                "next_task": {
                    "title": next_plan.title if next_plan else None,
                    "date": next_plan.study_date.isoformat() if next_plan else None,
                    "time": f"{next_plan.start_time.strftime('%H:%M')} - {next_plan.end_time.strftime('%H:%M')}" if next_plan else None,
                } if next_plan else None,
                "weak_areas": weak_summary[:3],
                "unread_notifications": unread_notifications,
            }

            import json
            yield f"data: {json.dumps(event_data, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"

        await asyncio.sleep(5)


@router.get(
    "/stream",
    summary="Realtime Dashboard Stream (SSE)",
    description="Stream tiến độ học tập realtime: tasks hôm nay, tổng quan lộ trình, quiz stats, weak areas."
)
async def dashboard_stream(
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    return StreamingResponse(
        generate_progress_events(current_user.id, db),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )
