"""LLM Client — Multi-provider interface (Anthropic + OpenAI) with robust JSON parsing."""

import json
import os
import re
import time
from dataclasses import dataclass, field

try:
    import anthropic
except ImportError:
    anthropic = None

try:
    import openai
except ImportError:
    openai = None

_DEFAULTS = {
    "anthropic": "claude-sonnet-4-20250514",
    "openai": "gpt-4o",
}

_ENV_VARS = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
}


@dataclass
class LLMResponse:
    """Structured response from any LLM provider."""

    raw_text: str
    parsed_json: dict | None
    model: str
    provider: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    success: bool
    error: str | None = None


class LLMClient:
    """Unified LLM client supporting Anthropic and OpenAI providers."""

    def __init__(
        self,
        provider: str = "anthropic",
        model: str | None = None,
        api_key: str | None = None,
    ) -> None:
        if provider not in ("anthropic", "openai"):
            raise ValueError(
                f"Unsupported provider '{provider}'. Choose 'anthropic' or 'openai'."
            )

        if provider == "anthropic" and anthropic is None:
            raise ImportError(
                "anthropic package not installed. Run: pip install anthropic"
            )
        if provider == "openai" and openai is None:
            raise ImportError(
                "openai package not installed. Run: pip install openai"
            )

        self.provider = provider
        self.model = model or _DEFAULTS[provider]

        resolved_key = api_key or os.environ.get(_ENV_VARS[provider])
        if not resolved_key:
            env_var = _ENV_VARS[provider]
            raise ValueError(
                f"No API key found. Set {env_var} or pass api_key parameter."
            )

        if provider == "anthropic":
            self._client = anthropic.Anthropic(api_key=resolved_key)
        else:
            self._client = openai.OpenAI(api_key=resolved_key)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze(
        self,
        prompt: dict,
        temperature: float = 0.0,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        """Send a {system, user} prompt to the LLM and return a structured response.

        Always returns LLMResponse — never raises exceptions to the caller.
        """
        start = time.monotonic()
        try:
            if self.provider == "anthropic":
                raw_text, input_tokens, output_tokens = self._call_anthropic(
                    prompt, temperature, max_tokens
                )
            else:
                raw_text, input_tokens, output_tokens = self._call_openai(
                    prompt, temperature, max_tokens
                )
        except Exception as exc:
            latency_ms = (time.monotonic() - start) * 1000
            return LLMResponse(
                raw_text="",
                parsed_json=None,
                model=self.model,
                provider=self.provider,
                input_tokens=0,
                output_tokens=0,
                latency_ms=latency_ms,
                success=False,
                error=f"{type(exc).__name__}: {exc}",
            )

        latency_ms = (time.monotonic() - start) * 1000
        parsed = self._parse_json(raw_text)

        return LLMResponse(
            raw_text=raw_text,
            parsed_json=parsed,
            model=self.model,
            provider=self.provider,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            success=parsed is not None,
            error=None if parsed is not None else "Failed to parse JSON from response",
        )

    # ------------------------------------------------------------------
    # Private provider calls
    # ------------------------------------------------------------------

    def _call_anthropic(
        self, prompt: dict, temperature: float, max_tokens: int
    ) -> tuple[str, int, int]:
        """Call Anthropic SDK and return (raw_text, input_tokens, output_tokens)."""
        response = self._client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=prompt["system"],
            messages=[{"role": "user", "content": prompt["user"]}],
        )
        raw_text = response.content[0].text
        return raw_text, response.usage.input_tokens, response.usage.output_tokens

    def _call_openai(
        self, prompt: dict, temperature: float, max_tokens: int
    ) -> tuple[str, int, int]:
        """Call OpenAI SDK and return (raw_text, input_tokens, output_tokens)."""
        response = self._client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {"role": "system", "content": prompt["system"]},
                {"role": "user", "content": prompt["user"]},
            ],
        )
        raw_text = response.choices[0].message.content
        return raw_text, response.usage.prompt_tokens, response.usage.completion_tokens

    # ------------------------------------------------------------------
    # JSON parser
    # ------------------------------------------------------------------

    def _parse_json(self, text: str) -> dict | None:
        """Robust JSON extraction from LLM output.

        Tries (in order):
        1. Direct parse
        2. Code fence extraction (```json ... ``` or ``` ... ```)
        3. First { ... last } extraction
        Returns None if all strategies fail.
        """
        text = text.strip()

        # Strategy 1: direct
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Strategy 2: code fences
        patterns = [
            r"```json\s*\n?(.*?)\n?\s*```",
            r"```\s*\n?(.*?)\n?\s*```",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1).strip())
                except json.JSONDecodeError:
                    continue

        # Strategy 3: first { ... last }
        first_brace = text.find("{")
        last_brace = text.rfind("}")
        if first_brace != -1 and last_brace > first_brace:
            try:
                return json.loads(text[first_brace : last_brace + 1])
            except json.JSONDecodeError:
                pass

        return None
