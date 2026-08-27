# DraftWars

Draft an all-time XI from cricket's greatest eras, simulate matches, and climb a global leaderboard.

Player names are original/altered and inspired by real cricketing legends across different countries and eras — they are **not** official names, likenesses, or endorsements of any real player.

## Stack

- **Backend:** FastAPI + SQLModel (SQLite locally, Postgres in production)
- **Frontend:** React + TypeScript + Vite
- **Deploy:** Vercel (Python serverless function for the API, static build for the frontend)

## How it works

1. Pick a username (no password) — this is your identity on the leaderboard.
2. Draft 11 players within a 100-credit budget, respecting squad rules:
   - 1-2 Wicketkeepers, 3-6 Batters, 3-6 Bowlers, 0-4 All-rounders.
3. Pick a captain (scores 2x points).
4. Run simulated matches against randomly generated AI opponent XIs. Each match produces
   a full scorecard (simulated runs/wickets/points per player).
5. Points earned accumulate on the global leaderboard.

## Local development

Backend:

```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend (in another terminal):

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server proxies `/api/*` to `http://localhost:8000`.

## Deployment (Vercel)

The repo deploys as a single Vercel project:

- `frontend/` builds to static assets (`frontend/dist`).
- `api/index.py` wraps the FastAPI app as a Python serverless function.
- `vercel.json` rewrites `/api/*` to the function and everything else to the SPA.

You need a **Postgres** database for a persistent, shared leaderboard in production (SQLite
is file-based and won't survive across serverless invocations). Set the `DATABASE_URL`
environment variable in the Vercel project (e.g. Vercel Postgres / Neon, or any Postgres
connection string) before deploying to production.

```bash
vercel link
vercel env add DATABASE_URL production
vercel --prod
```

## Roadmap

This is the first sport. The draft/simulate/leaderboard pattern is written to generalize —
next up: basketball, football, and other sports using the same engine shape.
