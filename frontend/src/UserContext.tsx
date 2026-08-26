import { createContext, useContext, useState, useCallback, type ReactNode } from 'react'

const STORAGE_KEY = 'crickdraft_username'

interface UserContextValue {
  username: string | null
  setUsername: (name: string | null) => void
}

const UserContext = createContext<UserContextValue>({ username: null, setUsername: () => {} })

export function UserProvider({ children }: { children: ReactNode }) {
  const [username, setUsernameState] = useState<string | null>(() => localStorage.getItem(STORAGE_KEY))

  const setUsername = useCallback((name: string | null) => {
    if (name) localStorage.setItem(STORAGE_KEY, name)
    else localStorage.removeItem(STORAGE_KEY)
    setUsernameState(name)
  }, [])

  return <UserContext.Provider value={{ username, setUsername }}>{children}</UserContext.Provider>
}

export function useUser() {
  return useContext(UserContext)
}
