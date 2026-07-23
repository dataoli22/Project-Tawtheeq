# Project Tawtheeq — Tokenised Credit MVP

Open-source, zero-cost proof-of-concept of the full loop described in the PRD
([Tawtheeq_MVP_PRD.md](Tawtheeq_MVP_PRD.md)):

**invoice submitted → alt-data score computed → invoice tokenised (ERC-721) →
smart contract auto-disburses → repayment → score trajectory updates** — with
a persona-grounded chatbot explaining every score.

## Layout

| Path | What |
|---|---|
| [`data/`](data/) | Phase 1 — seed pipeline, 4 persona records, provenance docs |
| [`contracts/`](contracts/) | Phase 2 — Hardhat project: `InvoiceToken` (ERC-721), `CreditLogic` |
| [`backend/`](backend/) | Phase 2 — FastAPI oracle/API layer wrapping the contracts + alt-data provider adapters |
| [`frontend/`](frontend/) | Phase 3 — React + Tailwind sidebar-nav app, English/Arabic + RTL, light/dark mode, chatbot |

## Running the full demo locally

Four terminals:

```bash
# 1. Local chain
cd contracts && npm install && npm run node

# 2. Deploy contracts (writes ABI + address into backend/app/chain_config/)
cd contracts && npm run deploy:local

# 3. Backend API (run from the repo root — requirements.txt and .env live here)
python -m venv .venv && .venv/Scripts/activate   # or source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
cd backend && uvicorn app.main:app --reload --port 8000

# 4. Frontend
cd frontend
npm install
npm run dev
```

Open the printed Vite URL. The sidebar has 5 screens:

- **Dashboard** — score, available credit, active invoices at a glance.
- **Invoices** — upload a new invoice (mints on-chain, auto-checks funding).
- **Credit Score** — full weighted breakdown + a "Data Sources" panel showing exactly which alt-data signal drove each point.
- **Funding** — approve/deny is automatic at mint time (score ≥ 60 threshold), but this screen lets you re-check funding manually and simulate repayments to watch the score climb.
- **Playground** — a sandbox: drag sliders for every raw alt-data signal (POS volume, KYC speed, vendor ratings, etc.) and watch the Tawtheeq Score recompute live via `POST /playground/score` — pure function of its input, touches no persona/DB/chain. Includes a baked-in step-by-step guide.
- **About & Help** — what Tawtheeq is (problem, solution, scoring model, personas), plus a walkthrough of how to use this demo.

Top bar: pick a persona, toggle English/العربية (full RTL layout, not just translated strings), and toggle light/dark mode — all independent of your OS setting and persisted in `localStorage`.

To regenerate the seed personas: `cd data/pipeline && python generate_personas.py`.

## Milestone status (PRD Section 9)

- ✅ **M1** — data pipeline live, 4 personas with documented provenance
- ✅ **M2** — mint → score → fund → repay loop runs end-to-end on Hardhat local network
- ⬜ **M3** — Sepolia testnet deployment (deferred; local Hardhat is the guaranteed demo path per PRD Section 11)
- ✅ **M4** — Dashboard / Invoices / Credit Score / Funding wired to the live API, English/Arabic + RTL
- ✅ **M5** — chatbot answers score-explanation questions for all 4 personas (5-provider fallback chain, see below)
- 🟡 **M6** — demo polish: light/dark mode, About & Help page, and alt-data provider transparency done; Sepolia deployment still open

## Notes on fidelity to the PRD

- Funding threshold (score ≥ 60) and take rate (1.5%) are configurable constants in `CreditLogic.sol`, matching Section 6.4.
- The oracle pattern (Section 6.2) is a plain backend-signed push — `pushScore` / `requestFunding` / `recordRepayment` — no paid oracle network.
- Chatbot guardrails (Section 7.4): context-injected per persona only, never fine-tuned, never discusses other personas' data.
- Alt-data provider adapters (Section 6.5): each of the 5 scoring categories is backed by a named mock adapter (`backend/app/providers/adapters.py`) documenting the real API it stands in for (POS, ERP, KYC, B2B network, e-commerce/utility). `GET /providers/{persona_id}` and the Credit Score screen's "Data Sources" panel make every score traceable to a specific signal, per Section 10's success metric.

### Chatbot providers

`backend/app/chatbot.py` supports five providers, tried in this order:

1. Whichever of **Anthropic / OpenAI / Gemini / Groq** has an API key set in the root `.env` (`CHAT_PROVIDER=auto`, the default), or a specific one pinned via `CHAT_PROVIDER=anthropic|openai|gemini|groq`.
2. **Ollama** (local, zero API cost) — set `OLLAMA_BASE_URL`/`OLLAMA_MODEL`, run `ollama serve` + `ollama pull llama3`.
3. A deterministic rule-based explainer — guarantees the demo works with zero setup and zero cost, per PRD Section 11's risk mitigation.

Each step falls through to the next automatically on any error (missing key, quota, network, model not pulled), and the response says which providers were tried if it had to fall back.
