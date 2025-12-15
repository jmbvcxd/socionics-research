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

### `add_personality.py`
Demonstrates how to:
- Add personalities to the database
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
