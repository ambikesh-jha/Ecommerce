"""
schemas/tag.py
================
Tags are simple enough that `ProductCreate` accepts them as a plain
`list[str]` of names (see schemas/product.py) rather than a nested
`TagCreate` model on input. `TagRead` is still useful on the way OUT,
though: it's what `ProductRead.tags` is built from (a nested list of
models, one per related Tag row).
"""

from pydantic import BaseModel
from uuid import UUID

from schemas.base import ORMBase


class TagCreate(BaseModel):
    name: str


class TagRead(ORMBase):
    id: UUID
    name: str
