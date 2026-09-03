"""
examples/14_pydantic_validation.py
=====================================
Where Pydantic fits into this project:

    Raw/untrusted data (dict, "form input", "API request")
            |
            v
    Pydantic {*}Create schema validates + coerces it   <-- schemas/*.py
            |
            v
    We build a SQLAlchemy ORM object from the validated data
            |
            v
    session.add() / commit()  <-- normal SQLAlchemy, unchanged
            |
            v
    Pydantic  {*}Read schema converts the ORM object back to a
    clean dict/JSON for output (via `model_validate`, from_attributes=True)

The SQLAlchemy models themselves (models/*.py) are NOT changed at all —
Pydantic sits entirely in front of (input) and behind (output) the existing
ORM layer. This is exactly the same role it plays in front of a real web
framework like FastAPI; we're just calling it by hand here.

Concepts covered: ValidationError handling, Create -> ORM, ORM -> Read,
nested schemas, computed_field, model_validator.
"""

from pydantic import ValidationError
from sqlalchemy import select

from database import SessionLocal

# Make this file runnable on its own, same pattern as every other example.
from create_tables import create_all_tables
from seed_data import seed

create_all_tables()
seed()

from models import Category, Order, OrderItem, Product, Review, Tag, User
from schemas import (
    CategoryRead,
    OrderCreate,
    OrderRead,
    ProductCreate,
    ProductRead,
    ReviewCreate,
    ReviewRead,
    UserCreate,
    UserRead,
)


def banner(text: str) -> None:
    print(f"\n--- {text} ---")


