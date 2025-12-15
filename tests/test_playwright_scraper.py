"""Tests for Playwright scraper."""

import pytest
from socionics_research.database import init_database


# Skip tests if playwright is not installed
pytest.importorskip("playwright")


def test_playwright_scraper_initialization():
    """Test that Playwright scraper can be initialized."""
    from socionics_research.pipeline.playwright_scraper import (
        PlaywrightSociotypeScraper,
    )

    scraper = PlaywrightSociotypeScraper()
    assert scraper.base_url == "https://sociotype.xyz/e"
    assert scraper.headless is True


def test_playwright_scraper_context_manager():
    """Test that Playwright scraper works as context manager."""
    from socionics_research.pipeline.playwright_scraper import (
        PlaywrightSociotypeScraper,
    )

    try:
        with PlaywrightSociotypeScraper() as scraper:
            assert scraper.browser is not None
            assert scraper.playwright is not None
    except Exception as e:
        # If playwright browsers aren't installed, skip
        if "executable doesn't exist" in str(e).lower():
            pytest.skip("Playwright browsers not installed")
        raise


def test_save_to_database_playwright():
    """Test saving celebrities to database using Playwright scraper."""
    from socionics_research.pipeline.playwright_scraper import (
        PlaywrightSociotypeScraper,
    )

    # Use in-memory database for testing
    conn = init_database(None)

    # Create scraper (without browser for testing)
    scraper = PlaywrightSociotypeScraper()

    # Sample celebrity data
    celebrities = [
        {
            "name": "Test Playwright Person",
            "sociotype": "ILE",
            "url": "https://sociotype.xyz/person/test-pw",
            "confidence": 0.92,
        }
    ]

    saved_count = scraper.save_to_database(conn, celebrities)

    assert saved_count == 1

    # Verify data was saved
    result = conn.execute(
        """
        SELECT p.name, l.socionics_type, l.confidence, l.label_source
        FROM personalities p
        JOIN sociotype_labels l ON p.person_id = l.person_id
        WHERE p.name = 'Test Playwright Person'
    """
    ).fetchone()

    assert result is not None
    assert result[0] == "Test Playwright Person"
    assert result[1] == "ILE"
    assert abs(result[2] - 0.92) < 0.01
    assert "playwright" in result[3].lower()

    conn.close()


def test_fallback_function_exists():
    """Test that scrape_with_fallback function exists and is callable."""
    from socionics_research.pipeline.playwright_scraper import scrape_with_fallback

    assert callable(scrape_with_fallback)
