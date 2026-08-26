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
      <h1>Draft your all-time XI.</h1>
      <p className="subtitle">
        Pick 11 players from cricket's greatest eras — any country, any year, one credit budget.
        Then run simulated matches and climb the global leaderboard.
      </p>
      <form onSubmit={handleSubmit} className="username-form">
        <input
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="Choose a username"
          maxLength={20}
          autoFocus
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Entering...' : 'Enter the draft room'}
        </button>
      </form>
      {error && <p className="error">{error}</p>}
      <p className="hint">No password needed — your username is your identity on the leaderboard.</p>
    </div>
  )
}
