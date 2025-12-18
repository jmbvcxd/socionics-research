"""Tests for scrape_with_fallback flow."""

import pytest

import socionics_research.pipeline.playwright_scraper as pw_module


def test_scrape_with_fallback_uses_playwright_when_http_returns_none(
    monkeypatch, tmp_path
):
    """Ensure fallback path saves via Playwright scraper."""

    class DummyHttpScraper:
        def scrape_celebrities(self, limit=None):
            return []  # Force fallback

        def save_to_database(self, conn, celebrities):
            pytest.fail("HTTP scraper should not be used for saving when fallback runs")

    class DummyPlaywrightScraper:
        def __init__(self, *args, **kwargs):
            self.saved = False

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            return False

        def scrape_celebrities(self, limit=None):
            return [
                {
                    "name": "Playwright Person",
                    "sociotype": "ILE",
                    "url": "https://example.com",
                    "confidence": 0.9,
                }
            ]

        def save_to_database(self, conn, celebrities):
            self.saved = True
            return len(celebrities)

        def search_person(self, person_name):
            return None

    class DummyConn:
        def close(self):
            pass

    # Patch dependencies to avoid real network/DB access
    monkeypatch.setattr(
        "socionics_research.pipeline.sociotype_scraper.SociotypeXyzScraper",
        lambda: DummyHttpScraper(),
    )
    monkeypatch.setattr(
        "socionics_research.database.get_connection",
        lambda *args, **kwargs: DummyConn(),
    )

    dummy_pw = DummyPlaywrightScraper()
    monkeypatch.setattr(
        pw_module, "PlaywrightSociotypeScraper", lambda *args, **kwargs: dummy_pw
    )

    db_path = tmp_path / "fallback.duckdb"
    count = pw_module.scrape_with_fallback(str(db_path), limit=1)

    assert count == 1
    assert dummy_pw.saved is True
