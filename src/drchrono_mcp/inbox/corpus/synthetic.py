"""Synthetic physician-style sent messages for development without live PHI.

The voice mirrors the real drafted message in the source material (warm, structured, explains
the *why*, numbered "Next Steps"). The canonical gestational-glucose -> 3-hour OGTT case is
included verbatim-in-spirit so retrieval can be validated against the known example.

Each message carries ``meta["gold"]`` (topic/normalcy/problem/demographic/action) so the
extractor and graph can be scored later. All items are flagged ``synthetic=True``.
"""

from __future__ import annotations

import random
import textwrap
from dataclasses import dataclass
from datetime import datetime, timedelta

from drchrono_mcp.inbox.corpus.models import SentMessage

FIRST_NAMES = [
    "Deborah", "Maria", "James", "Aisha", "Robert", "Linda", "Carlos", "Wei",
    "Sofia", "David", "Priya", "Thomas", "Grace", "Omar", "Hannah", "Daniel",
]


def _b(text: str) -> str:
    """Dedent and trim a block written with source indentation."""
    return textwrap.dedent(text).strip("\n")


@dataclass(frozen=True)
class Template:
    key: str
    category: str
    subject: str
    normalcy: str
    problem: str
    demographic: str | None
    action: str | None
    opening: str
    core: str
    steps: str = ""
    value: tuple[float, float, str] | None = None  # (lo, hi, "int"|"float1")


TEMPLATES: list[Template] = [
    Template(
        key="gestational_glucose",
        category="lab_result",
        subject="Important Update: Your Prenatal Lab Results",
        normalcy="abnormal",
        problem="gestational diabetes screening",
        demographic="prenatal",
        action="schedule 3-hour oral glucose tolerance test (OGTT)",
        opening="Your prenatal blood work and gestational screening results are back.",
        core=_b(
            """
            Overall your blood counts, immunity, and standard prenatal screenings look great.
            There is one value we should follow up on:

            - Gestational Glucose Screen: {value} mg/dL, which is above the standard 1-hour
              cutoff of <140 mg/dL.

            An elevated 1-hour screen doesn't diagnose anything by itself -- it just tells us
            we need the more definitive test to see how your body is processing sugar.
            """
        ),
        steps=_b(
            """
            Next Steps:
            1. Schedule a 3-hour Oral Glucose Tolerance Test (OGTT) -- my office will help you
               set this up.
            2. Preparation: fast (water only) for 8-12 hours beforehand, and plan for about
               3 hours at the lab with blood draws each hour.
            """
        ),
        value=(190, 235, "int"),
    ),
    Template(
        key="prenatal_normal",
        category="lab_result",
        subject="Your Prenatal Lab Results",
        normalcy="normal",
        problem="routine prenatal labs",
        demographic="prenatal",
        action=None,
        opening="Your full prenatal lab panel is back.",
        core=_b(
            """
            Everything looks reassuring: your blood counts, blood type, immunity, and
            infectious-disease screening are all normal, and your glucose screen is within
            range. There is nothing you need to do -- we'll continue with your routine visits.
            """
        ),
    ),
    Template(
        key="cbc_microcytic",
        category="lab_result",
        subject="Your Recent Blood Count (CBC)",
        normalcy="abnormal",
        problem="microcytic anemia",
        demographic=None,
        action="order iron studies (ferritin, iron, TIBC)",
        opening="Your complete blood count (CBC) came back.",
        core=_b(
            """
            Most values are normal. One thing stands out: your red cells are a little smaller
            than average (MCV {value} fL, reference 80-100 fL), which can be an early sign of
            low iron.
            """
        ),
        steps=_b(
            """
            Next Steps:
            1. I'd like to check iron studies (ferritin, iron, TIBC) to confirm.
            2. There's nothing you need to change for now -- we'll let the numbers guide us.
            """
        ),
        value=(72, 79, "int"),
    ),
    Template(
        key="lipid_ldl",
        category="lab_result",
        subject="Your Cholesterol Results",
        normalcy="abnormal",
        problem="hyperlipidemia",
        demographic=None,
        action="lifestyle changes and recheck lipid panel in 3 months",
        opening="Your cholesterol panel is back.",
        core=_b(
            """
            Your LDL (the "bad" cholesterol) is {value} mg/dL, which is higher than we'd like
            (goal under 100 mg/dL for most patients). The rest of the panel is reasonable.
            """
        ),
        steps=_b(
            """
            Next Steps:
            1. Let's start with diet and activity changes -- I'll send over my one-page handout.
            2. We'll recheck the panel in 3 months. If it's still elevated, we can discuss
               whether a statin makes sense for you.
            """
        ),
        value=(160, 205, "int"),
    ),
    Template(
        key="tsh_high",
        category="lab_result",
        subject="Your Thyroid (TSH) Result",
        normalcy="abnormal",
        problem="hypothyroidism",
        demographic=None,
        action="repeat TSH with free T4 in 6 weeks",
        opening="Your thyroid test (TSH) came back.",
        core=_b(
            """
            Your TSH is {value} mIU/L, slightly above the normal range (about 0.4-4.0). This
            often means the thyroid is a touch underactive, but a single value can be misleading.
            """
        ),
        steps=_b(
            """
            Next Steps:
            1. Let's repeat the TSH along with a free T4 in about 6 weeks.
            2. Tell me if you've noticed fatigue, cold intolerance, or weight changes -- it
               helps me interpret the trend.
            """
        ),
        value=(5.5, 9.9, "float1"),
    ),
    Template(
        key="vitamin_d_low",
        category="lab_result",
        subject="Your Vitamin D Result",
        normalcy="abnormal",
        problem="vitamin D deficiency",
        demographic=None,
        action="start vitamin D3 2000 IU daily and recheck in 3 months",
        opening="Your vitamin D level is back.",
        core=_b(
            """
            Your vitamin D is {value} ng/mL, which is low (we like to see at least 30 ng/mL).
            This is very common and easy to correct.
            """
        ),
        steps=_b(
            """
            Next Steps:
            1. Start vitamin D3 2000 IU once daily, with a meal.
            2. We'll recheck the level in about 3 months.
            """
        ),
        value=(12, 25, "int"),
    ),
    Template(
        key="a1c_elevated",
        category="lab_result",
        subject="Your A1c (Blood Sugar) Result",
        normalcy="abnormal",
        problem="prediabetes",
        demographic=None,
        action="lifestyle changes and recheck A1c in 3 months",
        opening="Your hemoglobin A1c (average blood sugar) is back.",
        core=_b(
            """
            Your A1c is {value}%, which falls in the prediabetes range (5.7-6.4%). This is a
            heads-up, not diabetes -- and it's very responsive to small changes.
            """
        ),
        steps=_b(
            """
            Next Steps:
            1. Focus on cutting back sugary drinks and adding a daily walk; I'll send my handout.
            2. We'll recheck in 3 months to see the trend.
            """
        ),
        value=(5.7, 6.4, "float1"),
    ),
    Template(
        key="urine_culture_uti",
        category="lab_result",
        subject="Your Urine Culture Results",
        normalcy="abnormal",
        problem="urinary tract infection",
        demographic=None,
        action="send antibiotic prescription per culture sensitivities",
        opening="Your urine culture results are in.",
        core=_b(
            """
            The culture confirms a urinary tract infection. The good news is it's sensitive to a
            standard antibiotic, so this is straightforward to treat.
            """
        ),
        steps=_b(
            """
            Next Steps:
            1. I'm sending a prescription to your pharmacy now -- please start it today and
               finish the full course.
            2. Drink plenty of water, and let me know if you develop fevers or back pain.
            """
        ),
    ),
    Template(
        key="refill_approved",
        category="refill",
        subject="Your Refill Request",
        normalcy="normal",
        problem="medication refill",
        demographic=None,
        action="refill sent to pharmacy",
        opening="I've reviewed your refill request.",
        core=_b(
            """
            Your refill is approved and has been sent to your pharmacy -- it should be ready
            shortly. You're due for a routine check-in soon, so my office will reach out to
            schedule a visit.
            """
        ),
    ),
    Template(
        key="pap_normal",
        category="lab_result",
        subject="Your Pap Smear Result",
        normalcy="normal",
        problem="cervical cancer screening",
        demographic=None,
        action=None,
        opening="Your Pap smear result is back.",
        core=_b(
            """
            Everything is normal -- no abnormal cells were found, which is exactly what we want
            to see. No action is needed; we'll plan your next routine screening in 3 years.
            """
        ),
    ),
]

