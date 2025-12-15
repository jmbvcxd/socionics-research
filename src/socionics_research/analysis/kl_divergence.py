"""KL divergence computation for token distributions.

This module implements utilities for computing KL divergence between
token distributions from different LLM runs.
"""

from typing import Dict, List
import numpy as np
from scipy.stats import entropy


def normalize_distribution(
    topk_probs: List[Dict[str, float]], epsilon: float = 1e-10
) -> Dict[str, float]:
    """Normalize a top-k probability distribution.

    Args:
        topk_probs: List of dicts with 'token' and 'logprob' keys
        epsilon: Small value to add for numerical stability

    Returns:
        Dictionary mapping token to normalized probability
    """
    # Convert logprobs to probabilities
    probs = {}
    for item in topk_probs:
        token = item["token"]
        logprob = item.get("logprob", item.get("log_prob", 0))
        probs[token] = np.exp(logprob)

    # Normalize
    total = sum(probs.values())
    if total > 0:
        probs = {k: v / total for k, v in probs.items()}
    else:
        # Uniform distribution if all zero
        probs = {k: 1.0 / len(probs) for k in probs.keys()}

    return probs


def align_distributions(
    p_dist: Dict[str, float], q_dist: Dict[str, float], epsilon: float = 1e-10
) -> tuple[np.ndarray, np.ndarray]:
    """Align two distributions over the same vocabulary.

    Args:
        p_dist: First distribution (dict: token -> probability)
        q_dist: Second distribution (dict: token -> probability)
        epsilon: Small value for missing tokens

    Returns:
        Tuple of (p_array, q_array) as aligned numpy arrays
    """
    # Get union of all tokens
    all_tokens = sorted(set(p_dist.keys()) | set(q_dist.keys()))

    # Create aligned arrays
    p_array = np.array([p_dist.get(token, epsilon) for token in all_tokens])
    q_array = np.array([q_dist.get(token, epsilon) for token in all_tokens])

    # Renormalize to ensure they sum to 1
    p_array = p_array / p_array.sum()
    q_array = q_array / q_array.sum()

    return p_array, q_array


def compute_kl_divergence(
    p_topk: List[Dict[str, float]],
    q_topk: List[Dict[str, float]],
    epsilon: float = 1e-10,
) -> float:
    """Compute KL divergence KL(P || Q) between two token distributions.

    Args:
        p_topk: Top-k distribution from model P
        q_topk: Top-k distribution from model Q
        epsilon: Small value for numerical stability

    Returns:
        KL divergence value (nats)

    Example:
        >>> p = [{"token": "the", "logprob": -0.1}, {"token": "a", "logprob": -2.5}]
        >>> q = [{"token": "the", "logprob": -0.5}, {"token": "a", "logprob": -1.5}]
        >>> kl = compute_kl_divergence(p, q)
    """
    # Normalize distributions
    p_dist = normalize_distribution(p_topk, epsilon)
    q_dist = normalize_distribution(q_topk, epsilon)

    # Align to same vocabulary
    p_array, q_array = align_distributions(p_dist, q_dist, epsilon)

    # Compute KL divergence using scipy
    kl_value = entropy(p_array, q_array)

    return float(kl_value)


def compute_sequence_kl(
    run_a_tokens: List[List[Dict[str, float]]],
    run_b_tokens: List[List[Dict[str, float]]],
    aggregate: str = "mean",
) -> float:
    """Compute sequence-level KL divergence.

    Args:
        run_a_tokens: List of token distributions from model A
        run_b_tokens: List of token distributions from model B
        aggregate: How to aggregate ('mean', 'sum', 'max')

    Returns:
        Aggregated KL divergence

    Example:
        >>> run_a = [[{"token": "the", "logprob": -0.1}], ...]
        >>> run_b = [[{"token": "the", "logprob": -0.5}], ...]
        >>> seq_kl = compute_sequence_kl(run_a, run_b, aggregate="mean")
    """
    if len(run_a_tokens) != len(run_b_tokens):
        raise ValueError(
            f"Token sequence lengths don't match: "
            f"{len(run_a_tokens)} vs {len(run_b_tokens)}"
        )

    # Compute per-token KL divergences
    kl_values = []
    for p_topk, q_topk in zip(run_a_tokens, run_b_tokens):
        kl = compute_kl_divergence(p_topk, q_topk)
        kl_values.append(kl)

    # Aggregate
    kl_array = np.array(kl_values)

    if aggregate == "mean":
        return float(np.mean(kl_array))
    elif aggregate == "sum":
        return float(np.sum(kl_array))
    elif aggregate == "max":
        return float(np.max(kl_array))
    else:
        raise ValueError(f"Unknown aggregate method: {aggregate}")


def compute_entropy_from_topk(topk_probs: List[Dict[str, float]]) -> float:
    """Compute entropy of a top-k distribution.

    Args:
        topk_probs: Top-k distribution

    Returns:
        Entropy in nats

    Example:
        >>> topk = [{"token": "the", "logprob": -0.1}, {"token": "a", "logprob": -2.5}]
        >>> h = compute_entropy_from_topk(topk)
    """
    dist = normalize_distribution(topk_probs)
    probs = np.array(list(dist.values()))
    return float(entropy(probs))
