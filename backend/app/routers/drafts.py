from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..models import User, Draft
from ..schemas import DraftCreate, DraftOut
from ..players_data import validate_squad, PLAYERS_BY_ID

router = APIRouter(prefix="/api/drafts", tags=["drafts"])


def _get_or_create_user(session: Session, username: str) -> User:
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        user = User(username=username)
        session.add(user)
        session.commit()
        session.refresh(user)
    return user


@router.post("", response_model=DraftOut)
def create_draft(payload: DraftCreate, session: Session = Depends(get_session)):
    ok, message = validate_squad(payload.player_ids)
    if not ok:
        raise HTTPException(status_code=400, detail=message)
    if payload.captain_id is not None and payload.captain_id not in payload.player_ids:
        raise HTTPException(status_code=400, detail="Captain must be one of the selected players.")

    user = _get_or_create_user(session, payload.username)

    old_active = session.exec(
        select(Draft).where(Draft.user_id == user.id, Draft.is_active == True)  # noqa: E712
    ).all()
    for d in old_active:
        d.is_active = False
        session.add(d)

    draft = Draft(
        user_id=user.id,
        name=payload.name,
        player_ids=payload.player_ids,
        captain_id=payload.captain_id,
    )
    session.add(draft)
    session.commit()
    session.refresh(draft)
    return draft


@router.get("/{username}")
def get_active_draft(username: str, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    draft = session.exec(
        select(Draft).where(Draft.user_id == user.id, Draft.is_active == True)  # noqa: E712
    ).first()
    if not draft:
        return None
    players = [PLAYERS_BY_ID[pid] for pid in draft.player_ids if pid in PLAYERS_BY_ID]
    return {
        "id": draft.id,
        "user_id": draft.user_id,
        "name": draft.name,
        "captain_id": draft.captain_id,
        "players": players,
    }
