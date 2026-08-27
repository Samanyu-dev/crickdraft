import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence, type Variants } from 'framer-motion'
import { api } from '../api'
import { useUser } from '../UserContext'
import type { Player, Role, Squad } from '../types'

const ROLE_RULES: Record<Role, [number, number]> = {
  WK: [1, 2],
  BAT: [3, 6],
  BOWL: [3, 6],
  AR: [0, 4],
}
const ROLES: Role[] = ['WK', 'BAT', 'BOWL', 'AR']
const SQUAD_SIZE = 11
const CREDIT_CAP = 100
const TOTAL_REROLLS = 2
const MAX_ROLL_ATTEMPTS = 24

function tally(picks: Player[]) {
  const counts: Record<Role, number> = { WK: 0, BAT: 0, BOWL: 0, AR: 0 }
  picks.forEach((p) => counts[p.role]++)
  return counts
}

function totalCredits(picks: Player[]) {
  return picks.reduce((sum, p) => sum + p.credit, 0)
}

function eligibility(picks: Player[], candidate: Player): { ok: boolean; reason?: string } {
  const counts = tally(picks)
  const [, max] = ROLE_RULES[candidate.role]
  if (counts[candidate.role] >= max) return { ok: false, reason: `${candidate.role} slots full` }
  if (totalCredits(picks) + candidate.credit > CREDIT_CAP) return { ok: false, reason: 'Over credit budget' }

  const remainingAfterThis = SQUAD_SIZE - picks.length
  let totalNeeded = 0
  const neededByRole: Record<Role, number> = { WK: 0, BAT: 0, BOWL: 0, AR: 0 }
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

export default function Draft() {
  const { username } = useUser()
  const navigate = useNavigate()

  const [picks, setPicks] = useState<Player[]>([])
  const [captainId, setCaptainId] = useState<number | null>(null)
  const [currentSquad, setCurrentSquad] = useState<Squad | null>(null)
  const [seenSquadKeys, setSeenSquadKeys] = useState<string[]>([])
  const [rerollsLeft, setRerollsLeft] = useState(TOTAL_REROLLS)
  const [phase, setPhase] = useState<'rolling' | 'picking' | 'captain'>('rolling')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const startedRef = useRef(false)

  async function performRoll(picksSnapshot: Player[], seenSnapshot: string[]) {
    setPhase('rolling')
    setError(null)
    let seen = [...seenSnapshot]
    try {
      for (let i = 0; i < MAX_ROLL_ATTEMPTS; i++) {
        const squad = await api.rollSquad(seen)
        seen = [...seen, squad.key]
        const hasEligible = squad.players.some((p) => eligibility(picksSnapshot, p).ok)
        if (hasEligible || i === MAX_ROLL_ATTEMPTS - 1) {
          setSeenSquadKeys(seen)
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
    performRoll([], [])
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  function handlePick(player: Player) {
    const check = eligibility(picks, player)
    if (!check.ok) return
    const newPicks = [...picks, player]
    setPicks(newPicks)
    setCurrentSquad(null)
    if (newPicks.length === SQUAD_SIZE) {
      setPhase('captain')
    } else {
      performRoll(newPicks, seenSquadKeys)
    }
  }

  function handleReroll() {
    if (rerollsLeft <= 0 || phase !== 'picking') return
    setRerollsLeft((n) => n - 1)
    performRoll(picks, seenSquadKeys)
  }

  async function handleSubmit() {
    if (!username || captainId === null) return
    setSubmitting(true)
    setError(null)
    try {
      await api.submitDraft({
        username,
        name: `${username}'s XI`,
        player_ids: picks.map((p) => p.id),
        captain_id: captainId,
      })
      navigate('/team')
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
              <span className="p-name" style={{ fontFamily: 'Fraunces, serif' }}>
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
          <span className="pick-label">Pick {picks.length + 1} of {SQUAD_SIZE}</span>
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
                          {p.batting ? `Bat ${p.batting.avg.toFixed(0)} avg` : ''}
                          {p.batting && p.bowling ? ' · ' : ''}
                          {p.bowling ? `Bowl ${p.bowling.avg.toFixed(0)} avg` : ''}
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
