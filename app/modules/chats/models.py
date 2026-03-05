from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class Chat(Base):
    __tablename__ = "chats"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    message = Column(Text, nullable=False)
    read = Column(Boolean, default=False, nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="chats")
    sender = relationship("User", foreign_keys=[sender_id], back_populates="chats_sent")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="chats_received")