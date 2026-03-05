from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class Cart(Base):
    __tablename__ = "carts"
    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("users.id"), nullable=False, index=True)
    active = Column(Boolean, default=True)
    user = relationship("User", back_populates="cart")
    cart_details = relationship("CartDetail", back_populates="cart", cascade="all, delete-orphan")


class CartDetail(Base):
    __tablename__ = "cart_details"
    id = Column(Integer, primary_key=True)
    cart_id = Column(ForeignKey("carts.id"), nullable=False, index=True)
    product_id = Column(ForeignKey("products.id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10,2), nullable=False)

    cart = relationship("Cart", back_populates="cart_details")
    product = relationship("Product", back_populates="cart_details")