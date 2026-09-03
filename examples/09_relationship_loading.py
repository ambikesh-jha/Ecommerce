"""
examples/09_relationship_loading.py
======================================
HOW relationships get loaded matters a lot for performance. This file
demonstrates the N+1 query problem and the two most common fixes.

Concepts covered: Lazy Loading (`lazy="select"`, the default), Eager
Loading, `joinedload()`, `selectinload()`, the N+1 query problem.

Run this file directly and watch the SQL logged by `echo=True` in
database.py — that's the best way to *see* the difference between these
strategies.
"""

from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

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
from models import Order, User

# ---------------------------------------------------------------------------
# LAZY LOADING (the default: lazy="select")
# ---------------------------------------------------------------------------
# By default, `relationship()` uses lazy="select": the related objects are
# NOT fetched until you actually access the attribute (e.g. `order.user`).
# That access triggers a SEPARATE SELECT query at that moment.
print("=" * 70)
print("LAZY LOADING (default) — watch for MANY separate SELECTs below")
print("=" * 70)
with SessionLocal() as session:
    orders = session.scalars(select(Order)).all()  # query #1: get all orders
    for order in orders:
        # Each `order.user` access below fires its OWN SELECT the first
        # time it's touched — this is the classic "N+1 problem": 1 query to
        # get N orders, then N more queries (one per order) to get each
        # order's user. For 3 orders that's 4 queries total; for 10,000
        # orders it's 10,001 queries — very slow.
        print(f"  Order {order.id} belongs to user: {order.user.username}")

# ---------------------------------------------------------------------------
# EAGER LOADING — selectinload()
# ---------------------------------------------------------------------------
# `selectinload()` fixes N+1 by issuing exactly ONE extra query that fetches
# ALL related rows using `WHERE parent_id IN (...)`. Total queries: 2
# (1 for orders, 1 for all their users), regardless of how many orders there
# are. This is usually the best default choice for one-to-many/many-to-one.
print("\n" + "=" * 70)
print("EAGER LOADING via selectinload() — exactly 2 queries total")
print("=" * 70)
with SessionLocal() as session:
    stmt = select(Order).options(selectinload(Order.user))
    orders = session.scalars(stmt).all()
    for order in orders:
        # No additional SELECT fires here — `order.user` was already
        # populated by the selectinload() query above.
        print(f"  Order {order.id} belongs to user: {order.user.username}")

# ---------------------------------------------------------------------------
# EAGER LOADING — joinedload()
# ---------------------------------------------------------------------------
# `joinedload()` instead uses a SQL LEFT OUTER JOIN to fetch parent + related
# rows in a SINGLE query. Great for many-to-one / one-to-one (small, bounded
# related data). Less ideal for one-to-many with LARGE collections, because
# the parent row gets duplicated once per related row in the joined result
# set (SQLAlchemy de-duplicates it back into objects for you, but the raw
# result set transferred over the wire can be much bigger).
print("\n" + "=" * 70)
print("EAGER LOADING via joinedload() — exactly 1 query total")
print("=" * 70)
with SessionLocal() as session:
    stmt = select(Order).options(joinedload(Order.user))
    orders = session.scalars(stmt).unique().all()
    # `.unique()` is REQUIRED when using joinedload() on collections to
    # de-duplicate parent rows that got repeated by the JOIN.
    for order in orders:
        print(f"  Order {order.id} belongs to user: {order.user.username}")

# ---------------------------------------------------------------------------
# selectinload() on a ONE-TO-MANY collection (User -> Orders)
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("selectinload() on a collection: User.orders")
print("=" * 70)
with SessionLocal() as session:
    stmt = select(User).options(selectinload(User.orders))
    users = session.scalars(stmt).all()
    for user in users:
        print(f"  {user.username} has {len(user.orders)} order(s)")


if __name__ == "__main__":
    print("\nRelationship loading demo complete. Scroll up to compare query counts!")
