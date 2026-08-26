from typing import Optional
from fastapi import APIRouter, Query

from ..players_data import PLAYERS

router = APIRouter(prefix="/api/players", tags=["players"])


@router.get("")
def list_players(
    country: Optional[str] = None,
    role: Optional[str] = None,
    search: Optional[str] = None,
):
    results = PLAYERS
    if country:
        results = [p for p in results if p["country"].lower() == country.lower()]
    if role:
        results = [p for p in results if p["role"].upper() == role.upper()]
    if search:
        s = search.lower()
        results = [p for p in results if s in p["name"].lower()]
    return results


@router.get("/meta")
def players_meta():
    countries = sorted({p["country"] for p in PLAYERS})
    roles = sorted({p["role"] for p in PLAYERS})
    eras = sorted({p["era"] for p in PLAYERS})
    return {"countries": countries, "roles": roles, "eras": eras, "count": len(PLAYERS)}
