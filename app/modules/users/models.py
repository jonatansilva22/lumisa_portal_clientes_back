from sqlalchemy import Column, Integer, String, Boolean, SmallInteger, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(SmallInteger, primary_key=True)
    name = Column(String(20), nullable=False, unique=True)

    users = relationship("User", back_populates="role")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)

    email = Column(String(100), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    image_url = Column(String(255))

    role_id = Column(ForeignKey("roles.id"), nullable=False, index=True)
    company_id = Column(ForeignKey("companies.id"), nullable=True)

    active = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now(), nullable=True)

    # Relaciones
    role = relationship("Role", back_populates="users")
    company = relationship("Company", back_populates="users")

    orders_client = relationship(
        "Order",
        foreign_keys="Order.client_id",
        back_populates="client"
    )
    orders_advisor = relationship(
        "Order",
        foreign_keys="Order.advisor_id",
        back_populates="advisor"
    )

    notifications = relationship("Notification", back_populates="user")
    cart = relationship("Cart", back_populates="user", uselist=False)

    chats_sent = relationship(
        "Chat",
        foreign_keys="Chat.sender_id",
        back_populates="sender"
    )
    chats_received = relationship(
        "Chat",
        foreign_keys="Chat.receiver_id",
        back_populates="receiver"
    )