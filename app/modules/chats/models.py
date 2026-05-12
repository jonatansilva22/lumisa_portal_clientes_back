from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone, timedelta
from app.db.base import Base

# Zona horaria México (UTC-6)
MEXICO_TZ = timezone(timedelta(hours=-6))

def mexico_now():
    return datetime.now(MEXICO_TZ)

class Chat(Base):
    __tablename__ = "chats"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True, index=True)  # ✅ CAMBIO AQUÍ
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    message = Column(Text, nullable=False)
    read = Column(Boolean, default=False, nullable=False)
    sent_at = Column(DateTime, default=mexico_now)

    order = relationship("Order", back_populates="chats")
    sender = relationship("User", foreign_keys=[sender_id], back_populates="chats_sent")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="chats_received")