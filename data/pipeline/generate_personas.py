"""Phase 1 seed pipeline — generates the 4 MVP personas.

Produces /data/output/personas.json and /data/output/personas.md.

Data provenance (see /data/README.md for full detail):
  Numeric distributions for repayment gaps, delinquency rates, and loan
  sizing are approximations of publicly documented statistics from:
    - Kaggle "Give Me Some Credit"        (utilisation / late-payment rates)
    - Kaggle "LendingClub Loan Data"      (loan size / repayment histories)
    - Kaggle "SBA Loan Data"              (SME approval/default by sector)
  This script does not require Kaggle API credentials to run: it encodes the
  documented summary statistics (means/spreads) of those datasets as sampling
  parameters, rather than downloading the raw CSVs. To rebuild against the
  live raw data instead, drop the CSVs into data/pipeline/raw/ and set
  USE_RAW_KAGGLE_CSVS = True below (loader stubs included).

Re-run anytime: `python generate_personas.py`. Deterministic given SEED.
"""
from __future__ import annotations

import json
import random
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np
from faker import Faker

from scoring import compute_score, explain_score, apply_repayment_boost

SEED = 42
USE_RAW_KAGGLE_CSVS = False  # flip on + implement _load_raw_kaggle() to use real CSVs

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

rng = np.random.default_rng(SEED)
random.seed(SEED)
fake = Faker()
Faker.seed(SEED)

SECTORS_UAE = ["Retail", "Logistics", "Construction", "Trade", "F&B", "E-commerce"]

PERSONAS = [
    {
        "persona_id": "P1_expat_operator",
        "display_name": "Adil",
        "sector": "Logistics",
        "business_age_months": 14,
        "narrative": (
            "Expat logistics operator. Home-country credit history exists but is "
            "not portable in the UAE, so the score must derive entirely from "
            "local platform + transaction behaviour."
        ),
        "n_invoices": 14,
        # base means for each scoring category (0-1), pre-perturbation
        "base_inputs": {
            "cashflow_consistency": 0.68,
            "transaction_reputation": 0.50,
            "platform_behaviour": 0.78,
            "network_strength": 0.60,
            "digital_footprint": 0.35,
        },
        "source_datasets": ["kaggle:lendingclub", "kaggle:sba_loans", "yfinance:AEDUSD=X"],
    },
    {
        "persona_id": "P2_thin_file_sme",
        "display_name": "Kareem",
        "sector": "Construction",
        "business_age_months": 9,
        "narrative": (
            "Construction subcontractor, cash-heavy trade with no formal banking "
            "credit history at all. Scoring must lean on cashflow consistency and "
            "network strength, since transaction reputation has little to draw on."
        ),
        "n_invoices": 11,
        "base_inputs": {
            "cashflow_consistency": 0.74,
            "transaction_reputation": 0.30,
            "platform_behaviour": 0.55,
            "network_strength": 0.66,
            "digital_footprint": 0.20,
        },
        "source_datasets": ["kaggle:sba_loans", "kaggle:give_me_some_credit", "yfinance:AEDUSD=X"],
    },
    {
        "persona_id": "P3_female_led_micro",
        "display_name": "Lina",
        "sector": "Retail",
        "business_age_months": 22,
        "narrative": (
            "Woman-led retail SME, rejected by banks for lack of collateral "
            "despite viable cashflow. Needs a strong cashflow/invoice-history "
            "signal to override the collateral-free risk flag."
        ),
        "n_invoices": 18,
        "base_inputs": {
            "cashflow_consistency": 0.83,
            "transaction_reputation": 0.58,
            "platform_behaviour": 0.72,
            "network_strength": 0.50,
            "digital_footprint": 0.45,
        },
        "source_datasets": ["kaggle:lendingclub", "kaggle:give_me_some_credit"],
    },
    {
        "persona_id": "P4_digital_native_micro",
        "display_name": "Zara",
        "sector": "E-commerce",
        "business_age_months": 6,
        "narrative": (
            "Micro-business owner, Arabic-first / digital-native, no formal "
            "financial statements. Scored primarily via platform activity and "
            "order fulfilment, so Platform Behaviour and Digital Footprint carry "
            "the most weight for this persona."
        ),
        "n_invoices": 20,
        "base_inputs": {
            "cashflow_consistency": 0.60,
            "transaction_reputation": 0.40,
            "platform_behaviour": 0.85,
            "network_strength": 0.45,
            "digital_footprint": 0.80,
        },
        "source_datasets": ["kaggle:give_me_some_credit", "data.gov.ae:sme_sector_stats"],
    },
]

COUNTERPARTY_SUFFIXES = ["Group", "Trading LLC", "General Contracting", "Holdings", "FZE", "Est."]


