"""
examples/02_core_crud.py
==========================
SQLAlchemy CORE CRUD using the SQL Expression Language.

Instead of writing raw SQL strings (as used in 01_engine_and_connection.py), we build SQL with Python objects:
  - insert()
  - select()
  - update()
  - delete()

We do this WITHOUT using the ORM Session at all.
Everything works directly on Table objects.

We reuse our ORM model’s table (Product.__table__) as a Core Table.
This shows that every declarative model has a real Core Table underneath.

Concepts covered:
  - Core Workflow
  - SQL Expression Language
  - Core CRUD (insert / select / update / delete)
  - engine.begin()
"""

from sqlalchemy import delete, insert, select, update

from create_tables import create_all_tables
from database import engine
from models import Product

create_all_tables()  # make sure the table exists before we use it

# Get the Core Table object that sits under our Product ORM model
products_table = Product.__table__

# ---------------------------------------------------------------------------
# CORE INSERT
# ---------------------------------------------------------------------------
with engine.begin() as conn:
    stmt = insert(products_table).values(
        name="Core-Inserted Mug",
        description="Inserted via SQLAlchemy Core, not the ORM",
        price=9.99,
        stock=50,
        category_id=1,  # Core does NOT understand relationships.
                        # You must give the foreign key id yourself.
    )
    result = conn.execute(stmt)
    new_id = result.inserted_primary_key[0]
    print("Inserted product id:", new_id)

# ---------------------------------------------------------------------------
# CORE SELECT
# ---------------------------------------------------------------------------
with engine.connect() as conn:
    # products_table.c  →  access the columns of the table
    stmt = select(products_table).where(products_table.c.name == "Core-Inserted Mug")
    row = conn.execute(stmt).one()
    print("Selected row:", row)

# ---------------------------------------------------------------------------
# CORE UPDATE
# ---------------------------------------------------------------------------
with engine.begin() as conn:
    stmt = (
        update(products_table)
        .where(products_table.c.id == new_id)
        .values(stock=45, price=8.99)
    )
    conn.execute(stmt)
    print("Updated stock/price for product id", new_id)

# ---------------------------------------------------------------------------
# CORE DELETE
# ---------------------------------------------------------------------------
with engine.begin() as conn:
    stmt = delete(products_table).where(products_table.c.id == new_id)
    conn.execute(stmt)
    print("Deleted product id", new_id)

# Check that the row is really gone
with engine.connect() as conn:
    remaining = conn.execute(
        select(products_table).where(products_table.c.id == new_id)
    ).all()
    print("Rows remaining with that id (should be empty):", remaining)


if __name__ == "__main__":
    print("\nCore CRUD demo complete.")