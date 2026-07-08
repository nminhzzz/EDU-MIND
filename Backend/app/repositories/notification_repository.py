"""Repository for in-app notifications."""

from sqlalchemy.orm import Session

from app.core.enums import NotificationType
from app.models.notification import Notification


class NotificationRepository:
    """Data access for the notifications table."""

    def create(
        self,
        db: Session,
        *,
        user_id: int,
        title: str,
        content: str,
        notification_type: NotificationType,
    ) -> Notification:
        """Stage a new notification in the current session (no commit)."""
        notification = Notification(
            user_id=user_id,
            title=title,
            content=content,
            type=notification_type,
            is_read=False,
        )
        db.add(notification)
        return notification

    def count_unread_for_user(self, db: Session, user_id: int) -> int:
        """Return the number of unread notifications for a user."""
        return (
            db.query(Notification)
            .filter(Notification.user_id == user_id, Notification.is_read.is_(False))
            .count()
        )


notification_repository = NotificationRepository()
