"""
Redis-backed response cache utilities.

Usage:
    # Read
    data = await get_cached("my:key")
    if data is None:
        data = await expensive_operation()
        await set_cached("my:key", data, ttl_seconds=300)

    # Invalidate
    await invalidate("my:key")
    await invalidate_pattern("recs:*")          # wildcard (SCAN-safe)
"""

import asyncio
import hashlib
import json
from typing import Any, Optional

from app.core.logging import get_logger
from app.database.redis import get_redis

logger = get_logger(__name__)


def _make_key(*parts: Any) -> str:
    """Build a namespaced cache key from arbitrary parts."""
    return ":".join(str(p) for p in parts)


def _hash_text(text: str) -> str:
    """SHA-256 short hash for long string keys (e.g. query text)."""
    return hashlib.sha256(text.encode()).hexdigest()[:16]


# ── Core primitives ────────────────────────────────────────────────────────────

async def get_cached(key: str) -> Optional[Any]:
    """Return the cached value for *key*, or None on miss/error."""
    try:
        raw = await asyncio.to_thread(get_redis().get, key)
        if raw is None:
            return None
        return json.loads(raw)
    except Exception as exc:
        logger.warning("Cache GET error for key='%s': %s", key, exc)
        return None


async def set_cached(key: str, value: Any, ttl_seconds: int = 300) -> None:
    """Serialise *value* to JSON and store under *key* with a TTL."""
    try:
        serialised = json.dumps(value, ensure_ascii=False, default=str)
        await asyncio.to_thread(get_redis().setex, key, ttl_seconds, serialised)
    except Exception as exc:
        logger.warning("Cache SET error for key='%s': %s", key, exc)


async def invalidate(key: str) -> None:
    """Delete a single cache key."""
    try:
        await asyncio.to_thread(get_redis().delete, key)
    except Exception as exc:
        logger.warning("Cache INVALIDATE error for key='%s': %s", key, exc)


async def invalidate_pattern(pattern: str) -> None:
    """
    Delete all keys matching *pattern* using SCAN (non-blocking, production-safe).
    Example: invalidate_pattern("recs:*")
    """
    try:
        client = get_redis()
        cursor = 0
        deleted = 0
        while True:
            cursor, keys = await asyncio.to_thread(client.scan, cursor, match=pattern, count=100)
            if keys:
                await asyncio.to_thread(client.delete, *keys)
                deleted += len(keys)
            if cursor == 0:
                break
        if deleted:
            logger.debug("Cache INVALIDATE pattern='%s' deleted %d keys", pattern, deleted)
    except Exception as exc:
        logger.warning("Cache INVALIDATE_PATTERN error for pattern='%s': %s", pattern, exc)


# ── Named key builders ─────────────────────────────────────────────────────────

def system_analytics_key() -> str:
    return "analytics:system"


def rag_search_key(subject_id: int, query_text: str) -> str:
    return _make_key("rag", subject_id, _hash_text(query_text))


def student_recommendations_key(student_id: int) -> str:
    return _make_key("recs", student_id)
