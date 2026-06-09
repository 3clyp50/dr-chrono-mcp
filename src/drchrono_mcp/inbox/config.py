"""Configuration for the clinical inbox autopilot."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path


def _default_data_dir() -> Path:
    return Path(os.environ.get("INBOX_DATA_DIR", ".inbox_data")).expanduser()


@dataclass
class InboxConfig:
    """Runtime settings. Synthetic-first; flip ``source`` to ``"live"`` once OAuth is wired."""

    source: str = "synthetic"  # "synthetic" | "live"
    user_filter: str = ""  # optional message author filter when a live endpoint supports it
    status: tuple[str, ...] = ("sent", "archived")
    date_start: date = date(2024, 1, 1)
    date_end: date = date(2025, 12, 31)
    data_dir: Path = field(default_factory=_default_data_dir)
    embedder_model: str = "BAAI/bge-small-en-v1.5"
    doctor_id: int | None = None  # auto-detected from token if not set

    @property
    def corpus_path(self) -> Path:
        return self.data_dir / "corpus.jsonl"

    @property
    def graph_path(self) -> Path:
        return self.data_dir / "voice_graph.kuzu"

    def ensure_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_env(cls) -> InboxConfig:
        cfg = cls()
        if v := os.environ.get("INBOX_SOURCE"):
            cfg.source = v
        if v := os.environ.get("INBOX_USER_FILTER"):
            cfg.user_filter = v
        if v := os.environ.get("DRCHRONO_DOCTOR_ID"):
            try:
                cfg.doctor_id = int(v)
            except ValueError:
                pass
        return cfg
