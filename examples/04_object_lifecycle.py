"""
examples/04_object_lifecycle.py
==================================
Every ORM object moves through a clear set of states during its life.
Understanding these states helps you debug many common problems
(like "why didn't my change save?").

The five states are:

  TRANSIENT   → Object created in Python, never added to a Session.
                No database row yet.

  PENDING     → Added to a Session with session.add(),
                but not yet written to the database (no INSERT sent).

  PERSISTENT  → Has been flushed or committed.
                Corresponds to a real row in the database
                and is tracked by the Session's Identity Map.

  DELETED     → session.delete() was called and flushed.
                The database row is gone, but the Python object
                still exists until the transaction commits.

  DETACHED    → Was persistent, but is no longer tracked by any Session
                (Session was closed or object was expunged).
                The Python object still exists, but has no Session.

Concepts covered:
  Transient, Pending, Persistent, Deleted, Detached, Identity Map.
"""

from sqlalchemy import inspect

from database import SessionLocal

# Make this file runnable on its own.
# create_all_tables() only creates missing tables.
# seed() skips itself if data already exists.
from create_tables import create_all_tables
from seed_data import seed

create_all_tables()
seed()

from models import Tag

# ---------------------------------------------------------------------------
# 1. TRANSIENT
# ---------------------------------------------------------------------------
# Object exists only in Python. Not in any Session, no database row yet.
new_tag = Tag(name="limited-edition")
state = inspect(new_tag)
print("1) TRANSIENT   ->", "transient =", state.transient, "| pending =", state.pending)

with SessionLocal() as session:
    # -----------------------------------------------------------------
    # 2. PENDING
    # -----------------------------------------------------------------
    # Added to the Session, but not yet written to the database.
    session.add(new_tag)
    state = inspect(new_tag)
    print("2) PENDING     ->", "pending =", state.pending, "| persistent =", state.persistent)

    # -----------------------------------------------------------------
    # 3. PERSISTENT
    # -----------------------------------------------------------------
    # After commit, the object is linked to a real database row
    # and is tracked by the Session.
    session.commit()
    state = inspect(new_tag)
    print("3) PERSISTENT  ->", "persistent =", state.persistent, "| has id =", new_tag.id)

    # -----------------------------------------------------------------
    # 4. IDENTITY MAP
    # -----------------------------------------------------------------
    # Within the same Session, asking for the same row by primary key
    # always returns the exact same Python object.
    # This is called the Identity Map pattern.
    same_object = session.get(Tag, new_tag.id)
    print("4) IDENTITY MAP-> same object returned:", same_object is new_tag)

    # -----------------------------------------------------------------
    # 5. DELETED
    # -----------------------------------------------------------------
    # Marked for deletion and flushed.
    # The database row is gone, but the Python object still exists
    # until the transaction is committed.
    session.delete(new_tag)
    session.flush()
    state = inspect(new_tag)
    print("5) DELETED     ->", "deleted =", state.deleted, "| persistent =", state.persistent)
    session.commit()

# ---------------------------------------------------------------------------
# 6. DETACHED
# ---------------------------------------------------------------------------
# Create a fresh object, commit it, then detach it.
# A detached object still exists in Python but is no longer
# tracked by any Session.
with SessionLocal() as session:
    another_tag = Tag(name="clearance")
    session.add(another_tag)
    session.commit()

    # After commit, attributes are expired (expire_on_commit=True).
    # Access .id now while the object is still attached,
    # so SQLAlchemy loads and caches the value.
    cached_id = another_tag.id

    # Explicitly detach the object from the Session
    session.expunge(another_tag)
    state = inspect(another_tag)

    print("6) DETACHED    ->", "detached =", state.detached, "| still has id =", cached_id)

    # You can still read attributes that were already loaded/cached.
    # But accessing an unloaded attribute or a relationship
    # will raise DetachedInstanceError, because there is no Session left
    # to run the needed SELECT.


if __name__ == "__main__":
    print("\nObject lifecycle demo complete.")
