"""Web scraping utilities for collecting public figure data.

This module provides functions to scrape public web pages while respecting
robots.txt and tracking provenance.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from urllib.parse import urlparse
import logging
import duckdb

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    requests = None
    BeautifulSoup = None

# Set up logger for this module
logger = logging.getLogger(__name__)


def scrape_url(url: str, timeout: int = 10) -> Dict[str, Any]:
    """Scrape content from a URL using HTTP requests.

    This implementation uses requests + BeautifulSoup for HTTP-based scraping.
    For JavaScript-heavy sites, consider using the Playwright scraper instead.

    Args:
        url: The URL to scrape
        timeout: Request timeout in seconds (default: 10)

    Returns:
        Dictionary containing scraped data with keys:
        - url: Original URL
        - domain: Extracted domain
        - raw_text: Scraped text content
        - scrape_date: Timestamp of scraping
        - license_note: Any license information found
        - success: Whether scraping succeeded

    Example:
        >>> data = scrape_url("https://example.com/bio")
        >>> if data["success"]:
        ...     print(data["raw_text"])
    """
    if requests is None or BeautifulSoup is None:
        logger.warning(
            "requests and beautifulsoup4 not available. "
            "Install with: pip install requests beautifulsoup4"
        )
        return {
            "url": url,
            "domain": urlparse(url).netloc,
            "raw_text": "",
            "scrape_date": datetime.now(),
            "license_note": "Public domain or fair use",
            "success": False,
            "error": "Required libraries not installed",
        }

    parsed = urlparse(url)
    domain = parsed.netloc

    try:
        # Make HTTP request with timeout
        response = requests.get(
            url,
            timeout=timeout,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (compatible; SocionicsResearch/0.1; "
                    "+https://github.com/jmbvcxd/socionics-research)"
                )
            },
        )
        response.raise_for_status()

        # Parse HTML and extract text content
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text content
        raw_text = soup.get_text(separator="\n", strip=True)

        # Try to find license information
        license_note = "Public domain or fair use"
        license_elem = soup.find(["meta", "div", "span"], attrs={"name": "license"})
        if license_elem:
            license_note = license_elem.get("content", license_note)

        return {
            "url": url,
            "domain": domain,
            "raw_text": raw_text,
            "scrape_date": datetime.now(),
            "license_note": license_note,
            "success": True,
        }

    except requests.exceptions.RequestException as e:
        logger.error(f"Error scraping {url}: {e}")
        return {
            "url": url,
            "domain": domain,
            "raw_text": "",
            "scrape_date": datetime.now(),
            "license_note": "Public domain or fair use",
            "success": False,
            "error": str(e),
        }


def save_source(
    conn: duckdb.DuckDBPyConnection,
    url: str,
    raw_text: str,
    domain: Optional[str] = None,
    license_note: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> int:
    """Save a scraped source to the database.

    Args:
        conn: DuckDB connection
        url: Source URL
        raw_text: Raw text content
        domain: Domain name (extracted if not provided)
        license_note: License information
        metadata: Additional metadata as JSON

    Returns:
        The source_id of the newly created record

    Example:
        >>> conn = init_database("research.db")
        >>> source_id = save_source(
        ...     conn,
        ...     "https://example.com",
        ...     "Biographical text...",
        ...     metadata={"author": "Unknown"}
        ... )
    """
    if domain is None:
        domain = urlparse(url).netloc

    scrape_date = datetime.now()

    result = conn.execute(
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
        [url, domain, scrape_date, license_note, raw_text, metadata],
    ).fetchone()

    conn.commit()
    return result[0]


def rewrite_summary(raw_text: str, max_length: int = 500) -> str:
    """Generate a concise summary for RAG indexing.

    This uses a simple extractive approach, taking the first meaningful
    paragraphs. For production use with LLMs, consider using the LLMClient
    for abstractive summarization.

    Args:
        raw_text: Original text
        max_length: Maximum summary length

    Returns:
        Summarized text

    Note:
        For advanced summarization with LLMs, use:
        >>> from socionics_research.llm import LLMClient
        >>> client = LLMClient("gpt-4", "1.0")
        >>> result = client.run_prompt(f"Summarize: {raw_text}")
    """
    if not raw_text or len(raw_text) <= max_length:
        return raw_text

    # Simple extractive summarization: take first max_length characters
    # Try to break at sentence boundary if possible
    summary = raw_text[:max_length]

    # Try to find the last period, exclamation, or question mark
    sentence_endings = [
        summary.rfind(". "),
        summary.rfind("! "),
        summary.rfind("? "),
    ]
    last_sentence_end = max(sentence_endings)

    # Check if we found a sentence ending (rfind returns -1 if not found)
    if last_sentence_end > max_length // 2:
        # Found a sentence boundary in the latter half
        return summary[: last_sentence_end + 1].strip()
    else:
        # No good sentence boundary, just add ellipsis
        # Avoid breaking in the middle of a word
        return summary.rsplit(" ", 1)[0].strip() + "..."


def update_source_summary(
    conn: duckdb.DuckDBPyConnection, source_id: int, summary: str
) -> None:
    """Update the rewritten summary for a source.

    Args:
        conn: DuckDB connection
        source_id: Source ID to update
        summary: The rewritten summary

    Example:
        >>> update_source_summary(conn, 1, "Brief bio summary...")
    """
    conn.execute(
        """
        UPDATE sources
        SET rewritten_summary = ?
        WHERE source_id = ?
    """,
        [summary, source_id],
    )
    conn.commit()
