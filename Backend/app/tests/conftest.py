"""
Shared pytest fixtures — HTTP client, DB mocks, Redis cleanup, mock AI helpers.
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.database.redis import get_redis
from app.main import app
from app.models.subject import Subject
from app.models.user import User


@pytest.fixture
def test_client():
    """FastAPI TestClient with dependency overrides cleared after each test."""
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def mock_student():
    return User(
        id=999,
        email="test_student@edumind.vn",
        full_name="Student Test",
        role="student",
        is_active=True,
    )


@pytest.fixture
def mock_teacher():
    return User(
        id=10,
        email="teacher@edumind.vn",
        full_name="Teacher Test",
        role="teacher",
        is_active=True,
    )


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def mock_subject():
    subject = MagicMock(spec=Subject)
    subject.id = 1
    subject.name = "Java Programming"
    return subject


@pytest.fixture
def mock_db_with_subject(mock_db, mock_subject):
    """SQLAlchemy session mock pre-wired for subject_repository.get()."""
    mock_db.query().filter().first.return_value = mock_subject
    return mock_db


@pytest.fixture(autouse=True)
def clean_redis():
    """Remove test rate-limit and lock keys before and after each test."""
    redis_client = get_redis()
    for pattern in ("rate_limit:*", "lock:*"):
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
    yield
    for pattern in ("rate_limit:*", "lock:*"):
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)


@pytest.fixture
def mock_deepseek_generate():
    """Patch the central DeepSeek content generator (sync)."""
    with patch("app.infrastructure.ai.content.generate_content_deepseek") as mock:
        yield mock


@pytest.fixture
def mock_deepseek_stream():
    """Patch the central DeepSeek streaming content generator."""
    with patch("app.infrastructure.ai.content.generate_content_deepseek_stream") as mock:
        yield mock
