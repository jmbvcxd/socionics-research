"""LLM client abstraction for running prompts and capturing distributions.

This module provides a unified interface for working with different LLM APIs
and capturing token distributions for analysis.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
import duckdb


class LLMClient:
    """Abstract LLM client for running prompts.

    This is a base implementation. Extend this class for specific LLM providers
    (OpenAI, Anthropic, local models, etc.).

    Example:
        >>> client = LLMClient("gpt-4", "1.0")
        >>> response = client.run_prompt(
        ...     "Explain the LII sociotype",
        ...     system_personality={"sociotype": "LII", "dcnh": "C"}
        ... )
    """

    def __init__(self, model_name: str, model_version: str):
        """Initialize the LLM client.

        Args:
            model_name: Name of the model (e.g., "gpt-4", "llama-3")
            model_version: Version of the model
        """
        self.model_name = model_name
        self.model_version = model_version

    def run_prompt(
        self,
        prompt: str,
        system_personality: Optional[Dict[str, Any]] = None,
        temperature: float = 0.7,
        capture_logprobs: bool = True,
        top_k: int = 10,
    ) -> Dict[str, Any]:
        """Run a prompt and capture the response.

        NOTE: This is an abstract base implementation that returns placeholder data.
        For production use, create a subclass that implements actual LLM API calls:
        - OpenAIClient for OpenAI/GPT models
        - AnthropicClient for Claude models
        - LocalLLMClient for local models (llama.cpp, ollama, etc.)

        Args:
            prompt: The prompt text
            system_personality: Personality directives to inject
            temperature: Sampling temperature
            capture_logprobs: Whether to capture token log probabilities
            top_k: Number of top-k tokens to capture per position

        Returns:
            Dictionary with:
            - response_text: Generated text
            - tokens: List of token information (if capture_logprobs=True)
            - metadata: Additional metadata

        Example:
            To implement a real LLM client:
            >>> class OpenAIClient(LLMClient):
            ...     def __init__(self, model_name, api_key):
            ...         super().__init__(model_name, "1.0")
            ...         self.api_key = api_key
            ...
            ...     def run_prompt(self, prompt, **kwargs):
            ...         # Call OpenAI API here
            ...         response = openai.ChatCompletion.create(...)
            ...         return {"response_text": response.text, ...}
        """
        # Base implementation returns placeholder data
        # Subclasses should override this method with actual API calls
        return {
            "response_text": (
                "This is a placeholder response from the base LLMClient. "
                "Create a subclass (e.g., OpenAIClient, AnthropicClient) "
                "and implement run_prompt() to call actual LLM APIs."
            ),
            "tokens": [],
            "metadata": {
                "model_name": self.model_name,
                "model_version": self.model_version,
                "temperature": temperature,
                "system_personality": system_personality,
                "is_placeholder": True,
            },
        }


def save_prompt_run(
    conn: duckdb.DuckDBPyConnection,
    prompt_text: str,
    model_name: str,
    model_version: str,
    person_id: Optional[int] = None,
    run_meta: Optional[Dict[str, Any]] = None,
) -> int:
    """Save a prompt run to the database.

    Args:
        conn: DuckDB connection
        prompt_text: The prompt that was run
        model_name: Model identifier
        model_version: Model version
        person_id: Optional person this prompt relates to
        run_meta: Additional metadata (temperature, system prompts, etc.)

    Returns:
        The run_id of the created record

    Example:
        >>> run_id = save_prompt_run(
        ...     conn,
        ...     "Explain LII type",
        ...     "gpt-4",
        ...     "turbo",
        ...     run_meta={"temperature": 0.0}
        ... )
    """
    run_date = datetime.now()

    result = conn.execute(
        """
        INSERT INTO prompt_runs (
            run_id, person_id, prompt_text, model_name,
            model_version, run_date, run_meta
        )
        VALUES (
            nextval('prompt_runs_seq'), ?, ?, ?,
            ?, ?, ?
        )
        RETURNING run_id
    """,
        [person_id, prompt_text, model_name, model_version, run_date, run_meta],
    ).fetchone()

    conn.commit()
    return result[0]


def save_token_distribution(
    conn: duckdb.DuckDBPyConnection,
    run_id: int,
    token_index: int,
    token_text: str,
    token_id: Optional[int],
    topk_probs: List[Dict[str, Any]],
    entropy: Optional[float] = None,
) -> int:
    """Save token distribution data.

    Args:
        conn: DuckDB connection
        run_id: The prompt run this belongs to
        token_index: Position in sequence (0-based)
        token_text: The actual token text
        token_id: Tokenizer ID (if available)
        topk_probs: List of dicts with keys: token, id, logprob
        entropy: Optional entropy value for this distribution

    Returns:
        The token_dist_id of the created record

    Example:
        >>> topk = [
        ...     {"token": "the", "id": 123, "logprob": -0.02},
        ...     {"token": "a", "id": 58, "logprob": -3.1}
        ... ]
        >>> save_token_distribution(conn, run_id, 0, "the", 123, topk, 0.5)
    """
    created_at = datetime.now()

    result = conn.execute(
        """
        INSERT INTO token_distributions (
            token_dist_id, run_id, token_index, token_text,
            token_id, topk_json, entropy, created_at
        )
        VALUES (
            nextval('token_distributions_seq'), ?, ?, ?,
            ?, ?, ?, ?
        )
        RETURNING token_dist_id
    """,
        [
            run_id,
            token_index,
            token_text,
            token_id,
            topk_probs,
            entropy,
            created_at,
        ],
    ).fetchone()

    conn.commit()
    return result[0]
