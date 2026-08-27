from typing import Optional, List
from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=20, pattern=r"^[A-Za-z0-9_]+$")


class UserOut(BaseModel):
    id: int
    username: str
    elo_rating: float
    matches_played: int
    wins: int
    losses: int


class DraftCreate(BaseModel):
    username: str
    name: str = "My XI"
    player_ids: List[int]
    captain_id: Optional[int] = None


class DraftOut(BaseModel):
    id: int
    user_id: int
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
    win_pct: float
