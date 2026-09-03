"""
schemas/user.py
=================
Two schemas for User, one per direction:

  UserCreate  -> validates INPUT (e.g. a signup form / API request body)
  UserRead    -> shapes OUTPUT (never leaks hashed_password)

This Create/Read split is the core reason Pydantic sits in this project at
all: `models/user.py` has ONE shape (the database row, including
`hashed_password`), but the API needs TWO different shapes depending on
direction — a class can't safely serve as both an input contract and an
output contract when some fields (password) must appear on the way in and
never on the way out.

Concepts covered: Annotated + Field constraints, reusable Annotated type
aliases, EmailStr (needs the `email-validator` package — see
requirements.txt), ConfigDict(from_attributes=True) via ORMBase.
"""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from schemas.base import ORMBase

# Reusable Annotated type aliases — define a constraint once, drop it into
# any model that needs it. This is the "reusable types" pattern: instead of
# repeating `Field(min_length=3, max_length=50)` everywhere a username
# shows up, define it once here.
Username = Annotated[
    str, Field(min_length=3, max_length=50, description="Unique handle, 3-50 chars")
]
Password = Annotated[
    str,
    Field(min_length=8, max_length=50, description="Plaintext password from the client; hashed before storage"),
]


class UserCreate(BaseModel):
    """What we accept from a signup form. NEVER returned back to a client."""

    username: Username
    email: EmailStr
    password: Password
    # Note what's deliberately absent: `id`, `is_active`, `created_at` are
    # server-assigned, and `hashed_password` is derived from `password` by
    # business logic (hashing) that lives outside Pydantic entirely — see
    # examples_sqlalchemy/14_pydantic_validation.py.


class UserRead(ORMBase):
    """What we send back out. `password` / `hashed_password` never appear
    here — that's not an oversight, it's the entire point of having two
    separate schemas instead of one."""

    id: UUID
    username: str
    email: EmailStr
    is_active: bool
    created_at: datetime
