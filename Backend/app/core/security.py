"""
Security utilities: password hashing (bcrypt) + JWT creation/verification
+ token blacklisting via Redis.
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True if *plain_password* matches the stored bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except Exception:
        return False


def hash_password(password: str) -> str:
    """Hash *password* with bcrypt before persisting to the database."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


# ---------------------------------------------------------------------------
# Token blacklist (Redis) — lazy import to avoid startup side-effects
# ---------------------------------------------------------------------------

def _get_redis():
    """Lazily import Redis client to avoid import-time connection errors."""
    from app.database.redis import get_redis  # noqa: PLC0415
    return get_redis()


def is_token_blacklisted(jti: str) -> bool:
    """
    Return True if the given JWT ID is on the Redis blacklist.
    Fail-closed: treats Redis errors as blacklisted to prevent revoked
    tokens from granting access when Redis is unavailable.
    """
    if not jti:
        return False
    try:
        return _get_redis().exists(f"blacklist:{jti}") > 0
    except Exception as exc:
        logger.error("Redis blacklist check failed — treating token as revoked: %s", exc)
        return True  # fail-closed: deny access when Redis is unreachable


def blacklist_token(jti: str, expire_seconds: int) -> None:
    """Add a JWT ID to the Redis blacklist with the given TTL."""
    if not jti or expire_seconds <= 0:
        return
    try:
        _get_redis().setex(f"blacklist:{jti}", expire_seconds, "1")
    except Exception as exc:
        logger.error("Redis blacklist write failed: %s", exc)


def set_user_active_session(user_id: int, sid: str, expire_seconds: int) -> None:
    """
    Set the single active session ID (sid) for a user in Redis.
    Supercedes any previous active session ID for this user instantly.
    """
    if not user_id or not sid:
        return
    try:
        r = _get_redis()
        key = f"active_session:{user_id}"
        r.setex(key, expire_seconds, sid)
    except Exception as exc:
        logger.error("Redis set active session failed: %s", exc)


def get_user_active_session(user_id: int) -> Optional[str]:
    """Get current active session ID (sid) for user from Redis."""
    if not user_id:
        return None
    try:
        return _get_redis().get(f"active_session:{user_id}")
    except Exception as exc:
        logger.error("Redis get active session failed: %s", exc)
        return None


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------

def _make_token(data: dict, expires_delta: timedelta) -> str:
    payload = data.copy()
    payload.setdefault("jti", uuid.uuid4().hex)
    payload["exp"] = datetime.now(timezone.utc) + expires_delta
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def _decode_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT; return None if invalid, blacklisted, or superseded by a newer login."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        jti = payload.get("jti")
        if jti and is_token_blacklisted(jti):
            return None

        sid = payload.get("sid")
        user_id = payload.get("sub")
        if sid and user_id:
            active_sid = get_user_active_session(int(user_id))
            if active_sid and active_sid != sid:
                return None

        return payload
    except Exception:
        return None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    delta = expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return _make_token({**data, "typ": "access"}, delta)


def decode_access_token(token: str) -> Optional[dict]:
    payload = _decode_token(token)
    return payload if payload and payload.get("typ") == "access" else None


def create_refresh_token(data: dict) -> str:
    return _make_token({**data, "typ": "refresh"}, timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))


def decode_refresh_token(token: str) -> Optional[dict]:
    payload = _decode_token(token)
    return payload if payload and payload.get("typ") == "refresh" else None


def consume_refresh_token(token: str) -> Optional[dict]:
    """Atomically consume a refresh token so concurrent replay can only win once."""
    payload = decode_refresh_token(token)
    if not payload:
        return None
    jti = payload.get("jti")
    exp = payload.get("exp")
    if not jti or not exp:
        return None
    remaining = int(exp - datetime.now(timezone.utc).timestamp())
    if remaining <= 0:
        return None
    try:
        claimed = _get_redis().set(f"blacklist:{jti}", "1", nx=True, ex=remaining)
        return payload if claimed else None
    except Exception as exc:
        logger.error("Redis refresh-token consume failed: %s", exc)
        return None


def create_essay_upload_token(*, user_id: int, quiz_id: int, storage_name: str) -> str:
    """Issue a short-lived opaque reference to a server-side essay upload."""
    return _make_token(
        {
            "sub": str(user_id),
            "typ": "essay_upload",
            "quiz_id": quiz_id,
            "storage_name": storage_name,
        },
        timedelta(hours=2),
    )


def decode_essay_upload_token(token: str, *, user_id: int, quiz_id: int) -> Optional[str]:
    """Return the safe storage filename when the upload token belongs to user_id."""
    payload = _decode_token(token)
    if not payload or payload.get("typ") != "essay_upload":
        return None
    if payload.get("sub") != str(user_id):
        return None
    if payload.get("quiz_id") != quiz_id:
        return None
    storage_name = payload.get("storage_name")
    if not isinstance(storage_name, str) or not storage_name:
        return None
    return storage_name
