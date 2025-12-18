"""Playwright-based scraper for dynamic content from sociotype.xyz.

This module provides a fallback scraper using Playwright when the standard
HTTP scraper fails to retrieve data. It handles JavaScript-rendered content
and dynamic page elements.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
import time
import json

try:
    from playwright.sync_api import sync_playwright, Browser, Page, TimeoutError
except ImportError:
    sync_playwright = None
    Browser = None
    Page = None
    TimeoutError = Exception

import duckdb


class PlaywrightSociotypeScraper:
    """Playwright-based scraper for sociotype.xyz with JavaScript support."""

    def __init__(
        self, base_url: str = "https://sociotype.xyz/e", headless: bool = True
    ):
        """Initialize the Playwright scraper.

        Args:
            base_url: Base URL for the sociotype database
            headless: Whether to run browser in headless mode
        """
        if sync_playwright is None:
            raise ImportError(
                "playwright is required for dynamic scraping. "
                "Install with: pip install playwright && playwright install"
            )

        self.base_url = base_url
        self.headless = headless
        self.playwright = None
        self.browser = None

    def __enter__(self):
        """Context manager entry."""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def fetch_page_content(self, url: str, wait_for_selector: str = None) -> str:
        """Fetch page content using Playwright.

        Args:
            url: URL to fetch
            wait_for_selector: Optional CSS selector to wait for before parsing

        Returns:
            Page HTML content or empty string on error
        """
        try:
            page = self.browser.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=30000)

            # Wait for dynamic content to load
            if wait_for_selector:
                page.wait_for_selector(wait_for_selector, timeout=10000)
            else:
                # Default wait for common content containers
                time.sleep(2)

            content = page.content()
            page.close()
            return content

        except Exception as e:
            print(f"Error fetching {url} with Playwright: {e}")
            return ""

    def scrape_celebrity_table(self, page: Page) -> List[Dict[str, Any]]:
        """Scrape celebrity data from a Playwright page.

        Args:
            page: Playwright page object

        Returns:
            List of celebrity data dictionaries
        """
        celebrities = []

        try:
            # Wait for the table or list to load
            page.wait_for_selector(
                "table, .person-list, .celebrity-list, [data-testid='person-row']",
                timeout=10000,
            )

            # Extract data using JavaScript evaluation
            celebrity_data = page.evaluate(
                r"""
                () => {
                    const results = [];

                    // Try different selectors for different site structures
                    const selectors = [
                        'table tr',
                        '.person-row',
                        '.celebrity-item',
                        '[data-person]'
                    ];

                    for (const selector of selectors) {
                        const elements = document.querySelectorAll(selector);
                        if (elements.length > 0) {
                            elements.forEach(elem => {
                                // Try to extract name
                                const nameElem = elem.querySelector(
                                    '.name, .person-name, ' +
                                    'a[href*="person"], [data-name]'
                                );

                                // Try to extract type
                                const typeElem = elem.querySelector(
                                    '.type, .sociotype, .mbti, [data-type]'
                                );

                                // Try to extract confidence/votes
                                const confElem = elem.querySelector(
                                    '.confidence, .votes, .score, [data-confidence]'
                                );

                                if (nameElem && typeElem) {
                                    const result = {
                                        name: nameElem.textContent.trim(),
                                        sociotype: typeElem.textContent.trim(),
                                        url: nameElem.href || '',
                                        confidence: null
                                    };

                                    // Extract confidence if available
                                    if (confElem) {
                                        const confText = confElem.textContent.trim();
                                        const match = confText.match(/(\d+\.?\d*)/);
                                        if (match) {
                                            let val = parseFloat(match[1]);
                                            if (val > 1) val = val / 100;
                                            result.confidence = val;
                                        }
                                    }

                                    results.push(result);
                                }
                            });

                            // If we found results, stop trying other selectors
                            if (results.length > 0) break;
                        }
                    }

                    return results;
                }
            """
            )

            celebrities = celebrity_data if celebrity_data else []

        except Exception as e:
            print(f"Error scraping celebrity table: {e}")

        return celebrities

    def scrape_celebrities(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Scrape celebrity data using Playwright.

        Args:
            limit: Maximum number of celebrities to scrape

        Returns:
            List of celebrity dictionaries
        """
        if not self.browser:
            raise RuntimeError(
                "Browser not initialized. Use as context manager: "
                "with PlaywrightSociotypeScraper() as scraper: ..."
            )

        print(f"Scraping {self.base_url} with Playwright...")

        try:
            page = self.browser.new_page()
            page.goto(self.base_url, wait_until="domcontentloaded", timeout=30000)

            # Take a screenshot for debugging
            try:
                page.screenshot(path="/tmp/sociotype_screenshot.png")
                print("Screenshot saved to /tmp/sociotype_screenshot.png")
            except Exception:
                pass

            celebrities = self.scrape_celebrity_table(page)
            page.close()

            if limit and celebrities:
                celebrities = celebrities[:limit]

            print(f"Scraped {len(celebrities)} celebrities with Playwright")
            return celebrities

        except Exception as e:
            print(f"Error during Playwright scraping: {e}")
            return []

    def search_person(self, person_name: str) -> Optional[Dict[str, Any]]:
        """Search for a specific person on sociotype.xyz.

        Args:
            person_name: Name of the person to search for

        Returns:
            Dictionary with person data or None if not found
        """
        if not self.browser:
            raise RuntimeError("Browser not initialized.")

        print(f"Searching for {person_name} with Playwright...")

        try:
            page = self.browser.new_page()
            page.goto(self.base_url, wait_until="domcontentloaded", timeout=30000)

            # Try to find search box
            search_selectors = [
                'input[type="search"]',
                'input[name="search"]',
                'input[placeholder*="search"]',
                "#search",
                ".search-input",
            ]

            search_input = None
            for selector in search_selectors:
                try:
                    search_input = page.query_selector(selector)
                    if search_input:
                        break
                except Exception:
                    continue

            if search_input:
                # Perform search
                search_input.fill(person_name)
                page.keyboard.press("Enter")
                page.wait_for_timeout(2000)  # Wait for results

                # Try to extract result
                celebrities = self.scrape_celebrity_table(page)

                # Look for exact or close match
                for celeb in celebrities:
                    if person_name.lower() in celeb["name"].lower():
                        page.close()
                        return celeb
            else:
                # No search box, try to find in full list
                celebrities = self.scrape_celebrity_table(page)
                for celeb in celebrities:
                    if person_name.lower() in celeb["name"].lower():
                        page.close()
                        return celeb

            page.close()
            return None

        except Exception as e:
            print(f"Error searching for {person_name}: {e}")
            return None

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
                        "Public database - educational use (Playwright)",
                        json.dumps(celeb),
                        {"scraped_with": "playwright", "source": "sociotype.xyz"},
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
                        "sociotype.xyz (playwright)",
                        celeb["sociotype"],
                        None,
                        confidence,
                        f"Scraped with Playwright from {self.base_url}",
                        datetime.now(),
                    ],
                )

                conn.commit()
                saved_count += 1

            except Exception as e:
                print(f"Error saving {celeb['name']}: {e}")
                continue

        return saved_count


