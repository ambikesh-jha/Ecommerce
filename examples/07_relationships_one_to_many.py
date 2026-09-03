"""
examples/07_relationships_one_to_many.py
===========================================
Deep dive on ONE-TO-MANY / MANY-TO-ONE relationships using the already-seeded
User <-> Order data.

A single `relationship()` pair defined with `back_populates` on both models
gives you a bidirectional Python-level link:

    User.orders        (one User  -> many Order)   ["one" side]
    Order.user          (many Order -> one User)     ["many" side, has the FK]

Concepts covered: relationship(), back_populates, parent<->child navigation,
foreign key relationship, object assignment.
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
from models import Order, User

with SessionLocal() as session:
    # -----------------------------------------------------------------
    # Navigating "one" -> "many" (User.orders)
    # -----------------------------------------------------------------
    alice = session.scalar(select(User).where(User.username == "alice"))
    print("Alice's orders (via relationship, no manual JOIN needed):")
    for order in alice.orders:
        print("  ", order)

    # -----------------------------------------------------------------
    # Navigating "many" -> "one" (Order.user)
    # -----------------------------------------------------------------
    first_order = session.scalar(select(Order).limit(1))
    print("\nThe user who placed order", first_order.id, "is:", first_order.user)

    # -----------------------------------------------------------------
    # OBJECT ASSIGNMENT — the ORM way to "re-parent" a child
    # -----------------------------------------------------------------
    # Instead of manually setting `order.user_id = bob.id`, you assign the
    # RELATIONSHIP directly. SQLAlchemy computes the correct foreign key
    # for you when it flushes.
    bob = session.scalar(select(User).where(User.username == "bob"))
    print("\nBefore reassignment, order.user_id =", first_order.user_id)
    # (We don't actually commit this reassignment — just showing the API.
    #  Uncomment the next two lines to really move the order to bob.)
    # first_order.user = bob
    # session.commit()

    # -----------------------------------------------------------------
    # back_populates keeps BOTH sides in sync, in Python memory,
    # immediately — no SQL required for this sync step.
    # -----------------------------------------------------------------
    print("\nDemonstrating back_populates sync (not committed):")
    was_in_alice_orders = first_order in alice.orders
    print("  Is first_order currently in alice.orders?", was_in_alice_orders)


if __name__ == "__main__":
    print("\nOne-to-many relationship demo complete.")
