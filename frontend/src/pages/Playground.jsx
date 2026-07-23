import { useEffect, useRef, useState } from "react";
import { api } from "../api";
import { useLanguage } from "../i18n/LanguageContext";

// UI metadata (label/min/max/step) for each raw signal field. Kept in sync
// by hand with backend/app/providers/adapters.py's normalize() inputs —
// values themselves come from GET /playground/defaults.
const FIELD_SPECS = {
  pos_connector: {
    monthly_transaction_count: { label: "Monthly POS Transactions", min: 0, max: 150, step: 1 },
    revenue_volatility_pct: { label: "Revenue Volatility (%, lower is better)", min: 0, max: 40, step: 1 },
  },
  erp_invoice_connector: {
    on_time_payment_ratio: { label: "On-Time Invoice Payment Ratio", min: 0, max: 1, step: 0.01 },
  },
  onchain_reputation_connector: {
    repayment_streak: { label: "On-Chain Repayment Streak", min: 0, max: 10, step: 1 },
    late_repayments: { label: "Late Repayments (lower is better)", min: 0, max: 10, step: 1 },
  },
  vendor_feedback_connector: {
    avg_vendor_rating: { label: "Avg Vendor Rating (1-5)", min: 1, max: 5, step: 0.1 },
  },
  kyc_connector: {
    kyc_completion_days: { label: "KYC Completion Time (days, lower is better)", min: 0, max: 10, step: 0.5 },
    profile_completion_pct: { label: "Profile Completion (%)", min: 0, max: 100, step: 1 },
  },
  network_graph_connector: {
    recurring_buyer_count: { label: "Recurring Buyers", min: 0, max: 20, step: 1 },
    verified_partner_ratio: { label: "Verified Partner Ratio", min: 0, max: 1, step: 0.01 },
  },
  digital_footprint_connector: {
    monthly_online_orders: { label: "Monthly Online Orders", min: 0, max: 150, step: 1 },
    utility_ontime_ratio: { label: "Utility Payment On-Time Ratio", min: 0, max: 1, step: 0.01 },
  },
};

export default function Playground() {
  const { t } = useLanguage();
  const [meta, setMeta] = useState(null); // provider -> {category, real_world_analog, fields: defaults}
  const [signals, setSignals] = useState(null); // provider -> {field: value}
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const debounceRef = useRef(null);

  useEffect(() => {
    api
      .getPlaygroundDefaults()
      .then((defaults) => {
        setMeta(defaults);
        const initial = Object.fromEntries(
          Object.entries(defaults).map(([name, d]) => [name, { ...d.fields }])
        );
        setSignals(initial);
      })
      .catch((err) => setError(err.message));
  }, []);

  useEffect(() => {
    if (!signals) return;
    clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      api.scorePlayground(signals).then(setResult).catch((err) => setError(err.message));
    }, 200);
    return () => clearTimeout(debounceRef.current);
  }, [signals]);

  function updateField(provider, field, value) {
    setSignals((s) => ({ ...s, [provider]: { ...s[provider], [field]: value } }));
  }

  function resetDefaults() {
    if (!meta) return;
    setSignals(Object.fromEntries(Object.entries(meta).map(([name, d]) => [name, { ...d.fields }])));
  }

  if (error) return <p className="text-red-500 p-6">{error}</p>;
  if (!meta || !signals) return <p className="p-6 text-neutral-400">…</p>;

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">{t("playgroundTitle")}</h1>
          <p className="text-sm text-neutral-500 max-w-2xl">{t("playgroundIntro")}</p>
        </div>
        <button
          onClick={resetDefaults}
          className="shrink-0 border border-neutral-300 dark:border-neutral-700 px-3 py-1.5 rounded-lg text-sm"
        >
          {t("resetDefaults")}
        </button>
      </div>

      <div className="grid lg:grid-cols-[1fr_360px] gap-6 items-start">
        <div className="grid md:grid-cols-2 gap-4">
          {Object.entries(meta).map(([name, d]) => (
            <div key={name} className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 rounded-xl p-4">
              <p className="text-xs uppercase tracking-wide text-teal-600 font-medium">{t(d.category)}</p>
              <p className="text-xs text-neutral-400 mb-3">{d.real_world_analog}</p>
              <div className="space-y-3">
                {Object.entries(FIELD_SPECS[name]).map(([field, spec]) => (
                  <div key={field}>
                    <div className="flex justify-between text-xs text-neutral-500 mb-1">
                      <span>{spec.label}</span>
                      <span className="font-medium text-neutral-700 dark:text-neutral-300">
                        {signals[name][field]}
                      </span>
                    </div>
                    <input
                      type="range"
                      min={spec.min}
                      max={spec.max}
                      step={spec.step}
                      value={signals[name][field]}
                      onChange={(e) => updateField(name, field, Number(e.target.value))}
                      className="w-full accent-teal-600"
                    />
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="sticky top-4 space-y-4">
          <div className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 rounded-xl p-4 text-center">
            <p className="text-xs text-neutral-400">{t("liveScore")}</p>
            <p className="text-5xl font-bold text-teal-600 my-2">{result?.tawtheeq_score ?? "…"}</p>
          </div>

          {result && (
            <div className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 rounded-xl p-4">
              <h2 className="font-medium mb-3 text-sm">{t("scoreBreakdown")}</h2>
              <table className="w-full text-xs">
                <tbody>
                  {result.breakdown.map((c) => (
                    <tr key={c.category} className="border-t border-neutral-100 dark:border-neutral-800">
                      <td className="py-1.5">{t(c.category)}</td>
                      <td className="w-24">
                        <div className="w-full h-1.5 bg-neutral-100 dark:bg-neutral-800 rounded-full overflow-hidden">
                          <div className="h-full bg-teal-500" style={{ width: `${c.value * 100}%` }} />
                        </div>
                      </td>
                      <td className="text-right ps-2 text-neutral-500">{c.contribution_points}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <div className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 rounded-xl p-4">
            <h2 className="font-medium mb-2 text-sm">{t("guideTitle")}</h2>
            <ol className="text-xs text-neutral-500 space-y-1.5">
              <li>{t("guideStep1")}</li>
              <li>{t("guideStep2")}</li>
              <li>{t("guideStep3")}</li>
              <li>{t("guideStep4")}</li>
              <li>{t("guideStep5")}</li>
              <li>{t("guideStep6")}</li>
            </ol>
          </div>
        </div>
      </div>
    </div>
  );
}
