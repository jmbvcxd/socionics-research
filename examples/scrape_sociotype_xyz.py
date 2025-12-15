#!/usr/bin/env python3
"""Example script to scrape celebrity data from sociotype.xyz.

This demonstrates how to use the SociotypeXyzScraper to collect
personality type data for notable figures.
"""

import sys  # noqa: E402
from pathlib import Path  # noqa: E402

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from socionics_research.database import init_database, get_connection  # noqa: E402
from socionics_research.pipeline import (  # noqa: E402
    SociotypeXyzScraper,
    scrape_with_fallback,
)


def main():
    """Scrape celebrities from sociotype.xyz and import to database."""
    db_path = "socionics_research.duckdb"

    # Check if database exists, create if not
    if not Path(db_path).exists():
        print(f"Database {db_path} not found. Creating...")
        init_database(db_path)

    print("=" * 80)
    print("Scraping Celebrity Data from sociotype.xyz")
    print("=" * 80)

    # Option 1: Use the fallback scraper (tries HTTP first, then Playwright)
    print("\nOption 1: Using fallback scraper (HTTP → Playwright)")
    count = scrape_with_fallback(db_path, limit=50)
    print(f"\nSuccessfully imported {count} celebrities")

    # Option 2: Use the scraper directly for more control
    print("\n" + "=" * 80)
    print("Option 2: Using scraper directly")
    print("=" * 80)

    scraper = SociotypeXyzScraper()
    celebrities = scraper.scrape_celebrities(limit=10)

    if celebrities:
        print(f"\nScraped {len(celebrities)} celebrities:")
        for i, celeb in enumerate(celebrities[:5], 1):
            print(f"{i}. {celeb['name']} - {celeb['sociotype']}")
            if celeb.get("confidence"):
                print(f"   Confidence: {celeb['confidence']:.2%}")

        # Save to database
        conn = get_connection(db_path, read_only=False)
        saved = scraper.save_to_database(conn, celebrities)
        conn.close()
        print(f"\nSaved {saved} celebrities to database")
    else:
        print("\nNo celebrities scraped.")
        print("\nNote: If sociotype.xyz is unavailable, you can:")
        print("  1. Check if the site is accessible in your browser")
        print("  2. Use the add_personality.py script to add data manually")
        print("  3. Adapt the scraper to work with alternative sources")

    # Show database statistics
    conn = get_connection(db_path, read_only=True)
    stats = conn.execute(
        """
        SELECT
            COUNT(DISTINCT p.person_id) as total_personalities,
            COUNT(DISTINCT l.label_id) as total_labels,
            COUNT(DISTINCT l.socionics_type) as unique_types
        FROM personalities p
        LEFT JOIN sociotype_labels l ON p.person_id = l.person_id
    """
    ).fetchone()

    print("\n" + "=" * 80)
    print("Database Statistics")
    print("=" * 80)
    print(f"Total personalities: {stats[0]}")
    print(f"Total labels: {stats[1]}")
    print(f"Unique types: {stats[2]}")

    conn.close()


if __name__ == "__main__":
    main()
