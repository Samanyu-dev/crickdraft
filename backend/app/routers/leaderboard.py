from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from ..database import get_session
from ..models import User

router = APIRouter(prefix="/api/leaderboard", tags=["leaderboard"])


@router.get("")
def leaderboard(limit: int = 50, session: Session = Depends(get_session)):
    users = session.exec(
        select(User).where(User.matches_played > 0).order_by(User.total_points.desc()).limit(limit)
    ).all()
    entries = []
    for u in users:
        win_pct = round((u.wins / u.matches_played) * 100, 1) if u.matches_played else 0.0
        entries.append({
            "username": u.username,
            "total_points": round(u.total_points, 1),
            "matches_played": u.matches_played,
            "wins": u.wins,
            "losses": u.losses,
            "win_pct": win_pct,
        })
    return entries
