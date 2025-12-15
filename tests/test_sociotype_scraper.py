"""Tests for sociotype.xyz scraper."""

from socionics_research.pipeline.sociotype_scraper import SociotypeXyzScraper
from socionics_research.database import init_database


def test_scraper_initialization():
    """Test that scraper can be initialized."""
    scraper = SociotypeXyzScraper()
    assert scraper.base_url == "https://sociotype.xyz/e"
    assert scraper.session is not None


def test_parse_celebrity_list_with_sample_html():
    """Test parsing of celebrity list with sample HTML."""
    scraper = SociotypeXyzScraper()

    # Sample HTML structure that might be found on sociotype sites
    sample_html = """
    <html>
        <body>
            <div class="celebrity">
                <a class="name" href="/person/1">Albert Einstein</a>
                <span class="type">LII</span>
                <span class="confidence">85%</span>
            </div>
            <div class="celebrity">
                <span class="person-name">Isaac Newton</span>
                <div class="sociotype">LII</div>
                <div class="votes">90</div>
            </div>
        </body>
    </html>
    """

    celebrities = scraper.parse_celebrity_list(sample_html)

    # Should parse at least one celebrity
    assert len(celebrities) >= 1

    # Check structure
    if len(celebrities) > 0:
        celeb = celebrities[0]
        assert "name" in celeb
        assert "sociotype" in celeb
        assert "url" in celeb
        assert "confidence" in celeb


def test_save_to_database():
    """Test saving celebrities to database."""
    # Use in-memory database for testing
    conn = init_database(None)

    scraper = SociotypeXyzScraper()

    # Sample celebrity data
    celebrities = [
        {
            "name": "Test Person",
            "sociotype": "LII",
            "url": "https://sociotype.xyz/person/test",
            "confidence": 0.85,
        }
    ]

    saved_count = scraper.save_to_database(conn, celebrities)

    assert saved_count == 1

    # Verify data was saved
    result = conn.execute(
        """
        SELECT p.name, l.socionics_type, l.confidence
        FROM personalities p
        JOIN sociotype_labels l ON p.person_id = l.person_id
        WHERE p.name = 'Test Person'
    """
    ).fetchone()

    assert result is not None
    assert result[0] == "Test Person"
    assert result[1] == "LII"
    assert abs(result[2] - 0.85) < 0.01  # Float comparison with tolerance

    conn.close()


def test_empty_html_returns_empty_list():
    """Test that empty HTML returns empty list."""
    scraper = SociotypeXyzScraper()
    celebrities = scraper.parse_celebrity_list("<html><body></body></html>")
    assert celebrities == []
