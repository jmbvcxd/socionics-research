#!/usr/bin/env python3
"""Example script to add a personality to the database.

This demonstrates how to insert personality records and sociotype labels.
"""

import sys  # noqa: E402
from pathlib import Path  # noqa: E402

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from socionics_research.database import get_connection  # noqa: E402


def add_personality(
    conn,
    name: str,
    description: str,
    wikipedia_url: str = None,
    socionics_type: str = None,
    dcnh: str = None,
    confidence: float = 0.8,
    label_source: str = "manual_entry",
):
    """Add a personality and optional sociotype label to the database.

    Args:
        conn: DuckDB connection
        name: Name of the person/character
        description: Brief description
        wikipedia_url: Optional Wikipedia link
        socionics_type: Socionics type (e.g., "LII", "EIE")
        dcnh: DCNH classification
        confidence: Confidence in the label (0-1)
        label_source: Source of the label

    Returns:
        Tuple of (person_id, label_id)
    """
    # Insert personality
    result = conn.execute(
        """
        INSERT INTO personalities (
            person_id, name, canonical_name, description,
            wikipedia_url, source_refs
        )
        VALUES (
            nextval('personalities_seq'), ?, ?, ?,
            ?, ?
        )
        RETURNING person_id
    """,
        [name, name.lower(), description, wikipedia_url, []],
    ).fetchone()

    person_id = result[0]
    print(f"Added personality: {name} (ID: {person_id})")

    # Insert sociotype label if provided
    label_id = None
    if socionics_type:
        result = conn.execute(
            """
            INSERT INTO sociotype_labels (
                label_id, person_id, label_source, socionics_type,
                dcnh, confidence, evidence
            )
            VALUES (
                nextval('sociotype_labels_seq'), ?, ?, ?,
                ?, ?, ?
            )
            RETURNING label_id
        """,
            [
                person_id,
                label_source,
                socionics_type,
                dcnh,
                confidence,
                f"Manual entry for {name}",
            ],
        ).fetchone()

        label_id = result[0]
        print(f"Added label: {socionics_type} (confidence: {confidence})")

    conn.commit()
    return person_id, label_id


def list_personalities(conn):
    """List all personalities in the database."""
    result = conn.execute(
        """
        SELECT
            p.person_id,
            p.name,
            p.description,
            l.socionics_type,
            l.dcnh,
            l.confidence
        FROM personalities p
        LEFT JOIN sociotype_labels l ON p.person_id = l.person_id
        ORDER BY p.person_id
    """
    ).fetchall()

    if not result:
        print("No personalities in database.")
        return

    print("\nPersonalities in database:")
    print("-" * 80)
    for row in result:
        person_id, name, desc, stype, dcnh, conf = row
        print(f"ID {person_id}: {name}")
        print(f"  Description: {desc[:60]}...")
        if stype:
            print(f"  Type: {stype} (DCNH: {dcnh}, confidence: {conf:.2f})")
        print()


def main():
    """Add example personalities to the database."""
    db_path = "socionics_research.duckdb"

    # Check if database exists
    if not Path(db_path).exists():
        print(f"Database {db_path} not found.")
        print("Please run 'python examples/init_database.py' first.")
        return

    conn = get_connection(db_path, read_only=False)

    print("Adding example personalities...")
    print("=" * 80)

    # Add a few example personalities
    add_personality(
        conn,
        name="Albert Einstein",
        description=(
            "Theoretical physicist who developed the theory of relativity. "
            "Known for his intellectual curiosity and creative thinking."
        ),
        wikipedia_url="https://en.wikipedia.org/wiki/Albert_Einstein",
        socionics_type="LII",
        dcnh="N",
        confidence=0.7,
        label_source="community_consensus",
    )

    add_personality(
        conn,
        name="Steve Jobs",
        description=(
            "Co-founder of Apple Inc. Known for his visionary leadership "
            "and ability to blend technology with design."
        ),
        wikipedia_url="https://en.wikipedia.org/wiki/Steve_Jobs",
        socionics_type="EIE",
        dcnh="D",
        confidence=0.75,
        label_source="community_consensus",
    )

    add_personality(
        conn,
        name="Marie Curie",
        description=(
            "Pioneering physicist and chemist who conducted groundbreaking "
            "research on radioactivity."
        ),
        wikipedia_url="https://en.wikipedia.org/wiki/Marie_Curie",
        socionics_type="LII",
        dcnh="C",
        confidence=0.65,
        label_source="expert_analysis",
    )

    # List all personalities
    list_personalities(conn)

    conn.close()
    print(f"\nDatabase updated: {db_path}")


if __name__ == "__main__":
    main()
