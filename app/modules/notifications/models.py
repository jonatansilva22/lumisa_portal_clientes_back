from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone, timedelta
from app.db.base import Base

# Zona horaria México (UTC-6)
MEXICO_TZ = timezone(timedelta(hours=-6))

def mexico_now():
    return datetime.now(MEXICO_TZ)

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True, index=True)
    type = Column("title", String(50), nullable=False)
    message = Column(Text, nullable=False)
    read = Column(Boolean, default=False, nullable=False)

    user = relationship("User", back_populates="notifications")
    order = relationship("Order", back_populates="notifications")