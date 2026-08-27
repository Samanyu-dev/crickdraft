from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from ..database import get_session
from ..models import Draft, User, SimulationRun
from ..schemas import SimulateRequest
from ..players_data import PLAYERS_BY_ID
from ..simulation import simulate_match

router = APIRouter(prefix="/api/simulate", tags=["simulate"])

ELO_K = 32.0


def expected_score(rating: float, opponent_rating: float) -> float:
    return 1.0 / (1.0 + 10 ** ((opponent_rating - rating) / 400.0))


@router.post("")
def run_simulation(payload: SimulateRequest, session: Session = Depends(get_session)):
    draft = session.get(Draft, payload.draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    user = session.get(User, draft.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    squad = [PLAYERS_BY_ID[pid] for pid in draft.player_ids if pid in PLAYERS_BY_ID]
    captain_id = draft.captain_id or squad[0]["id"]

    match = simulate_match(squad, captain_id)

    elo_before = user.elo_rating
    expected = expected_score(elo_before, match["opponent_rating"])
    actual = 1.0 if match["result"] == "W" else 0.0
    elo_delta = round(ELO_K * (actual - expected), 1)
    elo_after = round(elo_before + elo_delta, 1)

    run = SimulationRun(
        draft_id=draft.id,
        user_id=user.id,
        opponent_name=match["opponent_name"],
        opponent_rating=match["opponent_rating"],
        team_score=match["team_score"],
        opponent_score=match["opponent_score"],
        result=match["result"],
        elo_before=elo_before,
        elo_after=elo_after,
        elo_delta=elo_delta,
        scorecard=match["scorecard"],
    )
    session.add(run)

    user.elo_rating = elo_after
    user.matches_played += 1
    if match["result"] == "W":
        user.wins += 1
    else:
        user.losses += 1
    session.add(user)
    session.commit()

    return {
        "username": user.username,
        "result": match["result"],
        "opponent_name": match["opponent_name"],
        "opponent_rating": match["opponent_rating"],
        "team_score": match["team_score"],
        "opponent_score": match["opponent_score"],
        "team_wickets": match["team_wickets"],
        "opponent_wickets": match["opponent_wickets"],
        "team_overs": match["team_overs"],
        "opponent_overs": match["opponent_overs"],
        "team_timeline": match["team_timeline"],
        "opponent_timeline": match["opponent_timeline"],
        "scorecard": match["scorecard"],
        "elo_before": elo_before,
        "elo_after": elo_after,
        "elo_delta": elo_delta,
        "totals": {
            "elo_rating": user.elo_rating,
            "matches_played": user.matches_played,
            "wins": user.wins,
            "losses": user.losses,
        },
    }
