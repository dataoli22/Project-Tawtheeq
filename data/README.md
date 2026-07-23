# Data — Provenance & Licensing

## What's here

- `pipeline/generate_personas.py` — seed pipeline, re-runnable (`python generate_personas.py`)
- `pipeline/scoring.py` — the canonical Tawtheeq Score formula (also imported by the Phase 2 backend)
- `output/personas.json` — structured persona records (schema in the PRD, Section 5.4)
- `output/personas.md` — human-readable data card, one section per persona

## Provenance

The 4 seed personas are **synthetic-but-grounded**: no real personal or business data is used.
Numeric distributions (loan sizing, repayment cadence, delinquency likelihood) are parameterised
from *documented summary statistics* of these public datasets, rather than raw downloads:

| Dataset | License | Used for |
|---|---|---|
| [Kaggle — Give Me Some Credit](https://www.kaggle.com/c/GiveMeSomeCredit) | Public competition data, free to use for research/education | Utilisation & late-payment rate ranges → Transaction Reputation |
| [Kaggle — LendingClub Loan Data](https://www.kaggle.com/datasets/wordsforthewise/lending-club) | CC0 (public domain) | Loan size distribution, repayment history shape → Cashflow Consistency, Transaction Reputation |
| [Kaggle — SBA Loan Data](https://www.kaggle.com/datasets/mirbektoktogaraev/should-this-loan-be-approved-or-denied) | CC0 | SME approval/default by sector → Cashflow Consistency, Network Strength |
| [UAE Open Data Portal (data.gov.ae)](https://www.data.gov.ae) | Open government data | Sector distribution used to weight persona industries (retail, logistics, construction, trade) |

**Why approximation instead of raw CSVs:** downloading Kaggle datasets requires a Kaggle account +
API token, which is a per-developer setup step, not a build-time dependency. To keep
`generate_personas.py` runnable with zero credentials, the sampling parameters (means/spreads per
persona) are set to match the *publicly documented* statistics of each dataset. If you want to
regenerate against the live raw data instead:

1. Get a free Kaggle API token, download the CSVs above into `data/pipeline/raw/`.
2. Set `USE_RAW_KAGGLE_CSVS = True` in `generate_personas.py` and implement `_load_raw_kaggle()`
   to sample directly from the CSVs instead of the hardcoded `base_inputs`.

This keeps the pipeline **reproducible with zero cost and zero credentials** for the MVP, while
staying honest under technical scrutiny: every persona record's `provenance.method` field states
plainly whether it came from raw data or from documented-statistic approximation.

## Regenerating

```bash
# from the repo root — requirements.txt lives there
python -m venv .venv && .venv/Scripts/activate  # or source .venv/bin/activate on Linux/Mac
pip install -r requirements.txt
cd data/pipeline && python generate_personas.py
```

Deterministic given the fixed `SEED` in the script — re-running produces identical output.
To scale beyond 4 personas, extend the `PERSONAS` list (pipeline scales to N with no code changes
beyond adding entries, per PRD Open Question 3).
