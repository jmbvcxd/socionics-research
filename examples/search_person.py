#!/usr/bin/env python3
"""Example script to search for a specific person on sociotype.xyz.

This demonstrates using the Playwright fallback scraper to find data
for a specific person when they're not found via HTTP scraping.
"""

import sys  # noqa: E402
from pathlib import Path  # noqa: E402

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from socionics_research.database import init_database, get_connection  # noqa: E402
from socionics_research.pipeline import scrape_with_fallback  # noqa: E402


def main():
    """Search for a specific person and add to database."""
    import argparse

    parser = argparse.ArgumentParser(description="Search for a person on sociotype.xyz")
    parser.add_argument("name", help="Name of the person to search for")
    parser.add_argument(
        "--db",
        default="socionics_research.duckdb",
        help="Path to database file",
    )

    args = parser.parse_args()

    db_path = args.db
    person_name = args.name

    # Check if database exists, create if not
    if not Path(db_path).exists():
        print(f"Database {db_path} not found. Creating...")
        init_database(db_path)

    print("=" * 80)
    print(f"Searching for: {person_name}")
    print("=" * 80)

    # Search using fallback scraper
    print(f"\nSearching sociotype.xyz for '{person_name}'...")
    count = scrape_with_fallback(db_path, person_name=person_name)

    if count > 0:
        print(f"\n✓ Successfully found and imported data for {person_name}")

        # Display the imported data
        conn = get_connection(db_path, read_only=True)
        result = conn.execute(
            """
            SELECT
                p.name,
                l.socionics_type,
                l.dcnh,
                l.confidence,
                l.label_source,
                s.url
            FROM personalities p
            JOIN sociotype_labels l ON p.person_id = l.person_id
            JOIN sources s ON s.source_id = ANY(p.source_refs)
            WHERE LOWER(p.name) LIKE LOWER(?)
            ORDER BY p.created_at DESC
            LIMIT 1
        """,
            [f"%{person_name}%"],
        ).fetchone()

        if result:
            name, stype, dcnh, conf, source, url = result
            print(f"\n{name}")
            print(f"  Type: {stype}")
            if dcnh:
                print(f"  DCNH: {dcnh}")
            print(f"  Confidence: {conf:.1%}" if conf else "  Confidence: N/A")
            print(f"  Source: {source}")
            print(f"  URL: {url}")

        conn.close()
    else:
        print(f"\n✗ Could not find data for '{person_name}'")
        print("\nTroubleshooting:")
        print("  1. Check the spelling of the name")
        print("  2. Try a different variation (e.g., 'Einstein' vs 'Albert Einstein')")
        print("  3. Verify the person exists on sociotype.xyz")
        print("  4. Check if Playwright is properly installed:")
        print("     pip install playwright && playwright install")


if __name__ == "__main__":
    main()
