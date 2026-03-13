"""JSON Sink — writes analysis results to a JSON file."""

import json
from pathlib import Path


class JsonSink:
    """Writes result dicts to a formatted JSON file."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, result: dict) -> str:
        """Write result as indented JSON. Returns the output file path."""
        self.path.write_text(
            json.dumps(result, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return str(self.path)
