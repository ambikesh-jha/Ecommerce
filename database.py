"""
database.py
============
This is the single place where we set up everything related to the database.

We configure three main things here:

  1. Engine          – the object that knows how to talk to the database
                       (dialect + DBAPI driver + connection pool).
  
  2. SessionLocal    – a factory that creates ORM `Session` objects 
                       (what we actually use for ORM work)
  3. Base            – re-exported so other files can simply do:
                       `from database import Base`

Topics covered: 
Engine, Database Connection, Connection Pool, 
Dialect, DBAPI Driver, sessionmaker, Session.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.base import Base

# ---------------------------------------------------------------------------
# 1. ENGINE
# ---------------------------------------------------------------------------
# The Engine is the starting point of any SQLAlchemy application (both Core
# and ORM).
# It does two jobs:
#   - database connections  : Knows how to connect to the database (dialect + driver)
#   - Connection Pool       : Manages a connection pool 
#                             (reuses open connections instead of creating a new one for every query)
#
# URL format:
#   dialect+driver://user:password@host:port/database
#
# In our case:
#   dialect = "sqlite"
#   driver  = (empty) → SQLAlchemy uses Python’s built-in sqlite3 module
#
# For PostgreSQL you would write something like:
#   "postgresql+psycopg2://user:pass@localhost/dbname"
#
# echo=True → prints every SQL statement to the console (very useful while learning)
# Turn it off in production.

DATABASE_URL = "sqlite:///./ecommerce.db"   # In real apps, read this from an env variable

engine = create_engine(
    DATABASE_URL,
    # echo=True,                              # log SQL statements (great for learning)
    # SQLite only: by default a connection can only be used by the thread that created it.
    # Web apps often use different threads, so we disable that check.
    # This setting is NOT needed for PostgreSQL or MySQL.
    connect_args={"check_same_thread": False},
)

# ---------------------------------------------------------------------------
# 2. CONNECTION POOL (created automatically)
# ---------------------------------------------------------------------------
# When you call create_engine(), SQLAlchemy also creates a connection pool
# and attaches it to the engine (engine.pool).
#
# The pool keeps a few open database connections ready to use,
# so we don’t have to open a new connection for every query.
#
# For small apps you usually don’t need to change the default settings.
# If you want more control you can do:
#
#   from sqlalchemy.pool import QueuePool
#   create_engine(..., poolclass=QueuePool, pool_size=5, max_overflow=10)

# ---------------------------------------------------------------------------
# 3. SESSION FACTORY (sessionmaker)
# ---------------------------------------------------------------------------
# sessionmaker creates a factory bound to our engine.
# Every time you call SessionLocal() you get a fresh Session object.
#
# autoflush=True (default)
#   → before running a query, the Session automatically sends any pending
#     changes to the database (so the query sees the latest data).
#
# expire_on_commit=True (default)
#   → after commit(), all objects in the Session are marked as “expired”.
#     The next time you access an attribute, it is reloaded from the database.
#     This prevents you from reading old/stale data.

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=True,
    expire_on_commit=True,
)


def get_db():
    """
    Helper that gives you a database Session and makes sure it is closed
    when you’re done. This is the same pattern FastAPI uses with Depends.

    Example in FastAPI:

        @app.get("/products")
        def list_products(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
