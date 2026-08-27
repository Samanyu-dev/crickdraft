import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { useUser } from '../UserContext'
import { api } from '../api'
import FlipScore from '../components/FlipScore'
import RankBadge from '../components/RankBadge'
import { getRank } from '../rankTiers'
import type { DraftDetail, MatchResult, OverEvent, User } from '../types'

const INNINGS_DURATION_MS = 4400
const BREAK_MS = 1300

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

function eventFor(over: OverEvent): { text: string; kind: 'wicket' | 'six' | 'four' } | null {
  if (over.balls.includes('W')) return { text: 'WICKET!', kind: 'wicket' }
  if (over.balls.includes('6')) return { text: 'SIX!', kind: 'six' }
  if (over.balls.includes('4')) return { text: 'FOUR!', kind: 'four' }
  return null
}

type Side = { score: number; wickets: number; over: number }
const ZERO_SIDE: Side = { score: 0, wickets: 0, over: 0 }

export default function Team() {
  const { username } = useUser()
  const [draft, setDraft] = useState<DraftDetail | null | undefined>(undefined)
  const [user, setUser] = useState<User | null>(null)
  const [live, setLive] = useState<{ team: Side; opp: Side }>({ team: ZERO_SIDE, opp: ZERO_SIDE })
  const [activeSide, setActiveSide] = useState<'team' | 'opp' | null>(null)
  const [banner, setBanner] = useState<{ text: string; kind: string } | null>(null)
  const [shake, setShake] = useState(0)
  const [breakText, setBreakText] = useState<string | null>(null)
  const [lastMatch, setLastMatch] = useState<MatchResult | null>(null)
  const [history, setHistory] = useState<MatchResult[]>([])
  const [playing, setPlaying] = useState(false)
  const [expanded, setExpanded] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)
  const scoreboardRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (shake === 0) return
    const el = scoreboardRef.current
    if (!el) return
    el.classList.remove('shake')
    void el.offsetWidth
    el.classList.add('shake')
    const t = setTimeout(() => el.classList.remove('shake'), 400)
    return () => clearTimeout(t)
  }, [shake])

  function refresh() {
    if (!username) return
    api.getDraft(username).then(setDraft)
    api.getUser(username).then(setUser)
  }

  useEffect(refresh, [username])

  async function playTimeline(timeline: OverEvent[], side: 'team' | 'opp', durationMs: number) {
    setActiveSide(side)
    const stepDelay = durationMs / Math.max(1, timeline.length)
    for (const over of timeline) {
      const ev = eventFor(over)
      setBanner(ev)
      if (ev?.kind === 'wicket') setShake((n) => n + 1)
      setLive((prev) => ({ ...prev, [side]: { score: over.score, wickets: over.wickets, over: over.over } }))
      await sleep(stepDelay)
    }
    setBanner(null)
  }

  async function handlePlay() {
    if (!draft || playing) return
    setPlaying(true)
    setError(null)
    setLastMatch(null)
    setLive({ team: ZERO_SIDE, opp: ZERO_SIDE })
    setBreakText(null)
    try {
      const match = await api.simulate(draft.id)
      await playTimeline(match.team_timeline, 'team', INNINGS_DURATION_MS)
      setActiveSide(null)
      setBreakText(`Innings break — target ${match.team_score + 1}`)
      await sleep(BREAK_MS)
      setBreakText(null)
      await playTimeline(match.opponent_timeline, 'opp', INNINGS_DURATION_MS)
      setActiveSide(null)
      setLastMatch(match)
      setHistory((prev) => [match, ...prev])
      setUser((u) => (u ? { ...u, ...match.totals } : u))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Simulation failed')
    } finally {
      setPlaying(false)
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

  const promoted =
    lastMatch && getRank(lastMatch.elo_before).name !== getRank(lastMatch.elo_after).name
      ? getRank(lastMatch.elo_after)
      : null

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
              <strong>{user.elo_rating.toFixed(0)}</strong>
              <span>elo rating</span>
            </div>
            <div>
              <RankBadge elo={user.elo_rating} />
              <span>rank</span>
            </div>
            <div>
              <strong>
                {user.wins}-{user.losses}
              </strong>
              <span>W-L · {user.matches_played} played</span>
            </div>
          </div>
        )}

        <div className="scoreboard-wrap" ref={scoreboardRef}>
          <div className="scoreboard">
            <div className={`scoreboard-side ${activeSide === 'team' ? 'active' : ''}`}>
              <div className="scoreboard-label">Your XI</div>
              <FlipScore value={live.team.score} />
              <div className="ledger muted" style={{ fontSize: '0.75rem', marginTop: '0.3rem' }}>
                {live.team.wickets} wkt · ov {live.team.over}
              </div>
            </div>
            <div className="scoreboard-vs">vs</div>
            <div className={`scoreboard-side ${activeSide === 'opp' ? 'active' : ''}`}>
              <div className="scoreboard-label">Opponent</div>
              <FlipScore value={live.opp.score} />
              <div className="ledger muted" style={{ fontSize: '0.75rem', marginTop: '0.3rem' }}>
                {live.opp.wickets} wkt · ov {live.opp.over}
              </div>
            </div>
          </div>
          <AnimatePresence>
            {banner && (
              <motion.div
                key={banner.text + Math.random()}
                className={`event-banner event-${banner.kind}`}
                initial={{ opacity: 0, scale: 0.7, y: 10 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.8 }}
                transition={{ duration: 0.25 }}
              >
                {banner.text}
              </motion.div>
            )}
            {breakText && (
              <motion.div
                key="break"
                className="event-banner event-info"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
              >
                {breakText}
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        <button className="btn-primary" onClick={handlePlay} disabled={playing} style={{ width: '100%' }}>
          {playing ? 'Match in progress…' : history.length === 0 ? 'Play a match' : 'Play another match'}
        </button>
        {error && <p className="error">{error}</p>}

        <AnimatePresence>
          {lastMatch && (
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              className="result-reveal"
            >
              <span className={`stamp ${lastMatch.result === 'W' ? 'win' : 'loss'}`}>
                {lastMatch.result === 'W' ? 'Match Won' : 'Match Lost'}
              </span>
              <span className="elo-change">
                {lastMatch.elo_before.toFixed(0)} → {lastMatch.elo_after.toFixed(0)}
                <b className={lastMatch.elo_delta >= 0 ? 'up' : 'down'}>
                  {' '}
                  ({lastMatch.elo_delta >= 0 ? '+' : ''}
                  {lastMatch.elo_delta.toFixed(1)})
                </b>
              </span>
              {promoted && <span className="promo-banner">Promoted to {promoted.name}!</span>}
            </motion.div>
          )}
        </AnimatePresence>

        {history.length > 0 && (
          <div className="results-list">
            <AnimatePresence initial={false}>
              {history.map((r, i) => (
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
                    <span className={`ledger elo-pill ${r.elo_delta >= 0 ? 'up' : 'down'}`}>
                      {r.elo_delta >= 0 ? '+' : ''}
                      {r.elo_delta.toFixed(1)}
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
                        <h4 style={{ fontSize: '0.85rem', color: 'var(--brass)' }}>
                          {r.opponent_name} <span className="muted">({r.opponent_rating.toFixed(0)} elo)</span>
                        </h4>
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
