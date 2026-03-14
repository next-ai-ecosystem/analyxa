"""Embeddings — semantic vector generation via OpenAI text-embedding-3-small."""

import os
import sys

try:
    import openai
except ImportError:
    openai = None


class EmbeddingGenerator:
    """Generates 1536-dimensional semantic vectors.

    Degrades silently when OpenAI is unavailable — generate() returns None
    instead of raising exceptions. The pipeline continues without embeddings.
    """

    def __init__(
        self,
        model: str = "text-embedding-3-small",
        api_key: str | None = None,
    ) -> None:
        self.model = model
        self._client = None

        if openai is None:
            return

        # Fallback chain: explicit api_key → config → os.environ
        if api_key is None:
            try:
                from analyxa.config import get_config
                config = get_config()
                api_key = config.openai_api_key
            except Exception:
                pass

        if api_key is None:
            api_key = os.environ.get("OPENAI_API_KEY")

        resolved_key = api_key
        if not resolved_key:
            return  # Silent degradation — no key configured

        self._client = openai.OpenAI(api_key=resolved_key)

    def generate(self, text: str) -> list[float] | None:
        """Generate a 1536D embedding vector for the given text.

        Returns None if:
        - No API client (key not configured or SDK missing)
        - text is empty
        - API call fails (logged to stderr)
        """
        if self._client is None:
            return None
        if not text or not text.strip():
            return None

        try:
            response = self._client.embeddings.create(model=self.model, input=text)
            return response.data[0].embedding
        except Exception as exc:
            print(f"[EmbeddingGenerator] Warning: {exc}", file=sys.stderr)
            return None

    @property
    def dimensions(self) -> int:
        """Fixed output dimension for text-embedding-3-small."""
        return 1536
