import time
import sys
from sqlalchemy import inspect, text
from sqlalchemy.exc import OperationalError
from app.database.mysql import Base, engine
from alembic import command
from alembic.config import Config

# Import all models to register them on Base.metadata
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

def wait_for_db():
    print("Waiting for database connection...")
    retries = 20
    while retries > 0:
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("Database is ready!")
            return
        except OperationalError as e:
            print(f"Database not ready yet. Retrying in 2 seconds...")
            retries -= 1
            time.sleep(2)
    print("Could not connect to database. Exiting.")
    sys.exit(1)

def main():
    wait_for_db()
    
    inspector = inspect(engine)
    alembic_cfg = Config("alembic.ini")

    if not inspector.has_table("users"):
        print("Empty database detected. Creating all tables via SQLAlchemy...")
        Base.metadata.create_all(bind=engine)
        print("Stamping Alembic to head...")
        command.stamp(alembic_cfg, "head")
        print("Database initialization completed successfully!")
    else:
        print("Database already initialized. Running Alembic migrations...")
        command.upgrade(alembic_cfg, "head")
        print("Database migrations applied successfully!")

if __name__ == "__main__":
    main()
