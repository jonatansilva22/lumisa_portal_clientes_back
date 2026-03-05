# app/modules/companies/models.py
from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True)
    rfc = Column(String(13), nullable=False, unique=True)
    address = Column(Text, nullable=False)
    phone = Column(String(15))
    email = Column(String(100), unique=True)
    active = Column(Boolean, default=True)

    users = relationship("User", back_populates="company")
    orders = relationship("Order", back_populates="company")