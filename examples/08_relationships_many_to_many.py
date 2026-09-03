"""
examples/08_relationships_many_to_many.py
============================================
Deep dive on MANY-TO-MANY relationships using Product <-> Tag.

Recall from models/associations.py: there's a plain `product_tag` Table
(Core-style, with a composite primary key of product_id + tag_id) sitting
between Product and Tag. Both `Product.tags` and `Tag.products` are declared
with `secondary="product_tag"`, which tells SQLAlchemy "route through this
association table automatically".

Concepts covered: Association Table, `secondary`, Composite Primary Key,
`append()`, automatic association-row management (no manual INSERT into the
association table needed).
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
from models import Product, Tag

with SessionLocal() as session:
    # -----------------------------------------------------------------
    # Navigating Product -> Tags
    # -----------------------------------------------------------------
    laptop = session.scalar(select(Product).where(Product.name == "UltraBook 14"))
    print("Tags on the laptop:", laptop.tags)

    # -----------------------------------------------------------------
    # Navigating Tag -> Products (the REVERSE direction)
    # -----------------------------------------------------------------
    new_arrival_tag = session.scalar(select(Tag).where(Tag.name == "new-arrival"))
    print("Products tagged 'new-arrival':", new_arrival_tag.products)

    # -----------------------------------------------------------------
    # append() — automatic association-row management
    # -----------------------------------------------------------------
    # We create a brand-new tag and attach it to an existing product using
    # plain Python list `.append()`. SQLAlchemy will INSERT the necessary
    # row into `product_tag` automatically at commit — we NEVER touch the
    # association table directly.
    clearance_tag = Tag(name="clearance-demo")
    laptop.tags.append(clearance_tag)
    session.add(clearance_tag)  # new object -> still needs to be added
    session.commit()

    reloaded_laptop = session.get(Product, laptop.id)
    print("\nLaptop tags after append+commit:", reloaded_laptop.tags)

    # -----------------------------------------------------------------
    # Removing an association — just remove() from the collection, don't
    # delete the Tag itself. This deletes the ROW IN product_tag, not the
    # Tag row (a Tag can be attached to other products).
    # -----------------------------------------------------------------
    reloaded_laptop.tags.remove(clearance_tag)
    session.commit()
    print("Laptop tags after remove():", session.get(Product, laptop.id).tags)

    # Clean up the demo tag entirely so re-running this script is idempotent.
    still_exists = session.get(Tag, clearance_tag.id)
    if still_exists:
        session.delete(still_exists)
        session.commit()


if __name__ == "__main__":
    print("\nMany-to-many relationship demo complete.")
