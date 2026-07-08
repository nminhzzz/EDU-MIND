"""
create_tables.py — DEVELOPMENT-ONLY utility.

⚠️  DO NOT USE IN PRODUCTION.
    Use Alembic migrations for all environments:

    # First time setup (new environment):
    alembic upgrade head

    # After changing a model (add migration):
    alembic revision --autogenerate -m "describe_your_change"
    alembic upgrade head

    # Rollback last migration:
    alembic downgrade -1

    # Check current DB version:
    alembic current

This script only exists for local dev when you need a completely FRESH
database (e.g. local testing with a clean slate). It will PROMPT before
destroying data and is blocked in production.
"""

import sys

from sqlalchemy import text

from app.database.mysql import Base, engine

# Import every model so SQLAlchemy registers all tables on Base.metadata
from app.models.ai_recommendation_review import AIRecommendationReview  # noqa: F401
from app.models.classroom import Classroom  # noqa: F401
from app.models.classroom_student import ClassroomStudent  # noqa: F401
from app.models.learning_analytic import LearningAnalytic  # noqa: F401
from app.models.notification import Notification  # noqa: F401
from app.models.quiz import Quiz  # noqa: F401
from app.models.quiz_attempt import QuizAttempt  # noqa: F401
from app.models.student_preference import StudentPreference  # noqa: F401
from app.models.study_document import StudyDocument  # noqa: F401
from app.models.study_goal import StudyGoal  # noqa: F401
from app.models.study_plan import StudyPlan  # noqa: F401
from app.models.study_plan_progress import StudyPlanProgress  # noqa: F401
from app.models.subject import Subject  # noqa: F401
from app.models.user import User  # noqa: F401


def _is_production() -> bool:
    import os
    return os.getenv("ENVIRONMENT", "development").lower() == "production"


def main(force: bool = False) -> None:
    if _is_production():
        print("❌  ABORTED — cannot run create_tables.py in PRODUCTION.")
        print("   Run: alembic upgrade head")
        sys.exit(1)

    if not force:
        print("⚠️  This will DROP and re-create ALL tables (dev only).")
        print("   For production / staging use: alembic upgrade head")
        answer = input("   Type 'yes' to continue: ").strip().lower()
        if answer != "yes":
            print("Aborted.")
            sys.exit(0)

    print("Dropping all tables...")
    with engine.connect() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        Base.metadata.drop_all(bind=conn)
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
        conn.commit()

    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)

    print("✔  Done. Tables created from SQLAlchemy models.")
    print()
    print("Next step — stamp Alembic baseline so future migrations work:")
    print("   alembic stamp head")


if __name__ == "__main__":
    main(force="--force" in sys.argv)
