"""
schemas/review.py
====================
Notice the `rating` constraint (`ge=1, le=5`) mirrors the database-level
`CheckConstraint` in models/review.py EXACTLY. That's intentional, and
worth calling out: Pydantic and the database each enforce the same rule
independently, at two different layers, for two different reasons:

  - Pydantic (here)              -> reject bad input FAST, before ever
    touching the database, with a clear field-level error message the
    caller can act on.
  - The database CheckConstraint -> the last line of defense, in case data
    ever reaches the table through a path that skips Pydantic entirely (a
    raw SQL script, a different service, a future bug).

Neither layer makes the other redundant — see the demo in
examples_sqlalchemy/14_pydantic_validation.py, step 5.
"""

from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from schemas.base import ORMBase


class ReviewCreate(BaseModel):
    user_id: UUID
    product_id: UUID
    rating: Annotated[int, Field(ge=1, le=5)]
    comment: Optional[Annotated[str, Field(max_length=500)]] = None


class ReviewRead(ORMBase):
    id: UUID
    user_id: UUID
    product_id: UUID
    rating: int
    comment: Optional[str] = None
    created_at: datetime
