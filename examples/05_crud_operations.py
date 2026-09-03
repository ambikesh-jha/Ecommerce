"""
examples/05_crud_operations.py
=================================
Full CRUD (Create, Read, Update, Delete) using the ORM
in SQLAlchemy 2.0 style.

In 2.0 style we use select() for reading data.
The old session.query(Model) style still works,
but is considered legacy. We use select() everywhere in this project.

Concepts covered:
  - Create, Read, Update, Delete
  - session.get()
  - select()
  - session.scalar()
  - session.scalars()
  - .all()
"""

from sqlalchemy import select

from database import SessionLocal

# Make this file runnable on its own.
# create_all_tables() only creates missing tables.
# seed() skips itself if data already exists.
from create_tables import create_all_tables
from seed_data import seed

create_all_tables()
seed()

from models import Category, Product

with SessionLocal() as session:
    # -----------------------------------------------------------------
    # CREATE
    # -----------------------------------------------------------------
    
    home_category = Category(
        name="Hotel & Home",
        description="Everything for the home",
    )
    session.add(home_category)
    session.commit()
    print("CREATE -> new category:", home_category)

    kettle = Product(
        name="bottle ",
        description="1.7L electric glass kettle",
        price=29.99,
        stock=40,
        category=home_category,  # link to the category via relationship
    )
    session.add(kettle)
    session.commit()
    print("CREATE -> new product:", kettle)

    # -----------------------------------------------------------------
    # READ
    # -----------------------------------------------------------------
    # (a) session.get() — load by primary key
    # Uses the Identity Map first (no SQL if the object is already loaded)
    fetched_by_pk = session.get(Product, kettle.id)
    print("READ (get) ->", fetched_by_pk)

    # (b) select() + session.scalars() + .all()
    # Modern 2.0 way to get full ORM objects that match a query.
    #
    # session.execute(stmt)  → returns rows (tuples)
    # session.scalars(stmt)  → returns only the first column of each row
    #                          (here: the Product object itself)
    # This is what you want most of the time for single-entity queries.
    stmt = select(Product).where(Product.category_id == home_category.id)
    all_home_products = session.scalars(stmt).all()
    print("READ (select + scalars + .all()) ->", all_home_products)

    # (c) session.scalar() — same as scalars(), but returns only one result
    # (or None). Use this when you expect at most one row.
    single = session.scalar(
        select(Product).where(Product.name == "Glass Kettle")
    )
    print("READ (scalar, single row) ->", single)

    # -----------------------------------------------------------------
    # UPDATE
    # -----------------------------------------------------------------
    # The normal ORM way to update:
    #   1. Load the object
    #   2. Change its Python attributes
    #   3. Call commit()
    #
    # SQLAlchemy notices the changes and issues an UPDATE automatically.
    # You never write the UPDATE statement yourself.
    kettle.price = 24.99
    kettle.stock -= 5
    session.commit()
    print("UPDATE -> price/stock changed:", kettle)

    # -----------------------------------------------------------------
    # DELETE
    # -----------------------------------------------------------------
    session.delete(kettle)
    session.commit()
    still_there = session.get(Product, kettle.id)
    print("DELETE -> product after delete (should be None):", still_there)


if __name__ == "__main__":
    print("\nCRUD demo complete.")