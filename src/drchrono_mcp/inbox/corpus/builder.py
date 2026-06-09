"""Builds the message corpus, from synthetic data (default) or the live DrChrono API."""

from __future__ import annotations

from typing import Any

from drchrono_mcp.inbox.config import InboxConfig
from drchrono_mcp.inbox.corpus import synthetic
from drchrono_mcp.inbox.corpus.models import SentMessage
from drchrono_mcp.inbox.corpus.store import CorpusStore


class CorpusBuilder:
    """Produces the physician's sent-message corpus and persists it to the local store.

    ``client`` is an optional ``DrChronoClient`` (typed loosely so corpus code stays importable
    without httpx). It is required only for ``build_live``.
    """

    def __init__(self, config: InboxConfig, client: Any | None = None) -> None:
        self.config = config
        self.client = client
        self.store = CorpusStore(config.corpus_path)

    def build_synthetic(self, n: int = 60, seed: int = 7) -> int:
        self.config.ensure_dirs()
        return self.store.write(synthetic.generate(n, seed=seed))

    async def build_live(self) -> int:
        """Pull the doctor's messages via /api/patient_messages with cursor pagination.

        Filters by doctor_id (from config or auto-detected from the token's user record).
        All pages are fetched; only messages with non-empty body are kept. PHI never logged.
        """
        from urllib.parse import parse_qs, urlparse

        if self.client is None:
            raise RuntimeError(
                "build_live requires a DrChronoClient with OAuth credentials. "
                "See the inbox AGENTS.md."
            )
        self.config.ensure_dirs()

        # Resolve doctor_id: config override, then auto-detect from token.
        doctor_id = self.config.doctor_id
        if doctor_id is None:
            user_info = await self.client.get("/users/current")
            doctor_id = user_info.get("doctor") if user_info else None
        if not doctor_id:
            raise RuntimeError(
                "Cannot determine doctor_id. Set DRCHRONO_DOCTOR_ID env var or ensure the "
                "authorized account is associated with a doctor."
            )

        # /api/patient_messages does not support a 'since' date filter; pull all pages.
        params: dict[str, Any] = {
            "doctor": doctor_id,
            "page_size": 100,
        }
        endpoint = "/patient_messages"
        messages: list[SentMessage] = []

        for _ in range(500):  # safety: caps at 50 000 messages
            response = await self.client.get(endpoint, params)
            if not response:
                break
            for item in response.get("results", []):
                msg = SentMessage.from_drchrono(item)
                if msg.body.strip():
                    messages.append(msg)
            next_url = response.get("next")
            if not next_url:
                break
            # Advance cursor: use query params from the next URL as-is.
            params = {k: v[0] for k, v in parse_qs(urlparse(next_url).query).items()}

        return self.store.write(messages)

    def _matches_author(self, message: SentMessage) -> bool:
        needle = self.config.user_filter.lower().strip()
        if not needle:
            return True
        return needle in (message.author or "").lower()
