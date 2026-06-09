"""Heuristic extractor: derive ``ResponseFacts`` from a message's subject + body.

The regex/keyword first pass described in the inbox AGENTS.md. It sees only subject and body --
the live path never has gold labels -- so it must stand on its own. An LLM enrichment pass can
refine these facts later, but only over a BAA-covered endpoint (the body is PHI). Satisfies the
``Extractor`` Protocol in ``interfaces.py``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from drchrono_mcp.inbox.interfaces import ResponseFacts

_WORD = re.compile(r"[a-z0-9]+")


@dataclass(frozen=True)
class _TopicRule:
    topic: str
    cues: tuple[str, ...]  # any cue present (substring match) -> this topic
    problem: str | None = None
    demographic: str | None = None


# Ordered most-specific-first; first matching rule wins.
_TOPIC_RULES: tuple[_TopicRule, ...] = (
    _TopicRule("gestational_glucose", ("gestational", "ogtt"),
               "gestational diabetes screening", "prenatal"),
    _TopicRule("prenatal_panel", ("prenatal",), "routine prenatal labs", "prenatal"),
    _TopicRule("cbc", ("mcv", "blood count", "cbc"), "complete blood count"),
    _TopicRule("lipid", ("ldl", "cholesterol", "lipid"), "hyperlipidemia"),
    _TopicRule("thyroid", ("tsh", "thyroid"), "thyroid function"),
    _TopicRule("vitamin_d", ("vitamin d",), "vitamin D deficiency"),
    _TopicRule("a1c", ("a1c", "hemoglobin a1c"), "glycemic screening"),
    _TopicRule("urine_culture", ("urine culture", "urinary tract", "uti"),
               "urinary tract infection"),
    _TopicRule("refill", ("refill",), "medication refill"),
    _TopicRule("pap", ("pap smear", "pap"), "cervical cancer screening"),
)


def _cue_hit(cue: str, text: str, tokens: set[str]) -> bool:
    """Multi-word cues match as substrings; single tokens match whole words.

    Whole-word matching for short cues avoids false hits like ``uti`` inside ``routine``.
    """
    return cue in text if " " in cue else cue in tokens

# Short result cues checked as whole words (avoid "low" matching "follow"/"below").
_ABNORMAL_WORDS = frozenset({"above", "elevated", "low", "high", "underactive", "deficient"})
_ABNORMAL_PHRASES = (
    "higher than", "follow up on", "stands out", "a little smaller", "slightly above",
    "prediabetes range", "confirms a", "an infection", "low iron",
)
_NORMAL_WORDS = frozenset({"normal", "reassuring"})
_NORMAL_PHRASES = (
    "within range", "no action is needed", "nothing you need to do", "no abnormal cells",
)
_RESULT_BEATS_CUTOFF_RE = re.compile(
    r"(\d+(?:\.\d+)?)\s*mg/dl.*?cutoff(?:\s+of)?\s*<\s*(\d+(?:\.\d+)?)",
    re.IGNORECASE | re.DOTALL,
)
_GESTATIONAL_OGTT_RE = re.compile(
    r"\b(?:ogtt|3\s*[- ]?\s*hour|three\s+hour|glucose\s+tolerance)\b",
    re.IGNORECASE,
)


def _normalcy(text: str) -> str:
    words = set(_WORD.findall(text))
    for match in _RESULT_BEATS_CUTOFF_RE.finditer(text):
        if float(match.group(1)) > float(match.group(2)):
            return "abnormal"
    if words & _ABNORMAL_WORDS or any(p in text for p in _ABNORMAL_PHRASES):
        return "abnormal"
    if words & _NORMAL_WORDS or any(p in text for p in _NORMAL_PHRASES):
        return "normal"
    return "unknown"


def _trim(line: str) -> str:
    """First clause of a step line: drop the doctor's parenthetical aside after ' -- '."""
    line = line.strip()
    for sep in (" -- ", " — ", "--"):
        if sep in line:
            line = line.split(sep, 1)[0].strip()
            break
    return line.rstrip(".")


_STEP_RE = re.compile(r"next steps:\s*\n\s*1\.\s*(.+)", re.IGNORECASE)


def _action(topic: str, text: str, body: str) -> str | None:
    match = _STEP_RE.search(body)
    if match:
        return _trim(match.group(1)) or None
    if topic == "gestational_glucose" and _GESTATIONAL_OGTT_RE.search(text):
        return "Schedule a 3-hour OGTT"
    return None


class HeuristicExtractor:
    """Keyword/regex extraction of topic, normalcy, problem, demographic, and next action."""

    def extract(self, subject: str, body: str) -> ResponseFacts:
        text = f"{subject}\n{body}".lower()
        tokens = set(_WORD.findall(text))
        topic, problem, demographic = "general", None, None
        for rule in _TOPIC_RULES:
            if any(_cue_hit(cue, text, tokens) for cue in rule.cues):
                topic, problem, demographic = rule.topic, rule.problem, rule.demographic
                break
        normalcy = _normalcy(text)
        return ResponseFacts(
            topic=topic,
            normalcy=normalcy,
            problem=problem,
            demographic=demographic,
            action=_action(topic, text, body),
            phrase_key=f"{topic}:{normalcy}",
        )
