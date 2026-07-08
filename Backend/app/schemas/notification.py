"""
Pydantic schemas for the Notification model.
"""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel


class NotificationCreate(BaseModel):
    user_id: int
    title: str
    content: str
    type: Literal["plan", "score", "recommendation", "system"] = "system"


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    content: str
    type: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationMarkRead(BaseModel):
    """Payload to mark one or more notifications as read."""
    notification_ids: Optional[list[int]] = None  # None = mark all
