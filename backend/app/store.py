"""SQLite-backed local index of invoices + persona state.

The chain (InvoiceToken/CreditLogic) is the source of truth for the
"on-chain audit trail" claim; this store just mirrors it for fast API reads
and keeps the persona JSON (scoring inputs, score history) mutable across a
demo session without touching the seed file on disk.
"""
import json
import os
import sqlite3
from pathlib import Path
from threading import Lock

DB_PATH = os.environ.get("DATABASE_PATH", "./tawtheeq.db")
PERSONAS_JSON = Path(__file__).resolve().parent.parent.parent / "data" / "output" / "personas.json"

_lock = Lock()


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS invoices (
                token_id INTEGER PRIMARY KEY,
                persona_id TEXT NOT NULL,
                counterparty TEXT NOT NULL,
                amount_aed REAL NOT NULL,
                due_date TEXT NOT NULL,
                status TEXT NOT NULL,
                score_at_mint INTEGER NOT NULL,
                mint_tx_hash TEXT NOT NULL,
                fund_tx_hash TEXT,
                repay_tx_hash TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS persona_state (
                persona_id TEXT PRIMARY KEY,
                record_json TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS provider_signals (
                persona_id TEXT NOT NULL,
                provider TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                PRIMARY KEY (persona_id, provider)
            )
            """
        )
        conn.commit()

    # Seed persona_state from the Phase 1 output on first run.
    with _connect() as conn:
        count = conn.execute("SELECT COUNT(*) FROM persona_state").fetchone()[0]
        if count == 0:
            records = json.loads(PERSONAS_JSON.read_text(encoding="utf-8"))
            for r in records:
                conn.execute(
                    "INSERT INTO persona_state (persona_id, record_json) VALUES (?, ?)",
                    (r["persona_id"], json.dumps(r)),
                )
            conn.commit()

    # Seed provider_signals (alt-data source stubs) from persona scoring_inputs
    # on first run — see app/providers/seed.py for how these are derived.
    with _connect() as conn:
        count = conn.execute("SELECT COUNT(*) FROM provider_signals").fetchone()[0]
        if count == 0:
            from app.providers.seed import build_seed_signals

            for persona in list_personas():
                for provider_name, payload in build_seed_signals(persona).items():
                    conn.execute(
                        "INSERT INTO provider_signals (persona_id, provider, payload_json) VALUES (?, ?, ?)",
                        (persona["persona_id"], provider_name, json.dumps(payload)),
                    )
            conn.commit()


def get_provider_signal(persona_id: str, provider: str) -> dict | None:
    with _connect() as conn:
        row = conn.execute(
            "SELECT payload_json FROM provider_signals WHERE persona_id = ? AND provider = ?",
            (persona_id, provider),
        ).fetchone()
    return json.loads(row["payload_json"]) if row else None


def get_persona(persona_id: str) -> dict | None:
    with _connect() as conn:
        row = conn.execute(
            "SELECT record_json FROM persona_state WHERE persona_id = ?", (persona_id,)
        ).fetchone()
    return json.loads(row["record_json"]) if row else None


def list_personas() -> list[dict]:
    with _connect() as conn:
        rows = conn.execute("SELECT record_json FROM persona_state").fetchall()
    return [json.loads(r["record_json"]) for r in rows]


def save_persona(record: dict):
    with _lock, _connect() as conn:
        conn.execute(
            "UPDATE persona_state SET record_json = ? WHERE persona_id = ?",
            (json.dumps(record), record["persona_id"]),
        )
        conn.commit()


def insert_invoice(row: dict):
    with _lock, _connect() as conn:
        conn.execute(
            """
            INSERT INTO invoices
                (token_id, persona_id, counterparty, amount_aed, due_date, status,
                 score_at_mint, mint_tx_hash, fund_tx_hash, repay_tx_hash)
            VALUES (:token_id, :persona_id, :counterparty, :amount_aed, :due_date, :status,
                    :score_at_mint, :mint_tx_hash, :fund_tx_hash, :repay_tx_hash)
            """,
            row,
        )
        conn.commit()


def update_invoice_status(token_id: int, status: str, **tx_hashes):
    fields = ", ".join(f"{k} = :{k}" for k in tx_hashes)
    with _lock, _connect() as conn:
        params = {"token_id": token_id, "status": status, **tx_hashes}
        set_clause = "status = :status" + (f", {fields}" if fields else "")
        conn.execute(f"UPDATE invoices SET {set_clause} WHERE token_id = :token_id", params)
        conn.commit()


def get_invoice(token_id: int) -> dict | None:
    with _connect() as conn:
        row = conn.execute("SELECT * FROM invoices WHERE token_id = ?", (token_id,)).fetchone()
    return dict(row) if row else None


def list_invoices(persona_id: str) -> list[dict]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM invoices WHERE persona_id = ? ORDER BY token_id", (persona_id,)
        ).fetchall()
    return [dict(r) for r in rows]
