"""Re-exports the canonical Phase 1 scoring function so the live API and the
seed pipeline never drift onto two different formulas (PRD Section 6.2).
"""
import sys
from pathlib import Path

_PIPELINE_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "pipeline"
if str(_PIPELINE_DIR) not in sys.path:
    sys.path.insert(0, str(_PIPELINE_DIR))

from scoring import (  # noqa: E402  (import after sys.path fix, by design)
    CATEGORY_WEIGHTS,
    compute_score,
    explain_score,
    apply_repayment_boost,
)

__all__ = ["CATEGORY_WEIGHTS", "compute_score", "explain_score", "apply_repayment_boost"]
