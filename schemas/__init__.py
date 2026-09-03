"""
schemas/__init__.py
=====================
Mirrors the same "single import point" pattern as models/__init__.py: every
schema is re-exported here so calling code (an example file today, a
FastAPI router tomorrow) can simply do:

    from schemas import UserCreate, UserRead, ProductCreate, ...

instead of reaching into each submodule individually.

Unlike models/__init__.py, importing this package has no side effect on
any global registry — Pydantic models don't need to be "registered"
anywhere the way SQLAlchemy models need to hit Base.metadata. This file
exists purely for import convenience.
"""

from schemas.base import ORMBase  # noqa: F401

from schemas.user import UserCreate, UserRead  # noqa: F401
from schemas.category import CategoryCreate, CategoryRead  # noqa: F401
from schemas.tag import TagCreate, TagRead  # noqa: F401
from schemas.product import ProductCreate, ProductRead  # noqa: F401
from schemas.order import (  # noqa: F401
    OrderItemCreate,
    OrderCreate,
    OrderItemRead,
    OrderRead,
)
from schemas.review import ReviewCreate, ReviewRead  # noqa: F401

__all__ = [
    "ORMBase",
    "UserCreate",
    "UserRead",
    "CategoryCreate",
    "CategoryRead",
    "TagCreate",
    "TagRead",
    "ProductCreate",
    "ProductRead",
    "OrderItemCreate",
    "OrderCreate",
    "OrderItemRead",
    "OrderRead",
    "ReviewCreate",
    "ReviewRead",
]
