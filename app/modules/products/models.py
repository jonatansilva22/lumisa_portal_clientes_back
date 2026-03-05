from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, SmallInteger, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class ProductType(Base):
    __tablename__ = "product_types"
    id = Column(SmallInteger, primary_key=True)
    name = Column(String(30), nullable=False, unique=True)
    products = relationship("Product", back_populates="type")


class Unit(Base):
    __tablename__ = "units"
    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    abbreviation = Column(String(10), unique=True)
    products = relationship("Product", back_populates="unit")


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, index=True)
    description = Column(Text)
    price = Column(Numeric(10,2), nullable=False)
    image_url = Column(String(255))
    quantity = Column(Integer, nullable=False, default=0)
    type_id = Column(SmallInteger, ForeignKey("product_types.id"), nullable=False, index=True)
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=False, index=True)
    active = Column(Boolean, default=True, nullable=False)

    # Relaciones
    type = relationship("ProductType", back_populates="products")
    unit = relationship("Unit", back_populates="products")
    order_details = relationship("OrderDetail", back_populates="product")
    cart_details = relationship("CartDetail", back_populates="product")