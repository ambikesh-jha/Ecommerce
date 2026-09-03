"""
examples/06_querying_filtering.py
====================================
Deeper dive into building `select()` statements: filtering, ordering,
limiting, and pagination.

Concepts covered: select(), where(), order_by(), limit(), offset(),
pagination, filtering.
"""

from sqlalchemy import select

from database import SessionLocal

# Bootstrap: make this file runnable on its own (e.g. `python -m
# examples.06_querying_filtering`) by ensuring the schema exists and sample
# data has been seeded. Both calls are idempotent/safe to repeat (create_all
# only creates missing tables; seed() skips itself if data already exists) —
# so this is harmless even when main.py already did this work.
from create_tables import create_all_tables
from seed_data import seed

create_all_tables()
seed()
from models import Product

with SessionLocal() as session:
    # -----------------------------------------------------------------
    # WHERE — filtering
    # -----------------------------------------------------------------
    stmt = select(Product).where(Product.price < 50)
    cheap_products = session.scalars(stmt).all()
    print("Products under $50:", cheap_products)

    # Multiple conditions passed to where() are AND-ed together.
    stmt = select(Product).where(Product.price < 1000, Product.stock > 10)
    in_stock_affordable = session.scalars(stmt).all()
    print("Under $1000 AND stock > 10:", in_stock_affordable)

    # -----------------------------------------------------------------
    # ORDER BY
    # -----------------------------------------------------------------
    stmt = select(Product).order_by(Product.price.desc())
    by_price_desc = session.scalars(stmt).all()
    print("All products, most expensive first:", by_price_desc)

    # Multiple sort keys: category first, then price ascending.
    stmt = select(Product).order_by(Product.category_id, Product.price.asc())
    multi_sort = session.scalars(stmt).all()
    print("Sorted by category then price:", multi_sort)

    # -----------------------------------------------------------------
    # LIMIT / OFFSET -> PAGINATION
    # -----------------------------------------------------------------
    def get_products_page(page: int, page_size: int = 2):
        """Classic offset-based pagination. `page` is 1-indexed."""
        stmt = (
            select(Product)
            .order_by(Product.id)
            .limit(page_size)
            .offset((page - 1) * page_size)
        )
        return session.scalars(stmt).all()

    print("Page 1 (size 2):", get_products_page(1))
    print("Page 2 (size 2):", get_products_page(2))

    # NOTE on pagination at scale: OFFSET gets slower as the offset grows
    # (the DB still has to skip over N rows). For large tables, "keyset
    # pagination" (a.k.a. cursor pagination) is preferred:
    #
    #   stmt = select(Product).where(Product.id > last_seen_id).order_by(Product.id).limit(page_size)
    #
    # — using the last row's id as the "cursor" instead of counting offset.


if __name__ == "__main__":
    print("\nQuerying/filtering demo complete.")
