import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'
import { useUser } from '../UserContext'
import PlayerCard from '../components/PlayerCard'
import type { Player, Role } from '../types'

const ROLE_RULES: Record<Role, [number, number]> = {
  WK: [1, 2],
  BAT: [3, 6],
  BOWL: [3, 6],
  AR: [0, 4],
}
const SQUAD_SIZE = 11
const CREDIT_CAP = 100

export default function Draft() {
  const { username } = useUser()
  const navigate = useNavigate()
  const [players, setPlayers] = useState<Player[]>([])
  const [countries, setCountries] = useState<string[]>([])
  const [country, setCountry] = useState('')
  const [role, setRole] = useState('')
  const [search, setSearch] = useState('')
  const [squad, setSquad] = useState<Player[]>([])
  const [captainId, setCaptainId] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    api.getMeta().then((m) => setCountries(m.countries))
  }, [])

  useEffect(() => {
    api.getPlayers({ country: country || undefined, role: role || undefined, search: search || undefined }).then(setPlayers)
  }, [country, role, search])

  const roleCounts = useMemo(() => {
    const counts: Record<Role, number> = { WK: 0, BAT: 0, BOWL: 0, AR: 0 }
    squad.forEach((p) => counts[p.role]++)
    return counts
  }, [squad])

  const totalCredits = useMemo(() => squad.reduce((sum, p) => sum + p.credit, 0), [squad])

  function toggle(player: Player) {
    setError(null)
    const already = squad.some((p) => p.id === player.id)
    if (already) {
      setSquad(squad.filter((p) => p.id !== player.id))
      if (captainId === player.id) setCaptainId(null)
      return
    }
    if (squad.length >= SQUAD_SIZE) {
      setError(`Your XI is already full (${SQUAD_SIZE} players).`)
      return
    }
    const [, max] = ROLE_RULES[player.role]
    if (roleCounts[player.role] >= max) {
      setError(`You can only pick up to ${max} ${player.role} players.`)
      return
    }
    if (totalCredits + player.credit > CREDIT_CAP) {
      setError(`Adding ${player.name} would exceed the ${CREDIT_CAP} credit budget.`)
      return
    }
    setSquad([...squad, player])
  }

  const roleStatus = (r: Role) => {
    const [min, max] = ROLE_RULES[r]
    const count = roleCounts[r]
    const ok = count >= min && count <= max
    return { min, max, count, ok }
  }

  const canSubmit =
    squad.length === SQUAD_SIZE &&
    (Object.keys(ROLE_RULES) as Role[]).every((r) => roleStatus(r).ok) &&
    totalCredits <= CREDIT_CAP &&
    captainId !== null

  async function handleSubmit() {
    if (!username || !canSubmit) return
    setSubmitting(true)
    setError(null)
    try {
      await api.submitDraft({
        username,
        name: `${username}'s XI`,
        player_ids: squad.map((p) => p.id),
        captain_id: captainId,
      })
      navigate('/team')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not save draft')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="draft-layout">
      <div className="draft-pool">
        <div className="filters">
          <input placeholder="Search players..." value={search} onChange={(e) => setSearch(e.target.value)} />
          <select value={country} onChange={(e) => setCountry(e.target.value)}>
            <option value="">All countries</option>
            {countries.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
          <select value={role} onChange={(e) => setRole(e.target.value)}>
            <option value="">All roles</option>
            <option value="BAT">Batters</option>
            <option value="BOWL">Bowlers</option>
            <option value="AR">All-rounders</option>
            <option value="WK">Wicketkeepers</option>
          </select>
        </div>
        <div className="player-grid">
          {players.map((p) => (
            <PlayerCard key={p.id} player={p} selected={squad.some((s) => s.id === p.id)} onToggle={() => toggle(p)} />
          ))}
        </div>
      </div>

      <aside className="squad-panel">
        <h2>
          Your XI <span className="squad-count">{squad.length}/{SQUAD_SIZE}</span>
        </h2>
        <div className="credit-bar">
          <div
            className="credit-fill"
            style={{ width: `${Math.min(100, (totalCredits / CREDIT_CAP) * 100)}%` }}
          />
        </div>
        <p className="credit-text">
          {totalCredits.toFixed(1)} / {CREDIT_CAP} credits
        </p>
        <ul className="role-checklist">
          {(Object.keys(ROLE_RULES) as Role[]).map((r) => {
            const s = roleStatus(r)
            return (
              <li key={r} className={s.ok ? 'ok' : ''}>
                {r}: {s.count} <span>(need {s.min}-{s.max})</span>
              </li>
            )
          })}
        </ul>

        <div className="squad-list">
          {squad.map((p) => (
            <div key={p.id} className="squad-row">
              <span>{p.name}</span>
              <button
                className={`btn-captain small ${captainId === p.id ? 'is-captain' : ''}`}
                onClick={() => setCaptainId(p.id)}
              >
                {captainId === p.id ? '★' : 'C'}
              </button>
              <button className="btn-remove small" onClick={() => toggle(p)}>
                ✕
              </button>
            </div>
          ))}
          {squad.length === 0 && <p className="muted">Add players from the left to build your XI.</p>}
        </div>

        {error && <p className="error">{error}</p>}
        {!captainId && squad.length === SQUAD_SIZE && <p className="hint">Pick a captain (2x points) before saving.</p>}

        <button className="btn-primary" disabled={!canSubmit || submitting} onClick={handleSubmit}>
          {submitting ? 'Saving...' : 'Save my XI'}
        </button>
      </aside>
    </div>
  )
}
