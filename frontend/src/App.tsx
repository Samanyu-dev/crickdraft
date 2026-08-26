import { Routes, Route, NavLink, Navigate } from 'react-router-dom'
import { UserProvider, useUser } from './UserContext'
import Home from './pages/Home'
import Draft from './pages/Draft'
import Team from './pages/Team'
import Leaderboard from './pages/Leaderboard'

function RequireUser({ children }: { children: React.ReactNode }) {
  const { username } = useUser()
  if (!username) return <Navigate to="/" replace />
  return <>{children}</>
}

function Shell() {
  const { username, setUsername } = useUser()
  return (
    <div className="shell">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark">🏏</span> CrickDraft
        </div>
        <nav>
          <NavLink to="/draft" className={({ isActive }) => (isActive ? 'active' : '')}>
            Draft
          </NavLink>
          <NavLink to="/team" className={({ isActive }) => (isActive ? 'active' : '')}>
            My XI
          </NavLink>
          <NavLink to="/leaderboard" className={({ isActive }) => (isActive ? 'active' : '')}>
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
