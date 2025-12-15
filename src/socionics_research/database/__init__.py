"""Database module for DuckDB storage and schema management."""

from .schema import init_database, get_connection, verify_schema

__all__ = ["init_database", "get_connection", "verify_schema"]
