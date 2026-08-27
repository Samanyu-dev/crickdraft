from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Column, JSON


class User(SQLModel, table=True):
    __tablename__ = "app_user"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    elo_rating: float = 1200.0
    matches_played: int = 0
    wins: int = 0
    losses: int = 0


class Draft(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="app_user.id")
    name: str = "My XI"
    player_ids: List[int] = Field(sa_column=Column(JSON))
    captain_id: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True


class SimulationRun(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    draft_id: int = Field(index=True, foreign_key="draft.id")
    user_id: int = Field(index=True, foreign_key="app_user.id")
    opponent_name: str
    opponent_rating: float = 1200.0
    team_score: float
    opponent_score: float
    result: str  # "W" or "L"
    elo_before: float = 1200.0
    elo_after: float = 1200.0
    elo_delta: float = 0.0
    scorecard: dict = Field(sa_column=Column(JSON))
    played_at: datetime = Field(default_factory=datetime.utcnow)
