"""
models/tag.py
==============
The "other side" of the Product <-> Tag many-to-many relationship.
See models/associations.py for the association table, and models/product.py
for the matching `relationship(..., secondary=...)` declaration.
"""

import uuid
from typing import List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class Tag(Base):
    """A label that can be attached to many products, e.g. 'on-sale'."""

    __tablename__ = "tags"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)

    # MANY-TO-MANY: `secondary=` points at the association table. No
    # `back_populates` foreign key lives on this model directly — the FK
    # pairs live entirely in `product_tag_association`.
    products: Mapped[List["Product"]] = relationship(
        secondary="product_tag",  # string form: the __tablename__ of the
                                   # association table (avoids needing to
                                   # import it and risk circular imports)
        back_populates="tags",
    )

    def __repr__(self) -> str:
        return f"Tag(id={self.id!r}, name={self.name!r})"
