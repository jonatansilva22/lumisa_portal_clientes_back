from sqlalchemy import Column, Integer, SmallInteger, Numeric, ForeignKey, DateTime, Boolean, String
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class PaymentMethod(Base):
    __tablename__ = "payment_methods"
    id = Column(SmallInteger, primary_key=True)
    name = Column(String(40), nullable=False, unique=True)
    active = Column(Boolean, default=True)
    payments = relationship("Payment", back_populates="method")


class PaymentStatus(Base):
    __tablename__ = "payment_statuses"
    id = Column(SmallInteger, primary_key=True)
    name = Column(String(20), nullable=False, unique=True)
    payments = relationship("Payment", back_populates="status")


class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    amount = Column(Numeric(10,2), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    status_id = Column(SmallInteger, ForeignKey("payment_statuses.id"), nullable=False, index=True)
    method_id = Column(SmallInteger, ForeignKey("payment_methods.id"), nullable=False, index=True)
    paid_at = Column(DateTime, nullable=True)

    order = relationship("Order", back_populates="payments")
    status = relationship("PaymentStatus", back_populates="payments")
    method = relationship("PaymentMethod", back_populates="payments")