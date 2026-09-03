"""
examples/12_advanced_filtering.py
====================================
Advanced WHERE-clause construction: boolean composition (and_/or_),
membership (in_), ranges (between), pattern matching (like), and existence
checks (exists).

Concepts covered: and_, or_, in_, between, like, exists.
"""

from sqlalchemy import and_, exists, or_, select

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
from models import Order, Product, Review

with SessionLocal() as session:
    # -----------------------------------------------------------------
    # or_()  — either condition can match
    # -----------------------------------------------------------------
    stmt = select(Product).where(
        or_(Product.price < 20, Product.stock > 150)
    )
    print("Cheap OR high-stock products:", session.scalars(stmt).all())

    # -----------------------------------------------------------------
    # and_()  — explicit AND (equivalent to comma-separating conditions
    # inside .where(), but useful when combined with or_() for grouping)
    # -----------------------------------------------------------------
    stmt = select(Product).where(
        or_(
            and_(Product.price < 20, Product.stock > 100),
            and_(Product.price > 500, Product.stock < 50),
        )
    )
    print("\n(cheap AND well-stocked) OR (expensive AND scarce):", session.scalars(stmt).all())

    # -----------------------------------------------------------------
    # in_()  — membership test, translates to SQL "IN (...)"
    # -----------------------------------------------------------------
    stmt = select(Product).where(Product.name.in_(["The Silent Orbit", "UltraBook 14"]))
    print("\nProducts with specific names:", session.scalars(stmt).all())

    # -----------------------------------------------------------------
    # between()  — inclusive range test
    # -----------------------------------------------------------------
    stmt = select(Product).where(Product.price.between(10, 200))
    print("\nProducts priced between $10 and $200:", session.scalars(stmt).all())

    # -----------------------------------------------------------------
    # like()  — SQL pattern matching ('%' = any chars, '_' = single char)
    # -----------------------------------------------------------------
    stmt = select(Product).where(Product.name.like("%Book%"))
    print("\nProducts with 'Book' in the name:", session.scalars(stmt).all())
    # case-insensitive version: Product.name.ilike("%book%")

    # -----------------------------------------------------------------
    # exists()  — correlated subquery: "does at least one match exist?"
    # -----------------------------------------------------------------
    # "Find every product that has at least one 5-star review."
    five_star_exists = (
        select(Review.id)
        .where(Review.product_id == Product.id, Review.rating == 5)
        .correlate(Product)
    )
    stmt = select(Product).where(exists(five_star_exists))
    print("\nProducts with at least one 5-star review:", session.scalars(stmt).all())

    # "Find every user who has placed at least one order" (same idea,
    # different tables).
    from models import User

    has_order = select(Order.id).where(Order.user_id == User.id).correlate(User)
    stmt = select(User).where(exists(has_order))
    print("Users who have placed at least one order:", session.scalars(stmt).all())


if __name__ == "__main__":
    print("\nAdvanced filtering demo complete.")
