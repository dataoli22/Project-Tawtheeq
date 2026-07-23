"""Tawtheeq Score — shared weighted scoring function.

Reused verbatim by the Phase 2 FastAPI scoring engine (backend/app/scoring.py
imports this module directly) so the seed pipeline and the live API can never
drift onto two different formulas.
"""

CATEGORY_WEIGHTS = {
    "cashflow_consistency": 0.30,
    "transaction_reputation": 0.25,
    "platform_behaviour": 0.15,
    "network_strength": 0.15,
    "digital_footprint": 0.15,
}

assert abs(sum(CATEGORY_WEIGHTS.values()) - 1.0) < 1e-9


def compute_score(scoring_inputs: dict) -> int:
    """scoring_inputs: dict of category -> value in [0, 1]. Returns 0-100 int."""
    missing = set(CATEGORY_WEIGHTS) - set(scoring_inputs)
    if missing:
        raise ValueError(f"missing scoring inputs: {missing}")
    total = sum(CATEGORY_WEIGHTS[k] * scoring_inputs[k] for k in CATEGORY_WEIGHTS)
    return round(total * 100)


def explain_score(scoring_inputs: dict) -> list[dict]:
    """Per-category contribution breakdown, sorted by contribution descending.
    Powers both the chatbot's "why this score" answers and the UI's score
    explanation panel.
    """
    breakdown = []
    for category, weight in CATEGORY_WEIGHTS.items():
        value = scoring_inputs[category]
        breakdown.append({
            "category": category,
            "weight": weight,
            "value": round(value, 3),
            "contribution_points": round(weight * value * 100, 1),
        })
    return sorted(breakdown, key=lambda c: c["contribution_points"], reverse=True)


def apply_repayment_boost(scoring_inputs: dict, streak: int) -> dict:
    """Model the deck's "68 -> 72 after 3 successful repayments" mechanic:
    each on-time repayment nudges transaction_reputation and platform_behaviour
    up (diminishing returns via sqrt), capped at 1.0.
    """
    import math

    boosted = dict(scoring_inputs)
    bump = min(0.25, 0.06 * math.sqrt(streak))
    boosted["transaction_reputation"] = min(1.0, boosted["transaction_reputation"] + bump)
    boosted["platform_behaviour"] = min(1.0, boosted["platform_behaviour"] + bump * 0.4)
    return boosted
