from sqlalchemy import Column, Integer, Text, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import sqlalchemy as sa
from app.db.base import Base



class Chat(Base):
    __tablename__ = "chats"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True, index=True)  # ✅ CAMBIO AQUÍ
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    message = Column(Text, nullable=False)
    file_url = Column(String(255))  # URL de archivo o imagen en S3
    read = Column(Boolean, default=False, nullable=False)
    sent_at = Column(DateTime(timezone=True), server_default=sa.text("DATE_ADD(now(), INTERVAL -6 HOUR)"), nullable=True)

    order = relationship("Order", back_populates="chats")
    sender = relationship("User", foreign_keys=[sender_id], back_populates="chats_sent")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="chats_received")