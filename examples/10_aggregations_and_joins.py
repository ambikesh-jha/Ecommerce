"""
examples/10_aggregations_and_joins.py
========================================
Aggregations (`func.count`, `func.sum`, `func.avg`) and explicit ORM JOINs.

Concepts covered: ORM Joins, Aggregations (`func`), `group_by`, `having`.
"""

from sqlalchemy import func, select

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
from models import Category, Order, OrderItem, Product, Review, User

with SessionLocal() as session:
    # -----------------------------------------------------------------
    # Simple aggregation: count all products
    # -----------------------------------------------------------------
    total_products = session.scalar(select(func.count(Product.id)))
    print("Total products:", total_products)

    # -----------------------------------------------------------------
    # GROUP BY + aggregation: average rating per product
    # -----------------------------------------------------------------
    stmt = (
        select(Product.name, func.avg(Review.rating).label("avg_rating"), func.count(Review.id).label("review_count"))
        .join(Review, Review.product_id == Product.id)  # explicit ORM JOIN
        .group_by(Product.id)
    )
    # session.execute() (not scalars()) because each row has MULTIPLE
    # columns (name, avg_rating, count) — scalars() only makes sense for
    # single-column results.
    for row in session.execute(stmt):
        print(f"  {row.name}: avg rating {row.avg_rating:.1f} from {row.review_count} review(s)")

    # -----------------------------------------------------------------
    # JOIN across THREE tables + GROUP BY + HAVING
    # -----------------------------------------------------------------
    # "Which categories have total revenue (from order items) over $100?"
    stmt = (
        select(
            Category.name,
            func.sum(OrderItem.unit_price * OrderItem.quantity).label("revenue"),
        )
        .join(Product, Product.category_id == Category.id)
        .join(OrderItem, OrderItem.product_id == Product.id)
        .group_by(Category.id)
        .having(func.sum(OrderItem.unit_price * OrderItem.quantity) > 100)
        .order_by(func.sum(OrderItem.unit_price * OrderItem.quantity).desc())
    )
    print("\nCategories with revenue > $100:")
    for row in session.execute(stmt):
        print(f"  {row.name}: ${row.revenue}")

    # -----------------------------------------------------------------
    # JOIN User -> Order to answer "how many orders has each user placed?"
    # -----------------------------------------------------------------
    stmt = (
        select(User.username, func.count(Order.id).label("order_count"))
        .outerjoin(Order, Order.user_id == User.id)  # LEFT OUTER JOIN so
        # users with ZERO orders still show up with count = 0
        .group_by(User.id)
    )
    print("\nOrders per user:")
    for row in session.execute(stmt):
        print(f"  {row.username}: {row.order_count} order(s)")


if __name__ == "__main__":
    print("\nAggregations/joins demo complete.")
