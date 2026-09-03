"""
models/product.py
===================
The central entity of the store. Demonstrates:
  - Numeric column type (`Numeric` for money — never use float for currency!)
  - ForeignKey (many-to-one to Category)
  - many-to-one relationship() (Product -> Category)
  - one-to-many relationship() (Product -> OrderItem, Product -> Review)
  - many-to-many relationship() (Product <-> Tag)
"""
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, utcnow


class Product(Base):
    """A sellable item in the store."""

    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # `Numeric(10, 2)` = up to 10 total digits, 2 after the decimal point.
    # Using Numeric (maps to Python's Decimal) instead of Float avoids
    # binary floating-point rounding errors with money.
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    # ------------------------------------------------------------------
    # FOREIGN KEY: many-to-one to Category
    # ------------------------------------------------------------------
    # This is a REAL column (stores an integer that references
    # categories.id). `nullable=False` means every product MUST belong to
    # a category.
    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("categories.id"), nullable=False)

    # The ORM-level relationship that lets you do `product.category.name`
    # instead of manually querying by `category_id`. This is the "many"
    # side pointing back to the "one" (Category.products).
    category: Mapped["Category"] = relationship(back_populates="products")

    # One Product -> many OrderItems (every time it's purchased, a line
    # item is created). No cascade delete here on purpose: you shouldn't be
    # able to delete a product that has historical order records — in a
    # real system you'd "soft delete" (e.g. an `is_active` flag) instead.
    order_items: Mapped[List["OrderItem"]] = relationship(back_populates="product")

    # One Product -> many Reviews.
    reviews: Mapped[List["Review"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )

    # MANY-TO-MANY: Product <-> Tag, via the product_tag association table.
    tags: Mapped[List["Tag"]] = relationship(
        secondary="product_tag",
        back_populates="products",
    )

    def __repr__(self) -> str:
        return f"Product(id={self.id!r}, name={self.name!r}, price={self.price!r}, stock={self.stock!r})"

