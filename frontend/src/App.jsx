import { BrowserRouter, Routes, Route } from "react-router-dom";
import { PersonaProvider } from "./PersonaContext";
import { LanguageProvider } from "./i18n/LanguageContext";
import { ThemeProvider } from "./ThemeContext";
import Sidebar from "./components/Sidebar";
import TopBar from "./components/TopBar";
import ChatWidget from "./components/ChatWidget";
import Dashboard from "./pages/Dashboard";
import Invoices from "./pages/Invoices";
import CreditScore from "./pages/CreditScore";
import Funding from "./pages/Funding";
import Playground from "./pages/Playground";
import About from "./pages/About";

export default function App() {
  return (
    <ThemeProvider>
      <LanguageProvider>
        <PersonaProvider>
          <BrowserRouter>
            <div className="flex min-h-screen">
              <Sidebar />
              <div className="flex-1 min-w-0">
                <TopBar />
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/invoices" element={<Invoices />} />
                  <Route path="/credit-score" element={<CreditScore />} />
                  <Route path="/funding" element={<Funding />} />
                  <Route path="/playground" element={<Playground />} />
                  <Route path="/about" element={<About />} />
                </Routes>
              </div>
              <ChatWidget />
            </div>
          </BrowserRouter>
        </PersonaProvider>
      </LanguageProvider>
    </ThemeProvider>
  );
}
