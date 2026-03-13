"""File Source — reads conversations from text files."""

import re
from pathlib import Path


class FileSource:
    """Reads conversation text from a file."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(f"Conversation file not found: {self.path}")

    def read(self) -> str:
        """Return the full file contents as a string (UTF-8)."""
        return self.path.read_text(encoding="utf-8")

    def read_messages(self) -> list[dict]:
        """Parse the file into a list of {role, content} message dicts.

        Expected format: lines starting with "Role: message text".
        Lines that don't match are appended to the previous message's content.
        """
        text = self.read()
        messages: list[dict] = []
        pattern = re.compile(r"^(\w+):\s+(.+)$")

        for line in text.splitlines():
            match = pattern.match(line)
            if match:
                role = match.group(1).lower()
                content = match.group(2).strip()
                messages.append({"role": role, "content": content})
            elif messages and line.strip():
                # Continuation of previous message
                messages[-1]["content"] += " " + line.strip()

        return messages

    def metadata(self) -> dict:
        """Return source metadata."""
        return {
            "source": "file",
            "path": str(self.path),
            "filename": self.path.name,
        }
