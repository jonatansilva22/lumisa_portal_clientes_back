from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    order_id: Optional[int] = None
    type: str
    message: str
    read: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NotificationMarkRead(BaseModel):
    notification_id: int