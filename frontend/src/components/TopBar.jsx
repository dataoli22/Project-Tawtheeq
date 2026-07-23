import { usePersona } from "../PersonaContext";
import { useLanguage } from "../i18n/LanguageContext";
import { useTheme } from "../ThemeContext";

export default function TopBar() {
  const { personas, personaId, setPersonaId, loading, error } = usePersona();
  const { lang, setLang } = useLanguage();
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="flex items-center justify-between px-6 py-3 bg-white dark:bg-neutral-900 border-b border-neutral-200 dark:border-neutral-800">
      <div className="text-sm">
        {error && <span className="text-red-500">{error}</span>}
        {!error && !loading && (
          <select
            value={personaId || ""}
            onChange={(e) => setPersonaId(e.target.value)}
            className="input !w-auto"
          >
            {personas.map((p) => (
              <option key={p.persona_id} value={p.persona_id}>
                {p.display_name} — {p.sector}
              </option>
            ))}
          </select>
        )}
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={toggleTheme}
          aria-label="Toggle dark mode"
          className="w-8 h-8 flex items-center justify-center rounded-full border border-neutral-200 dark:border-neutral-700 text-sm"
        >
          {theme === "dark" ? "☀️" : "🌙"}
        </button>

        <div className="flex rounded-full border border-neutral-200 dark:border-neutral-700 overflow-hidden text-sm">
          <button
            onClick={() => setLang("en")}
            className={`px-3 py-1 ${lang === "en" ? "bg-teal-600 text-white" : "text-neutral-500"}`}
          >
            English
          </button>
          <button
            onClick={() => setLang("ar")}
            className={`px-3 py-1 ${lang === "ar" ? "bg-teal-600 text-white" : "text-neutral-500"}`}
          >
            العربية
          </button>
        </div>
      </div>
    </div>
  );
}
