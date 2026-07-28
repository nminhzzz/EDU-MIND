import time
import sys
from sqlalchemy import inspect, text
from sqlalchemy.exc import OperationalError
from app.database.mysql import Base, engine
from alembic import command
from alembic.config import Config

# Import all models to register them on Base.metadata
import app.models  # noqa: F401

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

def sync_missing_columns():
    inspector = inspect(engine)
    with engine.connect() as conn:
        for table_name, table in Base.metadata.tables.items():
            if inspector.has_table(table_name):
                existing_cols = {c['name'] for c in inspector.get_columns(table_name)}
                for col in table.columns:
                    if col.name not in existing_cols:
                        col_type = col.type.compile(engine.dialect)
                        nullable = 'NULL' if col.nullable else 'NOT NULL'
                        default = ''
                        if col.default is not None and hasattr(col.default, 'arg') and isinstance(col.default.arg, (int, str, float)):
                            default = f" DEFAULT {repr(col.default.arg)}"
                        sql = f"ALTER TABLE {table_name} ADD COLUMN {col.name} {col_type} {nullable}{default};"
                        print(f"Adding missing column: {sql}")
                        conn.execute(text(sql))
        conn.commit()

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
        print("Running Alembic migrations and syncing schema...")
        Base.metadata.create_all(bind=engine)
        sync_missing_columns()
        command.upgrade(alembic_cfg, "head")
        print("Database migrations and column sync applied successfully!")

if __name__ == "__main__":
    main()
