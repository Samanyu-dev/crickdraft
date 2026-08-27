import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useUser } from '../UserContext'
import { api } from '../api'

export default function Home() {
  const { username, setUsername } = useUser()
  const [value, setValue] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  if (username) {
    navigate('/draft', { replace: true })
    return null
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    const name = value.trim()
    if (!/^[A-Za-z0-9_]{3,20}$/.test(name)) {
      setError('3-20 characters: letters, numbers, underscore only.')
      return
    }
    setLoading(true)
    try {
      await api.createUser(name)
      setUsername(name)
      navigate('/draft')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="hero">
      <div className="hero-copy">
        <span className="eyebrow">Est. today · Pavilion XI</span>
        <h1>
          Roll the archives.
          <br />
          <em>Draft your legends.</em>
        </h1>
        <p className="subtitle">
          Every pick is a roll of a country and a year — India '83, Australia '99, Sri Lanka '96 — pick
          one name off the board, then roll again. Eleven picks, two rerolls, one XI worth putting your
          name on.
        </p>
        <form onSubmit={handleSubmit} className="username-form">
          <input
            value={value}
            onChange={(e) => setValue(e.target.value)}
            placeholder="sign the ledger..."
            maxLength={20}
            autoFocus
          />
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? 'Entering...' : 'Enter the pavilion'}
          </button>
        </form>
        {error && <p className="error">{error}</p>}
        <p className="hint">No password — your name on the ledger is your name on the leaderboard.</p>
      </div>

      <div className="plaque-preview">
        <div className="plaque-title">India · 1983 World Cup Winners</div>
        <div className="plaque-row">
          <span>Kapeel Dev</span>
          <span>AR · 8.5 cr</span>
        </div>
        <div className="plaque-row">
          <span>Sunil Gavaskaar</span>
          <span>BAT · 8.0 cr</span>
        </div>
        <div className="plaque-row">
          <span>Syed Kirmanii</span>
          <span>WK · 7.0 cr</span>
        </div>
      </div>
    </div>
  )
}
