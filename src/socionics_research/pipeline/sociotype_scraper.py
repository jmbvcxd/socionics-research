"""Scraper for sociotype.xyz celebrity database.

This module provides functions to scrape personality type data for notable
figures from sociotype.xyz.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
import time

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    requests = None
    BeautifulSoup = None

import duckdb


class SociotypeXyzScraper:
    """Scraper for sociotype.xyz database."""

    def __init__(self, base_url: str = "https://sociotype.xyz/e"):
        """Initialize the scraper.

        Args:
            base_url: Base URL for the sociotype database
        """
        if requests is None or BeautifulSoup is None:
            raise ImportError(
                "requests and beautifulsoup4 are required for scraping. "
                "Install with: pip install requests beautifulsoup4"
            )

        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (compatible; SocionicsResearch/0.1; "
                    "+https://github.com/jmbvcxd/socionics-research)"
                )
            }
        )

    def fetch_page(self, url: str) -> Optional[str]:
        """Fetch a page with error handling and rate limiting.

        Args:
            url: URL to fetch

        Returns:
            HTML content or None if failed
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            time.sleep(1)  # Rate limiting: 1 second between requests
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def parse_celebrity_list(self, html: str) -> List[Dict[str, Any]]:
        """Parse the celebrity list page.

        Args:
            html: HTML content of the page

        Returns:
            List of celebrity data dictionaries with keys:
            - name: Celebrity name
            - sociotype: Their socionics type
            - url: Link to their profile
            - confidence: Confidence level if available
        """
        soup = BeautifulSoup(html, "html.parser")
        celebrities = []

        # This is a generic parser - adjust based on actual site structure
        # Looking for common patterns in socionics databases
        for row in soup.find_all(["tr", "div"], class_=["celebrity", "person"]):
            try:
                name_elem = row.find(["a", "span"], class_=["name", "person-name"])
                type_elem = row.find(
                    ["span", "div"], class_=["type", "sociotype", "mbti"]
                )

                if name_elem and type_elem:
                    celebrity = {
                        "name": name_elem.get_text(strip=True),
                        "sociotype": type_elem.get_text(strip=True),
                        "url": name_elem.get("href", ""),
                        "confidence": None,
                    }

                    # Try to extract confidence if available
                    confidence_elem = row.find(
                        ["span", "div"], class_=["confidence", "votes"]
                    )
                    if confidence_elem:
                        try:
                            confidence_text = confidence_elem.get_text(strip=True)
                            # Extract number from text like "85%" or "0.85"
                            import re

                            match = re.search(r"(\d+\.?\d*)", confidence_text)
                            if match:
                                val = float(match.group(1))
                                # Normalize to 0-1 range
                                if val > 1:
                                    val = val / 100
                                celebrity["confidence"] = val
                        except (ValueError, AttributeError):
                            pass

                    celebrities.append(celebrity)
            except Exception as e:
                print(f"Error parsing row: {e}")
                continue

        return celebrities

    def scrape_celebrities(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Scrape celebrity data from sociotype.xyz.

        Args:
            limit: Maximum number of celebrities to scrape

        Returns:
            List of celebrity dictionaries
        """
        print(f"Fetching celebrity data from {self.base_url}...")
        html = self.fetch_page(self.base_url)

        if html is None:
            print("Failed to fetch the page. Returning empty list.")
            return []

        celebrities = self.parse_celebrity_list(html)

        if limit:
            celebrities = celebrities[:limit]

        print(f"Scraped {len(celebrities)} celebrities")
        return celebrities

    def save_to_database(
        self, conn: duckdb.DuckDBPyConnection, celebrities: List[Dict[str, Any]]
    ) -> int:
        """Save scraped celebrities to the database.

        Args:
            conn: DuckDB connection
            celebrities: List of celebrity dictionaries

        Returns:
            Number of celebrities saved
        """
        saved_count = 0

        for celeb in celebrities:
            try:
                # Create source record
                source_result = conn.execute(
                    """
                    INSERT INTO sources (
                        source_id, url, domain, scrape_date,
                        license_note, raw_text, metadata_json
                    )
                    VALUES (
                        nextval('sources_seq'), ?, ?, ?,
                        ?, ?, ?
                    )
                    RETURNING source_id
                """,
                    [
                        celeb.get("url", self.base_url),
                        "sociotype.xyz",
                        datetime.now(),
                        "Public database - educational use",
                        f"Name: {celeb['name']}, Type: {celeb['sociotype']}",
                        {"scraped_from": "sociotype.xyz"},
                    ],
                ).fetchone()

                source_id = source_result[0]

                # Create personality record
                person_result = conn.execute(
                    """
                    INSERT INTO personalities (
                        person_id, name, canonical_name, description,
                        wikipedia_url, source_refs, created_at
                    )
                    VALUES (
                        nextval('personalities_seq'), ?, ?, ?,
                        ?, ?, ?
                    )
                    RETURNING person_id
                """,
                    [
                        celeb["name"],
                        celeb["name"].lower(),
                        f"Notable figure with sociotype {celeb['sociotype']}",
                        None,
                        [source_id],
                        datetime.now(),
                    ],
                ).fetchone()

                person_id = person_result[0]

                # Create label record
                confidence = celeb.get("confidence", 0.7)
                conn.execute(
                    """
                    INSERT INTO sociotype_labels (
                        label_id, person_id, label_source, socionics_type,
                        dcnh, confidence, evidence, inserted_at
                    )
                    VALUES (
                        nextval('sociotype_labels_seq'), ?, ?, ?,
                        ?, ?, ?, ?
                    )
                """,
                    [
                        person_id,
                        "sociotype.xyz",
                        celeb["sociotype"],
                        None,  # dcnh not provided by default
                        confidence,
                        f"Scraped from {self.base_url}",
                        datetime.now(),
                    ],
                )

                conn.commit()
                saved_count += 1

            except Exception as e:
                print(f"Error saving {celeb['name']}: {e}")
                continue

        return saved_count


def scrape_and_import_celebrities(db_path: str, limit: Optional[int] = None) -> int:
    """Convenience function to scrape and import celebrities.

    Args:
        db_path: Path to DuckDB database
        limit: Optional limit on number of celebrities

    Returns:
        Number of celebrities imported
    """
    from ..database import get_connection

    scraper = SociotypeXyzScraper()
    celebrities = scraper.scrape_celebrities(limit=limit)

    if not celebrities:
        print("No celebrities scraped. Check website availability.")
        return 0

    conn = get_connection(db_path, read_only=False)
    saved_count = scraper.save_to_database(conn, celebrities)
    conn.close()

    return saved_count
