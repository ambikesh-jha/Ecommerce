"""
models/order.py
=================
Concepts covered: Enum-like status via String + CheckConstraint alternative
(kept simple as String here), one-to-many (Order -> OrderItem), many-to-one
(Order -> User).
"""

import uuid
from datetime import datetime
from typing import List

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, utcnow


class Order(Base):
    """A single purchase order placed by a user (may contain many products)."""

    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    # many-to-one FK back to the user who placed this order.
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)

    # A simple status field. In a production app you might use a real SQL
    # ENUM type (`sqlalchemy.Enum`) bound to a Python `enum.Enum` — shown
    # here as a comment so you know the option exists:
    #
    #   import enum
    #   class OrderStatus(str, enum.Enum):
    #       PENDING = "pending"; PAID = "paid"; SHIPPED = "shipped"
    #   status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.PENDING)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)

    total_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    # many-to-one: the "many" (Order) side pointing to the "one" (User)
    user: Mapped["User"] = relationship(back_populates="orders")

    # one-to-many: an Order has many OrderItems (line items). `cascade=
    # "all, delete-orphan"` means deleting an Order deletes its line items
    # too — that's correct here (line items are meaningless without their
    # parent order), unlike Product (which outlives any single order).
    items: Mapped[List["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"Order(id={self.id!r}, user_id={self.user_id!r}, status={self.status!r}, total={self.total_amount!r})"
