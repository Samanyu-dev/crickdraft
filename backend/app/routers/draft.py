import random
from typing import Optional

from fastapi import APIRouter, HTTPException

from ..players_data import squads_for_tournament
from ..tournaments import get_tournament

router = APIRouter(prefix="/api/draft", tags=["draft"])


@router.get("/roll")
def roll_squad(tournament: Optional[str] = None, exclude: Optional[str] = None):
    pool = squads_for_tournament(get_tournament(tournament))
    if not pool:
        raise HTTPException(status_code=409, detail="No squads available for this tournament.")
    excluded_keys = set(exclude.split(",")) if exclude else set()
    candidates = [s for key, s in pool.items() if key not in excluded_keys]
    # If the exclude list happens to cover the whole pool (small tournament
    # pools + a client that over-accumulates its "recently seen" list),
    # degrade gracefully by ignoring the exclusion rather than erroring -
    # squads are allowed to repeat within a draft by design.
    if not candidates:
        candidates = list(pool.values())
    return random.choice(candidates)


@router.get("/squads")
def list_squads(tournament: Optional[str] = None):
    """Full squad+player data for every squad in the tournament pool, fetched
    once up front so the client can roll/reroll entirely in memory instead of
    round-tripping to /roll on every attempt - a tournament with a smaller,
    more constrained squad pool could otherwise need many sequential retries
    to find a squad with an eligible pick, each one a real network call."""
    pool = squads_for_tournament(get_tournament(tournament))
    return list(pool.values())
