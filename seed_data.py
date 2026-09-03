"""
seed_data.py
=============
Populates the database with sample rows using the ORM Session — this is a
practical, real-world "Create" workflow: build Python objects, hook up
relationships in memory, `add()` + `commit()` once.

Concepts covered: Session lifecycle, `add()` / `add_all()`, `commit()`,
assigning relationships directly (instead of raw foreign key ids), the
`append()` pattern for many-to-many.
"""

from database import SessionLocal
from models import Category, Order, OrderItem, Product, Review, Tag, User


def seed() -> None:
    # A Session is a "workspace" — it tracks every object you add to it and
    # figures out the right INSERT/UPDATE/DELETE statements at flush/commit
    # time. Using it as a context manager guarantees it's closed afterwards.
    with SessionLocal() as session:
        # Guard: don't double-seed if this script is run twice.
        existing = session.query(User).first()
        if existing:
            print("Database already has data — skipping seed.")
            return

        # -------------------------------------------------------------
        # USERS
        # -------------------------------------------------------------
        alice = User(username="alice", email="alice@example.com", hashed_password="hash1")
        bob = User(username="bob", email="bob@example.com", hashed_password="hash2")

        # -------------------------------------------------------------
        # CATEGORIES
        # -------------------------------------------------------------
        electronics = Category(name="Electronics", description="Gadgets and devices")
        books = Category(name="Books", description="Physical and digital books")

        # -------------------------------------------------------------
        # TAGS
        # -------------------------------------------------------------
        tag_sale = Tag(name="on-sale")
        tag_best = Tag(name="bestseller")
        tag_new = Tag(name="new-arrival")

        # -------------------------------------------------------------
        # PRODUCTS
        # -------------------------------------------------------------
        # Note: we assign `category=electronics` (the RELATIONSHIP), not
        # `category_id=...`. SQLAlchemy figures out the FK id automatically
        # once `electronics` gets its own id at flush time. This is one of
        # the biggest ergonomic wins of the ORM over writing raw SQL.
        laptop = Product(
            name="UltraBook 14",
            description="A lightweight 14-inch laptop",
            price=999.99,
            stock=25,
            category=electronics,
        )
        headphones = Product(
            name="NoiseAway Headphones",
            description="Active noise-cancelling headphones",
            price=199.50,
            stock=100,
            category=electronics,
        )
        novel = Product(
            name="The Silent Orbit",
            description="A sci-fi thriller novel",
            price=14.99,
            stock=200,
            category=books,
        )

        # Many-to-many: `.append()` on the in-memory collection is enough —
        # SQLAlchemy will INSERT the matching rows into `product_tag` for
        # us automatically at flush time. This is the "Automatic
        # association management" topic from your list.
        laptop.tags.append(tag_sale)
        laptop.tags.append(tag_new)
        headphones.tags.append(tag_best)
        novel.tags.append(tag_new)

        # -------------------------------------------------------------
        # ORDERS + ORDER ITEMS
        # -------------------------------------------------------------
        # Alice buys a laptop and headphones in one order.
        order1 = Order(user=alice, status="paid")
        order1.items.append(OrderItem(product=laptop, quantity=1, unit_price=laptop.price))
        order1.items.append(OrderItem(product=headphones, quantity=2, unit_price=headphones.price))
        order1.total_amount = laptop.price + (headphones.price * 2)

        # Bob buys a novel.
        order2 = Order(user=bob, status="pending")
        order2.items.append(OrderItem(product=novel, quantity=1, unit_price=novel.price))
        order2.total_amount = novel.price

        # -------------------------------------------------------------
        # REVIEWS
        # -------------------------------------------------------------
        review1 = Review(user=alice, product=laptop, rating=5, comment="Excellent build quality!")
        review2 = Review(user=bob, product=novel, rating=4, comment="Gripping story, slow start.")
        review3 = Review(user=alice, product=headphones, rating=3, comment="Good but a bit heavy.")

        # -------------------------------------------------------------
        # PERSIST EVERYTHING
        # -------------------------------------------------------------
        # We only need to `add()` the "root" objects we've directly created
        # references to — SQLAlchemy's session will "cascade" and discover
        # every related object reachable through relationships (this is
        # called the "save-update cascade", which is on by default) and
        # insert them all in one flush/commit.
        session.add_all([alice, bob, electronics, books, order1, order2, review1, review2, review3])

        # `commit()` flushes all pending SQL (INSERTs here) inside a single
        # transaction and then commits it. If anything fails, nothing is
        # persisted (atomicity).
        session.commit()
        print("Seed data inserted successfully.")


if __name__ == "__main__":
    seed()
