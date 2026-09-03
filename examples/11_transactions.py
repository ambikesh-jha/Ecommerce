"""
examples/11_transactions.py
==============================
TRANSACTIONS: how to control atomicity explicitly, and the difference
between `flush()` (send SQL, keep transaction open) and `commit()` (send SQL
AND end the transaction durably).

Concepts covered: Transactions, session.begin(), flush(), rollback(),
commit().
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
    # flush() vs commit()
    # -----------------------------------------------------------------
    # `flush()` sends pending INSERT/UPDATE/DELETE statements to the DB
    # WITHIN the current transaction, but does NOT end the transaction —
    # you (or something else) can still roll it back afterwards. This is
    # useful when you need a generated primary key (e.g. for a FK on
    # another object you're about to create) but aren't ready to commit
    # yet.
    demo_product = Product(name="Transaction Demo Widget", price=1.00, stock=1, category_id=1)
    session.add(demo_product)
    session.flush()
    print("After flush() (not committed yet), id is already assigned:", demo_product.id)

    # We can still see it in THIS session's queries (flush makes it visible
    # to the current transaction)...
    found = session.scalar(select(Product).where(Product.id == demo_product.id))
    print("Visible within same transaction after flush:", found)

    # -----------------------------------------------------------------
    # rollback()
    # -----------------------------------------------------------------
    # ...but if we roll back instead of committing, the flush is UNDONE —
    # as if it never happened.
    session.rollback()
    found_after_rollback = session.get(Product, demo_product.id)
    print("After rollback(), row is gone:", found_after_rollback)

# -----------------------------------------------------------------------
# session.begin() as an explicit transaction block
# -----------------------------------------------------------------------
# A Session already "autobegins" a transaction the moment you use it, so
# `session.begin()` can only be called on a FRESH session that hasn't
# started a transaction yet (that's why we open a brand-new `with
# SessionLocal()` block here). Used as a context manager, `session.begin()`
# gives you an explicit "all or nothing" block: it commits automatically on
# success, and rolls back automatically if an exception escapes the block.
# This is the cleanest pattern for multi-step writes that must succeed or
# fail together.
with SessionLocal() as session:
    try:
        with session.begin():
            p1 = Product(name="Bundle Item A", price=5.00, stock=10, category_id=1)
            p2 = Product(name="Bundle Item B", price=7.00, stock=10, category_id=1)
            session.add_all([p1, p2])
            # Simulate a business-rule failure partway through — e.g.
            # discovering the bundle price doesn't add up.
            if (p1.price + p2.price) < 20:
                raise ValueError("Bundle price too low — aborting the whole transaction")
    except ValueError as exc:
        print(f"\nCaught expected error: {exc}")
        print("Because we used session.begin(), BOTH p1 and p2 were rolled back:")
        both_gone = session.scalars(
            select(Product).where(Product.name.in_(["Bundle Item A", "Bundle Item B"]))
        ).all()
        print("  Matching rows found (should be empty):", both_gone)


if __name__ == "__main__":
    print("\nTransactions demo complete.")
