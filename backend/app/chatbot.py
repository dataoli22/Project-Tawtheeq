"""Persona-grounded chatbot (PRD Section 7.4).

Context is assembled per-request from the persona's own data (narrative,
scoring breakdown, invoice history) — never fine-tuned, just context-injected,
so it stays free/open to build and never answers from outside the persona's
seeded record.

Provider chain (configurable via CHAT_PROVIDER, default "auto"):
  - anthropic — Claude API (ANTHROPIC_API_KEY)
  - openai    — OpenAI API (OPENAI_API_KEY)
  - gemini    — Google Gemini API (GEMINI_API_KEY)
  - groq      — Groq API, free tier (GROQ_API_KEY)
  - ollama    — self-hosted open-weight model, zero API cost (OLLAMA_BASE_URL/OLLAMA_MODEL)

"auto" tries CHAT_PROVIDER's target if set, else the first hosted provider
with a key present; if that call fails (quota, network, bad key) it falls
back to a local Ollama instance, and if Ollama isn't running either, falls
back to the deterministic rule-based explainer — so the demo always works,
per the PRD's risk mitigation (Section 11).
"""
import json
import logging
import os

import httpx

from app.scoring import explain_score

logger = logging.getLogger(__name__)

SYSTEM_PROMPT_TEMPLATE = """You are the Tawtheeq credit assistant for {display_name}, a {sector} \
SME on the Tawtheeq platform. Only discuss {display_name}'s own data below and general Tawtheeq \
product/GTM facts. Never invent numbers, never give real financial/legal advice, and never discuss \
other personas' data.

Persona narrative: {narrative}

Current Tawtheeq Score: {score}/100
Score breakdown (category: weight, value 0-1, points contributed):
{breakdown_lines}

Score history: {score_history}

Active invoices: {invoice_summary}

Answer the user's question in 2-4 short sentences, plain language, no jargon."""

HOSTED_PROVIDERS = ["anthropic", "openai", "gemini", "groq"]


def _format_breakdown(breakdown: list[dict]) -> str:
    return "\n".join(
        f"  - {c['category'].replace('_', ' ').title()}: weight {c['weight']:.0%}, "
        f"value {c['value']:.2f}, contributes {c['contribution_points']} pts"
        for c in breakdown
    )


def _format_invoices(invoices: list[dict]) -> str:
    if not invoices:
        return "none yet"
    counts = {}
    for inv in invoices:
        counts[inv["status"]] = counts.get(inv["status"], 0) + 1
    return ", ".join(f"{v} {k}" for k, v in counts.items())


def _build_context(persona: dict) -> str:
    breakdown = persona.get("score_breakdown") or explain_score(persona["scoring_inputs"])
    return SYSTEM_PROMPT_TEMPLATE.format(
        display_name=persona["display_name"],
        sector=persona["sector"],
        narrative=persona["narrative"],
        score=persona["tawtheeq_score"],
        breakdown_lines=_format_breakdown(breakdown),
        score_history=persona["score_history"],
        invoice_summary=_format_invoices(persona["invoices"]),
    )


def _rule_based_reply(persona: dict, message: str) -> str:
    breakdown = persona.get("score_breakdown") or explain_score(persona["scoring_inputs"])
    lowest = min(breakdown, key=lambda c: c["value"])
    highest = max(breakdown, key=lambda c: c["value"])
    msg = message.lower()

    if "improve" in msg or "raise" in msg or "increase" in msg:
        return (
            f"Your {highest['category'].replace('_', ' ')} is your strongest signal "
            f"({highest['value']:.0%}). The fastest way to raise your score is improving "
            f"{lowest['category'].replace('_', ' ')} ({lowest['value']:.0%} today) — for example, "
            "completing more on-time repayments, which is worth the most weighted points per PRD."
        )
    if "why" in msg or "score" in msg or "explain" in msg:
        top3 = sorted(breakdown, key=lambda c: c["contribution_points"], reverse=True)[:3]
        parts = ", ".join(
            f"{c['category'].replace('_', ' ')} contributes {c['contribution_points']} pts"
            for c in top3
        )
        return (
            f"Your Tawtheeq Score is {persona['tawtheeq_score']}/100. The biggest drivers are: "
            f"{parts}. {persona['narrative']}"
        )
    return (
        f"Hi, I'm the Tawtheeq assistant for {persona['display_name']}. Current score is "
        f"{persona['tawtheeq_score']}/100. Ask me 'why is my score X' or 'how do I improve my score'."
    )


