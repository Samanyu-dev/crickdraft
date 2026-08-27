import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'
import { useUser } from '../UserContext'
import type { Tournament } from '../types'

const FORMAT_LABEL: Record<string, string> = {
  T20: '20 overs a side',
  ODI: '50 overs a side',
  TEST: 'Two innings a side',
}

export default function Lobby() {
  const [tournaments, setTournaments] = useState<Tournament[] | null>(null)
  const navigate = useNavigate()
  const { setTournament } = useUser()

  useEffect(() => {
    api.getTournaments().then(setTournaments)
  }, [])

  return (
    <div>
      <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <span className="eyebrow" style={{ display: 'block', marginBottom: '0.5rem' }}>
          Choose your competition
        </span>
        <h1 style={{ fontSize: '2rem' }}>Pick a tournament</h1>
        <p className="subtitle" style={{ margin: '0 auto' }}>
          The squad pool and match format both depend on what you enter — pick before you draft.
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
              navigate(`/draft?tournament=${t.slug}`)
            }}
          >
            <div className={`tournament-format format-${t.format}`}>{t.format}</div>
            <h3>{t.name}</h3>
            <p>{t.tagline}</p>
            <div className="tournament-meta">{FORMAT_LABEL[t.format]}</div>
          </button>
        ))}
      </div>
    </div>
  )
}
