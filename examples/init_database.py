#!/usr/bin/env python3
"""Example script to initialize the database.

This script creates a new DuckDB database with the required schema
for the socionics research platform.
"""

import sys  # noqa: E402
from pathlib import Path  # noqa: E402

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from socionics_research.database import init_database, verify_schema  # noqa: E402


def main():
    """Initialize database and verify schema."""
    db_path = "socionics_research.duckdb"

    print(f"Initializing database: {db_path}")
    conn = init_database(db_path)

    print("\nVerifying schema...")
    tables = verify_schema(conn)

    print("\nDatabase tables created:")
    for table, count in tables.items():
        print(f"  - {table}: {count} rows")

    print(f"\nDatabase ready at: {db_path}")
    conn.close()


if __name__ == "__main__":
    main()
