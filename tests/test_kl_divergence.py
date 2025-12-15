"""Tests for KL divergence computation."""

from socionics_research.analysis import (
    compute_kl_divergence,
    compute_sequence_kl,
)


def test_identical_distributions():
    """Test that KL divergence is 0 for identical distributions."""
    dist = [
        {"token": "the", "logprob": -0.1},
        {"token": "a", "logprob": -2.0},
    ]

    kl = compute_kl_divergence(dist, dist)
    assert abs(kl) < 1e-6, f"KL should be ~0 for identical distributions, got {kl}"


def test_different_distributions():
    """Test that KL divergence is positive for different distributions."""
    p = [
        {"token": "the", "logprob": -0.1},
        {"token": "a", "logprob": -3.0},
    ]

    q = [
        {"token": "the", "logprob": -2.0},
        {"token": "a", "logprob": -0.5},
    ]

    kl = compute_kl_divergence(p, q)
    assert kl > 0, f"KL should be positive for different distributions, got {kl}"


def test_sequence_kl_mean():
    """Test sequence-level KL with mean aggregation."""
    run_a = [
        [{"token": "the", "logprob": -0.1}],
        [{"token": "cat", "logprob": -1.0}],
    ]

    run_b = [
        [{"token": "the", "logprob": -0.1}],
        [{"token": "cat", "logprob": -1.0}],
    ]

    kl = compute_sequence_kl(run_a, run_b, aggregate="mean")
    assert abs(kl) < 1e-6, f"Sequence KL should be ~0 for identical, got {kl}"


def test_sequence_kl_length_mismatch():
    """Test that mismatched sequence lengths raise an error."""
    run_a = [[{"token": "the", "logprob": -0.1}]]
    run_b = [
        [{"token": "the", "logprob": -0.1}],
        [{"token": "cat", "logprob": -1.0}],
    ]

    try:
        compute_sequence_kl(run_a, run_b)
        assert False, "Should raise ValueError for length mismatch"
    except ValueError as e:
        assert "don't match" in str(e)
