"""Smoke tests to verify basic functionality."""

import sys  # noqa: E402
from pathlib import Path  # noqa: E402

# Add src directory to path for importing the package
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from socionics_research import hello  # noqa: E402


def test_hello():
    """Test the hello function works correctly."""
    assert hello("test") == "hello test"


def test_hello_default():
    """Test the hello function with default parameter."""
    assert hello() == "hello world"
