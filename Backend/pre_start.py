import time
import sys
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from app.database.mysql import engine
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
    print("Running reviewed Alembic migrations...")
    command.upgrade(alembic_cfg, "head")
    print("Database migrations applied successfully!")

if __name__ == "__main__":
    main()
