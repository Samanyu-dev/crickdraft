import random

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..models import Draft, User, SimulationRun, TournamentStats
from ..schemas import SimulateRequest
from ..players_data import PLAYERS_BY_ID, squads_for_tournament
from ..simulation import simulate_match, build_ai_opponent, assign_batting_order, name_opponent, team_elo_rating
from ..tournaments import get_tournament
from ..time_utils import ist_today

router = APIRouter(prefix="/api/simulate", tags=["simulate"])

ELO_K = 32.0
DAILY_MATCH_LIMIT = 20


def expected_score(rating: float, opponent_rating: float) -> float:
    return 1.0 / (1.0 + 10 ** ((opponent_rating - rating) / 400.0))


def _get_or_create_stats(session: Session, user_id: int, tournament: str) -> TournamentStats:
    stats = session.exec(
        select(TournamentStats).where(TournamentStats.user_id == user_id, TournamentStats.tournament == tournament)
    ).first()
    if not stats:
        stats = TournamentStats(user_id=user_id, tournament=tournament)
        session.add(stats)
        session.commit()
        session.refresh(stats)
    return stats


def find_opponent(session: Session, user: User, my_elo: float, tournament: str, draft_id: int):
    """Prefer a real opponent from another user's active draft in the SAME
    tournament, weighted towards a close Elo match; fall back to a random
    AI XI (drawn from that tournament's squad pool) scaled to the
    challenger's own rating when no real opponent is available."""
    rows = session.exec(
        select(User, Draft, TournamentStats)
        .join(Draft, Draft.user_id == User.id)  # type: ignore[arg-type]
        .join(
            TournamentStats,
            (TournamentStats.user_id == User.id) & (TournamentStats.tournament == tournament),  # type: ignore[arg-type]
            isouter=True,
        )
        .where(Draft.tournament == tournament, Draft.is_active == True, Draft.id != draft_id)  # noqa: E712
    ).all()

    if rows:
        rows = sorted(rows, key=lambda row: abs((row[2].elo_rating if row[2] else 1200.0) - my_elo))
        pool = rows[:8]
        opp_user, opp_draft, opp_stats = random.choice(pool)
        squad = [PLAYERS_BY_ID[pid] for pid in opp_draft.player_ids if pid in PLAYERS_BY_ID]
        captain_id = opp_draft.captain_id or squad[0]["id"]
        return squad, f"{opp_user.username}'s XI", opp_stats.elo_rating if opp_stats else 1200.0, captain_id

    tournament_pool = [p for sq in squads_for_tournament(get_tournament(tournament)).values() for p in sq["players"]]
    pool_squad = build_ai_opponent([], target_elo=my_elo, pool=tournament_pool)
    order = assign_batting_order(pool_squad)
    name = name_opponent(pool_squad)
    rating = team_elo_rating(order)
    return order, name, rating, None


@router.post("")
def run_simulation(payload: SimulateRequest, session: Session = Depends(get_session)):
    draft = session.get(Draft, payload.draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    user = session.get(User, draft.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    today = ist_today()
    if user.last_match_date != today:
        user.matches_today = 0
        user.last_match_date = today
    if user.matches_today >= DAILY_MATCH_LIMIT:
        raise HTTPException(
            status_code=429,
            detail=f"You've played {DAILY_MATCH_LIMIT} matches today. Resets at midnight IST.",
        )

    tournament_slug = draft.tournament
    tournament = get_tournament(tournament_slug)
    stats = _get_or_create_stats(session, user.id, tournament_slug)

    squad = [PLAYERS_BY_ID[pid] for pid in draft.player_ids if pid in PLAYERS_BY_ID]
    captain_id = draft.captain_id or squad[0]["id"]

    opponent_order, opponent_name, opponent_rating, opponent_captain_id = find_opponent(
        session, user, stats.elo_rating, tournament_slug, draft.id
    )
    match = simulate_match(
        squad, captain_id, opponent_order, opponent_name, opponent_rating, opponent_captain_id,
        overs=tournament["overs"], innings_per_side=tournament["innings_per_side"],
    )

    elo_before = stats.elo_rating
    expected = expected_score(elo_before, match["opponent_rating"])
    actual = 1.0 if match["result"] == "W" else (0.5 if match["result"] == "D" else 0.0)
    elo_delta = round(ELO_K * (actual - expected), 1)
    elo_after = round(elo_before + elo_delta, 1)

    run = SimulationRun(
        draft_id=draft.id,
        user_id=user.id,
        tournament=tournament_slug,
        opponent_name=match["opponent_name"],
        opponent_rating=match["opponent_rating"],
        result=match["result"],
        elo_before=elo_before,
        elo_after=elo_after,
        elo_delta=elo_delta,
        scorecard=match["scorecard"],
        innings=match["innings"],
    )
    session.add(run)

    stats.elo_rating = elo_after
    stats.matches_played += 1
    if match["result"] == "W":
        stats.wins += 1
    elif match["result"] == "L":
        stats.losses += 1
    else:
        stats.draws += 1
    session.add(stats)

    user.matches_today += 1
    session.add(user)
    session.commit()

    return {
        "username": user.username,
        "tournament": tournament_slug,
        "format": tournament["format"],
        "result": match["result"],
        "opponent_name": match["opponent_name"],
        "opponent_rating": match["opponent_rating"],
        "team_total": match["team_total"],
        "opponent_total": match["opponent_total"],
        "innings": match["innings"],
        "scorecard": match["scorecard"],
        "elo_before": elo_before,
        "elo_after": elo_after,
        "elo_delta": elo_delta,
        "totals": {
            "elo_rating": stats.elo_rating,
            "matches_played": stats.matches_played,
            "wins": stats.wins,
            "losses": stats.losses,
            "draws": stats.draws,
        },
        "matches_today": user.matches_today,
        "matches_remaining_today": max(0, DAILY_MATCH_LIMIT - user.matches_today),
    }
