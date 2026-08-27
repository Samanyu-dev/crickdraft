import random
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func

from ..database import get_session
from ..models import User, Draft, TournamentStats, SimulationRun
from ..schemas import UserCreate, DraftCreate, DraftOut, SimulateRequest
from ..time_utils import ist_today
from ..soccer.players_data import PLAYERS_BY_ID, squads_for_tournament, validate_squad, SQUADS
from ..soccer.tournaments import get_tournament, list_tournaments, DEFAULT_TOURNAMENT
from ..soccer.simulation import simulate_match, build_ai_opponent, name_opponent, team_elo_rating
from ..moderation import contains_blocked_term

router = APIRouter(prefix="/api/soccer", tags=["soccer"])

ELO_K = 32.0
DAILY_MATCH_LIMIT = 20


def expected_score(rating: float, opponent_rating: float) -> float:
    return 1.0 / (1.0 + 10 ** ((opponent_rating - rating) / 400.0))


def _get_or_create_user(session: Session, username: str) -> User:
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        if contains_blocked_term(username):
            raise HTTPException(status_code=400, detail="That username isn't allowed.")
        user = User(username=username)
        session.add(user)
        session.commit()
        session.refresh(user)
    return user


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


def _serialize_user(user: User, session: Session, tournament: str) -> dict:
    matches_today = user.matches_today if user.last_match_date == ist_today() else 0
    stats = session.exec(
        select(TournamentStats).where(TournamentStats.user_id == user.id, TournamentStats.tournament == tournament)
    ).first()
    rank = None
    if stats and stats.matches_played > 0:
        ahead = session.exec(
            select(func.count()).select_from(TournamentStats).where(
                TournamentStats.tournament == tournament,
                TournamentStats.matches_played > 0,
                TournamentStats.elo_rating > stats.elo_rating,
            )
        ).one()
        rank = ahead + 1
    return {
        "id": user.id, "username": user.username, "tournament": tournament,
        "elo_rating": stats.elo_rating if stats else 1200.0,
        "matches_played": stats.matches_played if stats else 0,
        "wins": stats.wins if stats else 0,
        "losses": stats.losses if stats else 0,
        "draws": stats.draws if stats else 0,
        "matches_today": matches_today,
        "matches_remaining_today": max(0, DAILY_MATCH_LIMIT - matches_today),
        "rank": rank,
    }


@router.get("/tournaments")
def get_tournaments():
    return list_tournaments()


@router.get("/draft/roll")
def roll_squad(tournament: Optional[str] = None, exclude: Optional[str] = None):
    pool = squads_for_tournament(get_tournament(tournament))
    if not pool:
        raise HTTPException(status_code=409, detail="No squads available for this tournament.")
    excluded_keys = set(exclude.split(",")) if exclude else set()
    candidates = [s for key, s in pool.items() if key not in excluded_keys]
    if not candidates:
        candidates = list(pool.values())
    return random.choice(candidates)


@router.get("/draft/squads")
def list_squads(tournament: Optional[str] = None):
    """Full squad+player data for every squad in the tournament pool, fetched
    once up front so the client can roll/reroll entirely in memory instead of
    round-tripping to /draft/roll on every attempt."""
    pool = squads_for_tournament(get_tournament(tournament))
    return list(pool.values())


@router.post("/users")
def create_or_get_user(payload: UserCreate, session: Session = Depends(get_session)):
    user = _get_or_create_user(session, payload.username)
    return _serialize_user(user, session, DEFAULT_TOURNAMENT)


