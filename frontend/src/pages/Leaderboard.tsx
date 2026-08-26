import { useEffect, useState } from 'react'
import { api } from '../api'
import type { LeaderboardEntry } from '../types'
import { useUser } from '../UserContext'

export default function Leaderboard() {
  const { username } = useUser()
  const [entries, setEntries] = useState<LeaderboardEntry[] | null>(null)

  useEffect(() => {
    api.getLeaderboard().then(setEntries)
  }, [])

  if (!entries) return <p className="muted">Loading leaderboard...</p>

  return (
    <div className="leaderboard">
      <h2>Global Leaderboard</h2>
      {entries.length === 0 ? (
        <p className="muted">No matches simulated yet. Be the first!</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Player</th>
              <th>Points</th>
              <th>Matches</th>
              <th>W-L</th>
              <th>Win %</th>
            </tr>
          </thead>
          <tbody>
            {entries.map((e, i) => (
              <tr key={e.username} className={e.username === username ? 'me' : ''}>
                <td>{i + 1}</td>
                <td>{e.username}</td>
                <td>{e.total_points.toFixed(0)}</td>
                <td>{e.matches_played}</td>
                <td>
                  {e.wins}-{e.losses}
                </td>
                <td>{e.win_pct.toFixed(0)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
