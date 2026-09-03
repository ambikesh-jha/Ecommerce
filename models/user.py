
"""
models/user.py
================
Concepts covered:
  - Mapped
  - mapped_column
  - Column types (Integer, String, DateTime, Boolean)
  - Constraints (primary_key, nullable, unique, default)
  - one-to-many relationship() with back_populates
"""

import uuid
from datetime import datetime
from typing import List

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from models.base import Base, utcnow


class User(Base):
    """A registered customer of the store."""

    # Name of the actual database table this class maps to
    __tablename__ = "users"

    # ------------------------------------------------------------------
    # COLUMNS
    # ------------------------------------------------------------------
    # Mapped[int] + mapped_column() is the modern SQLAlchemy 2.0 style to declare a column.
    # The type inside Mapped[...] tells Python the type of the attribute.
    # We also write the SQL type explicitly for clarity while learning.

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    # username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False) 
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    phone_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # default= is a Python-side default (SQLAlchemy sets it before INSERT).
    # server_default= would put the default in the database itself
    # (for example: server_default=func.now()).
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    # ------------------------------------------------------------------
    # RELATIONSHIPS (ORM only — these are not real database columns)
    # ------------------------------------------------------------------
    # One User has many Orders.
    # back_populates links this side with Order.user.
    # - When you set one side, SQLAlchemy keeps the other side in sync
    # - in memory (no extra SQL needed for that).
    #
    # cascade="all, delete-orphan" means:
    #   - If a User is deleted → delete all their Orders
    #   - If an Order is removed from user.orders → delete that Order
    #     (an Order cannot exist without a User)

    orders: Mapped[List["Order"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # One User has many Reviews they have written
    reviews: Mapped[List["Review"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        # A clear __repr__ makes debugging much easier
        return f"User(id={self.id!r}, username={self.username!r}, email={self.email!r})"
    
        # output without `__repr__`:  <__main__.User object at 0x0000023A5F8A2B20>

        # output with `__repr__`:     User(id=1, username='john')




