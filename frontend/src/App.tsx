import { useEffect, useState } from 'react'
import { Routes, Route, NavLink, Navigate, useLocation } from 'react-router-dom'
import { UserProvider, useUser } from './UserContext'
import { api } from './api'
import { soccerApi } from './soccer/api'
import RankBadge from './components/RankBadge'
import Home from './pages/Home'
import Sports from './pages/Sports'
import Lobby from './pages/Lobby'
import Draft from './pages/Draft'
import Team from './pages/Team'
import Leaderboard from './pages/Leaderboard'
import SoccerLobby from './soccer/SoccerLobby'
import SoccerDraft from './soccer/SoccerDraft'
import SoccerTeam from './soccer/SoccerTeam'
import SoccerLeaderboard from './soccer/SoccerLeaderboard'

function RequireUser({ children }: { children: React.ReactNode }) {
  const { username } = useUser()
  if (!username) return <Navigate to="/" replace />
  return <>{children}</>
}

function Shell() {
  const { username, setUsername, tournament, sport } = useUser()
  const location = useLocation()
  const [elo, setElo] = useState<number | null>(null)

  useEffect(() => {
    if (!username) {
      setElo(null)
      return
    }
    const client = sport === 'soccer' ? soccerApi : api
    client.getUser(username, tournament).then((u) => setElo(u.elo_rating))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [username, tournament, sport, location.pathname])

  const draftPath = sport === 'soccer' ? `/soccer/draft?tournament=${tournament}` : `/draft?tournament=${tournament}`
  const teamPath = sport === 'soccer' ? `/soccer/team?tournament=${tournament}` : `/team?tournament=${tournament}`
  const leaderboardPath =
    sport === 'soccer' ? `/soccer/leaderboard?tournament=${tournament}` : `/leaderboard?tournament=${tournament}`

  return (
    <div className="shell">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark">{sport === 'soccer' ? '⚽' : '🏏'}</span> CrickDraft
        </div>
        <nav>
          <NavLink to="/sports" className={({ isActive }) => (isActive ? 'active' : '')}>
            Sports
          </NavLink>
          <NavLink to={draftPath} className={({ isActive }) => (isActive ? 'active' : '')}>
            Draft
          </NavLink>
          <NavLink to={teamPath} className={({ isActive }) => (isActive ? 'active' : '')}>
            My XI
          </NavLink>
          <NavLink to={leaderboardPath} className={({ isActive }) => (isActive ? 'active' : '')}>
            Leaderboard
          </NavLink>
        </nav>
        <div className="user-chip">
          {username ? (
            <>
              {elo !== null && <RankBadge elo={elo} size="sm" />}
              <span>{username}</span>
              <button className="link-btn" onClick={() => setUsername(null)}>
                switch
              </button>
            </>
          ) : null}
        </div>
      </header>
      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route
            path="/sports"
            element={
              <RequireUser>
                <Sports />
              </RequireUser>
            }
          />
          <Route
            path="/lobby"
            element={
              <RequireUser>
                <Lobby />
              </RequireUser>
            }
          />
          <Route
            path="/draft"
            element={
              <RequireUser>
                <Draft />
              </RequireUser>
            }
          />
          <Route
            path="/team"
            element={
              <RequireUser>
                <Team />
              </RequireUser>
            }
          />
          <Route path="/leaderboard" element={<Leaderboard />} />
          <Route
            path="/soccer/lobby"
            element={
              <RequireUser>
                <SoccerLobby />
              </RequireUser>
            }
          />
          <Route
            path="/soccer/draft"
            element={
              <RequireUser>
                <SoccerDraft />
              </RequireUser>
            }
          />
          <Route
            path="/soccer/team"
            element={
              <RequireUser>
                <SoccerTeam />
              </RequireUser>
            }
          />
          <Route path="/soccer/leaderboard" element={<SoccerLeaderboard />} />
        </Routes>
      </main>
    </div>
  )
}

export default function App() {
  return (
    <UserProvider>
      <Shell />
    </UserProvider>
  )
}
