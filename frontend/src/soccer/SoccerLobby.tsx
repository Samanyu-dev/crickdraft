import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { soccerApi } from './api'
import { useUser } from '../UserContext'
import type { SoccerTournament } from './types'

export default function SoccerLobby() {
  const [tournaments, setTournaments] = useState<SoccerTournament[] | null>(null)
  const navigate = useNavigate()
  const { setTournament, setSport } = useUser()
  useEffect(() => setSport('soccer'), [setSport])

  useEffect(() => {
    soccerApi.getTournaments().then(setTournaments)
  }, [])

  return (
    <div>
      <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <span className="eyebrow" style={{ display: 'block', marginBottom: '0.5rem' }}>
          Choose your competition
        </span>
        <h1 style={{ fontSize: '2rem' }}>Pick a soccer tournament</h1>
        <p className="subtitle" style={{ margin: '0 auto' }}>
          Every match is 90 minutes, GK-DEF-MID-FWD. The squad pool depends on which tournament you enter.
        </p>
      </div>
      <div className="tournament-grid">
        {tournaments === null && <p className="muted">Loading tournaments…</p>}
        {tournaments?.map((t) => (
          <button
            key={t.slug}
            className="tournament-card"
            onClick={() => {
              setTournament(t.slug)
              navigate(`/soccer/draft?tournament=${t.slug}`)
            }}
          >
            <div className="tournament-format format-T20">SOCCER</div>
            <h3>{t.name}</h3>
            <p>{t.tagline}</p>
            <div className="tournament-meta">90 minutes a side</div>
          </button>
        ))}
      </div>
    </div>
  )
}
