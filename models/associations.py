"""
models/associations.py
========================
Many-to-Many relationships need an association table.

An association table is a simple Table (Core style, not a full model class)
that sits between two entity tables and stores pairs of foreign keys.

Example here:
  Product ↔ Tag
  - One product can have many tags
  - One tag can belong to many products
  (e.g. "electronics", "on-sale", "bestseller")

Concepts covered:
  - Association Table
  - Composite Primary Key
  - secondary= (used later in product.py and tag.py)
"""

from sqlalchemy import Column, ForeignKey, Table

from models.base import Base

# This is a Core-style Table, not a declarative class.
# We use a plain Table because it only stores foreign keys
# and does not need its own Python behavior.
#
# If we needed extra columns on the link itself
# (for example "added_at"), we would use a full model class instead
# (see the alternative pattern at the bottom).

product_tag_association = Table(
    "product_tag",
    Base.metadata,  # register this table on the same MetaData as our models
    Column(
        "product_id",
        ForeignKey("products.id"),
        primary_key=True,  # part 1 of the composite primary key
    ),
    Column(
        "tag_id",
        ForeignKey("tags.id"),
        primary_key=True,  # part 2 of the composite primary key
    ),
    # Together (product_id, tag_id) form a composite primary key.
    # This prevents the same product from being linked to the same tag twice.
)

# ---------------------------------------------------------------------------
# Alternative pattern (not used in this project)
# ---------------------------------------------------------------------------
# If the relationship itself needs extra data
# (for example: who added the tag and when),
# use a full mapped class instead of a plain Table:
#
#   class ProductTag(Base):
#       __tablename__ = "product_tag"
#       product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), primary_key=True)
#       tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), primary_key=True)
#       added_at: Mapped[datetime] = mapped_column(default=utcnow)
#
# Then both Product and Tag would use relationship() through ProductTag
# instead of using 'secondary='.
# ---------------------------------------------------------------------------