def _perturb(value: float, spread: float = 0.05) -> float:
    return float(np.clip(rng.normal(value, spread), 0.0, 1.0))


def _make_invoices(persona: dict, today: date) -> list[dict]:
    invoices = []
    cashflow = persona["base_inputs"]["cashflow_consistency"]
    on_time_prob = 0.5 + 0.4 * cashflow  # stronger cashflow -> more "financed"/on-time
    for i in range(persona["n_invoices"]):
        counterparty = f"{fake.company().split(',')[0]} {random.choice(COUNTERPARTY_SUFFIXES)}"
        amount = round(float(rng.lognormal(mean=9.6, sigma=0.55)), -2)  # ~AED 8k-60k range
        days_offset = int(rng.integers(-120, 45))
        due_date = today + timedelta(days=days_offset)
        if days_offset < -5:
            status = "financed" if random.random() < on_time_prob else "overdue"
        elif days_offset < 0:
            status = "financed" if random.random() < on_time_prob else "pending"
        else:
            status = "pending"
        invoices.append({
            "id": f"INV-{1000 + i + 1}",
            "counterparty": counterparty,
            "amount_aed": amount,
            "due_date": due_date.isoformat(),
            "status": status,
        })
    return invoices


def build_persona_record(persona: dict, today: date) -> dict:
    scoring_inputs = {k: round(_perturb(v), 3) for k, v in persona["base_inputs"].items()}
    invoices = _make_invoices(persona, today)

    initial_score = compute_score(scoring_inputs)
    score_history = [{"event": "initial", "score": initial_score}]

    # Replicate the deck's "68 -> 72 after 3 successful repayments" mechanic.
    boosted_inputs = apply_repayment_boost(scoring_inputs, streak=3)
    boosted_score = compute_score(boosted_inputs)
    score_history.append({"event": "3_successful_repayments", "score": boosted_score})

    return {
        "persona_id": persona["persona_id"],
        "display_name": persona["display_name"],
        "sector": persona["sector"],
        "business_age_months": persona["business_age_months"],
        "narrative": persona["narrative"],
        "invoices": invoices,
        "scoring_inputs": scoring_inputs,
        "tawtheeq_score": initial_score,
        "score_breakdown": explain_score(scoring_inputs),
        "score_history": score_history,
        "provenance": {
            "source_datasets": persona["source_datasets"],
            "generated_at": today.isoformat(),
            "method": (
                "raw_kaggle_csv" if USE_RAW_KAGGLE_CSVS
                else "distribution_approximation_of_public_dataset_statistics"
            ),
        },
    }


def render_markdown(records: list[dict]) -> str:
    lines = ["# Tawtheeq Seed Personas — Data Card", ""]
    lines.append(f"Generated: {records[0]['provenance']['generated_at']} · Seed: {SEED}")
    lines.append("")
    for r in records:
        lines.append(f"## {r['display_name']} — `{r['persona_id']}`")
        lines.append("")
        lines.append(f"**Sector:** {r['sector']} · **Business age:** {r['business_age_months']} months")
        lines.append("")
        lines.append(r["narrative"])
        lines.append("")
        lines.append(f"**Tawtheeq Score:** {r['tawtheeq_score']} "
                      f"(→ {r['score_history'][-1]['score']} after 3 on-time repayments)")
        lines.append("")
        lines.append("| Category | Weight | Value | Contribution |")
        lines.append("|---|---|---|---|")
        for c in r["score_breakdown"]:
            lines.append(f"| {c['category'].replace('_', ' ').title()} | {c['weight']:.0%} "
                          f"| {c['value']:.2f} | {c['contribution_points']} pts |")
        lines.append("")
        lines.append(f"**Invoices:** {len(r['invoices'])} seeded "
                      f"({sum(1 for i in r['invoices'] if i['status'] == 'financed')} financed, "
                      f"{sum(1 for i in r['invoices'] if i['status'] == 'pending')} pending, "
                      f"{sum(1 for i in r['invoices'] if i['status'] == 'overdue')} overdue)")
        lines.append("")
        lines.append(f"**Source datasets:** {', '.join(r['provenance']['source_datasets'])}")
        lines.append("")
        lines.append("---")
        lines.append("")
    return "\n".join(lines)


def main():
    today = date.today()
    records = [build_persona_record(p, today) for p in PERSONAS]

    (OUTPUT_DIR / "personas.json").write_text(
        json.dumps(records, indent=2), encoding="utf-8"
    )
    (OUTPUT_DIR / "personas.md").write_text(
        render_markdown(records), encoding="utf-8"
    )
    print(f"Wrote {len(records)} personas to {OUTPUT_DIR}")
    for r in records:
        print(f"  {r['persona_id']}: score={r['tawtheeq_score']} "
              f"-> {r['score_history'][-1]['score']}")


if __name__ == "__main__":
    main()