# --- Hosted provider calls -------------------------------------------------
# Each raises on failure (missing key, network, quota) so the caller can fall
# back to the next option in the chain.

def _call_anthropic(system: str, message: str) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    response = client.messages.create(
        model=os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5"),
        max_tokens=300,
        system=system,
        messages=[{"role": "user", "content": message}],
    )
    return response.content[0].text


def _call_openai(system: str, message: str) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    response = client.chat.completions.create(
        model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
        max_tokens=300,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": message},
        ],
    )
    return response.choices[0].message.content


def _call_gemini(system: str, message: str) -> str:
    import google.generativeai as genai

    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel(
        os.environ.get("GEMINI_MODEL", "gemini-1.5-flash"), system_instruction=system
    )
    response = model.generate_content(message)
    return response.text


def _call_groq(system: str, message: str) -> str:
    # Groq exposes an OpenAI-compatible endpoint, so the openai client works
    # unmodified with a different base_url — no separate groq SDK needed.
    from openai import OpenAI

    client = OpenAI(api_key=os.environ["GROQ_API_KEY"], base_url="https://api.groq.com/openai/v1")
    response = client.chat.completions.create(
        model=os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant"),
        max_tokens=300,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": message},
        ],
    )
    return response.choices[0].message.content


def _call_ollama(system: str, message: str) -> str:
    base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.environ.get("OLLAMA_MODEL", "llama3")
    resp = httpx.post(
        f"{base_url}/api/chat",
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": message},
            ],
            "stream": False,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["message"]["content"]


_PROVIDER_FNS = {
    "anthropic": _call_anthropic,
    "openai": _call_openai,
    "gemini": _call_gemini,
    "groq": _call_groq,
    "ollama": _call_ollama,
}

_PROVIDER_KEY_ENV = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "groq": "GROQ_API_KEY",
}


def _resolve_provider_order() -> list[str]:
    """CHAT_PROVIDER pins a specific provider first; "auto" (default) tries
    whichever hosted provider has a key configured, in a fixed preference
    order. Ollama is always appended last as the zero-cost fallback.
    """
    configured = os.environ.get("CHAT_PROVIDER", "auto").lower()
    if configured in _PROVIDER_FNS and configured != "ollama":
        order = [configured]
    else:
        order = [p for p in HOSTED_PROVIDERS if os.environ.get(_PROVIDER_KEY_ENV[p])]
    if "ollama" not in order:
        order.append("ollama")
    return order


def get_chat_reply(persona: dict, message: str) -> tuple[str, list[str]]:
    grounded_in = ["scoring_inputs", "score_breakdown", "score_history", "invoices", "narrative"]
    system = _build_context(persona)

    failed_providers = []
    for provider in _resolve_provider_order():
        try:
            reply = _PROVIDER_FNS[provider](system, message)
            return reply, grounded_in
        except Exception:  # noqa: BLE001 — try the next provider in the chain
            # Full exception (may include partial key fragments or internal
            # URLs from provider SDKs) stays server-side only; callers only
            # ever see which providers were tried, not why they failed.
            logger.warning("chat provider %s failed", provider, exc_info=True)
            failed_providers.append(provider)
            continue

    # Every hosted/local model attempt failed (no Ollama running, no keys
    # configured) — deterministic fallback guarantees the demo still works.
    note = (
        f"[LLM providers unavailable ({', '.join(failed_providers)}), using rule-based fallback]\n"
        if failed_providers
        else ""
    )
    return note + _rule_based_reply(persona, message), grounded_in
