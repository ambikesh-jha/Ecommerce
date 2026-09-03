"""
create_tables.py
==================
This file creates (and can drop) all database tables.

Concepts covered:
  - Base.metadata
  - create_all()
  - model registration

How it works:
  Base.metadata is a container that holds a `Table` for every model class
  that has been imported.
  (see models/__init__.py which import all models to ensure they are registered on Base.metadata)

  When we call Base.metadata.create_all(engine), SQLAlchemy issues
  CREATE TABLE IF NOT EXISTS ... for each table.
  It automatically creates parent tables before child tables
  (so foreign keys work correctly).
"""

from database import engine

# Import the whole models package (not just one model).
# This makes sure EVERY model is registered on Base.metadata
# before we call create_all().
#
# Common beginner mistake:
#   Forgetting to import a model → its table never gets created.
from models import Base


def create_all_tables() -> None:
    """Physically create every table in the database (if it does not already exist)."""
    print("Creating tables:", list(Base.metadata.tables.keys()))
    Base.metadata.create_all(bind=engine)    # this creates the tables in the database
    print("Done.")


def drop_all_tables() -> None:
    """Delete all tables. Useful while learning and experimenting."""
    Base.metadata.drop_all(bind=engine)  # this drops the tables in the database
    print("All tables dropped.")


if __name__ == "__main__":
    create_all_tables()
    # drop_all_tables()