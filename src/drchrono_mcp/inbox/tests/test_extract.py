"""Heuristic extractor must read topic + normalcy + action from the doctor's own wording."""

from __future__ import annotations

import pytest

from drchrono_mcp.inbox.corpus.synthetic import generate
from drchrono_mcp.inbox.extract import HeuristicExtractor

# generate(10) yields exactly one message per template, keyed by its gold topic.
_BY_KEY = {m.meta["gold"]["topic"]: m for m in generate(10)}

# gold template key -> (expected normalized topic, expected normalcy)
_EXPECTED = {
    "gestational_glucose": ("gestational_glucose", "abnormal"),
    "prenatal_normal": ("prenatal_panel", "normal"),
    "cbc_microcytic": ("cbc", "abnormal"),
    "lipid_ldl": ("lipid", "abnormal"),
    "tsh_high": ("thyroid", "abnormal"),
    "vitamin_d_low": ("vitamin_d", "abnormal"),
    "a1c_elevated": ("a1c", "abnormal"),
    "urine_culture_uti": ("urine_culture", "abnormal"),
    "pap_normal": ("pap", "normal"),
}


@pytest.mark.parametrize("gold_key,expected", list(_EXPECTED.items()), ids=list(_EXPECTED))
def test_topic_and_normalcy(gold_key: str, expected: tuple[str, str]) -> None:
    message = _BY_KEY[gold_key]
    facts = HeuristicExtractor().extract(message.subject, message.body)
    assert (facts.topic, facts.normalcy) == expected


def test_gestational_action_is_ogtt() -> None:
    message = _BY_KEY["gestational_glucose"]
    facts = HeuristicExtractor().extract(message.subject, message.body)
    assert facts.action and "OGTT" in facts.action


def test_live_style_gestational_action_is_ogtt() -> None:
    facts = HeuristicExtractor().extract(
        "RESULTS",
        "Your gestational diabetes screening was elevated. I ordered a 3 hour glucose "
        "tolerance test at the lab.",
    )
    assert facts.topic == "gestational_glucose"
    assert facts.normalcy == "abnormal"
    assert facts.action == "Schedule a 3-hour OGTT"


def test_result_above_cutoff_is_abnormal() -> None:
    facts = HeuristicExtractor().extract(
        "Lab result available",
        "Gestational glucose screening, 1-hour, result 197 mg/dL for prenatal patient "
        "(cutoff < 140).",
    )
    assert facts.topic == "gestational_glucose"
    assert facts.normalcy == "abnormal"


def test_normal_results_carry_no_action() -> None:
    for key in ("prenatal_normal", "pap_normal"):
        message = _BY_KEY[key]
        facts = HeuristicExtractor().extract(message.subject, message.body)
        assert facts.action is None


def test_refill_is_not_flagged_abnormal() -> None:
    facts = HeuristicExtractor().extract(*_msg("refill_approved"))
    assert facts.topic == "refill"
    assert facts.normalcy != "abnormal"


def _msg(key: str) -> tuple[str, str]:
    message = _BY_KEY[key]
    return message.subject, message.body
