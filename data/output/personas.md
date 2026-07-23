# Tawtheeq Seed Personas — Data Card

Generated: 2026-07-23 · Seed: 42

## Adil — `P1_expat_operator`

**Sector:** Logistics · **Business age:** 14 months

Expat logistics operator. Home-country credit history exists but is not portable in the UAE, so the score must derive entirely from local platform + transaction behaviour.

**Tawtheeq Score:** 58 (→ 61 after 3 on-time repayments)

| Category | Weight | Value | Contribution |
|---|---|---|---|
| Cashflow Consistency | 30% | 0.69 | 20.8 pts |
| Platform Behaviour | 15% | 0.82 | 12.3 pts |
| Transaction Reputation | 25% | 0.45 | 11.2 pts |
| Network Strength | 15% | 0.65 | 9.7 pts |
| Digital Footprint | 15% | 0.25 | 3.8 pts |

**Invoices:** 14 seeded (7 financed, 7 pending, 0 overdue)

**Source datasets:** kaggle:lendingclub, kaggle:sba_loans, yfinance:AEDUSD=X

---

## Kareem — `P2_thin_file_sme`

**Sector:** Construction · **Business age:** 9 months

Construction subcontractor, cash-heavy trade with no formal banking credit history at all. Scoring must lean on cashflow consistency and network strength, since transaction reputation has little to draw on.

**Tawtheeq Score:** 54 (→ 58 after 3 on-time repayments)

| Category | Weight | Value | Contribution |
|---|---|---|---|
| Cashflow Consistency | 30% | 0.77 | 23.0 pts |
| Network Strength | 15% | 0.68 | 10.2 pts |
| Platform Behaviour | 15% | 0.57 | 8.6 pts |
| Transaction Reputation | 25% | 0.32 | 8.0 pts |
| Digital Footprint | 15% | 0.31 | 4.6 pts |

**Invoices:** 11 seeded (5 financed, 5 pending, 1 overdue)

**Source datasets:** kaggle:sba_loans, kaggle:give_me_some_credit, yfinance:AEDUSD=X

---

## Lina — `P3_female_led_micro`

**Sector:** Retail · **Business age:** 22 months

Woman-led retail SME, rejected by banks for lack of collateral despite viable cashflow. Needs a strong cashflow/invoice-history signal to override the collateral-free risk flag.

**Tawtheeq Score:** 67 (→ 70 after 3 on-time repayments)

| Category | Weight | Value | Contribution |
|---|---|---|---|
| Cashflow Consistency | 30% | 0.87 | 26.2 pts |
| Transaction Reputation | 25% | 0.59 | 14.8 pts |
| Platform Behaviour | 15% | 0.75 | 11.3 pts |
| Network Strength | 15% | 0.50 | 7.5 pts |
| Digital Footprint | 15% | 0.46 | 7.0 pts |

**Invoices:** 18 seeded (10 financed, 4 pending, 4 overdue)

**Source datasets:** kaggle:lendingclub, kaggle:give_me_some_credit

---

## Zara — `P4_digital_native_micro`

**Sector:** E-commerce · **Business age:** 6 months

Micro-business owner, Arabic-first / digital-native, no formal financial statements. Scored primarily via platform activity and order fulfilment, so Platform Behaviour and Digital Footprint carry the most weight for this persona.

**Tawtheeq Score:** 60 (→ 63 after 3 on-time repayments)

| Category | Weight | Value | Contribution |
|---|---|---|---|
| Cashflow Consistency | 30% | 0.63 | 18.9 pts |
| Platform Behaviour | 15% | 0.87 | 13.1 pts |
| Digital Footprint | 15% | 0.78 | 11.7 pts |
| Transaction Reputation | 25% | 0.39 | 9.6 pts |
| Network Strength | 15% | 0.42 | 6.3 pts |

**Invoices:** 20 seeded (14 financed, 3 pending, 3 overdue)

**Source datasets:** kaggle:give_me_some_credit, data.gov.ae:sme_sector_stats

---
