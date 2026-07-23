"""Mock adapters for the alternative-data sources named in the PRD (Section 2)
and the data-flow diagram's "Fetch Alternate Data from ERP and Transactions"
step, which runs before "Run Credit Scoring".

Each adapter is named after the category of real provider it stands in for
and returns raw, source-shaped metrics (transaction counts, KYC turnaround
days, vendor ratings, etc.) from a seeded SQLite table
(`provider_signals`) rather than a live API call. Swapping in the real
integration later means replacing `fetch()`'s body only — `normalize()` and
everything downstream (scoring.py) is untouched.

Registry below groups adapters by the 5 PRD scoring categories.
"""
from app.providers.adapters import (
    PosConnector,
    ErpInvoiceConnector,
    OnChainReputationConnector,
    VendorFeedbackConnector,
    KycConnector,
    NetworkGraphConnector,
    DigitalFootprintConnector,
)

PROVIDERS_BY_CATEGORY = {
    "cashflow_consistency": [PosConnector(), ErpInvoiceConnector()],
    "transaction_reputation": [OnChainReputationConnector(), VendorFeedbackConnector()],
    "platform_behaviour": [KycConnector()],
    "network_strength": [NetworkGraphConnector()],
    "digital_footprint": [DigitalFootprintConnector()],
}

ALL_PROVIDERS = [p for providers in PROVIDERS_BY_CATEGORY.values() for p in providers]
PROVIDERS_BY_NAME = {p.name: p for p in ALL_PROVIDERS}

__all__ = ["PROVIDERS_BY_CATEGORY", "ALL_PROVIDERS", "PROVIDERS_BY_NAME"]
