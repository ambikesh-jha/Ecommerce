"""
examples/01_engine_and_connection.py
======================================
SQLAlchemy has two main layers:

    ┌─────────────────────────────────────────┐
    │                  ORM                    │   ← Session, Query, relationship()
    ├─────────────────────────────────────────┤
    │            SQLAlchemy Core              │   ← Engine, Connection, SQL expressions
    ├─────────────────────────────────────────┤
    │              DBAPI Driver               │   ← e.g. sqlite3, psycopg2
    ├─────────────────────────────────────────┤
    │                Database                 │   ← SQLite, PostgreSQL, MySQL, ...
    └─────────────────────────────────────────┘

The ORM is built on top of Core.
Every ORM query eventually becomes a Core SQL statement that runs through the Engine.

This file focuses on:
  - Engine
  - Dialect
  - DBAPI Driver
  - Connection
  - Connection Pool
  - engine.connect() vs engine.begin()
"""

from sqlalchemy import text

from database import engine

# ---------------------------------------------------------------------------
# DIALECT + DBAPI DRIVER
# ---------------------------------------------------------------------------
# Dialect  = SQLAlchemy’s translator for a specific database (SQLite, Postgres, etc.)
# DBAPI    = the low-level Python library that actually talks to the database
#            (for SQLite this is the built-in `sqlite3` module)

print("Dialect name:      ", engine.dialect.name)
print("DBAPI module used: ", engine.dialect.dbapi.__name__)

# ---------------------------------------------------------------------------
# engine.connect() — connection WITHOUT automatic commit
# ---------------------------------------------------------------------------
# Gets a Connection from the pool.
# Any changes you make are inside a transaction, but YOU must call .commit().
# If you don’t commit, everything is rolled back when the `with` block ends.

with engine.connect() as conn:
    result = conn.execute(text("SELECT 1 + 1 AS answer"))
    row = result.one()
    print("engine.connect() demo -> 1 + 1 =", row.answer)
    # No writes here, so nothing to commit.
    # If we had done an INSERT/UPDATE, we would need: conn.commit()

# ---------------------------------------------------------------------------
# engine.begin() — connection WITH automatic commit
# ---------------------------------------------------------------------------
# Opens a connection AND starts a transaction.
# If the block finishes without error → automatically COMMITS.
# If an exception is raised → automatically ROLLS BACK.
# This is the preferred way when you write data using Core.

with engine.begin() as conn:
    conn.execute(text("CREATE TABLE IF NOT EXISTS scratch (id INTEGER PRIMARY KEY, note TEXT)"))
    conn.execute(
        text("INSERT INTO scratch (note) VALUES (:note)"),
        {"note": "hello from Core"},
    )
    # No need to call commit() — engine.begin() does it for you.

# Read the data we just inserted
with engine.connect() as conn:
    rows = conn.execute(text("SELECT * FROM scratch")).all()
    print("Rows in scratch table:", rows)

    # Clean up
    conn.execute(text("DROP TABLE scratch"))
    conn.commit()   # needed because we used engine.connect()

# ---------------------------------------------------------------------------
# CONNECTION POOL
# ---------------------------------------------------------------------------
# The Engine keeps a pool of open database connections.
# This way, calling connect() repeatedly is cheap — it reuses existing
# connections instead of opening a new one every time.

print("Pool class in use:", type(engine.pool).__name__)
print("Pool status:      ", engine.pool.status())


if __name__ == "__main__":
    print("\n(Run this file directly to see the printed output above.)")