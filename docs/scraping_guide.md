# Scraping Guide

This guide explains how to use the intelligent scraping system to collect personality type data from sociotype.xyz.

## Overview

The scraping system uses a **two-tier approach** for maximum reliability:

1. **HTTP Scraper (Primary)**: Fast and lightweight, uses requests + BeautifulSoup
2. **Playwright Scraper (Fallback)**: Handles JavaScript-rendered content with full browser automation

When data cannot be found with the HTTP scraper, the system automatically falls back to Playwright.

## Installation

### Basic Setup

```bash
pip install -r requirements.txt
```

### Playwright Setup (Optional but Recommended)

For the Playwright fallback to work, you need to install browser binaries:

```bash
pip install playwright
playwright install chromium
```

## Usage

### 1. Bulk Import of Celebrities

Use `scrape_sociotype_xyz.py` to import many celebrities at once:

```bash
python examples/scrape_sociotype_xyz.py
```

This script:
- Tries HTTP scraping first (fast)
- Falls back to Playwright if needed (automatic)
- Imports up to 50 celebrities by default
- Stores all data in the database with source attribution

### 2. Search for Specific Person

Use `search_person.py` when you need data for a specific individual:

```bash
python examples/search_person.py "Albert Einstein"
python examples/search_person.py "Marie Curie" --db custom.duckdb
```

This script:
- Searches for the person by name
- Uses both HTTP and Playwright scrapers
- Imports the person's data if found
- Displays their personality type information

### 3. Programmatic Usage

In your own code:

```python
from socionics_research.pipeline import scrape_with_fallback
from socionics_research.database import init_database

# Initialize database
init_database("research.duckdb")

# Import multiple celebrities
count = scrape_with_fallback("research.duckdb", limit=100)
print(f"Imported {count} celebrities")

# Search for specific person
count = scrape_with_fallback(
    "research.duckdb",
    person_name="Carl Jung"
)
```

## How It Works

### HTTP Scraper (Primary Method)

**Pros:**
- Fast execution (no browser overhead)
- Low resource usage
- Works for static content

**Cons:**
- Cannot handle JavaScript-rendered pages
- Limited to what's in the initial HTML

### Playwright Scraper (Fallback Method)

**Pros:**
- Handles JavaScript-rendered content
- Can navigate and search the site
- Takes screenshots for debugging
- Full browser automation

**Cons:**
- Slower (needs to launch browser)
- Higher resource usage
- Requires browser binaries

### Automatic Fallback Flow

```
scrape_with_fallback()
    ↓
Try HTTP Scraper
    ↓
Success? → Save to DB → Done
    ↓
Failure?
    ↓
Try Playwright Scraper
    ↓
Success? → Save to DB → Done
    ↓
Failure? → Report error
```

## Database Schema

All scraped data follows this structure:

### Sources Table
- `source_id`: Unique identifier
- `url`: Original URL
- `domain`: Domain name (sociotype.xyz)
- `scrape_date`: When data was collected
- `license_note`: License information
- `raw_text`: Original content
- `metadata_json`: Additional metadata including scraping method

### Personalities Table
- `person_id`: Unique identifier
- `name`: Full name
- `canonical_name`: Lowercase normalized name
- `description`: Brief description
- `source_refs`: References to source records

### Sociotype Labels Table
- `label_id`: Unique identifier
- `person_id`: Reference to personality
- `label_source`: Where the label came from (e.g., "sociotype.xyz")
- `socionics_type`: The personality type (e.g., "LII", "EIE")
- `dcnh`: Optional DCNH classification
- `confidence`: Confidence score (0-1)
- `evidence`: How the label was determined

## Troubleshooting

### HTTP Scraper Not Working

If the HTTP scraper fails:
1. Check internet connectivity
2. Verify sociotype.xyz is accessible
3. The system will automatically try Playwright

### Playwright Not Working

If you see "Playwright not available":
1. Install: `pip install playwright`
2. Install browsers: `playwright install chromium`
3. Verify installation: `python -c "from playwright.sync_api import sync_playwright; print('OK')"`

### No Data Found

If no data is found for a person:
1. Check spelling of the name
2. Try variations (e.g., "Einstein" vs "Albert Einstein")
3. Verify the person exists on sociotype.xyz in your browser
4. Check if the site structure has changed

### Rate Limiting

The scrapers include built-in rate limiting:
- HTTP scraper: 1 second between requests
- Playwright scraper: 2 second delays for dynamic content

If you encounter rate limiting errors, increase these delays.

## Best Practices

1. **Start Small**: Test with a small limit first
   ```bash
   python examples/scrape_sociotype_xyz.py  # Uses limit=50
   ```

2. **Use Specific Searches**: When you know who you want
   ```bash
   python examples/search_person.py "Person Name"
   ```

3. **Monitor the Database**: Check what's been imported
   ```python
   conn = get_connection("research.duckdb")
   stats = conn.execute("""
       SELECT COUNT(*) FROM personalities
   """).fetchone()
   print(f"Total personalities: {stats[0]}")
   ```

4. **Respect the Source**: 
   - Don't scrape more than you need
   - Include proper attribution in your research
   - Follow sociotype.xyz's terms of service

## Advanced Usage

### Custom Playwright Configuration

```python
from socionics_research.pipeline import PlaywrightSociotypeScraper

with PlaywrightSociotypeScraper(headless=False) as scraper:
    # Browser will be visible (useful for debugging)
    celebrities = scraper.scrape_celebrities(limit=10)
```

### Direct Database Access

```python
from socionics_research.database import get_connection

conn = get_connection("research.duckdb")

# Query all LII types
results = conn.execute("""
    SELECT p.name, l.confidence
    FROM personalities p
    JOIN sociotype_labels l ON p.person_id = l.person_id
    WHERE l.socionics_type = 'LII'
    ORDER BY l.confidence DESC
""").fetchall()

for name, confidence in results:
    print(f"{name}: {confidence:.1%}")
```

## Examples

### Import Top 100 Celebrities
```bash
# Modify the script to increase limit
python examples/scrape_sociotype_xyz.py
# Then update limit in the script from 50 to 100
```

### Search for Multiple People
```bash
python examples/search_person.py "Albert Einstein"
python examples/search_person.py "Isaac Newton"
python examples/search_person.py "Marie Curie"
```

### Export to CSV
```python
import csv
from socionics_research.database import get_connection

conn = get_connection("research.duckdb")
results = conn.execute("""
    SELECT p.name, l.socionics_type, l.confidence
    FROM personalities p
    JOIN sociotype_labels l ON p.person_id = l.person_id
""").fetchall()

with open("personalities.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Name", "Type", "Confidence"])
    writer.writerows(results)
```

## Future Enhancements

Planned improvements:
- [ ] Support for multiple personality type systems (MBTI, Big Five)
- [ ] Automatic duplicate detection
- [ ] Batch processing with progress bars
- [ ] Export functionality built-in
- [ ] API endpoint for programmatic access
