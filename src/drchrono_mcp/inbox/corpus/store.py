"""Local JSONL store for the message corpus. One ``SentMessage`` per line."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from pathlib import Path

from drchrono_mcp.inbox.corpus.models import SentMessage


class CorpusStore:
    """Append-or-replace JSONL persistence for corpus messages."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)

    def write(self, messages: Iterable[SentMessage]) -> int:
        """Replace the corpus with ``messages``."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        count = 0
        with self.path.open("w", encoding="utf-8") as fh:
            for message in messages:
                fh.write(message.model_dump_json() + "\n")
                count += 1
        return count

    def append(self, messages: Iterable[SentMessage]) -> int:
        """Append ``messages`` to the corpus."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        count = 0
        with self.path.open("a", encoding="utf-8") as fh:
            for message in messages:
                fh.write(message.model_dump_json() + "\n")
                count += 1
        return count

    def __iter__(self) -> Iterator[SentMessage]:
        if not self.path.exists():
            return
        with self.path.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    yield SentMessage.model_validate_json(line)

    def load(self) -> list[SentMessage]:
        return list(self)

    def count(self) -> int:
        return sum(1 for _ in self)

    def clear(self) -> None:
        self.path.unlink(missing_ok=True)