with SessionLocal() as session:
    # -----------------------------------------------------------------
    # 1) VALIDATE input with a *Create schema, then build the ORM object
    # -----------------------------------------------------------------
    banner("1) UserCreate: validate raw signup data")

    # Pretend this dict came from a signup form / JSON request body. Note
    # the age-old type-hints-don't-enforce-anything problem the Pydantic
    # notes start with: nothing stops a caller from sending garbage here
    # UNLESS something validates it. That "something" is UserCreate.
    raw_signup = {
        "username": "Ambikesh_jha",
        "email": "ambikesh@example.com",
        "password": "My-Password-08",
    }
    validated_user = UserCreate.model_validate(raw_signup)
    print("Validated:", validated_user)

    # Hashing the password is business logic, not Pydantic's job — Pydantic
    # only guarantees `validated_user.password` is a str of length >= 8.
    # (We use a fake "hash" here to keep this example dependency-free.)
    fake_hashed_password = f"hashed::{validated_user.password}"

    new_user = User(
        username=validated_user.username,
        email=validated_user.email,
        hashed_password=fake_hashed_password,
    )
    session.add(new_user)
    session.commit()
    print("Inserted ORM row:", new_user)

    banner("1b) UserCreate: same call, but with BAD data")
    bad_signup = {
        "username": "a",  # too short (min_length=3)
        "email": "not-an-email",  # invalid format
        "password": "short",  # too short (min_length=8)
    }
    try:
        UserCreate.model_validate(bad_signup)
    except ValidationError as exc:
        # Pydantic's ValidationError lists EVERY failing field at once,
        # not just the first one — very useful for returning a single,
        # complete error response to a caller instead of one-at-a-time.
        print(f"Rejected as expected, {exc.error_count()} error(s):")
        for error in exc.errors():
            print(f"  - {error['loc'][0]}: {error['msg']}")

    # -----------------------------------------------------------------
    # 2) ORM object -> *Read schema (serialization side)
    # -----------------------------------------------------------------
    banner("2) UserRead: convert the ORM row back out")

    # `model_validate` also accepts an arbitrary object (not just a dict)
    # because UserRead inherits ORMBase, whose `ConfigDict(from_attributes=True)`
    # tells Pydantic "go read .username, .email, ... as attributes".
    user_out = UserRead.model_validate(new_user)
    print("As a Pydantic object:", user_out)
    print("As a plain dict     :", user_out.model_dump())  # Converts the Pydantic object into a Python dictionary
    print("As a JSON string    :", user_out.model_dump_json())  # Converts the Pydantic object into a JSON string
    # Notice `hashed_password` never appears anywhere above — UserRead
    # simply doesn't declare that field, so it can never leak into output.

    # -----------------------------------------------------------------
    # 3) Nested schemas: ProductCreate -> Product (+ existing Tags)
    # -----------------------------------------------------------------
    banner("3) ProductCreate: nested tags, computed field on the way out")

    home_category = session.scalar(select(Category).where(Category.name == "Electronics"))

    raw_product = {
        "name": "Wireless Mouse",
        "description": "2.4GHz wireless mouse",
        "price": "19.999",  # string on purpose — Pydantic coerces "19.999" -> 19.999
        "stock": 25,
        "category_id": home_category.id,
        "tags": ["on-sale", "bestseller"],
    }
    validated_product = ProductCreate.model_validate(raw_product)
    # `round_price` (a field_validator in schemas/product.py) already
    # rounded this for us:
    print("Validated price (rounded to cents):", validated_product.price)

    # Look up-or-create each requested tag by name, then attach it via the
    # normal SQLAlchemy relationship — Pydantic's job (validating the tag
    # NAMES) is already done; this part is plain ORM code.
    tag_objects = []
    for tag_name in validated_product.tags:
        tag = session.scalar(select(Tag).where(Tag.name == tag_name))
        if tag is None:
            tag = Tag(name=tag_name)
            session.add(tag)
        tag_objects.append(tag)

    new_product = Product(
        name=validated_product.name,
        description=validated_product.description,
        price=validated_product.price,
        stock=validated_product.stock,
        category_id=validated_product.category_id,
        tags=tag_objects,
    )
    session.add(new_product)
    session.commit()

    product_out = ProductRead.model_validate(new_product)
    print("ProductRead ->", product_out.model_dump())
    # `category` came out as a nested dict (built from CategoryRead), and
    # `in_stock` appears even though nobody ever "set" it — it's computed.

    # -----------------------------------------------------------------
    # 4) OrderCreate: validate a whole order, snapshot prices, save it
    # -----------------------------------------------------------------
    banner("4) OrderCreate: validate items, look up prices server-side")

    raw_order = {
        "user_id": new_user.id,
        "items": [
            {"product_id": new_product.id, "quantity": 2},
        ],
    }
    validated_order = OrderCreate.model_validate(raw_order)

    order_items = []
    running_total = 0.0
    for item in validated_order.items:
        product = session.get(Product, item.product_id)
        # unit_price is snapshotted from the product's CURRENT price here —
        # never taken from client input (see the note in schemas/order.py).
        order_items.append(OrderItem(product=product, quantity=item.quantity, unit_price=product.price))
        running_total += float(product.price) * item.quantity

    new_order = Order(user_id=validated_order.user_id, items=order_items, total_amount=round(running_total, 2))
    session.add(new_order)
    session.commit()

    order_out = OrderRead.model_validate(new_order)
    print("OrderRead ->", order_out.model_dump())
    # Each item in `order_out.items` carries a computed `line_total`
    # (quantity * unit_price) that was never stored in the database.

    banner("4b) OrderCreate: rejecting a duplicated product line")
    try:
        OrderCreate.model_validate(
            {
                "user_id": new_user.id,
                "items": [
                    {"product_id": new_product.id, "quantity": 1},
                    {"product_id": new_product.id, "quantity": 3},  # duplicate!
                ],
            }
        )
    except ValidationError as exc:
        # This is the `model_validator(mode="after")` in schemas/order.py
        # firing — a rule that spans the WHOLE `items` list, not any single
        # field, so a plain `Field(...)` constraint couldn't express it.
        print("Rejected as expected:", exc.errors()[0]["msg"])

    # -----------------------------------------------------------------
    # 5) ReviewCreate: the same 1-5 rule enforced at two layers
    # -----------------------------------------------------------------
    banner("5) ReviewCreate: Pydantic AND the DB CheckConstraint agree")

    validated_review = ReviewCreate.model_validate(
        {
            "user_id": new_user.id,
            "product_id": new_product.id,
            "rating": 5,
            "comment": "Great mouse, very responsive.",
        }
    )
    new_review = Review(**validated_review.model_dump())
    session.add(new_review)
    session.commit()
    print("ReviewRead ->", ReviewRead.model_validate(new_review).model_dump())

    try:
        # Fails fast in Pydantic (Field(ge=1, le=5)) — never even reaches
        # the database's CheckConstraint at all.
        ReviewCreate.model_validate(
            {"user_id": new_user.id, "product_id": new_product.id, "rating": 9}
        )
    except ValidationError as exc:
        print("Rejected by Pydantic before hitting the DB:", exc.errors()[0]["msg"])


if __name__ == "__main__":
    print("\nPydantic + SQLAlchemy integration demo complete.")
