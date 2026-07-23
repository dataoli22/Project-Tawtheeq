import { useEffect, useState } from "react";
import { api } from "../api";
import { usePersona } from "../PersonaContext";
import { useLanguage } from "../i18n/LanguageContext";
import { StatusPill } from "./Dashboard";

export default function Invoices() {
  const { personaId } = usePersona();
  const { t } = useLanguage();
  const [invoices, setInvoices] = useState([]);
  const [form, setForm] = useState({ counterparty: "", amount_aed: "", due_date: "" });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  function refresh() {
    if (personaId) api.getInvoices(personaId).then(setInvoices).catch((err) => setError(err.message));
  }

  useEffect(refresh, [personaId]);

  async function onSubmit(e) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await api.createInvoice({
        persona_id: personaId,
        counterparty: form.counterparty,
        amount_aed: Number(form.amount_aed),
        due_date: form.due_date,
      });
      setForm({ counterparty: "", amount_aed: "", due_date: "" });
      refresh();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div className="bg-white dark:bg-neutral-900 border border-dashed border-neutral-300 dark:border-neutral-700 rounded-xl p-6">
        <h1 className="text-lg font-semibold mb-1">{t("uploadInvoice")}</h1>
        <p className="text-sm text-neutral-400 mb-4">{t("dragDrop")}</p>
        <form onSubmit={onSubmit} className="grid md:grid-cols-4 gap-3 items-end">
          <label className="block md:col-span-2">
            <span className="text-xs text-neutral-500">{t("counterparty")}</span>
            <input
              required
              className="input mt-1"
              value={form.counterparty}
              onChange={(e) => setForm({ ...form, counterparty: e.target.value })}
            />
          </label>
          <label className="block">
            <span className="text-xs text-neutral-500">{t("amount")} (AED)</span>
            <input
              required
              type="number"
              min="1"
              className="input mt-1"
              value={form.amount_aed}
              onChange={(e) => setForm({ ...form, amount_aed: e.target.value })}
            />
          </label>
          <label className="block">
            <span className="text-xs text-neutral-500">{t("dueDate")}</span>
            <input
              required
              type="date"
              className="input mt-1"
              value={form.due_date}
              onChange={(e) => setForm({ ...form, due_date: e.target.value })}
            />
          </label>
          <button
            disabled={submitting}
            className="bg-teal-600 text-white px-4 py-2 rounded-lg disabled:opacity-50 md:col-span-4 w-fit"
          >
            {submitting ? t("submitting") : t("submitInvoice")}
          </button>
        </form>
        {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
      </div>

      <div className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-neutral-400 bg-neutral-50 dark:bg-neutral-800 rtl:text-right">
              <th className="py-2 px-3 font-normal">{t("invoice")}</th>
              <th className="font-normal">{t("counterparty")}</th>
              <th className="font-normal">{t("date")}</th>
              <th className="font-normal">{t("amount")}</th>
              <th className="font-normal">{t("status")}</th>
            </tr>
          </thead>
          <tbody>
            {invoices.map((inv) => (
              <tr key={inv.token_id} className="border-t border-neutral-100 dark:border-neutral-800">
                <td className="py-2 px-3">#{inv.token_id}</td>
                <td>{inv.counterparty}</td>
                <td>{inv.due_date}</td>
                <td>AED {inv.amount_aed.toLocaleString()}</td>
                <td>
                  <StatusPill status={inv.status} t={t} />
                </td>
              </tr>
            ))}
            {invoices.length === 0 && (
              <tr>
                <td colSpan={5} className="text-neutral-400 py-4 px-3">
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
