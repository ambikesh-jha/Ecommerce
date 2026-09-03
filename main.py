"""
main.py
========
Runs the entire project end-to-end:
  1. Create all tables
  2. Seed sample data
  3. Walk through every example module in order

Run with:  python main.py

Feel free to comment out sections while you're studying a specific topic —
each example module is also fully runnable on its own via:
  python -m examples.06_querying_filtering
"""


# Examples 02 and 11 are currently commented out because they require `category_id` to be provided manually.
# Previously, `category_id` was implemented as an integer, which allowed these examples to work. 
# However, using an integer ID is not considered the preferred approach for this project, 
# so we will continue using UUIDs for all including `category_id`.

# If required, `category_id` can be changed back to an integer throughout the project. 
# In that case, Examples 02 and 11 will work as expected without any additional changes.


import importlib

from create_tables import create_all_tables
from seed_data import seed

EXAMPLE_MODULES = [
    "examples.01_engine_and_connection",
    # "examples.02_core_crud",   
    "examples.04_object_lifecycle",
    "examples.05_crud_operations",
    "examples.06_querying_filtering",
    "examples.07_relationships_one_to_many",
    "examples.08_relationships_many_to_many",
    "examples.09_relationship_loading",
    "examples.10_aggregations_and_joins",
    # "examples.11_transactions",
    "examples.12_advanced_filtering",
    "examples.13_inspection_and_metadata",
    "examples.14_pydantic_validation",
]


def banner(text: str) -> None:
    line = "=" * 78
    print(f"\n{line}\n{text}\n{line}")


def main() -> None:
    banner("STEP 1: create_tables.py — building the schema")
    create_all_tables()

    banner("STEP 2: seed_data.py — inserting sample rows")
    seed()

    for module_name in EXAMPLE_MODULES:
        banner(f"RUNNING: {module_name}")
        # Each example module executes its demo code at import time (that's
        # why they're structured as top-level scripts rather than
        # functions) — importing it here is enough to run it.
        importlib.import_module(module_name)


if __name__ == "__main__":
    main()