def scrape_with_fallback(
    db_path: str, person_name: Optional[str] = None, limit: Optional[int] = None
) -> int:
    """Scrape using HTTP first, fall back to Playwright if needed.

    Args:
        db_path: Path to DuckDB database
        person_name: Optional specific person to search for
        limit: Optional limit on number of celebrities

    Returns:
        Number of celebrities imported
    """
    from ..database import get_connection
    from .sociotype_scraper import SociotypeXyzScraper

    used_playwright = False

    # Try HTTP scraper first
    print("Attempting HTTP scraping...")
    try:
        http_scraper = SociotypeXyzScraper()
    except ImportError as e:
        print(f"HTTP scraper not available: {e}")
        http_scraper = None

    if http_scraper:
        if person_name:
            celebrities = http_scraper.scrape_celebrities()
            celebrities = [
                c for c in celebrities if person_name.lower() in c["name"].lower()
            ]
        else:
            celebrities = http_scraper.scrape_celebrities(limit=limit)
    else:
        celebrities: List[Dict[str, Any]] = []

    # If HTTP scraping failed or found nothing, try Playwright
    if not celebrities:
        print("HTTP scraping failed or returned no results.")
        print("Falling back to Playwright scraper...")

        try:
            with PlaywrightSociotypeScraper() as pw_scraper:
                if person_name:
                    result = pw_scraper.search_person(person_name)
                    celebrities = [result] if result else []
                else:
                    celebrities = pw_scraper.scrape_celebrities(limit=limit)
                used_playwright = True
        except ImportError as e:
            print(f"Playwright not available: {e}")
            return 0
        except Exception as e:
            print(f"Playwright scraping error: {e}")
            return 0

    if not celebrities:
        print("No celebrities found with either method.")
        return 0

    # Save to database
    conn = get_connection(db_path, read_only=False)

    # Use appropriate scraper for saving
    if used_playwright:
        with PlaywrightSociotypeScraper() as pw_scraper:
            saved_count = pw_scraper.save_to_database(conn, celebrities)
    else:
        saved_count = http_scraper.save_to_database(conn, celebrities)

    conn.close()
    return saved_count
