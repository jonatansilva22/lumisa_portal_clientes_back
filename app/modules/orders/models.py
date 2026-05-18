from sqlalchemy import Column, Integer, String, Text, Numeric, SmallInteger, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class OrderStatus(Base):
    __tablename__ = "order_statuses"
    id = Column(SmallInteger, primary_key=True)
    name = Column(String(20), nullable=False, unique=True)
    orders = relationship("Order", back_populates="status")


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    folio = Column(String(10), unique=True, nullable=False, index=True)
    description = Column(Text)
    total_payment = Column(Numeric(10,2), default=0)
    shipping_price = Column(Numeric(10,2), default=0)
    status_id = Column(SmallInteger, ForeignKey("order_statuses.id"), nullable=False, index=True)
    client_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    advisor_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    # Relaciones
    client = relationship("User", foreign_keys=[client_id], back_populates="orders_client")
    advisor = relationship("User", foreign_keys=[advisor_id], back_populates="orders_advisor")
    company = relationship("Company", back_populates="orders")
    status = relationship("OrderStatus", back_populates="orders")
    order_details = relationship("OrderDetail", back_populates="order", cascade="all, delete-orphan")
    chats = relationship("Chat", back_populates="order")
    notifications = relationship("Notification", back_populates="order")
    payments = relationship("Payment", back_populates="order")


class OrderDetail(Base):
    __tablename__ = "order_details"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10,2), nullable=False)

    order = relationship("Order", back_populates="order_details")
    product = relationship("Product", back_populates="order_details")