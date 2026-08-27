import { useEffect, useRef, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { useUser } from '../UserContext'
import { soccerApi } from './api'
import FlipScore from '../components/FlipScore'
import RankBadge from '../components/RankBadge'
import PlayerCard from '../components/PlayerCard'
import { getRank } from '../rankTiers'
import { soccerCardStats } from '../playerCardStats'
import type { SoccerDraftDetail, SoccerHistoryEntry, SoccerMatchEvent, SoccerMatchResult, SoccerRole, SoccerUser } from './types'

const MATCH_DURATION_MS = 9500
const ROLE_ORDER: SoccerRole[] = ['GK', 'DEF', 'MID', 'FWD']

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

const RESULT_LABEL: Record<string, string> = { W: 'Match Won', L: 'Match Lost', D: 'Match Drawn' }
const RESULT_SHORT: Record<string, string> = { W: 'Won', L: 'Lost', D: 'Drawn' }
const RESULT_CLASS: Record<string, string> = { W: 'win', L: 'loss', D: 'draw' }

export default function SoccerTeam() {
  const { username, tournament: currentTournament, setSport } = useUser()
  useEffect(() => setSport('soccer'), [setSport])
  const [searchParams] = useSearchParams()
  const tournament = searchParams.get('tournament') || currentTournament

  const [draft, setDraft] = useState<SoccerDraftDetail | null | undefined>(undefined)
  const [user, setUser] = useState<SoccerUser | null>(null)
  const [live, setLive] = useState({ team: 0, opponent: 0, minute: 0 })
  const [banner, setBanner] = useState<{ text: string; kind: string } | null>(null)
  const [shake, setShake] = useState(0)
  const [lastMatch, setLastMatch] = useState<SoccerMatchResult | null>(null)
  const [history, setHistory] = useState<SoccerHistoryEntry[]>([])
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
    soccerApi.getDraft(username, tournament).then(setDraft)
    soccerApi.getUser(username, tournament).then(setUser)
    soccerApi.getMatchHistory(username, tournament).then(setHistory)
  }

  useEffect(refresh, [username, tournament])

  async function playTimeline(timeline: SoccerMatchEvent[]) {
    const stepDelay = MATCH_DURATION_MS / Math.max(1, timeline.length)
    for (const e of timeline) {
      if (e.event === 'goal') {
        setBanner({ text: `GOAL! ${e.scorer}`, kind: e.side === 'team' ? 'six' : 'wicket' })
        setShake((n) => n + 1)
      } else if (e.event === 'chance') {
        setBanner({ text: 'Close chance!', kind: 'four' })
      } else {
        setBanner(null)
      }
      setLive({ team: e.score_team, opponent: e.score_opponent, minute: e.minute })
      await sleep(stepDelay)
    }
    setBanner(null)
  }

  async function handlePlay() {
    if (!draft || playing) return
    setPlaying(true)
    setError(null)
    setLastMatch(null)
    setLive({ team: 0, opponent: 0, minute: 0 })
    try {
      const match = await soccerApi.simulate(draft.id)
      await playTimeline(match.timeline)
      setLastMatch(match)
      setHistory((prev) => [
        {
          opponent_name: match.opponent_name, opponent_rating: match.opponent_rating, result: match.result,
          team_goals: match.team_goals, opponent_goals: match.opponent_goals,
          elo_before: match.elo_before, elo_after: match.elo_after, elo_delta: match.elo_delta,
          scorecard: match.scorecard,
        },
        ...prev,
      ])
      setUser((u) =>
        u
          ? { ...u, ...match.totals, matches_today: match.matches_today, matches_remaining_today: match.matches_remaining_today }
          : u,
      )
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
        <p>You haven't drafted an XI for this tournament yet.</p>
        <Link className="btn-primary" to={`/soccer/draft?tournament=${tournament}`}>
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
        <div className="pick-label" style={{ marginBottom: '0.5rem' }}>
          {tournament.replace(/-/g, ' ')}
        </div>
        <h2>{draft.name}</h2>
        <div className="player-card-grid">
          {[...draft.players]
            .sort((a, b) => ROLE_ORDER.indexOf(a.role) - ROLE_ORDER.indexOf(b.role))
            .map((p, i) => (
              <PlayerCard
                key={p.id}
                name={p.name}
                role={p.role}
                country={p.country}
                era={p.era}
                rating={p.rating}
                rarity={p.rarity}
                credit={p.credit}
                stats={soccerCardStats(p)}
                badge={draft.captain_id === p.id ? '★ C' : `#${i + 1}`}
              />
            ))}
        </div>
        <Link to={`/soccer/draft?tournament=${tournament}`} className="link-btn">
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
                {user.draws > 0 ? `-${user.draws}` : ''}
              </strong>
              <span>W-L{user.draws > 0 ? '-D' : ''} · {user.matches_played} played</span>
            </div>
            <div>
              <strong>{user.matches_remaining_today}/20</strong>
              <span>matches left today</span>
            </div>
          </div>
        )}

        {playing && (
          <div className="live-badge" style={{ marginBottom: '0.5rem' }}>
            <span className="live-dot" /> Live · {live.minute}'
          </div>
        )}
        <div className="scoreboard-wrap" ref={scoreboardRef}>
          <div className="scoreboard">
            <div className="scoreboard-side">
              <div className="scoreboard-label">Your XI</div>
              <FlipScore value={live.team} />
            </div>
            <div className="scoreboard-vs">vs</div>
            <div className="scoreboard-side">
              <div className="scoreboard-label">Opponent</div>
              <FlipScore value={live.opponent} />
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
          </AnimatePresence>
        </div>

        <button
          className="btn-primary"
          onClick={handlePlay}
          disabled={playing || (user?.matches_remaining_today ?? 1) <= 0}
          style={{ width: '100%' }}
        >
          {playing
            ? 'Match in progress…'
            : (user?.matches_remaining_today ?? 1) <= 0
              ? 'No matches left today'
              : history.length === 0
                ? 'Play a match'
                : 'Play another match'}
        </button>
        {error && <p className="error">{error}</p>}

        <AnimatePresence>
          {lastMatch && (
            <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="result-reveal">
              <span className={`stamp ${RESULT_CLASS[lastMatch.result]}`}>{RESULT_LABEL[lastMatch.result]}</span>
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
                    <span className={`stamp ${RESULT_CLASS[r.result]}`}>{RESULT_SHORT[r.result]}</span>
                    <span>
                      {r.team_goals} — {r.opponent_goals} vs {r.opponent_name}
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
                            <span className="muted">{p.goals} goal{p.goals !== 1 ? 's' : ''}</span>
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
                            <span className="muted">{p.goals} goal{p.goals !== 1 ? 's' : ''}</span>
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
