"""
Security utilities: password hashing (bcrypt) + JWT creation/verification
+ token blacklisting via Redis.
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# passlib 1.7.x expects bcrypt.__about__.__version__, removed in bcrypt 4.x+.
# We call bcrypt directly (not via passlib), but keep this shim so passlib
# does not crash on import when other packages pull it in transitively.
# Pin bcrypt in requirements.txt to match this compatibility range.
if not hasattr(bcrypt, "__about__"):

    class _BcryptAbout:
        __version__ = getattr(bcrypt, "__version__", "4.0.0")

    bcrypt.__about__ = _BcryptAbout()


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


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------

def _make_token(data: dict, expires_delta: timedelta) -> str:
    payload = data.copy()
    payload.setdefault("jti", uuid.uuid4().hex)
    payload["exp"] = datetime.now(timezone.utc) + expires_delta
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def _decode_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT; return None if invalid or blacklisted."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        jti = payload.get("jti")
        if jti and is_token_blacklisted(jti):
            return None
        return payload
    except JWTError:
        return None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    delta = expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return _make_token(data, delta)


def decode_access_token(token: str) -> Optional[dict]:
    return _decode_token(token)


def create_refresh_token(data: dict) -> str:
    return _make_token(data, timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))


def decode_refresh_token(token: str) -> Optional[dict]:
    return _decode_token(token)
