from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..models import User
from ..schemas import UserCreate
from ..time_utils import ist_today

router = APIRouter(prefix="/api/users", tags=["users"])
DAILY_MATCH_LIMIT = 20


def _serialize(user: User) -> dict:
    matches_today = user.matches_today if user.last_match_date == ist_today() else 0
    return {
        "id": user.id,
        "username": user.username,
        "elo_rating": user.elo_rating,
        "matches_played": user.matches_played,
        "wins": user.wins,
        "losses": user.losses,
        "matches_today": matches_today,
        "matches_remaining_today": max(0, DAILY_MATCH_LIMIT - matches_today),
    }


@router.post("")
def create_or_get_user(payload: UserCreate, session: Session = Depends(get_session)):
    existing = session.exec(select(User).where(User.username == payload.username)).first()
    if existing:
        return _serialize(existing)
    user = User(username=payload.username)
    session.add(user)
    session.commit()
    session.refresh(user)
    return _serialize(user)


@router.get("/{username}")
def get_user(username: str, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return _serialize(user)
