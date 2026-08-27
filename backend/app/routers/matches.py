from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..models import User, SimulationRun
from ..tournaments import DEFAULT_TOURNAMENT

router = APIRouter(prefix="/api/matches", tags=["matches"])


@router.get("/{username}")
def get_match_history(
    username: str, tournament: Optional[str] = None, limit: int = 20, session: Session = Depends(get_session)
):
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    tournament_slug = tournament or DEFAULT_TOURNAMENT

    runs = session.exec(
        select(SimulationRun)
        .where(SimulationRun.user_id == user.id, SimulationRun.tournament == tournament_slug)
        .order_by(SimulationRun.played_at.desc())
        .limit(limit)
    ).all()

    results = []
    for r in runs:
        team_total = sum(i["score"] for i in r.innings if i["side"] == "team")
        opponent_total = sum(i["score"] for i in r.innings if i["side"] == "opponent")
        results.append({
            "opponent_name": r.opponent_name,
            "opponent_rating": r.opponent_rating,
            "result": r.result,
            "team_total": team_total,
            "opponent_total": opponent_total,
            "elo_before": r.elo_before,
            "elo_after": r.elo_after,
            "elo_delta": r.elo_delta,
            "scorecard": r.scorecard,
            "played_at": r.played_at.isoformat(),
        })
    return results
