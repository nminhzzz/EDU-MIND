import redis
from app.core.config import settings

REDIS_URL = settings.REDIS_URL

# Khởi tạo Redis client
# Do Redis client tự động quản lý Connection Pool nên có thể dùng trực tiếp
redis_client = redis.from_url(REDIS_URL, decode_responses=True)


def get_redis():
    """
    Trả về client kết nối Redis.
    """
    return redis_client


def get_redis_client():
    """
    Trả về client kết nối Redis (alias cho get_redis).
    """
    return redis_client
