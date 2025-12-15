"""DuckDB schema definitions and initialization for socionics research platform.

This module implements the database schema from the implementation plan,
including tables for sources, personalities, labels, prompts, tokens, and
activations.
"""

import duckdb
from pathlib import Path
from typing import Optional


# SQL schema definitions
SCHEMA_SQL = """
-- 1) sources: where you scraped text from
CREATE TABLE IF NOT EXISTS sources (
  source_id         INTEGER PRIMARY KEY,
  url               TEXT,
  domain            TEXT,
  scrape_date       TIMESTAMP,
  license_note      TEXT,
  raw_text          TEXT,
  rewritten_summary TEXT,
  metadata_json     JSON
);

CREATE SEQUENCE IF NOT EXISTS sources_seq START 1;

-- 2) personalities: canonical people/characters
CREATE TABLE IF NOT EXISTS personalities (
  person_id     INTEGER PRIMARY KEY,
  name          TEXT,
  canonical_name TEXT,
  description   TEXT,
  wikipedia_url TEXT,
  source_refs   INTEGER[],
  created_at    TIMESTAMP DEFAULT current_timestamp
);

CREATE SEQUENCE IF NOT EXISTS personalities_seq START 1;

-- 3) sociotype_labels: labels assigned to persons
CREATE TABLE IF NOT EXISTS sociotype_labels (
  label_id     INTEGER PRIMARY KEY,
  person_id    INTEGER,
  label_source TEXT,
  socionics_type TEXT,
  dcnh         TEXT,
  confidence   REAL,
  evidence     TEXT,
  inserted_at  TIMESTAMP DEFAULT current_timestamp,
  FOREIGN KEY (person_id) REFERENCES personalities(person_id)
);

CREATE SEQUENCE IF NOT EXISTS sociotype_labels_seq START 1;

-- 4) prompts_runs: each LLM run (for a given prompt) from either model
CREATE TABLE IF NOT EXISTS prompt_runs (
  run_id       INTEGER PRIMARY KEY,
  person_id    INTEGER,
  prompt_text  TEXT,
  model_name   TEXT,
  model_version TEXT,
  run_date     TIMESTAMP DEFAULT current_timestamp,
  run_meta     JSON,
  FOREIGN KEY (person_id) REFERENCES personalities(person_id)
);

CREATE SEQUENCE IF NOT EXISTS prompt_runs_seq START 1;

-- 5) token_distributions: per-token logprob distributions (sparse)
CREATE TABLE IF NOT EXISTS token_distributions (
  token_dist_id INTEGER PRIMARY KEY,
  run_id        INTEGER,
  token_index   INTEGER,
  token_text    TEXT,
  token_id      INTEGER,
  topk_json     JSON,
  entropy       REAL,
  created_at    TIMESTAMP DEFAULT current_timestamp,
  FOREIGN KEY (run_id) REFERENCES prompt_runs(run_id)
);

CREATE SEQUENCE IF NOT EXISTS token_distributions_seq START 1;

-- 6) activation_vectors: optional, only if you can capture model activations
CREATE TABLE IF NOT EXISTS activation_vectors (
  activation_id INTEGER PRIMARY KEY,
  run_id        INTEGER,
  token_index   INTEGER,
  layer_index   INTEGER,
  vector_blob   BLOB,
  shape_json    JSON,
  created_at    TIMESTAMP DEFAULT current_timestamp,
  FOREIGN KEY (run_id) REFERENCES prompt_runs(run_id)
);

CREATE SEQUENCE IF NOT EXISTS activation_vectors_seq START 1;

-- 7) computed_vectors: aggregated statistics per run for quick experiments
CREATE TABLE IF NOT EXISTS computed_vectors (
  comp_id       INTEGER PRIMARY KEY,
  run_id        INTEGER,
  vector_type   TEXT,
  vector_blob   BLOB,
  meta_json     JSON,
  created_at    TIMESTAMP DEFAULT current_timestamp,
  FOREIGN KEY (run_id) REFERENCES prompt_runs(run_id)
);

CREATE SEQUENCE IF NOT EXISTS computed_vectors_seq START 1;

-- Create indices for common queries
CREATE INDEX IF NOT EXISTS idx_sources_domain ON sources(domain);
CREATE INDEX IF NOT EXISTS idx_sources_scrape_date ON sources(scrape_date);
CREATE INDEX IF NOT EXISTS idx_personalities_name ON personalities(name);
CREATE INDEX IF NOT EXISTS idx_sociotype_labels_person_id
    ON sociotype_labels(person_id);
CREATE INDEX IF NOT EXISTS idx_sociotype_labels_type
    ON sociotype_labels(socionics_type);
CREATE INDEX IF NOT EXISTS idx_prompt_runs_person_id ON prompt_runs(person_id);
CREATE INDEX IF NOT EXISTS idx_prompt_runs_model ON prompt_runs(model_name);
CREATE INDEX IF NOT EXISTS idx_token_distributions_run_id
    ON token_distributions(run_id);
CREATE INDEX IF NOT EXISTS idx_activation_vectors_run_id
    ON activation_vectors(run_id);
CREATE INDEX IF NOT EXISTS idx_computed_vectors_run_id
    ON computed_vectors(run_id);
"""


def get_connection(
    db_path: Optional[str] = None, read_only: bool = False
) -> duckdb.DuckDBPyConnection:
    """Get a connection to the DuckDB database.

    Args:
        db_path: Path to the database file. If None, uses in-memory database.
        read_only: Whether to open in read-only mode.

    Returns:
        DuckDB connection object.
    """
    if db_path is None:
        return duckdb.connect(":memory:")

    db_path_obj = Path(db_path)
    db_path_obj.parent.mkdir(parents=True, exist_ok=True)

    return duckdb.connect(str(db_path), read_only=read_only)


def init_database(db_path: Optional[str] = None) -> duckdb.DuckDBPyConnection:
    """Initialize the database with the required schema.

    Args:
        db_path: Path to the database file. If None, uses in-memory database.

    Returns:
        DuckDB connection object with initialized schema.
    """
    conn = get_connection(db_path, read_only=False)

    # Execute schema creation
    conn.execute(SCHEMA_SQL)
    conn.commit()

    return conn


def verify_schema(conn: duckdb.DuckDBPyConnection) -> dict:
    """Verify that all required tables exist in the database.

    Args:
        conn: DuckDB connection object.

    Returns:
        Dictionary with table names as keys and row counts as values.
    """
    expected_tables = [
        "sources",
        "personalities",
        "sociotype_labels",
        "prompt_runs",
        "token_distributions",
        "activation_vectors",
        "computed_vectors",
    ]

    result = {}
    for table in expected_tables:
        try:
            count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            result[table] = count
        except Exception as e:
            result[table] = f"Error: {str(e)}"

    return result
