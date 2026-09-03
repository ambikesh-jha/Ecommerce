"""
schemas/product.py
=====================
The richest schema pair in this project. Demonstrates:

  - `field_validator` (mode="after", the default) that TRANSFORMS a value
    rather than just checking it — `round_price` runs after
    Pydantic has already coerced the input to float, and rounds it.
  - Nested Read schemas (`CategoryRead`, `TagRead`) built AUTOMATICALLY
    from a Product ORM instance's relationships (`Product.category`,
    `Product.tags`) — `from_attributes=True` recurses into related objects
    the same way it reads plain columns.
  - `computed_field`: `in_stock` is derived from `stock`, never provided by
    a caller, never stored in the database — it exists only in the
    serialization (output) direction, not the validation (input) one.
"""

from typing import Annotated, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, computed_field, field_validator

from schemas.base import ORMBase
from schemas.category import CategoryRead
from schemas.tag import TagRead


class ProductCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=150)]
    description: Annotated[ Optional[str], Field(max_length=500)] = None
    price: Annotated[float, Field(gt=0, description="Price in the store's currency")]
    stock: Annotated[int, Field(ge=0)] = 0
    category_id: UUID

    # Accept tag NAMES here (not ids, not full Tag objects) — the caller
    # just says "attach these tags"; looking each name up (or creating it
    # if new) is plain ORM/business logic, done AFTER validation, in
    # examples_sqlalchemy/14_pydantic_validation.py.
    tags: List[str] = Field(default_factory=list)

    @field_validator("price")
    @classmethod
    def round_price(cls, value: float) -> float:
        """Money should never carry more than 2 decimal places."""
        return round(value, 2)


class ProductRead(ORMBase):
    id: UUID
    name: str
    description: Optional[str] = None
    price: float
    stock: int

    # Nested Read schemas: Pydantic pulls `product.category` (a single
    # Category ORM instance) and `product.tags` (a list of Tag ORM
    # instances) straight off the object, validating each one through its
    # own from_attributes-enabled schema — no manual conversion needed.
    category: CategoryRead
    tags: List[TagRead] = []

    @computed_field
    @property
    def in_stock(self) -> bool:
        """Derived from `stock` — never stored, never accepted as input."""
        return self.stock > 0
