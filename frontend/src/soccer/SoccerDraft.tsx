import { useEffect, useRef, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { motion, AnimatePresence, type Variants } from 'framer-motion'
import { soccerApi } from './api'
import { useUser } from '../UserContext'
import type { SoccerPlayer, SoccerRole, SoccerSquad } from './types'

const ROLE_RULES: Record<SoccerRole, [number, number]> = {
  GK: [1, 1],
  DEF: [3, 5],
  MID: [3, 5],
  FWD: [1, 3],
}
const ROLES: SoccerRole[] = ['GK', 'DEF', 'MID', 'FWD']
const SQUAD_SIZE = 11
const CREDIT_CAP = 100
const TOTAL_REROLLS = 2
const MAX_ROLL_ATTEMPTS = 24
const RECENT_WINDOW = 3

function tally(picks: SoccerPlayer[]) {
  const counts: Record<SoccerRole, number> = { GK: 0, DEF: 0, MID: 0, FWD: 0 }
  picks.forEach((p) => counts[p.role]++)
  return counts
}

function totalCredits(picks: SoccerPlayer[]) {
  return picks.reduce((sum, p) => sum + p.credit, 0)
}

function eligibility(picks: SoccerPlayer[], candidate: SoccerPlayer): { ok: boolean; reason?: string } {
  if (picks.some((p) => p.id === candidate.id)) return { ok: false, reason: 'Already in your XI' }
  const counts = tally(picks)
  const [, max] = ROLE_RULES[candidate.role]
  if (counts[candidate.role] >= max) return { ok: false, reason: `${candidate.role} slots full` }
  if (totalCredits(picks) + candidate.credit > CREDIT_CAP) return { ok: false, reason: 'Over credit budget' }

  const remainingAfterThis = SQUAD_SIZE - picks.length
  let totalNeeded = 0
  const neededByRole: Record<SoccerRole, number> = { GK: 0, DEF: 0, MID: 0, FWD: 0 }
  for (const r of ROLES) {
    const need = Math.max(0, ROLE_RULES[r][0] - counts[r])
    neededByRole[r] = need
    totalNeeded += need
  }
  if (totalNeeded === remainingAfterThis && neededByRole[candidate.role] === 0) {
    return { ok: false, reason: 'Must fill required roles first' }
  }
  return { ok: true }
}

const plaqueVariants: Variants = {
  initial: { opacity: 0, rotateX: -14, y: -24, scale: 0.96 },
  animate: { opacity: 1, rotateX: 0, y: 0, scale: 1, transition: { duration: 0.4, ease: 'easeOut' } },
  exit: { opacity: 0, rotateX: 10, y: 14, scale: 0.97, transition: { duration: 0.22 } },
}
const rowContainerVariants: Variants = {
  initial: {},
  animate: { transition: { staggerChildren: 0.045, delayChildren: 0.15 } },
}
const rowVariants: Variants = {
  initial: { opacity: 0, y: 10 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.25 } },
}

