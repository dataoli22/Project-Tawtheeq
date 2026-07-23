import { useLanguage } from "../i18n/LanguageContext";

const VIDEO_URL = "/media/Project%20Tawtheeq.mp4";
const DECK_URL = "/media/Project_Tawtheeq.pdf";

const COMPARISON_ROWS = [
  ["Approval Speed", "7–14 days", "2–3 days", "Minutes (on-chain execution)"],
  ["Collateral-Free Lending", "Rare", "Sometimes", "Always (tokenised asset-based)"],
  ["Access for Thin-File SMEs", "Very limited", "Partial", "Embedded alt-data scoring"],
  ["Smart Contract Automation", "No", "No", "Built-in (rules + repayments)"],
  ["Tokenised Invoices / Assets", "No", "No", "Yes (ERC-721/1155-based)"],
  ["Real-Time Credit Scoring", "Static", "Periodic", "Live & programmable"],
  ["Transparency & Traceability", "Opaque", "Limited", "On-chain audit trail"],
];

const SCORING_ROWS = [
  ["Cashflow Consistency", "POS data, invoice history, payment receipts", "30%"],
  ["Transaction Reputation", "On-chain repayment history, vendor feedback, token lifecycle", "25%"],
  ["Platform Behaviour", "Time to upload docs, completion rate, multi-party KYC", "15%"],
  ["Network Strength", "Recurring buyers, B2B relationships, verified partners", "15%"],
  ["Digital Footprint (optional)", "E-commerce accounts, utility payments, social proof", "15%"],
];

const PERSONAS = [
  { name: "Lina", role: "Woman-Led Retail SME", before: "Rejected by banks due to lack of collateral", after: "Received AED 20K in 48 hours via Tawtheeq" },
  { name: "Adil", role: "Expat Logistics Operator", before: "Credit score too low from home country", after: "Approved for 3 loans; now gets better terms" },
  { name: "Zara", role: "Micro-Business, Arabic-First User", before: "No formal credit history or financial statements", after: "Scored via platform activity and order fulfilment" },
  { name: "Kareem", role: "Construction Subcontractor", before: "No banking credit history", after: "Received AED 20K in 48 hours via Tawtheeq" },
];

