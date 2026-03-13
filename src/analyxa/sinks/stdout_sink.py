"""Stdout Sink — prints analysis results to the terminal."""

import json


class StdoutSink:
    """Prints result dicts as formatted JSON to stdout."""

    def write(self, result: dict) -> None:
        """Print result as indented JSON (supports international characters)."""
        print(json.dumps(result, indent=2, ensure_ascii=False))
