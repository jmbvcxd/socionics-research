# Examples

This directory contains example scripts demonstrating how to use the socionics research platform.

## Getting Started

1. **Initialize the Database**
   ```bash
   python examples/init_database.py
   ```
   
   Creates a new DuckDB database with the required schema.

2. **KL Divergence Example**
   ```bash
   python examples/kl_divergence_example.py
   ```
   
   Demonstrates computing KL divergence between token distributions from different models.

## Available Examples

### `init_database.py`
Initializes a new DuckDB database with all required tables:
- sources: Scraped web pages
- personalities: Public figures/characters
- sociotype_labels: Personality type assignments
- prompt_runs: LLM execution records
- token_distributions: Per-token probability captures
- activation_vectors: Neural activation data
- computed_vectors: Aggregated features for ML

### `scrape_sociotype_xyz.py`
**NEW** - Scrapes celebrity personality data from sociotype.xyz:
- Automatically fetches notable figures and their socionics types
- **Uses intelligent fallback: HTTP first, then Playwright for dynamic content**
- Imports data directly into the database
- Includes confidence scores when available
- Respects rate limits and includes proper error handling
- Can scrape a limited number or full dataset

Usage:
```bash
python examples/scrape_sociotype_xyz.py
```

This populates the database with real personality type assignments from the sociotype.xyz community database.

### `search_person.py`
**NEW** - Search for a specific person on sociotype.xyz:
- Finds and imports data for a specific individual
- Uses Playwright fallback when HTTP scraping fails
- Displays imported personality data

Usage:
```bash
python examples/search_person.py "Albert Einstein"
python examples/search_person.py "Marie Curie" --db custom.duckdb
```

Perfect for finding data on a specific person when they're not in the initial scrape.

### `add_personality.py`
Demonstrates how to:
- Add personalities to the database manually
- Assign sociotype labels with confidence scores
- List all personalities with their types
- Work with the database programmatically

Example public figures included:
- Albert Einstein (LII)
- Steve Jobs (EIE)
- Marie Curie (LII)

### `kl_divergence_example.py`
Shows how to:
- Compare token distributions between models
- Compute per-token KL divergence
- Aggregate KL divergence across sequences
- Interpret the results

## Next Steps

After running these examples, you can:

1. **Implement data collection**: Extend `src/socionics_research/pipeline/scraper.py` to scrape real data
2. **Connect to LLMs**: Implement actual API calls in `src/socionics_research/llm/client.py`
3. **Build analysis pipelines**: Use the KL divergence utilities to compare models
4. **Train sparse autoencoders**: Use the computed vectors for feature discovery

## Integration with Notebooks

You can also explore these features interactively in Jupyter notebooks:

```bash
jupyter notebook notebooks/placeholder.ipynb
```

## Database Location

By default, the database is created as `socionics_research.duckdb` in the current directory.
You can specify a different location when calling `init_database()`.

## Requirements

All examples require the dependencies in `requirements.txt`:
```bash
pip install -r requirements.txt
```
