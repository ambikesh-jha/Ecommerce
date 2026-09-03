"""
models/order_item.py
======================
A "line item" inside an Order: which product, how many, at what price
(price is snapshotted here because the Product's price may change later —
this is a real-world e-commerce pattern worth learning).

Concepts covered: two foreign keys on one table, many-to-one relationships
to two different parents (Order and Product), the difference between a
surrogate PK (what we use) and a composite PK (discussed below).
"""

import uuid
from sqlalchemy import ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class OrderItem(Base):
    """One line of an order: N units of a Product, at the price paid."""

    __tablename__ = "order_items"

    # We use a simple surrogate integer PK here rather than a composite key
    # of (order_id, product_id), because a real cart CAN contain the same
    # product added twice as separate line items (e.g. different
    # promotions applied), and a surrogate key keeps that flexible.
    #
    # If you wanted a composite PK instead (forcing at most one row per
    # order+product pair), you would do:
    #
    #   order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), primary_key=True)
    #   product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), primary_key=True)
    #
    # (no separate `id` column needed in that version).
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id"), nullable=False)

    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Snapshot of the product's price *at the time of purchase* — a classic
    # real-world reason to duplicate data rather than always joining to
    # Product.price (which could change tomorrow).
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    # Two many-to-one relationships from the same table, to two different
    # parent tables:
    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(back_populates="order_items")

    def __repr__(self) -> str:
        return (
            f"OrderItem(id={self.id!r}, order_id={self.order_id!r}, "
            f"product_id={self.product_id!r}, qty={self.quantity!r}, unit_price={self.unit_price!r})"
        )
