"""Builds seeded raw signals per persona from their Phase 1 scoring_inputs,
so each adapter's normalize() round-trips back to (approximately) the same
value the persona was generated with. Read alongside app/providers/adapters.py
— the two must stay in sync since one is the inverse of the other.

This is what a real deployment would fetch from the actual APIs named in each
adapter's `real_world_analog`; here it's deterministic so the demo's
narrative (score 58/54/67/60 etc.) stays consistent with Phase 1.
"""


def build_seed_signals(persona: dict) -> dict[str, dict]:
    inputs = persona["scoring_inputs"]
    v_cash = inputs["cashflow_consistency"]
    v_rep = inputs["transaction_reputation"]
    v_plat = inputs["platform_behaviour"]
    v_net = inputs["network_strength"]
    v_dig = inputs["digital_footprint"]

    return {
        "pos_connector": {
            "monthly_transaction_count": round(v_cash * 100),
            "revenue_volatility_pct": round((1 - v_cash) * 40, 1),
        },
        "erp_invoice_connector": {
            "on_time_payment_ratio": round(v_cash, 3),
            "avg_days_to_pay": round(3 + (1 - v_cash) * 27, 1),
            "invoice_count_90d": len(persona["invoices"]),
        },
        "onchain_reputation_connector": {
            "repayment_streak": round(v_rep * 10),
            "late_repayments": 0,
        },
        "vendor_feedback_connector": {
            "avg_vendor_rating": round(1 + v_rep * 4, 1),
            "feedback_count": round(5 + v_rep * 20),
        },
        "kyc_connector": {
            "kyc_completion_days": round((1 - v_plat) * 10, 1),
            "profile_completion_pct": round(v_plat * 100),
            "doc_upload_avg_hours": round(2 + (1 - v_plat) * 46, 1),
        },
        "network_graph_connector": {
            "recurring_buyer_count": round(v_net * 20),
            "verified_partner_ratio": round(v_net, 2),
            "distinct_counterparties": round(2 + v_net * 15),
        },
        "digital_footprint_connector": {
            "monthly_online_orders": round(v_dig * 150),
            "utility_ontime_ratio": round(v_dig, 2),
            "social_verified": v_dig > 0.5,
        },
    }
