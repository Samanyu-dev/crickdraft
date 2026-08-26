import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useUser } from '../UserContext'
import { api } from '../api'
import type { DraftDetail, MatchResult, User } from '../types'

export default function Team() {
  const { username } = useUser()
  const [draft, setDraft] = useState<DraftDetail | null | undefined>(undefined)
  const [user, setUser] = useState<User | null>(null)
  const [rounds, setRounds] = useState(5)
  const [results, setResults] = useState<MatchResult[] | null>(null)
  const [simulating, setSimulating] = useState(false)
  const [expanded, setExpanded] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)

  function refresh() {
    if (!username) return
    api.getDraft(username).then(setDraft)
    api.getUser(username).then(setUser)
  }

  useEffect(refresh, [username])

  async function handleSimulate() {
    if (!draft) return
    setSimulating(true)
    setError(null)
    setResults(null)
    try {
      const res = await api.simulate(draft.id, rounds)
      setResults(res.results)
      setUser((u) => (u ? { ...u, ...res.totals } : u))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Simulation failed')
    } finally {
      setSimulating(false)
    }
  }

  if (draft === undefined) return <p className="muted">Loading your XI...</p>

  if (draft === null) {
    return (
      <div className="empty-state">
        <p>You haven't saved an XI yet.</p>
        <Link className="btn-primary" to="/draft">
          Go build your squad
        </Link>
      </div>
    )
  }

  return (
    <div className="team-layout">
      <section className="team-summary">
        <h2>{draft.name}</h2>
        <div className="team-list">
          {draft.players.map((p) => (
            <div key={p.id} className="team-row">
              <span className={`role-badge role-${p.role}`}>{p.role}</span>
              <span className="team-row-name">
                {p.name} {draft.captain_id === p.id && <span className="captain-star">★</span>}
              </span>
              <span className="muted">{p.country} · {p.era}</span>
            </div>
          ))}
        </div>
        <Link to="/draft" className="link-btn">
          Edit squad
        </Link>
      </section>

      <section className="sim-panel">
        {user && (
          <div className="stat-row">
            <div>
              <strong>{user.total_points.toFixed(0)}</strong>
              <span>points</span>
            </div>
            <div>
              <strong>{user.matches_played}</strong>
              <span>matches</span>
            </div>
            <div>
              <strong>{user.wins}-{user.losses}</strong>
              <span>W-L</span>
            </div>
          </div>
        )}

        <div className="sim-controls">
          <label>
            Rounds
            <select value={rounds} onChange={(e) => setRounds(Number(e.target.value))}>
              {[1, 3, 5, 10].map((n) => (
                <option key={n} value={n}>
                  {n}
                </option>
              ))}
            </select>
          </label>
          <button className="btn-primary" onClick={handleSimulate} disabled={simulating}>
            {simulating ? 'Simulating...' : `Simulate ${rounds} match${rounds > 1 ? 'es' : ''}`}
          </button>
        </div>
        {error && <p className="error">{error}</p>}

        {results && (
          <div className="results-list">
            {results.map((r, i) => (
              <div key={i} className={`result-card ${r.result === 'W' ? 'win' : 'loss'}`}>
                <div className="result-head" onClick={() => setExpanded(expanded === i ? null : i)}>
                  <span className={`result-badge ${r.result === 'W' ? 'win' : 'loss'}`}>{r.result}</span>
                  <span>
                    You {r.team_score.toFixed(0)} — {r.opponent_score.toFixed(0)} {r.opponent_name}
                  </span>
                  <span className="chevron">{expanded === i ? '▲' : '▼'}</span>
                </div>
                {expanded === i && (
                  <div className="scorecard">
                    <div>
                      <h4>Your XI</h4>
                      {r.scorecard.team.map((p) => (
                        <div key={p.id} className="scorecard-row">
                          <span>
                            {p.name} {p.captain && '★'}
                          </span>
                          <span className="muted">
                            {p.runs}r {p.wickets ? `/ ${p.wickets}w` : ''}
                          </span>
                          <span>{p.points.toFixed(0)} pts</span>
                        </div>
                      ))}
                    </div>
                    <div>
                      <h4>{r.opponent_name}</h4>
                      {r.scorecard.opponent.map((p) => (
                        <div key={p.id} className="scorecard-row">
                          <span>
                            {p.name} {p.captain && '★'}
                          </span>
                          <span className="muted">
                            {p.runs}r {p.wickets ? `/ ${p.wickets}w` : ''}
                          </span>
                          <span>{p.points.toFixed(0)} pts</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  )
}
