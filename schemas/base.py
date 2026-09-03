"""
schemas/base.py

Context:
The project uses Pydantic for two main purposes:

1. Validate input (Create/Write):
   Data received from the client, such as username, email, and password.

2. Serialize output (Read):
   Data returned to the client, while controlling which fields are exposed
   and preventing sensitive fields such as hashed_password from being leaked.

Problem solved by ORMBase:
Pydantic normally validates dictionary/JSON-like data, while SQLAlchemy
returns ORM objects when fetching data from the database.

ORMBase bridges this gap by enabling Pydantic to read attributes directly
from SQLAlchemy ORM objects.

Core idea:

    Create (e.g POST ) → client sends JSON/dict → it accepts JSON/dict input -> No ORMBase needed -> SQLAlchemy ORM object created from this input
    Read (e.g GET ) → client requests data  → SQLAlchemy ORM object fetched from the database -> ORMBase needed -> produces the API response

`from_attributes=True` allows Pydantic to create a schema directly from
an ORM object by reading its attributes.

Example:
    user = User(id=1, name="Ambikesh")
    UserRead.model_validate(user)

Without `from_attributes=True`, Pydantic expects dictionary-like data.

Only *Read schemas inherit from ORMBase because they are created from
SQLAlchemy ORM objects. *Create schemas receive input data directly from
the client.

"""

from pydantic import BaseModel, ConfigDict


class ORMBase(BaseModel):
    """Every *Read schema in schemas/*.py inherits this instead of BaseModel."""

    model_config = ConfigDict(from_attributes=True)