export default function SoccerDraft() {
  const { username, tournament: currentTournament, setTournament, setSport } = useUser()
  useEffect(() => setSport('soccer'), [setSport])
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const tournament = searchParams.get('tournament') || currentTournament

  useEffect(() => {
    if (tournament !== currentTournament) setTournament(tournament)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tournament])

  const [picks, setPicks] = useState<SoccerPlayer[]>([])
  const [captainId, setCaptainId] = useState<number | null>(null)
  const [currentSquad, setCurrentSquad] = useState<SoccerSquad | null>(null)
  const [lastSquadKey, setLastSquadKey] = useState<string | null>(null)
  const [rerollsLeft, setRerollsLeft] = useState(TOTAL_REROLLS)
  const [phase, setPhase] = useState<'rolling' | 'picking' | 'captain'>('rolling')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const startedRef = useRef(false)

  async function performRoll(picksSnapshot: SoccerPlayer[], excludeKey: string | null) {
    setPhase('rolling')
    setError(null)
    let tried: string[] = excludeKey ? [excludeKey] : []
    try {
      for (let i = 0; i < MAX_ROLL_ATTEMPTS; i++) {
        const squad = await soccerApi.rollSquad(tournament, tried)
        tried = [...tried, squad.key].slice(-RECENT_WINDOW)
        const hasEligible = squad.players.some((p) => eligibility(picksSnapshot, p).ok)
        if (hasEligible || i === MAX_ROLL_ATTEMPTS - 1) {
          setLastSquadKey(squad.key)
          setCurrentSquad(squad)
          setPhase('picking')
          return
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not roll a squad')
      setPhase('picking')
    }
  }

  useEffect(() => {
    if (startedRef.current) return
    startedRef.current = true
    performRoll([], null)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  function handlePick(player: SoccerPlayer) {
    const check = eligibility(picks, player)
    if (!check.ok) return
    const newPicks = [...picks, player]
    setPicks(newPicks)
    setCurrentSquad(null)
    if (newPicks.length === SQUAD_SIZE) {
      setPhase('captain')
    } else {
      performRoll(newPicks, lastSquadKey)
    }
  }

  function handleReroll() {
    if (rerollsLeft <= 0 || phase !== 'picking') return
    setRerollsLeft((n) => n - 1)
    performRoll(picks, lastSquadKey)
  }

  async function handleSubmit() {
    if (!username || captainId === null) return
    setSubmitting(true)
    setError(null)
    try {
      await soccerApi.submitDraft({
        username,
        name: `${username}'s XI`,
        player_ids: picks.map((p) => p.id),
        captain_id: captainId,
        tournament,
      })
      navigate('/soccer/team')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not save draft')
    } finally {
      setSubmitting(false)
    }
  }

  const counts = tally(picks)
  const credits = totalCredits(picks)

  if (phase === 'captain') {
    return (
      <div className="squad-panel" style={{ maxWidth: 640, margin: '0 auto' }}>
        <h2>Name your captain</h2>
        <p className="muted" style={{ fontSize: '0.85rem' }}>
          Your captain scores double points in every simulated match.
        </p>
        <div className="captain-list">
          {picks.map((p) => (
            <div className="captain-row" key={p.id}>
              <span className={`role-tag role-${p.role}`}>{p.role}</span>
              <span className="p-name">
                {p.name} <span className="muted ledger" style={{ fontSize: '0.72rem' }}>· {p.country} {p.era}</span>
              </span>
              <button
                className={`btn-crown ${captainId === p.id ? 'is-captain' : ''}`}
                onClick={() => setCaptainId(p.id)}
              >
                {captainId === p.id ? '★ Captain' : 'Make captain'}
              </button>
            </div>
          ))}
        </div>
        {error && <p className="error">{error}</p>}
        <button className="btn-primary" disabled={captainId === null || submitting} onClick={handleSubmit}>
          {submitting ? 'Sealing the XI…' : 'Begin simulation'}
        </button>
      </div>
    )
  }

  return (
    <div className="draft-shell">
      <div>
        <div className="draft-head">
          <span className="pick-label">
            {tournament.replace(/-/g, ' ')} · Pick {picks.length + 1} of {SQUAD_SIZE}
          </span>
          <div className="reroll-tokens">
            Rerolls
            {Array.from({ length: TOTAL_REROLLS }).map((_, i) => (
              <span key={i} className={`coin ${i < rerollsLeft ? '' : 'spent'}`} />
            ))}
          </div>
        </div>

        <AnimatePresence mode="wait">
          {phase === 'rolling' || !currentSquad ? (
            <motion.div
              key="rolling"
              className="plaque"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              style={{ textAlign: 'center', padding: '3.5rem 1rem' }}
            >
              <span className="pick-label">Rolling the archives…</span>
            </motion.div>
          ) : (
            <motion.div
              key={currentSquad.key}
              className="plaque"
              variants={plaqueVariants}
              initial="initial"
              animate="animate"
              exit="exit"
            >
              <div className="plaque-header">
                <div className="country-era">
                  {currentSquad.country} · {currentSquad.era}
                </div>
                <div className="squad-name">{currentSquad.squad_name}</div>
              </div>
              <motion.div className="plaque-rows" variants={rowContainerVariants} initial="initial" animate="animate">
                {currentSquad.players.map((p) => {
                  const check = eligibility(picks, p)
                  return (
                    <motion.button
                      key={p.id}
                      variants={rowVariants}
                      className="plaque-row-btn"
                      disabled={!check.ok}
                      onClick={() => handlePick(p)}
                      title={check.reason}
                    >
                      <span className={`role-tag role-${p.role}`}>{p.role}</span>
                      <span>
                        <span className="p-name">{p.name}</span>
                        <span className="p-stat">
                          ATK {p.attack.toFixed(0)} · DEF {p.defense.toFixed(0)} · PAS {p.passing.toFixed(0)} · PAC {p.pace.toFixed(0)}
                        </span>
                        {!check.ok && check.reason && <span className="disabled-reason">{check.reason}</span>}
                      </span>
                      <span className="p-credit">{p.credit.toFixed(1)} cr</span>
                    </motion.button>
                  )
                })}
              </motion.div>
              <div className="plaque-actions">
                <button className="btn-ghost" onClick={handleReroll} disabled={rerollsLeft <= 0}>
                  Reroll this squad ({rerollsLeft} left)
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
        {error && <p className="error">{error}</p>}
      </div>

      <aside className="squad-panel">
        <h2>
          Your XI <span className="squad-count">{picks.length}/{SQUAD_SIZE}</span>
        </h2>
        <div className="credit-bar">
          <div className="credit-fill" style={{ width: `${Math.min(100, (credits / CREDIT_CAP) * 100)}%` }} />
        </div>
        <p className="credit-text">
          {credits.toFixed(1)} / {CREDIT_CAP} credits
        </p>
        <ul className="role-checklist">
          {ROLES.map((r) => {
            const [min, max] = ROLE_RULES[r]
            const ok = counts[r] >= min && counts[r] <= max
            return (
              <li key={r} className={ok ? 'ok' : ''}>
                {r}: {counts[r]} <span>(need {min}-{max})</span>
              </li>
            )
          })}
        </ul>
        <div className="squad-slots">
          {Array.from({ length: SQUAD_SIZE }).map((_, i) => {
            const p = picks[i]
            return (
              <div key={i} className={`slot-row ${p ? 'filled' : 'empty'}`}>
                <span className="slot-num">{i + 1}</span>
                <span className="slot-name">{p ? p.name : '—'}</span>
              </div>
            )
          })}
        </div>
      </aside>
    </div>
  )
}
