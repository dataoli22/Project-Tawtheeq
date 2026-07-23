import { useState } from "react";
import { api } from "../api";
import { usePersona } from "../PersonaContext";
import { useLanguage } from "../i18n/LanguageContext";

export default function ChatWidget() {
  const { personaId } = usePersona();
  const { t } = useLanguage();
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);

  async function send() {
    if (!input.trim() || !personaId) return;
    const userMsg = input.trim();
    setMessages((m) => [...m, { role: "user", text: userMsg }]);
    setInput("");
    setSending(true);
    try {
      const res = await api.chat(personaId, userMsg);
      setMessages((m) => [...m, { role: "bot", text: res.reply }]);
    } catch (err) {
      setMessages((m) => [...m, { role: "bot", text: `Error: ${err.message}` }]);
    } finally {
      setSending(false);
    }
  }

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="fixed bottom-6 end-6 rounded-full bg-teal-600 text-white w-14 h-14 shadow-lg text-xl"
      >
        💬
      </button>
    );
  }

  return (
    <div className="fixed bottom-6 end-6 w-80 h-96 bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 rounded-xl shadow-xl flex flex-col overflow-hidden">
      <div className="flex justify-between items-center px-3 py-2 bg-teal-600 text-white text-sm font-medium">
        <span>{t("assistantName")}</span>
        <button onClick={() => setOpen(false)}>×</button>
      </div>
      <div className="flex-1 overflow-y-auto p-3 space-y-2 text-sm">
        {messages.length === 0 && <p className="text-neutral-400">{t("chatEmpty")}</p>}
        {messages.map((m, i) => (
          <div
            key={i}
            className={`p-2 rounded-lg max-w-[85%] ${
              m.role === "user"
                ? "bg-teal-100 dark:bg-teal-950 ms-auto text-end"
                : "bg-neutral-100 dark:bg-neutral-800"
            }`}
          >
            {m.text}
          </div>
        ))}
        {sending && <div className="text-neutral-400 text-xs">{t("thinking")}</div>}
      </div>
      <div className="flex border-t border-neutral-200 dark:border-neutral-700">
        <input
          className="flex-1 px-3 py-2 text-sm outline-none bg-transparent"
          value={input}
          placeholder={t("chatPlaceholder")}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
        />
        <button onClick={send} className="px-3 text-teal-600 font-medium">
          {t("send")}
        </button>
      </div>
    </div>
  );
}
