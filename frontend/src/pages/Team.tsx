import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { useUser } from '../UserContext'
import { api } from '../api'
import FlipScore from '../components/FlipScore'
import type { DraftDetail, MatchResult, User } from '../types'

export default function Team() {
  const { username } = useUser()
  const [draft, setDraft] = useState<DraftDetail | null | undefined>(undefined)
  const [user, setUser] = useState<User | null>(null)
  const [rounds, setRounds] = useState(5)
  const [results, setResults] = useState<MatchResult[] | null>(null)
  const [liveScore, setLiveScore] = useState({ team: 0, opponent: 0, teamW: 0, oppW: 0, teamOv: 0, oppOv: 0 })
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
    setLiveScore({ team: 0, opponent: 0, teamW: 0, oppW: 0, teamOv: 0, oppOv: 0 })
    try {
      const res = await api.simulate(draft.id, rounds)
      setUser((u) => (u ? { ...u, ...res.totals } : u))
      // reveal matches one at a time so the scoreboard reads as a live feed
      for (let i = 0; i < res.results.length; i++) {
        const r = res.results[i]
        setLiveScore({
          team: r.team_score,
          opponent: r.opponent_score,
          teamW: r.team_wickets,
          oppW: r.opponent_wickets,
          teamOv: r.team_overs,
          oppOv: r.opponent_overs,
        })
        setResults((prev) => [...(prev ?? []), r])
        if (i < res.results.length - 1) {
          await new Promise((resolve) => setTimeout(resolve, 1100))
          setLiveScore({ team: 0, opponent: 0, teamW: 0, oppW: 0, teamOv: 0, oppOv: 0 })
          await new Promise((resolve) => setTimeout(resolve, 250))
        }
      }
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
        <p>You haven't drafted an XI yet.</p>
        <Link className="btn-primary" to="/draft">
          Start the draft
        </Link>
      </div>
    )
  }

  return (
    <div className="team-layout">
      <section className="team-summary">
        <h2>{draft.name}</h2>
        <div className="team-list">
          {draft.players.map((p, i) => (
            <div key={p.id} className="team-row">
              <span className={`role-tag role-${p.role}`}>#{i + 1}</span>
              <span className="p-name">
                {p.name} {draft.captain_id === p.id && <span className="captain-star">★</span>}
              </span>
              <span className="muted ledger" style={{ fontSize: '0.75rem' }}>
                {p.country} · {p.era}
              </span>
            </div>
          ))}
        </div>
        <Link to="/draft" className="link-btn">
          Draft a new XI
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

        <div className="scoreboard">
          <div className="scoreboard-side">
            <div className="scoreboard-label">Your XI</div>
            <FlipScore value={liveScore.team} />
            <div className="ledger muted" style={{ fontSize: '0.75rem', marginTop: '0.3rem' }}>
              {liveScore.teamW} wkt · {liveScore.teamOv.toFixed(1)} ov
            </div>
          </div>
          <div className="scoreboard-vs">vs</div>
          <div className="scoreboard-side">
            <div className="scoreboard-label">Opponent</div>
            <FlipScore value={liveScore.opponent} />
            <div className="ledger muted" style={{ fontSize: '0.75rem', marginTop: '0.3rem' }}>
              {liveScore.oppW} wkt · {liveScore.oppOv.toFixed(1)} ov
            </div>
          </div>
        </div>

        <div className="sim-controls">
          <label>
            Rounds
            <select value={rounds} onChange={(e) => setRounds(Number(e.target.value))} disabled={simulating}>
              {[1, 3, 5, 10].map((n) => (
                <option key={n} value={n}>
                  {n}
                </option>
              ))}
            </select>
          </label>
          <button className="btn-primary" onClick={handleSimulate} disabled={simulating}>
            {simulating ? 'Playing…' : `Simulate ${rounds} match${rounds > 1 ? 'es' : ''}`}
          </button>
        </div>
        {error && <p className="error">{error}</p>}

        {results && (
          <div className="results-list">
            <AnimatePresence initial={false}>
              {results.map((r, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                  className="result-card"
                >
                  <div className="result-head" onClick={() => setExpanded(expanded === i ? null : i)}>
                    <span className={`stamp ${r.result === 'W' ? 'win' : 'loss'}`}>
                      {r.result === 'W' ? 'Won' : 'Lost'}
                    </span>
                    <span>
                      {r.team_score.toFixed(0)}/{r.team_wickets} ({r.team_overs.toFixed(1)}) — {r.opponent_score.toFixed(0)}/{r.opponent_wickets} ({r.opponent_overs.toFixed(1)}) vs {r.opponent_name}
                    </span>
                    <span className="chevron">{expanded === i ? '▲' : '▼'}</span>
                  </div>
                  {expanded === i && (
                    <div className="scorecard">
                      <div>
                        <h4 style={{ fontSize: '0.85rem', color: 'var(--brass)' }}>Your XI</h4>
                        {r.scorecard.team.map((p) => (
                          <div key={p.id} className="scorecard-row">
                            <span>
                              {p.name} {p.captain && '★'}
                            </span>
                            <span className="muted">
                              {p.runs}({p.balls}) {p.wickets ? `· ${p.wickets}/${p.runs_conceded} (${p.overs?.toFixed(1)}ov)` : ''}
                            </span>
                            <span>{p.points.toFixed(0)} pts</span>
                          </div>
                        ))}
                      </div>
                      <div>
                        <h4 style={{ fontSize: '0.85rem', color: 'var(--brass)' }}>{r.opponent_name}</h4>
                        {r.scorecard.opponent.map((p) => (
                          <div key={p.id} className="scorecard-row">
                            <span>
                              {p.name} {p.captain && '★'}
                            </span>
                            <span className="muted">
                              {p.runs}({p.balls}) {p.wickets ? `· ${p.wickets}/${p.runs_conceded} (${p.overs?.toFixed(1)}ov)` : ''}
                            </span>
                            <span>{p.points.toFixed(0)} pts</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}
      </section>
    </div>
  )
}
