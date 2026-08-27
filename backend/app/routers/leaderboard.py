from typing import Optional

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from ..database import get_session
from ..models import User, TournamentStats
from ..tournaments import DEFAULT_TOURNAMENT

router = APIRouter(prefix="/api/leaderboard", tags=["leaderboard"])


@router.get("")
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
            "username": u.username,
            "elo_rating": round(s.elo_rating, 1),
            "matches_played": s.matches_played,
            "wins": s.wins,
            "losses": s.losses,
            "draws": s.draws,
            "win_pct": win_pct,
        })
    return entries
