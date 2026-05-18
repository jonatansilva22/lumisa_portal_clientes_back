from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ChatCreate(BaseModel):
    order_id: int
    receiver_id: int
    message: str = ""
    file_url: Optional[str] = None

class ChatResponse(BaseModel):
    id: int
    order_id: Optional[int]
    sender_id: int
    receiver_id: int
    message: str
    file_url: Optional[str] = None
    read: bool
    sent_at: datetime

    class Config:
        from_attributes = True

class ChatMarkRead(BaseModel):
    message_id: int

class DirectMessageCreate(BaseModel):
    receiver_id: int
    message: str