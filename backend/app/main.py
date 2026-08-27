from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db
from .routers import players, users, drafts, simulate, leaderboard, draft, tournaments, matches

app = FastAPI(title="CrickDraft API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/api/health")
def health():
    return {"status": "ok"}


app.include_router(tournaments.router)
app.include_router(matches.router)
app.include_router(draft.router)
app.include_router(players.router)
app.include_router(users.router)
app.include_router(drafts.router)
app.include_router(simulate.router)
app.include_router(leaderboard.router)
