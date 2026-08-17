import time
import sys
from sqlalchemy import inspect, text
from sqlalchemy.exc import OperationalError
from app.database.mysql import engine
from app.models import Base  # Imports all models and registers their tables.
from alembic import command
from alembic.config import Config

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
    alembic_cfg = Config("alembic.ini")

    # The first Alembic revision is a baseline for databases that existed
    # before migrations were introduced; it intentionally creates no tables.
    # A completely fresh deployment therefore needs the current model schema
    # once, after which Alembic owns all subsequent schema changes.
    if not inspect(engine).has_table("users"):
        print("Fresh database detected. Creating the current schema...")
        Base.metadata.create_all(bind=engine)
        command.stamp(alembic_cfg, "head")
        print("Database schema created and stamped successfully!")
        return

    print("Running reviewed Alembic migrations...")
    command.upgrade(alembic_cfg, "head")
    print("Database migrations applied successfully!")

if __name__ == "__main__":
    main()
