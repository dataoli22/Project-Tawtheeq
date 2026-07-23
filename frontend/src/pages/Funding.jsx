import { useEffect, useState } from "react";
import { api } from "../api";
import { usePersona } from "../PersonaContext";
import { useLanguage } from "../i18n/LanguageContext";

const TAKE_RATE = 0.015; // mirrors CreditLogic.takeRateBps

export default function Funding() {
  const { personaId } = usePersona();
  const { t } = useLanguage();
  const [invoices, setInvoices] = useState([]);
  const [busyId, setBusyId] = useState(null);
  const [error, setError] = useState(null);

  function refresh() {
    if (personaId) api.getInvoices(personaId).then(setInvoices).catch((err) => setError(err.message));
  }

  useEffect(refresh, [personaId]);

  async function fund(tokenId) {
    setBusyId(tokenId);
    try {
      await api.fundInvoice?.(tokenId);
    } finally {
      setBusyId(null);
      refresh();
    }
  }

  async function repay(tokenId) {
    setBusyId(tokenId);
    try {
      await api.repay(tokenId);
    } finally {
      setBusyId(null);
      refresh();
    }
  }

  const pending = invoices.filter((i) => i.status === "pending");
  const financed = invoices.filter((i) => i.status === "financed");

  if (error) return <p className="text-red-500 p-6">{error}</p>;

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-semibold">{t("funding")}</h1>

      <Section title={t("awaitingFunding")} empty={t("noPendingFunding")} items={pending}>
        {(inv) => (
          <FundCard key={inv.token_id} inv={inv} t={t}>
            <button
              onClick={() => fund(inv.token_id)}
              disabled={busyId === inv.token_id}
              className="bg-teal-600 text-white px-4 py-1.5 rounded-lg text-sm disabled:opacity-50"
            >
              {t("fundNow")}
            </button>
          </FundCard>
        )}
      </Section>

      <Section title={t("readyToRepay")} empty={t("noFinancedInvoices")} items={financed}>
        {(inv) => (
          <FundCard key={inv.token_id} inv={inv} t={t}>
            <button
              onClick={() => repay(inv.token_id)}
              disabled={busyId === inv.token_id}
              className="bg-green-600 text-white px-4 py-1.5 rounded-lg text-sm disabled:opacity-50"
            >
              {busyId === inv.token_id ? t("recordingRepayment") : t("simulateRepayment")}
            </button>
          </FundCard>
        )}
      </Section>
    </div>
  );
}

function Section({ title, empty, items, children }) {
  return (
    <div className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 rounded-xl p-4">
      <h2 className="font-medium mb-3">{title}</h2>
      {items.length === 0 ? (
        <p className="text-neutral-400 text-sm">{empty}</p>
      ) : (
        <div className="space-y-3">{items.map(children)}</div>
      )}
    </div>
  );
}

function FundCard({ inv, t, children }) {
  const fee = Math.round(inv.amount_aed * TAKE_RATE);
  return (
    <div className="flex items-center justify-between border border-neutral-100 dark:border-neutral-800 rounded-lg p-3">
      <div>
        <p className="font-medium">
          #{inv.token_id} · {inv.counterparty}
        </p>
        <p className="text-xs text-neutral-400">
          AED {inv.amount_aed.toLocaleString()} · {t("fee")} {fee.toLocaleString()} · {t("dueDate")} {inv.due_date}
        </p>
      </div>
      {children}
    </div>
  );
}
