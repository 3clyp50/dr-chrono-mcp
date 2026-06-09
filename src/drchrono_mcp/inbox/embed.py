"""Embedders for the inbox corpus. Local-only by default -- PHI must not leave without a BAA.

``HashingEmbedder`` has no third-party deps and is fully deterministic, so the corpus and graph
run end-to-end with zero model downloads (the synthetic-first default).
``SentenceTransformerEmbedder`` is the production-quality local model, loaded lazily and only if
``sentence-transformers`` is installed. Both satisfy the ``Embedder`` Protocol in ``interfaces.py``.
"""

from __future__ import annotations

import hashlib
import math
import re
from collections.abc import Sequence

from drchrono_mcp.inbox.interfaces import Embedder

_TOKEN = re.compile(r"[a-z0-9]+")


def _tokens(text: str) -> list[str]:
    return _TOKEN.findall(text.lower())


class HashingEmbedder:
    """Deterministic hashed bag-of-words embedding. No deps, no network, no model download.

    Signed-hash projection into a fixed-dim L2-normalized vector. Good enough to cluster
    same-topic messages for dev and tests; swap in a real local model for production quality.
    """

    def __init__(self, dim: int = 256) -> None:
        self.dim = dim

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        return [self._embed_one(t) for t in texts]

    def _embed_one(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        for token in _tokens(text):
            digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
            code = int.from_bytes(digest, "big")
            sign = 1.0 if (code >> 1) & 1 else -1.0
            vec[code % self.dim] += sign
        norm = math.sqrt(sum(v * v for v in vec))
        if norm:
            vec = [v / norm for v in vec]
        return vec


class SentenceTransformerEmbedder:
    """Local ``sentence-transformers`` model (default ``BAAI/bge-small-en-v1.5``), lazy-loaded.

    Stays on-device: no PHI leaves the machine. Only import path; requires the optional dep.
    """

    def __init__(self, model_id: str) -> None:
        from sentence_transformers import SentenceTransformer

        self._model = SentenceTransformer(model_id)
        self.dim = int(self._model.get_sentence_embedding_dimension())

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        vectors = self._model.encode(
            list(texts), normalize_embeddings=True, convert_to_numpy=True
        )
        return [v.tolist() for v in vectors]


def build_embedder(model_id: str | None = None) -> Embedder:
    """Return the best available local embedder: the ST model if installed, else hashing.

    Never falls back to a remote API -- the corpus is PHI and must stay on-device.
    """
    if model_id:
        try:
            return SentenceTransformerEmbedder(model_id)
        except Exception:  # noqa: BLE001 -- any load/download failure -> deterministic local fallback
            pass
    return HashingEmbedder()
