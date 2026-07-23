from datetime import datetime, timezone

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app import store
from app.chain import get_chain_client
from app.chatbot import get_chat_reply
from app.models import ChatIn, ChatOut, InvoiceCreate, InvoiceOut, PlaygroundIn, RepayIn, ScoreOut
from app.providers import ALL_PROVIDERS, PROVIDERS_BY_NAME
from app.providers.playground_defaults import PLAYGROUND_DEFAULTS
from app.scoring import apply_repayment_boost, compute_score, explain_score

app = FastAPI(title="Tawtheeq API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    store.init_db()


@app.get("/personas")
def list_personas():
    return [
        {
            "persona_id": p["persona_id"],
            "display_name": p["display_name"],
            "sector": p["sector"],
            "tawtheeq_score": p["tawtheeq_score"],
        }
        for p in store.list_personas()
    ]


@app.get("/score/{persona_id}", response_model=ScoreOut)
def get_score(persona_id: str):
    persona = store.get_persona(persona_id)
    if not persona:
        raise HTTPException(404, f"unknown persona_id {persona_id}")
    return ScoreOut(
        persona_id=persona["persona_id"],
        display_name=persona["display_name"],
        tawtheeq_score=persona["tawtheeq_score"],
        scoring_inputs=persona["scoring_inputs"],
        breakdown=persona.get("score_breakdown") or explain_score(persona["scoring_inputs"]),
        score_history=persona["score_history"],
    )


@app.get("/providers/{persona_id}")
def get_provider_signals(persona_id: str):
    """Raw alternative-data signals behind the score, grouped by source —
    the "Fetch Alternate Data from ERP and Transactions" step in the data
    flow, surfaced for demo narration. Each entry names the real provider
    category it stands in for (see app/providers/adapters.py docstrings).
    """
    if not store.get_persona(persona_id):
        raise HTTPException(404, f"unknown persona_id {persona_id}")
    return [p.score(persona_id) for p in ALL_PROVIDERS]


@app.get("/invoices/{persona_id}")
def get_invoices(persona_id: str):
    if not store.get_persona(persona_id):
        raise HTTPException(404, f"unknown persona_id {persona_id}")
    return store.list_invoices(persona_id)


@app.post("/invoices", response_model=InvoiceOut)
def create_invoice(payload: InvoiceCreate):
    """Full Phase 2 loop: mint invoice token -> push current score ->
    auto-check funding conditions -> disburse if approved. Mirrors the deck's
    3-step solution (PRD Section 6.3) with zero manual intervention.
    """
    persona = store.get_persona(payload.persona_id)
    if not persona:
        raise HTTPException(404, f"unknown persona_id {payload.persona_id}")

    due_date_unix = int(datetime.fromisoformat(payload.due_date).replace(tzinfo=timezone.utc).timestamp())
    score = persona["tawtheeq_score"]

    chain = get_chain_client()
    to_address = chain.oracle_account.address  # demo: SME wallet == oracle account (no wallet UX)

    token_id, mint_tx = chain.mint_invoice(
        to=to_address,
        persona_id=payload.persona_id,
        counterparty=payload.counterparty,
        amount_aed=int(payload.amount_aed),
        due_date_unix=due_date_unix,
        score_at_mint=score,
    )
    chain.push_score(payload.persona_id, score)
    funding = chain.request_funding(token_id)

    status = "financed" if funding["approved"] else "pending"

    store.insert_invoice({
        "token_id": token_id,
        "persona_id": payload.persona_id,
        "counterparty": payload.counterparty,
        "amount_aed": payload.amount_aed,
        "due_date": payload.due_date,
        "status": status,
        "score_at_mint": score,
        "mint_tx_hash": mint_tx,
        "fund_tx_hash": funding["tx_hash"] if funding["approved"] else None,
        "repay_tx_hash": None,
    })

    persona["invoices"].append({
        "id": f"onchain-{token_id}",
        "counterparty": payload.counterparty,
        "amount_aed": payload.amount_aed,
        "due_date": payload.due_date,
        "status": status,
    })
    store.save_persona(persona)

    return InvoiceOut(
        token_id=token_id,
        persona_id=payload.persona_id,
        counterparty=payload.counterparty,
        amount_aed=payload.amount_aed,
        due_date=payload.due_date,
        status=status,
        score_at_mint=score,
        mint_tx_hash=mint_tx,
        fund_tx_hash=funding["tx_hash"] if funding["approved"] else None,
    )


@app.post("/invoices/{token_id}/fund")
def fund_invoice(token_id: int):
    """Manual re-trigger of the funding check (e.g. after a liquidity top-up)."""
    chain = get_chain_client()
    funding = chain.request_funding(token_id)
    if funding["approved"]:
        store.update_invoice_status(token_id, "financed", fund_tx_hash=funding["tx_hash"])
    return funding


@app.post("/fund/repay")
def repay_invoice(payload: RepayIn):
    """Simulates a successful repayment: on-chain repay event + score
    recalculation, replicating the deck's 68 -> 72 trajectory mechanic.
    """
    invoice = store.get_invoice(payload.token_id)
    if not invoice:
        raise HTTPException(404, f"unknown token_id {payload.token_id}")

    chain = get_chain_client()
    repay_tx = chain.record_repayment(payload.token_id)
    store.update_invoice_status(payload.token_id, "repaid", repay_tx_hash=repay_tx)

    persona = store.get_persona(invoice["persona_id"])
    streak = len([i for i in store.list_invoices(persona["persona_id"]) if i["status"] == "repaid"])
    boosted_inputs = apply_repayment_boost(persona["scoring_inputs"], streak=streak)
    new_score = compute_score(boosted_inputs)

    persona["scoring_inputs"] = boosted_inputs
    persona["tawtheeq_score"] = new_score
    persona["score_breakdown"] = explain_score(boosted_inputs)
    persona["score_history"].append({"event": f"repayment_streak_{streak}", "score": new_score})
    store.save_persona(persona)

    push_tx = chain.push_score(persona["persona_id"], new_score)

    return {
        "token_id": payload.token_id,
        "repay_tx_hash": repay_tx,
        "new_score": new_score,
        "score_push_tx_hash": push_tx,
    }


@app.get("/playground/defaults")
def playground_defaults():
    """Field defaults + which category/real-world source each maps to, so the
    frontend can render the form without hardcoding the schema twice.
    """
    return {
        name: {
            "category": provider.category,
            "real_world_analog": provider.real_world_analog,
            "fields": PLAYGROUND_DEFAULTS[name],
        }
        for name, provider in PROVIDERS_BY_NAME.items()
    }


@app.post("/playground/score")
def playground_score(payload: PlaygroundIn):
    """Real-time sandbox scoring: runs arbitrary user-supplied raw signals
    through the exact same adapters + weighted formula the live app uses,
    without touching any persona, the database, or the chain. Pure function
    of its input — safe to call on every keystroke.
    """
    category_values: dict[str, list[float]] = {}
    provider_results = []

    for name, provider in PROVIDERS_BY_NAME.items():
        raw = {**PLAYGROUND_DEFAULTS[name], **payload.signals.get(name, {})}
        try:
            value = max(0.0, min(1.0, provider.normalize(raw)))
        except (KeyError, TypeError, ZeroDivisionError) as exc:
            raise HTTPException(400, f"invalid signal for {name}: {exc}")
        provider_results.append({
            "provider": name,
            "category": provider.category,
            "real_world_analog": provider.real_world_analog,
            "raw": raw,
            "normalized_value": round(value, 3),
        })
        category_values.setdefault(provider.category, []).append(value)

    scoring_inputs = {cat: round(sum(vals) / len(vals), 3) for cat, vals in category_values.items()}
    score = compute_score(scoring_inputs)

    return {
        "tawtheeq_score": score,
        "scoring_inputs": scoring_inputs,
        "breakdown": explain_score(scoring_inputs),
        "providers": provider_results,
    }


@app.post("/chat", response_model=ChatOut)
def chat(payload: ChatIn):
    persona = store.get_persona(payload.persona_id)
    if not persona:
        raise HTTPException(404, f"unknown persona_id {payload.persona_id}")
    reply, grounded_in = get_chat_reply(persona, payload.message)
    return ChatOut(reply=reply, grounded_in=grounded_in)
