import redis

from app.core.config import settings

# Redis client manages its own connection pool — safe to use as a module-level singleton.
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


def get_redis() -> redis.Redis:
    """Return the shared Redis client."""
    return redis_client
