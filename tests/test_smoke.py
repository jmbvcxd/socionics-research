"""Smoke tests to verify basic functionality."""

from socionics_research import hello


def test_hello():
    """Test the hello function works correctly."""
    assert hello("test") == "hello test"


def test_hello_default():
    """Test the hello function with default parameter."""
    assert hello() == "hello world"
