import { useEffect, useState } from 'react'
import { Routes, Route, NavLink, Navigate, useLocation } from 'react-router-dom'
import { UserProvider, useUser } from './UserContext'
import { api } from './api'
import RankBadge from './components/RankBadge'
import Home from './pages/Home'
import Lobby from './pages/Lobby'
import Draft from './pages/Draft'
import Team from './pages/Team'
import Leaderboard from './pages/Leaderboard'

function RequireUser({ children }: { children: React.ReactNode }) {
  const { username } = useUser()
  if (!username) return <Navigate to="/" replace />
  return <>{children}</>
}

function Shell() {
  const { username, setUsername, tournament } = useUser()
  const location = useLocation()
  const [elo, setElo] = useState<number | null>(null)

  useEffect(() => {
    if (!username) {
      setElo(null)
      return
    }
    api.getUser(username, tournament).then((u) => setElo(u.elo_rating))
    // re-check whenever the route changes, so a badge going stale after
    // playing a match on the Team page catches up once you navigate away
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [username, tournament, location.pathname])

  return (
    <div className="shell">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark">🏏</span> CrickDraft
        </div>
        <nav>
          <NavLink to="/lobby" className={({ isActive }) => (isActive ? 'active' : '')}>
            Tournaments
          </NavLink>
          <NavLink to={`/draft?tournament=${tournament}`} className={({ isActive }) => (isActive ? 'active' : '')}>
            Draft
          </NavLink>
          <NavLink to={`/team?tournament=${tournament}`} className={({ isActive }) => (isActive ? 'active' : '')}>
            My XI
          </NavLink>
          <NavLink
            to={`/leaderboard?tournament=${tournament}`}
            className={({ isActive }) => (isActive ? 'active' : '')}
          >
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
