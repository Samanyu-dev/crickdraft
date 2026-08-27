import { Routes, Route, NavLink, Navigate } from 'react-router-dom'
import { UserProvider, useUser } from './UserContext'
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
