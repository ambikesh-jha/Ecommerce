# E-Commerce SQLAlchemy 2.0 Learning Project

A realistic, runnable E-Commerce backend data layer built **only** with SQLAlchemy 2.0
(no FastAPI / no Pydantic — since you already know those, this project isolates
SQLAlchemy so you can learn it deeply). Every file is heavily commented and maps to
a specific SQLAlchemy concept, so you can read top-to-bottom or jump straight to a
topic.

## 1. Install

```bash
python -m venv venv             # or py -3.12 -m venv venv (for env with specific python version)  
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Uses **SQLite** (zero setup, file-based) so you can run everything immediately.
The DB file `ecommerce.db` is created in the project root.


## 4. File folow 
for understanding the concept of SQLAlchemy read the files in the order mentioned below 

---

## Complete Dependency Flow Diagram

```text
Phase 1: Foundation
        ↓
    base.py
        ↓
    01_engine_and_connection.py
        ↓
Phase 2: Core vs ORM
        ↓
    02_core_crud.py  
        ↓
    03_orm_session_basics.py
        ↓
Phase 3: Object Lifecycle
        ↓
    04_object_lifecycle.py
        ↓
    05_crud_operations.py
        ↓
Phase 4: Models (Schema)
        ↓
    associations.py
        ↓
┌─────────────┬─────────────┐─────────────┐
│ user.py     │ category.py │ tag.py      │
└─────────────┴─────────────┘─────────────┘
        ↓
    product.py (central hub)
        ↓
Phase 5: Relationships
        ↓
    06_querying_filtering.py
        ↓
┌────────────────────┬─────────────────────┐
│ 07_one_to_many.py  │ 08_many_to_many.py  │
└────────────────────┴─────────────────────┘
        ↓
Phase 6: Performance & Advanced
        ↓
    09_relationship_loading.py
        ↓
┌───────────────────────────────┬───────────────────────────┐
│ 10_aggregations_and_joins.py  │ 12_advanced_filtering.py  │
└───────────────────────────────┴───────────────────────────┘
        ↓
Phase 7: Transactions & Inspection
        ↓
    11_transactions.py
        ↓
    13_inspection_and_metadata.py
        ↓
Phase 8: Pydantic 
( Validation & Serialization, sits ALONGSIDE 
Sqlalchemy,not on top of it; independent packages)
        ↓
    base.py  (ORMBase)
        ↓
┌─────────────┬───────────────┬─────────┐
│ user.py     │ category.py   │ tag.py  │
└─────────────┴───────────────┴─────────┘
        ↓
    product.py (nested models + computed_field)
        ↓
    order.py (model_validator across a list)
        ↓
    review.py (mirrors the DB CheckConstraint)
        ↓
    14_pydantic_validation.py
```


## 2. Quick start

```bash
python main.py
```

This will:
1. Create all tables (`create_tables.py`)
2. Seed sample data (`seed_data.py`)
3. Run a tour through every example module in `examples/`

You can also run any example file individually, e.g.:

```bash
python -m examples.07_relationships_one_to_many
```

## 3. Project structure

```
ecommerce_sqlalchemy/
├── database.py              # Engine, sessionmaker (SessionLocal), Base import
├── create_tables.py         # metadata.create_all() — builds the schema
├── seed_data.py             # Populates sample rows using the ORM
├── main.py                  # Orchestrates everything, runnable end-to-end demo
│
├── models/                 # ORM models = "Model Definition" + "Relationships"
│   ├── base.py                 # DeclarativeBase (the modern 2.0 Base)
│   ├── associations.py         # product_tag many-to-many association table
│   ├── user.py                 # User model            (1)---(N) Order, Review
│   ├── category.py             # Category model        (1)---(N) Product
│   ├── product.py              # Product model          (N)---(N) Tag
│   ├── tag.py                  # Tag model
│   ├── order.py                # Order model           (1)---(N) OrderItem
│   ├── order_item.py           # OrderItem model (line items, composite-style)
│   ├── review.py               # Review model (Product <-> User)
│   └── __init__.py             # Imports every model so Base.metadata "sees" them
│
├── schemas/                  # Pydantic schemas = "Data Validation" + "Serialization" + "Type Coercion"
│   ├── base.py                 # ORMBase: ConfigDict(from_attributes=True)
│   ├── user.py                 # UserCreate / UserRead — password never leaks out
│   ├── category.py             # CategoryCreate / CategoryRead — the plain baselinepair
│   ├── tag.py                  # TagCreate / TagRead — nested inside ProductRead
│   ├── product.py              # ProductCreate / ProductRead — nested models computed_field
│   ├── order.py                # OrderCreate / OrderRead — model_validator, computed_field
│   ├── review.py               # ReviewCreate / ReviewRead — mirrors the DB CheckConstraint
│   └── __init__.py             # Re-exports every schema from one place
│
└── examples/                 # One file per concept group, runnable standalone
    ├── 01_engine_and_connection.py     # Engine, connect(), begin(), pooling, dialect
    ├── 02_core_crud.py                 # SQLAlchemy Core: insert/select/update/delete
    ├── 03_orm_session_basics.py        # sessionmaker, add, commit, refresh, get
    ├── 04_object_lifecycle.py          # transient/pending/persistent/deleted/detached
    ├── 05_crud_operations.py           # Full ORM CRUD using 2.0 select()
    ├── 06_querying_filtering.py        # where, order_by, limit/offset, pagination
    ├── 07_relationships_one_to_many.py # relationship(), back_populates, FK
    ├── 08_relationships_many_to_many.py# secondary=, association table, append()
    ├── 09_relationship_loading.py      # lazy, joinedload, selectinload, N+1 problem
    ├── 10_aggregations_and_joins.py    # func, group_by, joins across tables
    ├── 11_transactions.py              # begin(), flush(), rollback(), commit()
    ├── 12_advanced_filtering.py        # and_, or_, in_, between, like, exists
    ├── 13_inspection_and_metadata.py   # inspect(), Base.metadata, mapper info
    └── 14_pydantic_validation.py       # schemas/ <-> models/ integration, full round trip
