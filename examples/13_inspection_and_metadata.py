"""
examples/13_inspection_and_metadata.py
=========================================
Introspecting models and the database schema itself using `inspect()` and
`Base.metadata`. Very useful for debugging and for writing generic
tooling (admin panels, serializers, etc.).

Concepts covered: Object Inspection (`inspect()`), `Base.metadata`, Mapper.
"""

from sqlalchemy import inspect, select

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
from models import Base, Product

# ---------------------------------------------------------------------------
# Base.metadata — every registered table
# ---------------------------------------------------------------------------
print("Tables known to Base.metadata:")
for table_name, table in Base.metadata.tables.items():
    columns = [c.name for c in table.columns]
    print(f"  {table_name}: {columns}")

# ---------------------------------------------------------------------------
# inspect() on a MAPPED CLASS — get Mapper-level info
# ---------------------------------------------------------------------------
mapper = inspect(Product)
print("\nMapper info for Product:")
print("  Primary key columns:", [c.name for c in mapper.primary_key])
print("  Column attributes:  ", [attr.key for attr in mapper.column_attrs])
print("  Relationship attrs: ", [rel.key for rel in mapper.relationships])

# ---------------------------------------------------------------------------
# inspect() on an INSTANCE — get its runtime state
# ---------------------------------------------------------------------------
with SessionLocal() as session:
    product = session.scalar(select(Product).limit(1))
    instance_state = inspect(product)
    print(f"\nRuntime state for {product}:")
    print("  Is persistent? ", instance_state.persistent)
    print("  Session it belongs to:", instance_state.session_id is not None)

    # `attrs` lets you introspect the loaded/unloaded/history of every
    # individual attribute — useful for building audit logs or dirty-field
    # detection.
    price_history = instance_state.attrs.price.history
    print("  Price attribute history object:", price_history)

    # Which attributes have been modified but not yet flushed?
    product.price = float(product.price) + 1
    print("  Unmodified vs modified check -> is 'price' modified now?",
          instance_state.attrs.price.history.has_changes())
    session.rollback()  # undo our test mutation so re-runs are clean


if __name__ == "__main__":
    print("\nInspection/metadata demo complete.")
