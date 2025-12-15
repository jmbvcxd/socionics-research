# Architecture

## System Components

### Data Layer

**DuckDB Database**: Single-file relational database containing:
- `sources`: Scraped web pages and text sources
- `personalities`: Canonical people/characters being analyzed
- `sociotype_labels`: Personality type assignments with provenance
- `prompt_runs`: LLM execution records
- `token_distributions`: Per-token probability distributions
- `activation_vectors`: Optional neuron activation captures
- `computed_vectors`: Aggregated features for ML pipelines

### Data Pipeline

1. **Scraping Module**: Collects public figure data with intelligent fallback
   - HTTP scraper for static content (fast, efficient)
   - Playwright scraper for JavaScript-rendered content (fallback)
   - Automatic retry logic when data not found
2. **Rewriting Module**: Summarizes and normalizes collected text
3. **Indexing Module**: Builds vector index for RAG capabilities
4. **LLM Orchestration**: Manages prompt execution across multiple models
5. **Capture Module**: Records token distributions and activations
6. **Analysis Module**: Computes KL divergence and other metrics

### ML Components

1. **Token Distribution Analysis**: Compare model outputs
2. **KL Divergence Computation**: Measure distributional differences
3. **Sparse Autoencoder Training**: Feature discovery from activations
4. **NeuronPedia Integration**: Interpretability layer

## Data Flow

```
Public Sources (sociotype.xyz, etc.)
    ↓
Scraping (HTTP → Playwright fallback)
    ↓
Data Extraction & Normalization
    ↓
DuckDB Storage (sources, personalities, labels)
    ↓
LLM Prompts → [Model A, Model B]
    ↓
Token Distributions + Activations
    ↓
KL Divergence & Feature Vectors
    ↓
Sparse Autoencoder
    ↓
NeuronPedia Labels
```

## Scraping Architecture

The scraping system uses a two-tier approach:

1. **HTTP Scraper (Primary)**
   - Fast and lightweight
   - Uses requests + BeautifulSoup
   - Works for static content
   - Minimal resource usage

2. **Playwright Scraper (Fallback)**
   - Handles JavaScript-rendered content
   - Full browser automation
   - Used when HTTP scraper fails or returns no data
   - Can perform searches and navigation
   - Takes screenshots for debugging

## Technology Stack

- **Database**: DuckDB (local SQL database)
- **Language**: Python 3.10+
- **ML Framework**: PyTorch
- **LLM Integration**: HuggingFace Transformers, API clients
- **Testing**: pytest
- **Code Quality**: black, flake8
- **CI/CD**: GitHub Actions
