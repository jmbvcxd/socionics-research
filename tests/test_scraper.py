"""Tests for the base scraper module."""

from socionics_research.pipeline.scraper import (
    scrape_url,
    rewrite_summary,
    save_source,
    update_source_summary,
)
from socionics_research.database import init_database


def test_scrape_url_structure():
    """Test that scrape_url returns proper structure."""
    result = scrape_url("https://example.com")

    # Check required keys exist
    assert "url" in result
    assert "domain" in result
    assert "raw_text" in result
    assert "scrape_date" in result
    assert "license_note" in result
    assert "success" in result

    # Check types
    assert isinstance(result["url"], str)
    assert isinstance(result["domain"], str)
    assert isinstance(result["raw_text"], str)
    assert isinstance(result["success"], bool)


def test_scrape_url_example_domain():
    """Test scraping example.com (should succeed)."""
    result = scrape_url("https://example.com")

    # example.com should be accessible
    if result["success"]:
        assert result["domain"] == "example.com"
        assert len(result["raw_text"]) > 0
        # example.com typically contains "Example Domain"
        assert "Example" in result["raw_text"] or len(result["raw_text"]) > 10
    else:
        # If it fails, should have error message
        assert "error" in result


def test_scrape_url_invalid_url():
    """Test scraping invalid URL returns proper error."""
    result = scrape_url("https://this-domain-should-not-exist-12345.com")

    assert result["success"] is False
    assert "error" in result
    assert result["raw_text"] == ""


def test_rewrite_summary_short_text():
    """Test summary with text shorter than max_length."""
    text = "This is a short text."
    summary = rewrite_summary(text, max_length=500)

    assert summary == text


def test_rewrite_summary_long_text():
    """Test summary with text longer than max_length."""
    text = "A" * 1000
    summary = rewrite_summary(text, max_length=100)

    assert len(summary) <= 105  # 100 + ellipsis "..."
    assert summary.startswith("A")


def test_rewrite_summary_sentence_boundary():
    """Test summary breaks at sentence boundary when possible."""
    text = (
        "This is the first sentence. This is the second sentence. "
        "This is the third sentence. This is the fourth sentence."
    )
    summary = rewrite_summary(text, max_length=80)

    # Should break at a sentence boundary
    assert summary.endswith(".") or summary.endswith("...")
    assert len(summary) <= 85  # Some margin for sentence boundary


def test_rewrite_summary_empty_text():
    """Test summary with empty text."""
    summary = rewrite_summary("", max_length=100)
    assert summary == ""


def test_save_source_to_database():
    """Test saving a source to the database."""
    conn = init_database(None)  # In-memory database

    source_id = save_source(
        conn,
        url="https://example.com/test",
        raw_text="Test content",
        domain="example.com",
        license_note="Test license",
        metadata={"test": "metadata"},
    )

    assert isinstance(source_id, int)
    assert source_id > 0

    # Verify data was saved
    result = conn.execute(
        """
        SELECT url, domain, raw_text, license_note
        FROM sources
        WHERE source_id = ?
        """,
        [source_id],
    ).fetchone()

    assert result is not None
    assert result[0] == "https://example.com/test"
    assert result[1] == "example.com"
    assert result[2] == "Test content"
    assert result[3] == "Test license"

    conn.close()


def test_update_source_summary():
    """Test updating source summary."""
    conn = init_database(None)

    # Create a source
    source_id = save_source(conn, url="https://example.com", raw_text="Original text")

    # Update summary
    update_source_summary(conn, source_id, "Updated summary")

    # Verify update
    result = conn.execute(
        """
        SELECT rewritten_summary
        FROM sources
        WHERE source_id = ?
        """,
        [source_id],
    ).fetchone()

    assert result is not None
    assert result[0] == "Updated summary"

    conn.close()


def test_save_source_extracts_domain():
    """Test that save_source extracts domain if not provided."""
    conn = init_database(None)

    source_id = save_source(
        conn, url="https://test-example.com/path", raw_text="Content"
    )

    result = conn.execute(
        "SELECT domain FROM sources WHERE source_id = ?", [source_id]
    ).fetchone()

    assert result[0] == "test-example.com"

    conn.close()
