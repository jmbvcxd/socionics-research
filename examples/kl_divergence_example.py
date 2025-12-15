#!/usr/bin/env python3
"""Example of computing KL divergence between token distributions.

This demonstrates how to compute KL divergence between two LLM outputs
at the token level.
"""

import sys  # noqa: E402
from pathlib import Path  # noqa: E402

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from socionics_research.analysis import (  # noqa: E402
    compute_kl_divergence,
    compute_sequence_kl,
)


def main():
    """Demonstrate KL divergence computation."""
    print("KL Divergence Example")
    print("=" * 60)

    # Example token distributions from two models
    # Model A's top-k distribution at token position 0
    model_a_token_0 = [
        {"token": "The", "logprob": -0.1},
        {"token": "A", "logprob": -2.5},
        {"token": "An", "logprob": -3.0},
    ]

    # Model B's top-k distribution at token position 0
    model_b_token_0 = [
        {"token": "The", "logprob": -0.5},
        {"token": "A", "logprob": -1.5},
        {"token": "This", "logprob": -2.0},
    ]

    print("\nModel A distribution:")
    for item in model_a_token_0:
        print(f"  {item['token']}: logprob={item['logprob']:.3f}")

    print("\nModel B distribution:")
    for item in model_b_token_0:
        print(f"  {item['token']}: logprob={item['logprob']:.3f}")

    # Compute KL divergence
    kl = compute_kl_divergence(model_a_token_0, model_b_token_0)
    print(f"\nKL(A || B) at token 0: {kl:.4f} nats")

    # Example sequence-level KL
    print("\n" + "=" * 60)
    print("Sequence-level KL Divergence")
    print("=" * 60)

    # Multiple tokens from each model
    run_a_tokens = [
        model_a_token_0,
        [{"token": "cat", "logprob": -1.0}, {"token": "dog", "logprob": -1.5}],
        [{"token": "is", "logprob": -0.2}, {"token": "was", "logprob": -2.0}],
    ]

    run_b_tokens = [
        model_b_token_0,
        [{"token": "cat", "logprob": -0.8}, {"token": "dog", "logprob": -2.0}],
        [{"token": "is", "logprob": -0.3}, {"token": "was", "logprob": -1.8}],
    ]

    seq_kl_mean = compute_sequence_kl(run_a_tokens, run_b_tokens, aggregate="mean")
    seq_kl_sum = compute_sequence_kl(run_a_tokens, run_b_tokens, aggregate="sum")

    print(f"\nMean KL across {len(run_a_tokens)} tokens: {seq_kl_mean:.4f} nats")
    print(f"Total KL across sequence: {seq_kl_sum:.4f} nats")

    print("\nInterpretation:")
    print("- Lower KL means distributions are more similar")
    print("- Higher KL indicates significant distributional differences")
    print("- Can be used to compare personality-conditioned outputs")


if __name__ == "__main__":
    main()
