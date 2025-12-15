# Contributing to Socionics Research

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Getting Started

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/jmbvcxd/socionics-research.git
   cd socionics-research
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Development Workflow

1. **Create a new branch** for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the coding standards below

3. **Run tests** to ensure everything works:
   ```bash
   pytest -q
   ```

4. **Format your code:**
   ```bash
   black .
   ```

5. **Lint your code:**
   ```bash
   flake8 .
   ```

6. **Commit your changes** with a clear message:
   ```bash
   git commit -m "Add feature: description"
   ```

7. **Push to your fork** and submit a pull request

## Coding Standards

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write docstrings for functions and classes
- Keep functions focused and modular
- Add tests for new functionality
- Update documentation for significant changes

## Testing

- Write unit tests for new features
- Ensure all tests pass before submitting PR
- Aim for high test coverage
- Include edge cases in tests

## Pull Request Process

1. Update the README.md or docs/ with details of changes if needed
2. Ensure CI checks pass (format, lint, tests)
3. Link related issues in the PR description
4. Request review from maintainers
5. Address feedback and update as needed

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## Questions?

Feel free to open an issue for questions or discussions.
