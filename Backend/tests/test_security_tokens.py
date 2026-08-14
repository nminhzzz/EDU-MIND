"""Regression tests for strict token-purpose separation and essay upload ownership."""

import unittest
from unittest.mock import patch

from app.core.security import (
    create_access_token,
    create_essay_upload_token,
    create_refresh_token,
    consume_refresh_token,
    decode_access_token,
    decode_essay_upload_token,
    decode_refresh_token,
)


class TokenPurposeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.redis_patches = (
            patch("app.core.security.is_token_blacklisted", return_value=False),
            patch("app.core.security.get_user_active_session", return_value=None),
        )
        for item in self.redis_patches:
            item.start()

    def tearDown(self) -> None:
        for item in reversed(self.redis_patches):
            item.stop()

    def test_refresh_token_cannot_be_used_as_access_token(self) -> None:
        token = create_refresh_token({"sub": "7", "sid": "session"})
        self.assertIsNone(decode_access_token(token))
        self.assertEqual(decode_refresh_token(token)["sub"], "7")

    def test_access_token_cannot_be_used_as_refresh_token(self) -> None:
        token = create_access_token({"sub": "7", "role": "student", "sid": "session"})
        self.assertIsNone(decode_refresh_token(token))
        self.assertEqual(decode_access_token(token)["role"], "student")

    def test_essay_upload_token_is_bound_to_owner(self) -> None:
        token = create_essay_upload_token(user_id=7, quiz_id=42, storage_name="safe-id.pdf")
        self.assertEqual(
            decode_essay_upload_token(token, user_id=7, quiz_id=42),
            "safe-id.pdf",
        )
        self.assertIsNone(decode_essay_upload_token(token, user_id=8, quiz_id=42))
        self.assertIsNone(decode_essay_upload_token(token, user_id=7, quiz_id=43))

    def test_refresh_token_is_consumed_once(self) -> None:
        token = create_refresh_token({"sub": "7", "sid": "session"})
        with patch("app.core.security._get_redis") as get_redis:
            get_redis.return_value.set.side_effect = [True, None]
            self.assertIsNotNone(consume_refresh_token(token))
            self.assertIsNone(consume_refresh_token(token))


if __name__ == "__main__":
    unittest.main()
