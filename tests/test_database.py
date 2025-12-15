"""Tests for database module."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))  # noqa: E402

from socionics_research.database import init_database, verify_schema  # noqa: E402


def test_init_database():
    """Test database initialization."""
    conn = init_database(None)  # In-memory database
    assert conn is not None

    # Verify schema
    tables = verify_schema(conn)
    assert "sources" in tables
    assert "personalities" in tables
    assert "sociotype_labels" in tables
    assert "prompt_runs" in tables
    assert "token_distributions" in tables

    conn.close()


def test_empty_tables():
    """Test that newly initialized database has empty tables."""
    conn = init_database(None)
    tables = verify_schema(conn)

    for table, count in tables.items():
        assert count == 0, f"Table {table} should be empty"

    conn.close()