_CLOSING = "Please don't hesitate to message me through the portal with any questions."
_SIGNOFF = "Warm regards,\nDr. Example"


def _render_value(spec: tuple[float, float, str], rng: random.Random) -> str:
    lo, hi, kind = spec
    if kind == "int":
        return str(rng.randint(int(lo), int(hi)))
    return f"{rng.uniform(lo, hi):.1f}"


def _render_body(template: Template, first: str, value: str) -> str:
    parts = [
        f"Dear {first},",
        f"I hope you're doing well. {template.opening}",
        template.core.format(first=first, value=value),
    ]
    if template.steps:
        parts.append(template.steps.format(first=first, value=value))
    parts.append(_CLOSING)
    parts.append(_SIGNOFF)
    return "\n\n".join(parts)


def generate(n: int = 60, seed: int = 7) -> list[SentMessage]:
    """Generate ``n`` synthetic sent messages spread across the templates."""
    rng = random.Random(seed)
    base = datetime(2024, 1, 1)
    out: list[SentMessage] = []
    for i in range(n):
        template = TEMPLATES[i % len(TEMPLATES)] if i < len(TEMPLATES) else rng.choice(TEMPLATES)
        first = rng.choice(FIRST_NAMES)
        value = _render_value(template.value, rng) if template.value else ""
        sent_at = base + timedelta(days=rng.randint(0, 720), hours=rng.randint(8, 18))
        gold = {
            "topic": template.key,
            "normalcy": template.normalcy,
            "problem": template.problem,
            "demographic": template.demographic,
            "action": template.action,
            "phrase_key": template.key,
        }
        meta: dict = {"gold": gold}
        if value:
            meta["value"] = value
        out.append(
            SentMessage(
                id=f"syn-{i:05d}",
                sent_at=sent_at,
                author="Dr. Example",
                patient_id=100000 + i,
                subject=template.subject,
                body=_render_body(template, first, value),
                status=rng.choice(["sent", "archived"]),
                category=template.category,
                synthetic=True,
                meta=meta,
            )
        )
    return out
