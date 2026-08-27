from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func

from ..database import get_session
from ..models import User, TournamentStats
from ..schemas import UserCreate
from ..time_utils import ist_today
from ..tournaments import DEFAULT_TOURNAMENT

router = APIRouter(prefix="/api/users", tags=["users"])
DAILY_MATCH_LIMIT = 20


def _serialize(user: User, session: Session, tournament: str) -> dict:
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
        "id": user.id,
        "username": user.username,
        "tournament": tournament,
        "elo_rating": stats.elo_rating if stats else 1200.0,
        "matches_played": stats.matches_played if stats else 0,
        "wins": stats.wins if stats else 0,
        "losses": stats.losses if stats else 0,
        "draws": stats.draws if stats else 0,
        "matches_today": matches_today,
        "matches_remaining_today": max(0, DAILY_MATCH_LIMIT - matches_today),
        "rank": rank,
    }


@router.post("")
def create_or_get_user(payload: UserCreate, session: Session = Depends(get_session)):
    existing = session.exec(select(User).where(User.username == payload.username)).first()
    if existing:
        return _serialize(existing, session, DEFAULT_TOURNAMENT)
    user = User(username=payload.username)
    session.add(user)
    session.commit()
    session.refresh(user)
    return _serialize(user, session, DEFAULT_TOURNAMENT)


@router.get("/{username}")
def get_user(username: str, tournament: Optional[str] = None, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return _serialize(user, session, tournament or DEFAULT_TOURNAMENT)
