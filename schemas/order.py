"""
schemas/order.py
===================
Demonstrates:

  - A nested Create schema (`OrderItemCreate`) inside a list field.
  - `model_validator(mode="after")` for a rule that spans the WHOLE
    `items` list — something no single `Field(...)` constraint on one
    field could express. `field_validator` only ever sees one field (or
    one item) at a time; this rule needs to compare every item against
    every other item.
  - `unit_price` is deliberately NOT accepted on `OrderItemCreate`: it is
    always looked up server-side from `Product.price` at save time (see
    examples_sqlalchemy/14_pydantic_validation.py), so a client can never
    claim its own price for a line item.
  - `computed_field` on `OrderItemRead` (`line_total`) that only exists in
    the serialization direction, same idea as `Product.in_stock`.
"""

from datetime import datetime
from typing import Annotated, List
from uuid import UUID

from pydantic import BaseModel, Field, computed_field, model_validator

from schemas.base import ORMBase


class OrderItemCreate(BaseModel):
    product_id: UUID
    quantity: Annotated[int, Field(gt=0)]


class OrderCreate(BaseModel):
    user_id: UUID
    items: Annotated[List[OrderItemCreate], Field(min_length=1)]

    @model_validator(mode="after")
    def no_duplicate_product_lines(self) -> "OrderCreate":
        """A rule about the WHOLE `items` list, not any single item — this
        is exactly why model_validator exists where field_validator can't
        help: field_validator never sees the other items."""
        product_ids = [item.product_id for item in self.items]
        if len(product_ids) != len(set(product_ids)):
            raise ValueError(
                "Duplicate product_id in items — increase quantity on the existing line instead"
            )
        return self


class OrderItemRead(ORMBase):
    id: UUID
    product_id: UUID
    quantity: int
    unit_price: float

    @computed_field
    @property
    def line_total(self) -> float:
        return round(self.unit_price * self.quantity, 2)


class OrderRead(ORMBase):
    id: UUID
    user_id: UUID
    status: str
    total_amount: float
    created_at: datetime
    items: List[OrderItemRead] = []
