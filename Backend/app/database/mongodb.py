"""
Async MongoDB client — Motor singleton for FastAPI requests.

Two access patterns:
  - get_mongodb_db()  → shared singleton for the FastAPI/uvicorn event loop.
  - make_mongodb_db() → creates a fresh client for Celery tasks.  Each
                        asyncio.run() in a Celery worker spins up and tears
                        down its own event loop; reusing the singleton would
                        bind Motor to a closed loop, causing
                        'Event loop is closed' errors.  The caller must call
                        mongo_client.close() after asyncio.run() returns.
"""

from urllib.parse import urlparse

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


def _db_name() -> str:
    """Parse the database name from the MongoDB connection URL."""
    parsed = urlparse(settings.MONGODB_URL)
    return parsed.path.lstrip("/").split("?")[0] or "chat_db"


def get_mongo_client() -> AsyncIOMotorClient | None:
    """Return the shared Motor client, or None if not yet initialised."""
    return _client


def get_mongodb_db() -> AsyncIOMotorDatabase:
    """
    Return the shared async MongoDB database instance (FastAPI singleton).
    Safe to use within the uvicorn event loop — one client per process lifetime.
    """
    global _client, _db
    if _client is None:
        _client = AsyncIOMotorClient(settings.MONGODB_URL)
        _db = _client[_db_name()]
    return _db


def make_mongodb_db() -> tuple[AsyncIOMotorClient, AsyncIOMotorDatabase]:
    """
    Create a fresh Motor client and database for Celery task contexts.

    Celery tasks use asyncio.run() which creates and destroys a new event loop
    per invocation.  Motor binds to the running event loop — reusing the
    singleton across asyncio.run() calls results in 'Event loop is closed'
    errors.  Always call mongo_client.close() after asyncio.run() returns.

    Example usage inside a Celery task:
        async def _run():
            mongo_client, db_mongo = make_mongodb_db()
            try:
                return await my_service(db_mongo=db_mongo, ...)
            finally:
                mongo_client.close()

        result = asyncio.run(_run())
    """
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[_db_name()]
    return client, db
