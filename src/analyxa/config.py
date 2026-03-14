"""Config — centralized configuration for Analyxa. Reads .env and provides defaults."""

import os
from pathlib import Path

from dotenv import load_dotenv


class AnalyxaConfig:
    """Centralized configuration. Single source of truth for all settings.

    Load order:
    1. .env file (if provided or found in cwd)
    2. os.environ
    3. Hardcoded defaults
    """

    def __init__(self, env_file: str | Path | None = None) -> None:
        if env_file is not None:
            load_dotenv(env_file)
        else:
            # Attempt to load .env from cwd, silently ignore if missing
            load_dotenv(dotenv_path=None, override=False)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def anthropic_api_key(self) -> str | None:
        return os.environ.get("ANTHROPIC_API_KEY") or None

    @property
    def openai_api_key(self) -> str | None:
        return os.environ.get("OPENAI_API_KEY") or None

    @property
    def default_provider(self) -> str:
        return os.environ.get("ANALYXA_PROVIDER", "anthropic")

    @property
    def default_model(self) -> str | None:
        return os.environ.get("ANALYXA_MODEL") or None

    @property
    def default_schema(self) -> str:
        return os.environ.get("ANALYXA_SCHEMA", "universal")

    @property
    def embedding_model(self) -> str:
        return os.environ.get("ANALYXA_EMBEDDING_MODEL", "text-embedding-3-small")

    @property
    def enable_embeddings(self) -> bool:
        raw = os.environ.get("ANALYXA_EMBEDDINGS", "true")
        return raw.lower() in ("true", "1", "yes")

    @property
    def schemas_dir(self) -> str | None:
        return os.environ.get("ANALYXA_SCHEMAS_DIR") or None

    @property
    def redis_url(self) -> str:
        return os.environ.get("REDIS_URL", "redis://localhost:6379")

    @property
    def qdrant_url(self) -> str:
        return os.environ.get("QDRANT_URL", "http://localhost:6333")

    @property
    def qdrant_collection(self) -> str:
        return os.environ.get("QDRANT_COLLECTION", "analyxa_analyses")

    @property
    def log_level(self) -> str:
        return os.environ.get("ANALYXA_LOG_LEVEL", "INFO")

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Return all settings. API keys are masked (last 4 chars only)."""

        def _mask(key: str | None) -> str | None:
            if key is None:
                return None
            if len(key) <= 4:
                return "..." + key
            return f"sk-...{key[-4:]}"

        return {
            "anthropic_api_key": _mask(self.anthropic_api_key),
            "openai_api_key": _mask(self.openai_api_key),
            "default_provider": self.default_provider,
            "default_model": self.default_model,
            "default_schema": self.default_schema,
            "embedding_model": self.embedding_model,
            "enable_embeddings": self.enable_embeddings,
            "schemas_dir": self.schemas_dir,
            "redis_url": self.redis_url,
            "qdrant_url": self.qdrant_url,
            "qdrant_collection": self.qdrant_collection,
            "log_level": self.log_level,
        }

    @classmethod
    def from_dict(cls, overrides: dict) -> "AnalyxaConfig":
        """Create config with manual overrides. Useful for testing and programmatic use."""
        _ENV_MAP = {
            "anthropic_api_key": "ANTHROPIC_API_KEY",
            "openai_api_key": "OPENAI_API_KEY",
            "default_provider": "ANALYXA_PROVIDER",
            "default_model": "ANALYXA_MODEL",
            "default_schema": "ANALYXA_SCHEMA",
            "embedding_model": "ANALYXA_EMBEDDING_MODEL",
            "enable_embeddings": "ANALYXA_EMBEDDINGS",
            "schemas_dir": "ANALYXA_SCHEMAS_DIR",
            "redis_url": "REDIS_URL",
            "qdrant_url": "QDRANT_URL",
            "qdrant_collection": "QDRANT_COLLECTION",
            "log_level": "ANALYXA_LOG_LEVEL",
        }
        for prop_name, value in overrides.items():
            env_var = _ENV_MAP.get(prop_name)
            if env_var and value is not None:
                os.environ[env_var] = str(value)
        return cls()


# ------------------------------------------------------------------
# Singleton
# ------------------------------------------------------------------

_default_config: AnalyxaConfig | None = None


def get_config(env_file: str | None = None) -> AnalyxaConfig:
    """Return config singleton. Creates if it doesn't exist."""
    global _default_config
    if _default_config is None:
        _default_config = AnalyxaConfig(env_file=env_file)
    return _default_config


def reset_config() -> None:
    """Reset singleton. Useful for tests."""
    global _default_config
    _default_config = None
