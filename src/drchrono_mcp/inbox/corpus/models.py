"""Corpus data model. A message body is treated as PHI everywhere downstream."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


def _parse_dt(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


class SentMessage(BaseModel):
    """One message authored by the physician (a corpus item)."""

    id: str
    sent_at: datetime | None = None
    author: str = ""
    patient_id: int | None = None
    subject: str = ""
    body: str = ""
    status: str = "sent"
    category: str = "unknown"  # inferred lane: lab_result | refill | scheduling | ...
    synthetic: bool = False
    meta: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_drchrono(cls, raw: dict[str, Any]) -> SentMessage:
        """Map a raw /api/patient_messages record onto SentMessage."""
        # Only use string-valued fields for body; 'message' in patient_messages is an int FK.
        body = ""
        for key in ("body", "text", "note"):
            val = raw.get(key)
            if isinstance(val, str) and val.strip():
                body = val
                break
        # created_at is the field name on patient_messages; fall back to updated_at.
        sent_at = _parse_dt(
            raw.get("created_at") or raw.get("created") or raw.get("updated_at") or raw.get("date")
        )
        return cls(
            id=str(raw.get("id", "")),
            sent_at=sent_at,
            author=str(raw.get("sender") or raw.get("user") or raw.get("doctor") or ""),
            patient_id=raw.get("patient"),
            subject=raw.get("subject") or "",
            body=body,
            status=raw.get("status") or "sent",
            synthetic=False,
            meta={"raw_keys": sorted(raw.keys())},
        )
