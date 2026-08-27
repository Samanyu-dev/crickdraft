import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { soccerApi } from './api'
import type { SoccerLeaderboardEntry, SoccerTournament } from './types'
import { useUser } from '../UserContext'
import RankBadge from '../components/RankBadge'

export default function SoccerLeaderboard() {
  const { username, tournament: currentTournament, setTournament, setSport } = useUser()
  useEffect(() => setSport('soccer'), [setSport])
  const [searchParams, setSearchParams] = useSearchParams()
  const tournament = searchParams.get('tournament') || currentTournament

  const [tournaments, setTournaments] = useState<SoccerTournament[] | null>(null)
  const [entries, setEntries] = useState<SoccerLeaderboardEntry[] | null>(null)

  useEffect(() => {
    soccerApi.getTournaments().then(setTournaments)
  }, [])

  useEffect(() => {
    setEntries(null)
    soccerApi.getLeaderboard(tournament).then(setEntries)
  }, [tournament])

  function selectTournament(slug: string) {
    setTournament(slug)
    setSearchParams({ tournament: slug })
  }

  const activeName = tournaments?.find((t) => t.slug === tournament)?.name || tournament.replace(/-/g, ' ')

  return (
    <div>
      {tournaments && (
        <div className="tournament-tabs">
          {tournaments.map((t) => (
            <button
              key={t.slug}
              className={`tournament-tab ${t.slug === tournament ? 'active' : ''}`}
              onClick={() => selectTournament(t.slug)}
            >
              {t.name}
            </button>
          ))}
        </div>
      )}
      <div className="leaderboard-board">
        <h2>Honours Board</h2>
        <div className="board-sub">{activeName} · ranked by Elo rating</div>
        {entries === null ? (
          <p className="muted">Loading the honours board...</p>
        ) : entries.length === 0 ? (
          <p className="muted" style={{ textAlign: 'center' }}>
            No names carved yet. Draft an XI in this tournament and play a match to be the first.
          </p>
        ) : (
          entries.map((e, i) => (
            <div key={e.username} className={`board-row ${e.username === username ? 'me' : ''}`}>
              <span className={`rank ${i < 3 ? 'gold' : ''}`}>{i + 1}</span>
              <span className="name">{e.username}</span>
              <RankBadge elo={e.elo_rating} size="sm" />
              <span className="points">{e.elo_rating.toFixed(0)} elo</span>
              <span className="matches">{e.matches_played}m</span>
              <span className="wl">
                {e.wins}-{e.losses}
                {e.draws > 0 ? `-${e.draws}` : ''} · {e.win_pct.toFixed(0)}%
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