```



## 5. Topic → File map

| Topic (from your list)                          | File(s)                                                   |
|---------------------------------------------------|-------------------------------------------------------------|
| Installation    | `requirements.txt` |
| configuration    | `database.py`             |
| SQLAlchemy Core (engine, connection, pool, dialect, DBAPI, Core CRUD) | `examples/01_engine_and_connection.py`, `examples/02_core_crud.py` |
| ORM fundamentals (DeclarativeBase, metadata, mapper, model, instance) | `models/base.py`, `models/__init__.py`, `examples/13_inspection_and_metadata.py` |
| Model definition (Mapped, mapped_column, types, constraints, FK) | every file in `models/`                                    |
| Session management (sessionmaker, add/commit/refresh/delete/get) | `database.py`, `examples/03_orm_session_basics.py`         |
| Object lifecycle (transient/pending/persistent/deleted/detached, identity map) | `examples/04_object_lifecycle.py`                          |
| CRUD operations                                    | `examples/05_crud_operations.py`                            |
| Querying (select/where/order_by/limit/offset, pagination) | `examples/06_querying_filtering.py`                         |
| Relationships (1-to-many, many-to-1, many-to-many) | `models/*.py`, `examples/07_*`, `examples/08_*`             |
| Relationship loading (lazy, joined, selectin, N+1) | `examples/09_relationship_loading.py`                        |
| Metadata (`create_all`, model registration)         | `create_tables.py`, `models/__init__.py`                    |
| Database schema concepts (PK, FK, unique, nullable, default, composite PK) | `models/*.py` (see comments), `models/order_item.py` for composite key discussion |
| Advanced: cascades, joins, aggregations, transactions, inspect, advanced filtering | `examples/10_*`, `examples/11_*`, `examples/12_*`, `examples/13_*` |


## 6. Pydantic layer (`schemas/`)

Pydantic sits entirely **in front of** and **behind** the SQLAlchemy layer —
`models/*.py` was not changed at all to add it:

```text
raw dict/JSON  --> (*Create schema: validate + coerce) --> build ORM object
  [ input ]           [ Pydantic ]                      [ SQLAlchemy ]
                                                              |
                                                              v
                                                    session.add/commit()
                                                              |
                                                              v
JSON/dict out  <-- (*Read schema: model_validate) <---- ORM object back out
  [ output ]          [ Pydantic ]                      [ SQLAlchemy ]
```

| Topic                                              | File(s)                                                      |
|-----------------------------------------------------|----------------------------------------------------------------|
| BaseModel, type validation & coercion, ValidationError | `schemas/user.py`, demoed in `examples_sqlalchemy/14_*`      |
| Field constraints, reusable `Annotated` type aliases | `schemas/user.py` (`Username`, `Password`), `schemas/*.py`   |
| Nested models (model-inside-model)                 | `schemas/product.py` (`category`, `tags`), `schemas/order.py` (`items`) |
| `field_validator` (transform one field)            | `schemas/product.py` — `round_price`                |
| `model_validator` (cross-field / whole-list rule)  | `schemas/order.py` — `no_duplicate_product_lines`             |
| `computed_field` (derived, output-only)            | `schemas/product.py` — `in_stock`; `schemas/order.py` — `line_total` |
| `EmailStr`                                          | `schemas/user.py`                                              |
| Validation schema vs. serialization schema          | any `*Create` vs `*Read` pair — e.g. `UserCreate` vs `UserRead` |
| `ConfigDict(from_attributes=True)` (ORM -> Pydantic) | `schemas/base.py` (`ORMBase`)                                 |
| Two enforcement layers agreeing (Pydantic + DB CheckConstraint) | `schemas/review.py` vs `models/review.py`         |
| Full validate -> ORM -> serialize round trip, for every model | `examples_sqlalchemy/14_pydantic_validation.py`     |

`schemas/*.py` never imports from `models/*.py` (or vice versa) — they're
independent packages that only meet in calling code. That's what keeps this
project from being "just SQLAlchemy": the validation layer is real,
separate, and ready to sit behind a FastAPI router next.

---