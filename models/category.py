"""
models/category.py
====================
Concepts covered:
  - one-to-many relationship (Category → Product)
  - Optional (nullable) columns with Mapped[Optional[str]]
"""

import uuid
from typing import List, Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class Category(Base):
    """A product category, e.g. 'Electronics', 'Books'."""

    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)

    # Mapped[Optional[str]] means this column can be NULL.
    # The Optional[...] in the type hint signals nullability.
    # We also write nullable=True explicitly for clarity and is good practice.
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # One Category has many Products.
    # No cascade="delete" here on purpose.
    # Deleting a category should NOT automatically delete its products.
    # In a real store you would usually reassign the products
    # or prevent the deletion instead.
    # This is different from User.orders, which does cascade.
    products: Mapped[List["Product"]] = relationship(back_populates="category")

    def __repr__(self) -> str:
        return f"Category(id={self.id!r}, name={self.name!r})"
