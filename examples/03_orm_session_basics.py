"""
examples/03_orm_session_basics.py
====================================
ORM workflow compared to Core:

    Core:  Table  →  insert/select/...  →  Connection  →  Database
    ORM:   Model class  →  instance  →  Session.add() / query  →  Database

The Session is the heart of the ORM.
It tracks changes, manages object identity, and turns Python object
changes into SQL automatically.

Concepts covered:
  - sessionmaker / SessionLocal
  - Session lifecycle
  - add(), commit(), refresh(), delete(), get()
  - Using Session as a context manager
"""

from database import SessionLocal

# Make this file runnable on its own.
# create_all_tables() only creates missing tables.
# seed() skips itself if data already exists.
from create_tables import create_all_tables
from seed_data import seed

create_all_tables()
seed()

from models import Category

# ---------------------------------------------------------------------------
# sessionmaker / SessionLocal
# ---------------------------------------------------------------------------
# SessionLocal (from database.py) is a factory.
# Calling it creates a new Session bound to our engine.
#
# Using it as a context manager:
#   with SessionLocal() as session:
# guarantees that session.close() is called even if an error happens.
# This returns the database connection back to the pool.

with SessionLocal() as session:
    # -----------------------------------------------------------------
    # add() + commit()
    # -----------------------------------------------------------------
    new_category = Category(name="Toys", description="Fun for all ages")
    session.add(new_category)  # mark the object for INSERT (state: pending)
    session.commit()           # write the INSERT to the database and commit

    print("New category id after commit:", new_category.id)
    # The id was assigned by the database (AUTOINCREMENT)
    # and SQLAlchemy put it back onto our Python object automatically.

    # -----------------------------------------------------------------
    # refresh()
    # -----------------------------------------------------------------
    # Because expire_on_commit=True (the default), after commit()
    # all attributes are marked as expired.
    # The next time you access them, SQLAlchemy reloads them from the DB.
    # refresh() forces that reload immediately.
    session.refresh(new_category)
    print("After refresh():", new_category.name, new_category.description)

    # -----------------------------------------------------------------
    # get() — fetch by primary key
    # -----------------------------------------------------------------
    # session.get(Model, primary_key) is the fastest way to load one row.
    # If the object is already in this Session’s Identity Map,
    # no SQL is sent — you get the same Python object back.
    fetched = session.get(Category, new_category.id)
    print("Fetched via get() is the SAME Python object:", fetched is new_category)

    # -----------------------------------------------------------------
    # delete()
    # -----------------------------------------------------------------
    session.delete(fetched)
    session.commit()
    print("Deleted. get() now returns:", session.get(Category, new_category.id))


if __name__ == "__main__":
    print("\nSession basics demo complete.")