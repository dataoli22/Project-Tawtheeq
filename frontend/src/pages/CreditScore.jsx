import { useEffect, useState } from "react";
import { api } from "../api";
import { usePersona } from "../PersonaContext";
import { useLanguage } from "../i18n/LanguageContext";
import ScoreChart from "../components/ScoreChart";

export default function CreditScore() {
  const { personaId } = usePersona();
  const { t } = useLanguage();
  const [score, setScore] = useState(null);
  const [providers, setProviders] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!personaId) return;
    Promise.all([api.getScore(personaId), api.getProviders(personaId)])
      .then(([s, p]) => {
        setScore(s);
        setProviders(p);
      })
      .catch((err) => setError(err.message));
  }, [personaId]);

  if (error) return <p className="text-red-500 p-6">{error}</p>;
  if (!score) return <p className="p-6 text-neutral-400">…</p>;

  return (
    <div className="p-6 space-y-6">
      <div className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 rounded-xl p-6 flex items-center gap-6">
        <div>
          <p className="text-xs text-neutral-400">{t("tawtheeqScore")}</p>
          <p className="text-5xl font-bold text-teal-600">{score.tawtheeq_score}</p>
        </div>
        <div className="flex-1">
          <ScoreChart history={score.score_history} />
        </div>
      </div>

      <div className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 rounded-xl p-4">
        <h2 className="font-medium mb-3">{t("scoreBreakdown")}</h2>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-neutral-400 rtl:text-right">
              <th className="py-1 font-normal"> </th>
              <th className="font-normal">{t("weight")}</th>
              <th className="font-normal">{t("value")}</th>
              <th className="font-normal">{t("points")}</th>
            </tr>
          </thead>
          <tbody>
            {score.breakdown.map((c) => (
              <tr key={c.category} className="border-t border-neutral-100 dark:border-neutral-800">
                <td className="py-2">{t(c.category)}</td>
                <td>{(c.weight * 100).toFixed(0)}%</td>
                <td>
                  <div className="w-32 h-2 bg-neutral-100 dark:bg-neutral-800 rounded-full overflow-hidden">
                    <div className="h-full bg-teal-500" style={{ width: `${c.value * 100}%` }} />
                  </div>
                </td>
                <td>{c.contribution_points}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 rounded-xl p-4">
        <h2 className="font-medium">{t("dataSources")}</h2>
        <p className="text-xs text-neutral-400 mb-3">{t("dataSourcesSubtitle")}</p>
        <div className="grid md:grid-cols-2 gap-3">
          {providers.map((p) => (
            <div
              key={p.provider}
              className="border border-neutral-100 dark:border-neutral-800 rounded-lg p-3 text-sm"
            >
              <div className="flex justify-between items-center mb-1">
                <span className="font-medium">{t(p.category)}</span>
                <span className="text-teal-600 text-xs font-medium">
                  {(p.normalized_value * 100).toFixed(0)}%
                </span>
              </div>
              <p className="text-xs text-neutral-400 mb-2">{p.real_world_analog}</p>
              <ul className="text-xs text-neutral-500 space-y-0.5">
                {Object.entries(p.raw).map(([k, v]) => (
                  <li key={k}>
                    {k.replace(/_/g, " ")}: <span className="text-neutral-700 dark:text-neutral-300">{String(v)}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
