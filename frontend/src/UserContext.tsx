import { createContext, useContext, useState, useCallback, type ReactNode } from 'react'

const STORAGE_KEY = 'crickdraft_username'
const TOURNAMENT_KEY = 'crickdraft_tournament'

interface UserContextValue {
  username: string | null
  setUsername: (name: string | null) => void
  tournament: string
  setTournament: (slug: string) => void
}

const UserContext = createContext<UserContextValue>({
  username: null,
  setUsername: () => {},
  tournament: 'showdown-league',
  setTournament: () => {},
})

export function UserProvider({ children }: { children: ReactNode }) {
  const [username, setUsernameState] = useState<string | null>(() => localStorage.getItem(STORAGE_KEY))
  const [tournament, setTournamentState] = useState<string>(
    () => localStorage.getItem(TOURNAMENT_KEY) || 'showdown-league',
  )

  const setUsername = useCallback((name: string | null) => {
    if (name) localStorage.setItem(STORAGE_KEY, name)
    else localStorage.removeItem(STORAGE_KEY)
    setUsernameState(name)
  }, [])

  const setTournament = useCallback((slug: string) => {
    localStorage.setItem(TOURNAMENT_KEY, slug)
    setTournamentState(slug)
  }, [])

  return (
    <UserContext.Provider value={{ username, setUsername, tournament, setTournament }}>
      {children}
    </UserContext.Provider>
  )
}

export function useUser() {
  return useContext(UserContext)
}
