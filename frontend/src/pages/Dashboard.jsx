import { useEffect, useState } from "react";
import { api } from "../api";
import { usePersona } from "../PersonaContext";
import { useLanguage } from "../i18n/LanguageContext";
import ScoreChart from "../components/ScoreChart";

export default function Dashboard() {
  const { personaId } = usePersona();
  const { t } = useLanguage();
  const [score, setScore] = useState(null);
  const [invoices, setInvoices] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!personaId) return;
    Promise.all([api.getScore(personaId), api.getInvoices(personaId)])
      .then(([s, inv]) => {
        setScore(s);
        setInvoices(inv);
      })
      .catch((err) => setError(err.message));
  }, [personaId]);

  if (error) return <p className="text-red-500 p-6">{error}</p>;
  if (!score) return <p className="p-6 text-neutral-400">…</p>;

  const financed = invoices.filter((i) => i.status === "financed" || i.status === "repaid");
  const availableCredit = Math.max(0, score.tawtheeq_score * 1000 - financed.reduce((s, i) => s + i.amount_aed, 0));
  const nextRepayment = invoices.find((i) => i.status === "financed")?.due_date;

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-semibold">
        {t("welcome")}, {score.display_name}!
      </h1>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <Stat label={t("tawtheeqScore")} value={`${score.tawtheeq_score}`} accent />
        <Stat label={t("availableCredit")} value={`AED ${availableCredit.toLocaleString()}`} />
        <Stat label={t("invoicesFinanced")} value={financed.length} />
        <Stat label={t("nextRepayment")} value={nextRepayment || "—"} />
      </div>

      <div className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 rounded-xl p-4">
        <h2 className="font-medium mb-2">{t("scoreTrajectory")}</h2>
        <ScoreChart history={score.score_history} />
      </div>

      <div className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 rounded-xl p-4">
        <h2 className="font-medium mb-3">{t("activeInvoices")}</h2>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-neutral-400 rtl:text-right">
              <th className="py-1 font-normal">{t("counterparty")}</th>
              <th className="font-normal">{t("amount")}</th>
              <th className="font-normal">{t("dueDate")}</th>
              <th className="font-normal">{t("status")}</th>
            </tr>
          </thead>
          <tbody>
            {invoices.map((inv) => (
              <tr key={inv.token_id} className="border-t border-neutral-100 dark:border-neutral-800">
                <td className="py-2">{inv.counterparty}</td>
                <td>{inv.amount_aed.toLocaleString()}</td>
                <td>{inv.due_date}</td>
                <td>
                  <StatusPill status={inv.status} t={t} />
                </td>
              </tr>
            ))}
            {invoices.length === 0 && (
              <tr>
                <td colSpan={4} className="text-neutral-400 py-3">
                  {t("noInvoices")}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export function StatusPill({ status, t }) {
  const styles = {
    financed: "bg-teal-50 text-teal-700 dark:bg-teal-950 dark:text-teal-300",
    pending: "bg-amber-50 text-amber-700 dark:bg-amber-950 dark:text-amber-300",
    repaid: "bg-green-50 text-green-700 dark:bg-green-950 dark:text-green-300",
    overdue: "bg-red-50 text-red-700 dark:bg-red-950 dark:text-red-300",
  };
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs ${styles[status] || "bg-neutral-100 text-neutral-600"}`}>
      {t(status)}
    </span>
  );
}

function Stat({ label, value, accent }) {
  return (
    <div className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 rounded-xl p-4">
      <p className="text-xs text-neutral-400">{label}</p>
      <p className={`text-2xl font-semibold ${accent ? "text-teal-600" : ""}`}>{value}</p>
    </div>
  );
}
