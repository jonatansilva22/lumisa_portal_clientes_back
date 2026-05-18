
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, DateTime
import sqlalchemy as sa


class Base(DeclarativeBase):
    created_at = Column(
        DateTime(timezone=True),
        server_default=sa.text("DATE_ADD(now(), INTERVAL -6 HOUR)"),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=sa.text("DATE_ADD(now(), INTERVAL -6 HOUR)"),
        nullable=True
    )