export default function About() {
  const { t } = useLanguage();

  return (
    <div className="p-6 space-y-8 max-w-4xl">
      <div>
        <h1 className="text-2xl font-semibold">Tawtheeq</h1>
        <p className="text-neutral-500">{t("aboutTagline")}</p>
      </div>

      <Section title={t("theProblem")}>
        <p className="text-sm text-neutral-600 dark:text-neutral-300">
          94% of UAE companies are SMEs, yet a $250B+ SME credit gap exists. Only 28% have ever
          received formal financing, and approval — where it happens at all — takes 30+ days.
          Banks require collateral and years of operating history; digital lenders still lean on
          bureau-style scoring; informal lenders don't scale or build trust. Most SMEs never get a
          "no" from a bank — they just get silence.
        </p>
      </Section>

      <Section title={t("theSolution")}>
        <p className="text-sm text-neutral-600 dark:text-neutral-300 mb-3">
          Tokenise SME invoices, auto-score them from alternative data, and let a smart contract
          disburse funding when conditions are met — fast, transparent, and inclusive, without
          wallets or crypto jargon exposed to the end user.
        </p>
        <div className="flex flex-col md:flex-row gap-3">
          {["Submit Verified Invoice", "Token minted with embedded data", "Smart contract executes funding when conditions are met"].map(
            (step, i) => (
              <div key={step} className="flex-1 bg-teal-50 dark:bg-teal-950 rounded-lg p-3 text-sm">
                <span className="font-semibold text-teal-700 dark:text-teal-300">{i + 1}.</span> {step}
              </div>
            )
          )}
        </div>
      </Section>

      <Section title={t("howScoringWorks")}>
        <p className="text-sm text-neutral-600 dark:text-neutral-300 mb-3">
          Creditworthiness is valuated from verifiable economic activity, not historical credit
          bureau scores — 5 weighted categories, each backed by on-chain or platform-integrated
          data (see the Credit Score screen's Data Sources panel for how this MVP implements each
          one).
        </p>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-neutral-400 rtl:text-right">
              <th className="py-1 font-normal">Category</th>
              <th className="font-normal">Data Sources</th>
              <th className="font-normal">Weight</th>
            </tr>
          </thead>
          <tbody>
            {SCORING_ROWS.map(([cat, sources, weight]) => (
              <tr key={cat} className="border-t border-neutral-100 dark:border-neutral-800">
                <td className="py-2 font-medium">{cat}</td>
                <td className="text-neutral-500">{sources}</td>
                <td>{weight}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className="text-xs text-neutral-400 mt-2">
          After 3 successful repayments, a persona's score rises (e.g. 68 → 72) and unlocks better
          terms — the exact mechanic this demo's Funding screen lets you trigger yourself.
        </p>
      </Section>

      <Section title={t("meetPersonas")}>
        <div className="grid md:grid-cols-2 gap-3">
          {PERSONAS.map((p) => (
            <div key={p.name} className="border border-neutral-100 dark:border-neutral-800 rounded-lg p-3 text-sm">
              <p className="font-medium">
                {p.name} <span className="text-neutral-400 font-normal">— {p.role}</span>
              </p>
              <p className="text-red-500 text-xs mt-1">✕ {p.before}</p>
              <p className="text-green-600 text-xs">✓ {p.after}</p>
            </div>
          ))}
        </div>
      </Section>

      <Section title={t("vsIncumbents")}>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-neutral-400 rtl:text-right">
              <th className="py-1 font-normal">Capability</th>
              <th className="font-normal">Banks</th>
              <th className="font-normal">Fintech Lenders</th>
              <th className="font-normal">Tawtheeq</th>
            </tr>
          </thead>
          <tbody>
            {COMPARISON_ROWS.map(([cap, banks, fintech, us]) => (
              <tr key={cap} className="border-t border-neutral-100 dark:border-neutral-800">
                <td className="py-2 font-medium">{cap}</td>
                <td className="text-neutral-400">{banks}</td>
                <td className="text-neutral-400">{fintech}</td>
                <td className="text-teal-700 dark:text-teal-300 font-medium">{us}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Section>

      <Section title="Pitch Deck & Video">
        <div className="grid md:grid-cols-2 gap-4">
          <video controls className="w-full rounded-lg border border-neutral-200 dark:border-neutral-700" preload="none">
            <source src={VIDEO_URL} type="video/mp4" />
            {t("watchPitch")}
          </video>
          <div className="flex flex-col justify-center gap-2 text-sm">
            <a href={VIDEO_URL} target="_blank" rel="noreferrer" className="text-teal-600 hover:underline">
              🎬 {t("watchPitch")} (new tab)
            </a>
            <a href={DECK_URL} target="_blank" rel="noreferrer" className="text-teal-600 hover:underline">
              📄 {t("downloadDeck")}
            </a>
            <p className="text-xs text-neutral-400 mt-2">
              Served locally from <code>/assets</code> — not committed to the repo (too large for
              git); only available when running the app locally from this machine.
            </p>
          </div>
        </div>
      </Section>

      <Section title={t("howToUseDemo")}>
        <ol className="list-decimal ps-5 text-sm text-neutral-600 dark:text-neutral-300 space-y-1.5">
          <li>Pick a persona from the top bar — each has a different seeded score and narrative.</li>
          <li>
            Go to <b>Invoices</b> and submit one — it mints on-chain and auto-checks funding
            conditions.
          </li>
          <li>
            Check <b>Funding</b>: invoices scoring ≥60 auto-fund ("Fund Now" also available for a
            manual re-check); simulate a repayment to see the score rise.
          </li>
          <li>
            Visit <b>Credit Score</b> to see the weighted breakdown and the "Data Sources" panel —
            every point is traceable to a named alt-data signal.
          </li>
          <li>Ask the chatbot (bottom-right) "why is my score X" or "how do I improve my score".</li>
          <li>Toggle English/العربية and light/dark mode from the top bar at any time.</li>
        </ol>
      </Section>
    </div>
  );
}

function Section({ title, children }) {
  return (
    <div className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 rounded-xl p-4">
      <h2 className="font-medium mb-3">{title}</h2>
      {children}
    </div>
  );
}
