from typing import Optional, List
from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=20, pattern=r"^[A-Za-z0-9_]+$")


class DraftCreate(BaseModel):
    username: str
    name: str = "My XI"
    player_ids: List[int]
    captain_id: Optional[int] = None
    tournament: str = "showdown-league"


class DraftOut(BaseModel):
    id: int
    user_id: int
    tournament: str
    name: str
    player_ids: List[int]
    captain_id: Optional[int]


class SimulateRequest(BaseModel):
    draft_id: int


class LeaderboardEntry(BaseModel):
    username: str
    elo_rating: float
    matches_played: int
    wins: int
    losses: int
    draws: int
    win_pct: float
