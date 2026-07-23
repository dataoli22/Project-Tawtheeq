"""Adapter implementations. Each `normalize()` inverts the metric shape
`data/pipeline/provider_seed.py` generated, so a provider's normalized value
round-trips back to (approximately) the scoring_inputs value it was seeded
from — the seed script and these adapters must be read together.
"""
from app.chain import get_chain_client
from app.providers.base import DataProvider


class PosConnector(DataProvider):
    """Stands in for a UAE POS/payments API (e.g. Network International,
    Magnati) reporting monthly transaction counts, volume, and volatility.
    """

    name = "pos_connector"
    category = "cashflow_consistency"
    real_world_analog = "Network International / Magnati POS analytics API"

    def normalize(self, raw: dict) -> float:
        # More transactions and lower revenue volatility -> higher score.
        volume_score = min(1.0, raw["monthly_transaction_count"] / 100)
        stability_score = max(0.0, 1 - raw["revenue_volatility_pct"] / 40)
        return 0.5 * volume_score + 0.5 * stability_score


class ErpInvoiceConnector(DataProvider):
    """Stands in for an accounting/ERP API (e.g. Zoho Books, QuickBooks)
    reporting invoice payment timeliness.
    """

    name = "erp_invoice_connector"
    category = "cashflow_consistency"
    real_world_analog = "Zoho Books / QuickBooks invoicing API"

    def normalize(self, raw: dict) -> float:
        return raw["on_time_payment_ratio"]


class OnChainReputationConnector(DataProvider):
    """Reads the persona's actual on-chain repayment streak from
    CreditLogic/InvoiceToken once invoices exist — this one is NOT a stub,
    it's the real on-chain audit trail the PRD describes. Falls back to the
    seeded baseline streak if the persona has no on-chain history yet.
    """

    name = "onchain_reputation_connector"
    category = "transaction_reputation"
    real_world_analog = "Tawtheeq's own on-chain CreditLogic/InvoiceToken event log"

    def fetch_raw(self, persona_id: str) -> dict:
        from app import store

        seeded = store.get_provider_signal(persona_id, self.name) or {}
        invoices = store.list_invoices(persona_id)
        onchain_streak = sum(1 for i in invoices if i["status"] == "repaid")
        return {**seeded, "onchain_repayment_streak": onchain_streak}

    def normalize(self, raw: dict) -> float:
        streak = max(raw.get("repayment_streak", 0), raw.get("onchain_repayment_streak", 0))
        late = raw.get("late_repayments", 0)
        return max(0.0, min(1.0, (streak - 0.5 * late) / 10))


class VendorFeedbackConnector(DataProvider):
    """Stands in for a vendor/counterparty rating system (e.g. post-invoice
    satisfaction surveys, marketplace seller ratings).
    """

    name = "vendor_feedback_connector"
    category = "transaction_reputation"
    real_world_analog = "Marketplace/vendor satisfaction rating API"

    def normalize(self, raw: dict) -> float:
        return (raw["avg_vendor_rating"] - 1) / 4  # 1-5 scale -> 0-1


class KycConnector(DataProvider):
    """Stands in for a KYC/onboarding API (e.g. Uqudo, Smart Dubai KYC)
    reporting how quickly and completely a persona onboarded.
    """

    name = "kyc_connector"
    category = "platform_behaviour"
    real_world_analog = "Uqudo / Smart Dubai digital KYC API"

    def normalize(self, raw: dict) -> float:
        speed_score = max(0.0, 1 - raw["kyc_completion_days"] / 10)
        completion_score = raw["profile_completion_pct"] / 100
        return 0.5 * speed_score + 0.5 * completion_score


class NetworkGraphConnector(DataProvider):
    """Stands in for a B2B relationship graph derived from invoice
    counterparties and verified-partner status (e.g. a trade-network API).
    """

    name = "network_graph_connector"
    category = "network_strength"
    real_world_analog = "B2B trade-network / verified-partner registry API"

    def normalize(self, raw: dict) -> float:
        buyer_score = min(1.0, raw["recurring_buyer_count"] / 20)
        return 0.5 * buyer_score + 0.5 * raw["verified_partner_ratio"]


class DigitalFootprintConnector(DataProvider):
    """Stands in for e-commerce + utility-payment APIs (e.g. Shopify/Salla
    order history, DEWA utility payment records).
    """

    name = "digital_footprint_connector"
    category = "digital_footprint"
    real_world_analog = "Shopify/Salla order history + DEWA utility payment API"

    def normalize(self, raw: dict) -> float:
        orders_score = min(1.0, raw["monthly_online_orders"] / 150)
        return 0.5 * orders_score + 0.5 * raw["utility_ontime_ratio"]
