import random
from typing import Optional

from fastapi import APIRouter, HTTPException

from ..players_data import squads_for_tournament
from ..tournaments import get_tournament

router = APIRouter(prefix="/api/draft", tags=["draft"])


@router.get("/roll")
def roll_squad(tournament: Optional[str] = None, exclude: Optional[str] = None):
    pool = squads_for_tournament(get_tournament(tournament))
    excluded_keys = set(exclude.split(",")) if exclude else set()
    candidates = [s for key, s in pool.items() if key not in excluded_keys]
    if not candidates:
        raise HTTPException(status_code=409, detail="No more squads left to roll.")
    return random.choice(candidates)


@router.get("/squads")
def list_squads(tournament: Optional[str] = None):
    pool = squads_for_tournament(get_tournament(tournament))
    return [
        {"key": s["key"], "country": s["country"], "era": s["era"], "squad_name": s["squad_name"]}
        for s in pool.values()
    ]
