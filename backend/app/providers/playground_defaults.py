"""Default raw-signal values for the scoring Playground (a neutral, roughly
mid-scoring baseline) — used to fill in any field the user hasn't set yet, so
the simulator always has a complete, valid input to score.
"""

PLAYGROUND_DEFAULTS = {
    "pos_connector": {
        "monthly_transaction_count": 50,
        "revenue_volatility_pct": 20.0,
    },
    "erp_invoice_connector": {
        "on_time_payment_ratio": 0.6,
    },
    "onchain_reputation_connector": {
        "repayment_streak": 3,
        "late_repayments": 1,
    },
    "vendor_feedback_connector": {
        "avg_vendor_rating": 3.0,
    },
    "kyc_connector": {
        "kyc_completion_days": 5.0,
        "profile_completion_pct": 60,
    },
    "network_graph_connector": {
        "recurring_buyer_count": 8,
        "verified_partner_ratio": 0.5,
    },
    "digital_footprint_connector": {
        "monthly_online_orders": 40,
        "utility_ontime_ratio": 0.5,
    },
}
