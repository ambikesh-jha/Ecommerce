"""
models/review.py
==================
A product review left by a user. Links User <-> Product (both many-to-one
from Review's perspective), demonstrating a table with two FKs to two
*different* other tables (compare with OrderItem, which also has two FKs).

Also demonstrates a `CheckConstraint` for validating data at the DB level.
"""

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, utcnow


class Review(Base):
    """A star rating + comment a User left on a Product."""

    __tablename__ = "reviews"

    # __table_args__ lets us attach table-level constraints (as opposed to
    # column-level ones like `nullable=`/`unique=`). A CheckConstraint adds
    # a raw SQL condition the database enforces on every INSERT/UPDATE.
    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="ck_review_rating_range"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id"), nullable=False)

    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5, enforced above
    comment: Mapped[str] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    user: Mapped["User"] = relationship(back_populates="reviews")
    product: Mapped["Product"] = relationship(back_populates="reviews")

    def __repr__(self) -> str:
        return f"Review(id={self.id!r}, product_id={self.product_id!r}, rating={self.rating!r})"
