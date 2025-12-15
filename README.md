# Socionics Research

A research platform for socionics personality analysis using modern ML/AI techniques.

## Overview

This repository provides a Python-based platform for collecting, analyzing, and understanding personality data through the lens of socionics. The project combines:

- **DuckDB** for local-first data storage
- **LLM Integration** for personality analysis and comparison
- **Token Distribution Analysis** for understanding model behavior
- **Sparse Autoencoder Training** for feature discovery
- **HuggingFace Integration** for ML pipeline compatibility

## Features

- 🔍 Collect and analyze public figure personality data
- 🤖 Compare outputs from multiple LLMs
- 📊 Token-level distribution capture and KL divergence computation
- 🧠 Sparse autoencoder training for interpretability
- 📚 Comprehensive documentation and examples

## Getting Started

1. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -e .  # Editable install (recommended)
   # or
   pip install -r requirements.txt  # Direct install
   ```

3. **Run tests:**
   ```bash
   pytest -q
   ```

4. **Format and lint code:**
   ```bash
   black .
   flake8 .
   ```

## Project Layout

```
├─ src/socionics_research/  # Main package source
├─ tests/                    # Test suite
├─ docs/                     # Documentation
├─ notebooks/                # Jupyter notebooks
├─ .github/                  # CI/CD and templates
└─ PROJECT_KICKSTART.md      # Implementation notes
```

## Documentation

- **[Overview](docs/overview.md)**: Project goals and features
- **[Architecture](docs/architecture.md)**: System design and components
- **[Roadmap](docs/roadmap.md)**: Development plan and milestones
- **[PROJECT_KICKSTART.md](PROJECT_KICKSTART.md)**: Setup and next steps

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Ethical Considerations

- Only public figure data is analyzed
- Clear provenance tracking for all data sources
- Explicit consent required for user personality analysis
- Transparent methodology and open documentation
