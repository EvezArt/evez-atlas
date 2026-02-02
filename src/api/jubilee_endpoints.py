"""Jubilee Debt Forgiveness Endpoints - Quantum Resource Redistribution"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
import time
from pathlib import Path

router = APIRouter(prefix="/jubilee", tags=["jubilee"])


class ForgivenessRequest(BaseModel):
    """Request model for debt forgiveness."""
    account_id: str
    debt_amount: Optional[float] = 0.0
    quantum_mode: Optional[bool] = False


# In-memory debt ledger (could be backed by database in production)
DEBT_LEDGER = {}


@router.post("/forgive")
async def forgive_debt(req: ForgivenessRequest) -> Dict:
    """
    Forgive debt via quantum superposition collapse to zero.
    
    In quantum mode, all debt states collapse to forgiven=0.
    In classical mode, debt is reduced by specified amount.
    
    Args:
        req: Forgiveness request containing account_id, debt_amount, and quantum_mode
        
    Returns:
        Dictionary containing forgiveness event details
    """
    old_debt = DEBT_LEDGER.get(req.account_id, 0.0)
    
    if req.quantum_mode:
        # Quantum collapse: all debt states collapse to forgiven=0
        new_debt = 0.0
        mechanism = "quantum_collapse"
    else:
        # Classical forgiveness
        new_debt = max(0.0, old_debt - req.debt_amount)
        mechanism = "classical_reduction"
    
    DEBT_LEDGER[req.account_id] = new_debt
    
    event = {
        "account_id": req.account_id,
        "old_debt": old_debt,
        "new_debt": new_debt,
        "forgiven": old_debt - new_debt,
        "mechanism": mechanism,
        "timestamp": time.time()
    }
    
    # Log to events.jsonl via swarm director
    try:
        from src.mastra.agents.swarm_director import director
        director._log_event("forgiveness", event)
    except Exception:
        # Fallback logging if director not available
        pass
    
    return event


@router.get("/ledger")
async def get_ledger() -> Dict:
    """Get current debt ledger state."""
    return {
        "accounts": len(DEBT_LEDGER),
        "total_debt": sum(DEBT_LEDGER.values()),
        "ledger": dict(DEBT_LEDGER),
        "timestamp": time.time()
    }


@router.get("/healthz")
async def health_check():
    """Health check endpoint for Jubilee service."""
    return {
        "status": "operational",
        "mode": "qsvc-ibm",
        "timestamp": time.time()
    }


@router.post("/add-debt")
async def add_debt(account_id: str, amount: float) -> Dict:
    """
    Add debt to an account (for testing purposes).
    
    Args:
        account_id: Account identifier
        amount: Amount to add to debt
        
    Returns:
        Updated account status
    """
    old_debt = DEBT_LEDGER.get(account_id, 0.0)
    new_debt = old_debt + amount
    DEBT_LEDGER[account_id] = new_debt
    
    return {
        "account_id": account_id,
        "old_debt": old_debt,
        "new_debt": new_debt,
        "added": amount,
        "timestamp": time.time()
    }
