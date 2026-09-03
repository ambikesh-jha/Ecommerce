"""
schemas/category.py
=====================
The simplest Create/Read pair in the project — no cross-field rules, no
nested models, no computed fields. Deliberately plain, so it's a clean
baseline to compare the fancier schemas (product.py, order.py) against.
"""

from typing import Annotated, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from schemas.base import ORMBase


class CategoryCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=80)]
    description: Optional[str] = None


class CategoryRead(ORMBase):
    id: UUID
    name: str
    description: Optional[str] = None
