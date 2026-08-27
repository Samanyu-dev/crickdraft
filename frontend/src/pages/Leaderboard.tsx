import { useEffect, useState } from 'react'
import { api } from '../api'
import type { LeaderboardEntry } from '../types'
import { useUser } from '../UserContext'
import RankBadge from '../components/RankBadge'

export default function Leaderboard() {
  const { username } = useUser()
  const [entries, setEntries] = useState<LeaderboardEntry[] | null>(null)

  useEffect(() => {
    api.getLeaderboard().then(setEntries)
  }, [])

  if (!entries) return <p className="muted">Loading the honours board...</p>

  return (
    <div className="leaderboard-board">
      <h2>Honours Board</h2>
      <div className="board-sub">Ranked by Elo rating</div>
      {entries.length === 0 ? (
        <p className="muted" style={{ textAlign: 'center' }}>
          No names carved yet. Draft an XI and play a match to be the first.
        </p>
      ) : (
        entries.map((e, i) => (
          <div key={e.username} className={`board-row ${e.username === username ? 'me' : ''}`}>
            <span className={`rank ${i < 3 ? 'gold' : ''}`}>{i + 1}</span>
            <span className="name">{e.username}</span>
            <RankBadge elo={e.elo_rating} size="sm" />
            <span className="points">{e.elo_rating.toFixed(0)} elo</span>
            <span className="matches">{e.matches_played}m</span>
            <span className="wl">
              {e.wins}-{e.losses} · {e.win_pct.toFixed(0)}%
            </span>
          </div>
        ))
      )}
    </div>
  )
}
