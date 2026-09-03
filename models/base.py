"""
models/base.py
===============
Defines the **Declarative Base** — the root class that all ORM models
inherit from. This is the SQLAlchemy 2.0 style (`DeclarativeBase`), which
replaces the old 1.x pattern of:

    Base = declarative_base()

Concepts covered: Declarative Base, `Base.metadata`, Declarative Mapping,
Table <-> Class Mapping.
"""

from datetime import datetime,timezone

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Every ORM model in the project (User, Product, Order, etc.) inherits from this class.

    When you create a new model that subclasses Base, SQLAlchemy automatically:
      1. Looks at the class attributes marked with Mapped[...]
      2. Builds a database Table for that model and stores it in Base.metadata
      3. Creates a Mapper that connects the Python class to the database table.
         This lets you:
           - create a Python object = work with a row in memory
           - session.add(instance) → INSERT into the database
           - change attributes → track them for UPDATE statements

    `Base.metadata` is what `create_tables.py` uses to physically create all the tables
    in the database with `Base.metadata.create_all(engine)`.

    You can optionally define `type_annotation_map` here to set default SQL types
    for Python types across the whole project.

    Example:
        class Base(DeclarativeBase):
            type_annotation_map = {
                datetime: DateTime(timezone=True),
            }

    With this setting, whenever you write:
        created_at: Mapped[datetime] = mapped_column()

    SQLAlchemy will automatically use DateTime(timezone=True) as the column type.
    You no longer need to repeat the type on every column.

    We keep it simple and specify column types explicitly in each model
    (see models/*.py) instead, which is clearer while learning.
    """
    pass

# A tiny reusable helper — NOT a SQLAlchemy concept itself, just a plain
# Python function we use in several models for default timestamp values.
def utcnow() -> datetime:
    """Return the current UTC time. Used as a `default=` callable for
    `created_at` columns (see models/user.py, models/order.py, etc.)."""
    return datetime.now(timezone.utc)
