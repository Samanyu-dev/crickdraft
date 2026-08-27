import { useEffect, useRef, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { motion, AnimatePresence, type Variants } from 'framer-motion'
import { api } from '../api'
import { useUser } from '../UserContext'
import { isValidOrder, tryAugment } from '../battingOrder'
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

function eligibility(
  picks: Player[],
  positionAssignment: (Player | null)[],
  candidate: Player,
): { ok: boolean; reason?: string } {
  if (picks.some((p) => p.id === candidate.id)) return { ok: false, reason: 'Already in your XI' }
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
  // Would this pick still leave a valid batting-order arrangement for
  // everyone (including players already picked)? Checked via an online
  // bipartite matching rather than only at the very end, so the draft can
  // never paint itself into a corner with too many same-range batters.
  if (!tryAugment(positionAssignment, candidate)) {
    return { ok: false, reason: `No batting slot left open for #${candidate.position_min}-${candidate.position_max}` }
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
  const { username, tournament: currentTournament, setTournament } = useUser()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const tournament = searchParams.get('tournament') || currentTournament

  useEffect(() => {
    if (tournament !== currentTournament) setTournament(tournament)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tournament])

  const [picks, setPicks] = useState<Player[]>([])
  const [positionAssignment, setPositionAssignment] = useState<(Player | null)[]>(Array(SQUAD_SIZE).fill(null))
  const [captainId, setCaptainId] = useState<number | null>(null)
  const [currentSquad, setCurrentSquad] = useState<Squad | null>(null)
  const [lastSquadKey, setLastSquadKey] = useState<string | null>(null)
  const [rerollsLeft, setRerollsLeft] = useState(TOTAL_REROLLS)
  const [phase, setPhase] = useState<'rolling' | 'picking' | 'captain' | 'order'>('rolling')
  const [order, setOrder] = useState<(Player | null)[]>([])
  const [orderError, setOrderError] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const startedRef = useRef(false)

  async function performRoll(picksSnapshot: Player[], excludeKey: string | null, positionSnapshot: (Player | null)[]) {
    setPhase('rolling')
    setError(null)
    // Only exclude the squad just shown, not every squad seen this draft -
    // small tournament pools (e.g. 10 squads) would otherwise run out
    // after a couple of rerolls. A local (non-persisted) exclude list
    // still avoids retrying the same dead-end squad within one search.
    const tried: string[] = excludeKey ? [excludeKey] : []
    try {
      for (let i = 0; i < MAX_ROLL_ATTEMPTS; i++) {
        const squad = await api.rollSquad(tournament, tried)
        tried.push(squad.key)
        const hasEligible = squad.players.some((p) => eligibility(picksSnapshot, positionSnapshot, p).ok)
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
    performRoll([], null, Array(SQUAD_SIZE).fill(null))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  function handlePick(player: Player) {
    const check = eligibility(picks, positionAssignment, player)
    if (!check.ok) return
    const augmented = tryAugment(positionAssignment, player)
    if (!augmented) return
    const newPicks = [...picks, player]
    setPicks(newPicks)
    setPositionAssignment(augmented)
    setCurrentSquad(null)
    if (newPicks.length === SQUAD_SIZE) {
      setOrder(augmented)
      setOrderError(null)
      setPhase('captain')
    } else {
      performRoll(newPicks, lastSquadKey, augmented)
    }
  }

  function handleReroll() {
    if (rerollsLeft <= 0 || phase !== 'picking') return
    setRerollsLeft((n) => n - 1)
    performRoll(picks, lastSquadKey, positionAssignment)
  }

  function goToOrder() {
    setPhase('order')
  }

  function handlePositionChange(playerId: number, newPos: number) {
    setOrder((prev) => {
      const arr = [...prev]
      const fromIdx = arr.findIndex((p) => p?.id === playerId)
      const toIdx = newPos - 1
      if (fromIdx === -1 || fromIdx === toIdx) return prev
      const player = arr[fromIdx]!
      const occupant = arr[toIdx]
      if (occupant && !(occupant.position_min <= fromIdx + 1 && fromIdx + 1 <= occupant.position_max)) {
        setOrderError(`Can't move there — ${occupant.name} can only bat positions ${occupant.position_min}-${occupant.position_max}.`)
        return prev
      }
      setOrderError(null)
      arr[toIdx] = player
      arr[fromIdx] = occupant
      return arr
    })
  }

  async function handleSubmit() {
    if (!username || captainId === null || !isValidOrder(order)) return
    setSubmitting(true)
    setError(null)
    try {
      await api.submitDraft({
        username,
        name: `${username}'s XI`,
        player_ids: order.map((p) => p!.id),
        captain_id: captainId,
        tournament,
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
        <button className="btn-primary" disabled={captainId === null} onClick={goToOrder}>
          Continue to batting order
        </button>
      </div>
    )
  }

  if (phase === 'order') {
    return (
      <div className="squad-panel" style={{ maxWidth: 640, margin: '0 auto' }}>
        <h2>Set your batting order</h2>
        <p className="muted" style={{ fontSize: '0.85rem' }}>
          Every player has a real batting-position range — openers can't bat at 9, tailenders can't open.
          We've suggested a valid order; swap anyone who needs it.
        </p>
        <div className="captain-list">
          {order.map((p, i) => {
            if (!p) return null
            const options = []
            for (let pos = p.position_min; pos <= p.position_max; pos++) options.push(pos)
            return (
              <div className="captain-row" key={p.id}>
                <span className="ledger" style={{ color: 'var(--brass)', fontSize: '0.85rem' }}>#{i + 1}</span>
                <span className="p-name" style={{ fontFamily: 'Fraunces, serif' }}>
                  {p.name} {captainId === p.id && <span className="captain-star">★</span>}
                  <span className="muted ledger" style={{ fontSize: '0.72rem' }}>
                    {' '}
                    · eligible {p.position_min}-{p.position_max}
                  </span>
                </span>
                <select value={i + 1} onChange={(e) => handlePositionChange(p.id, Number(e.target.value))}>
                  {options.map((pos) => (
                    <option key={pos} value={pos}>
                      Bat at #{pos}
                    </option>
                  ))}
                </select>
              </div>
            )
          })}
        </div>
        {orderError && <p className="error">{orderError}</p>}
        {error && <p className="error">{error}</p>}
        <div style={{ display: 'flex', gap: '0.6rem' }}>
          <button className="btn-ghost" onClick={() => setPhase('captain')}>
            Back
          </button>
          <button
            className="btn-ghost"
            onClick={() => {
              setOrder(positionAssignment)
              setOrderError(null)
            }}
          >
            Reset order
          </button>
          <button className="btn-primary" disabled={!isValidOrder(order) || submitting} onClick={handleSubmit}>
            {submitting ? 'Sealing the XI…' : 'Begin simulation'}
          </button>
        </div>
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
                  const check = eligibility(picks, positionAssignment, p)
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
                          {' · '}Field {p.fielding.toFixed(0)} · Morale {p.morale.toFixed(0)} · #{p.position_min}-{p.position_max}
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
