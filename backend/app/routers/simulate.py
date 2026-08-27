from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..models import Draft, User, SimulationRun
from ..schemas import SimulateRequest
from ..players_data import PLAYERS_BY_ID
from ..simulation import simulate_match

router = APIRouter(prefix="/api/simulate", tags=["simulate"])


@router.post("")
def run_simulation(payload: SimulateRequest, session: Session = Depends(get_session)):
    draft = session.get(Draft, payload.draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    user = session.get(User, draft.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    rounds = max(1, min(20, payload.rounds))
    squad = [PLAYERS_BY_ID[pid] for pid in draft.player_ids if pid in PLAYERS_BY_ID]
    captain_id = draft.captain_id or squad[0]["id"]

    results = []
    for _ in range(rounds):
        match = simulate_match(squad, captain_id)
        run = SimulationRun(
            draft_id=draft.id,
            user_id=user.id,
            opponent_name=match["opponent_name"],
            team_score=match["team_score"],
            opponent_score=match["opponent_score"],
            result=match["result"],
            scorecard=match["scorecard"],
        )
        session.add(run)

        user.total_points += match["fantasy_points"]
        user.matches_played += 1
        if match["result"] == "W":
            user.wins += 1
        else:
            user.losses += 1

        results.append(match)

    session.add(user)
    session.commit()

    return {
        "username": user.username,
        "rounds": rounds,
        "results": results,
        "totals": {
            "total_points": user.total_points,
            "matches_played": user.matches_played,
            "wins": user.wins,
            "losses": user.losses,
        },
    }