@router.get("/users/{username}")
def get_user(username: str, tournament: Optional[str] = None, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return _serialize_user(user, session, tournament or DEFAULT_TOURNAMENT)


@router.post("/drafts", response_model=DraftOut)
def create_draft(payload: DraftCreate, session: Session = Depends(get_session)):
    tournament_slug = payload.tournament or DEFAULT_TOURNAMENT
    ok, message = validate_squad(payload.player_ids, get_tournament(tournament_slug))
    if not ok:
        raise HTTPException(status_code=400, detail=message)
    if payload.captain_id is not None and payload.captain_id not in payload.player_ids:
        raise HTTPException(status_code=400, detail="Captain must be one of the selected players.")

    user = _get_or_create_user(session, payload.username)
    old_active = session.exec(
        select(Draft).where(
            Draft.user_id == user.id, Draft.tournament == tournament_slug, Draft.is_active == True  # noqa: E712
        )
    ).all()
    for d in old_active:
        d.is_active = False
        session.add(d)

    draft = Draft(
        user_id=user.id, tournament=tournament_slug, name=payload.name,
        player_ids=payload.player_ids, captain_id=payload.captain_id,
    )
    session.add(draft)
    session.commit()
    session.refresh(draft)
    return draft


@router.get("/drafts/{username}")
def get_active_draft(username: str, tournament: Optional[str] = None, session: Session = Depends(get_session)):
    tournament_slug = tournament or DEFAULT_TOURNAMENT
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    draft = session.exec(
        select(Draft).where(
            Draft.user_id == user.id, Draft.tournament == tournament_slug, Draft.is_active == True  # noqa: E712
        )
    ).first()
    if not draft:
        return None
    players = [PLAYERS_BY_ID[pid] for pid in draft.player_ids if pid in PLAYERS_BY_ID]
    return {
        "id": draft.id, "user_id": draft.user_id, "tournament": draft.tournament,
        "name": draft.name, "captain_id": draft.captain_id, "players": players,
    }


def find_opponent(session: Session, user: User, my_elo: float, tournament: str, draft_id: int):
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
    squad = build_ai_opponent([], target_elo=my_elo, pool=tournament_pool)
    name = name_opponent(squad)
    rating = team_elo_rating(squad)
    return squad, name, rating, None


@router.post("/simulate")
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
            status_code=429, detail=f"You've played {DAILY_MATCH_LIMIT} matches today. Resets at midnight IST."
        )

    tournament_slug = draft.tournament
    stats = _get_or_create_stats(session, user.id, tournament_slug)

    squad = [PLAYERS_BY_ID[pid] for pid in draft.player_ids if pid in PLAYERS_BY_ID]
    captain_id = draft.captain_id or squad[0]["id"]

    opponent_squad, opponent_name, opponent_rating, opponent_captain_id = find_opponent(
        session, user, stats.elo_rating, tournament_slug, draft.id
    )
    match = simulate_match(squad, captain_id, opponent_squad, opponent_name, opponent_rating, opponent_captain_id)

    elo_before = stats.elo_rating
    expected = expected_score(elo_before, match["opponent_rating"])
    actual = 1.0 if match["result"] == "W" else (0.5 if match["result"] == "D" else 0.0)
    elo_delta = round(ELO_K * (actual - expected), 1)
    elo_after = round(elo_before + elo_delta, 1)

    run = SimulationRun(
        draft_id=draft.id, user_id=user.id, tournament=tournament_slug,
        opponent_name=match["opponent_name"], opponent_rating=match["opponent_rating"], result=match["result"],
        elo_before=elo_before, elo_after=elo_after, elo_delta=elo_delta,
        scorecard=match["scorecard"],
        innings=[{
            "side": "team", "seq": 1, "score": match["team_goals"], "wickets": 0, "overs": 0,
            "timeline": [e for e in match["timeline"]],
        }],
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
        "result": match["result"],
        "opponent_name": match["opponent_name"],
        "opponent_rating": match["opponent_rating"],
        "team_goals": match["team_goals"],
        "opponent_goals": match["opponent_goals"],
        "timeline": match["timeline"],
        "scorecard": match["scorecard"],
        "elo_before": elo_before,
        "elo_after": elo_after,
        "elo_delta": elo_delta,
        "totals": {
            "elo_rating": stats.elo_rating, "matches_played": stats.matches_played,
            "wins": stats.wins, "losses": stats.losses, "draws": stats.draws,
        },
        "matches_today": user.matches_today,
        "matches_remaining_today": max(0, DAILY_MATCH_LIMIT - user.matches_today),
    }


@router.get("/leaderboard")
def leaderboard(tournament: Optional[str] = None, limit: int = 50, session: Session = Depends(get_session)):
    tournament_slug = tournament or DEFAULT_TOURNAMENT
    rows = session.exec(
        select(User, TournamentStats)
        .join(TournamentStats, TournamentStats.user_id == User.id)  # type: ignore[arg-type]
        .where(TournamentStats.tournament == tournament_slug, TournamentStats.matches_played > 0)
        .order_by(TournamentStats.elo_rating.desc())
        .limit(limit)
    ).all()
    entries = []
    for u, s in rows:
        win_pct = round((s.wins / s.matches_played) * 100, 1) if s.matches_played else 0.0
        entries.append({
            "username": u.username, "elo_rating": round(s.elo_rating, 1), "matches_played": s.matches_played,
            "wins": s.wins, "losses": s.losses, "draws": s.draws, "win_pct": win_pct,
        })
    return entries


@router.get("/matches/{username}")
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
        team_goals = r.innings[0]["score"] if r.innings else 0
        timeline = r.innings[0]["timeline"] if r.innings else []
        opponent_goals = timeline[-1]["score_opponent"] if timeline else 0
        results.append({
            "opponent_name": r.opponent_name, "opponent_rating": r.opponent_rating, "result": r.result,
            "team_goals": team_goals, "opponent_goals": opponent_goals,
            "elo_before": r.elo_before, "elo_after": r.elo_after, "elo_delta": r.elo_delta,
            "scorecard": r.scorecard, "played_at": r.played_at.isoformat(),
        })
    return results
