"""
models/__init__.py
====================
This file exists so that `Base.metadata` "knows about" every model.

Here's the subtlety that trips people up: a model class only registers
itself on `Base.metadata` when its **module is imported** (that's when the
declarative machinery runs). If you call `Base.metadata.create_all(engine)`
without ever having imported, say, `models/review.py`, the `reviews` table
will silently NOT be created — even though the file exists!

The fix: import every model module in one central place (here), and have
`create_tables.py` / anything else import `models` (this package) instead of
individual model files. This is exactly the pattern the topic list calls
"metadata.py for importing models".

Order matters a little for readability (not for correctness — SQLAlchemy
resolves string-based relationship() references lazily), so we import
"parent-like" tables first.
"""

from models.base import Base  # noqa: F401  (re-exported for convenience)

# noqa: F401 is a comment that tells the linter (usually flake8 or ruff) to ignore a specific warning.

from models.user import User  # noqa: F401
from models.category import Category  # noqa: F401
from models.tag import Tag  # noqa: F401
from models.product import Product  # noqa: F401
from models.associations import product_tag_association  # noqa: F401
from models.order import Order  # noqa: F401
from models.order_item import OrderItem  # noqa: F401
from models.review import Review  # noqa: F401

# `__all__` documents the public API of this package (optional but tidy).
__all__ = [
    "Base",  
    "User",
    "Category",
    "Tag",
    "Product",
    "product_tag_association",
    "Order",
    "OrderItem",
    "Review",
]
