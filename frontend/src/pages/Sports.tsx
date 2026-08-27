import { useNavigate } from 'react-router-dom'
import { useUser } from '../UserContext'

const SPORTS = [
  { key: 'cricket' as const, name: 'Cricket', tagline: 'Roll country+year squads, draft a batting order, simulate ball by ball.', path: '/lobby', emoji: '🏏' },
  { key: 'soccer' as const, name: 'Soccer', tagline: 'Draft a GK-DEF-MID-FWD XI from historic sides, simulate 90 minutes.', path: '/soccer/lobby', emoji: '⚽' },
]

export default function Sports() {
  const navigate = useNavigate()
  const { setSport } = useUser()

  return (
    <div>
      <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <span className="eyebrow" style={{ display: 'block', marginBottom: '0.5rem' }}>
          Choose your sport
        </span>
        <h1 style={{ fontSize: '2rem' }}>What are you drafting today?</h1>
      </div>
      <div className="tournament-grid" style={{ maxWidth: 680 }}>
        {SPORTS.map((s) => (
          <button
            key={s.key}
            className="tournament-card"
            onClick={() => {
              setSport(s.key)
              navigate(s.path)
            }}
          >
            <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>{s.emoji}</div>
            <h3>{s.name}</h3>
            <p>{s.tagline}</p>
          </button>
        ))}
      </div>
    </div>
  )
}
