import { NavLink } from "react-router-dom";
import { useLanguage } from "../i18n/LanguageContext";

const ICONS = {
  dashboard: "🏠",
  invoices: "🧾",
  creditScore: "📈",
  funding: "🏦",
  playground: "🧪",
  about: "❓",
};

export default function Sidebar() {
  const { t } = useLanguage();

  const items = [
    { to: "/", key: "nav_dashboard", icon: ICONS.dashboard, end: true },
    { to: "/invoices", key: "nav_invoices", icon: ICONS.invoices },
    { to: "/credit-score", key: "nav_creditScore", icon: ICONS.creditScore },
    { to: "/funding", key: "nav_funding", icon: ICONS.funding },
    { to: "/playground", key: "nav_playground", icon: ICONS.playground },
    { to: "/about", key: "nav_about", icon: ICONS.about },
  ];

  const linkClass = ({ isActive }) =>
    `flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm transition-colors border-s-2 ${
      isActive
        ? "bg-white/10 text-white font-medium border-teal-400"
        : "text-blue-100/70 hover:bg-white/5 hover:text-white border-transparent"
    }`;

  return (
    <aside className="w-56 shrink-0 bg-[#0f1b3d] min-h-screen py-6 px-3 flex flex-col gap-1">
      <div className="px-4 pb-6 flex items-center gap-2 text-xl font-bold text-white tracking-tight">
        <span className="text-teal-400">T</span>
        <span>{t("appName")}</span>
      </div>
      {items.map((item) => (
        <NavLink key={item.to} to={item.to} end={item.end} className={linkClass}>
          <span>{item.icon}</span>
          <span>{t(item.key)}</span>
        </NavLink>
      ))}
    </aside>
  );
}
