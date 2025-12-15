# Project Overview

## Purpose

This project provides a research platform for socionics personality analysis using modern ML/AI techniques. The platform combines:

- Data collection and storage using DuckDB
- LLM integration for personality analysis
- Token distribution analysis and KL divergence computation
- Sparse autoencoder training for feature discovery
- Integration with HuggingFace models and pipelines

## Key Features

1. **Local-First Architecture**: DuckDB provides a single-file database solution
2. **Ethical Data Collection**: Respects public data sources with proper provenance tracking
3. **Multi-Model Analysis**: Compare outputs from different LLMs
4. **Token-Level Analysis**: Capture and analyze token distributions
5. **ML Pipeline Ready**: Structured for sparse autoencoder training and NeuronPedia integration

## Target Users

- Researchers interested in personality psychology
- Data scientists exploring LLM behavior
- ML engineers building interpretability tools
- Socionics enthusiasts conducting analysis

## Design Principles

- **Transparency**: All data sources and methods clearly documented
- **Reproducibility**: Version control and provenance tracking
- **Privacy**: Only public figure data, with clear consent requirements for user analysis
- **Extensibility**: Modular design allowing easy addition of new models and methods
