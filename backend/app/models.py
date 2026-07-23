from typing import Optional

from pydantic import BaseModel, Field


class InvoiceCreate(BaseModel):
    persona_id: str
    counterparty: str
    amount_aed: float = Field(gt=0)
    due_date: str  # ISO date, e.g. "2026-09-01"


class InvoiceOut(BaseModel):
    token_id: int
    persona_id: str
    counterparty: str
    amount_aed: float
    due_date: str
    status: str
    score_at_mint: int
    mint_tx_hash: str
    fund_tx_hash: Optional[str] = None
    repay_tx_hash: Optional[str] = None


class ScoreOut(BaseModel):
    persona_id: str
    display_name: str
    tawtheeq_score: int
    scoring_inputs: dict
    breakdown: list
    score_history: list


class RepayIn(BaseModel):
    token_id: int


class PlaygroundIn(BaseModel):
    signals: dict[str, dict] = Field(default_factory=dict)


class ChatIn(BaseModel):
    persona_id: str
    message: str


class ChatOut(BaseModel):
    reply: str
    grounded_in: list[str]
