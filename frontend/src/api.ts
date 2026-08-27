import type { Player, DraftDetail, User, MatchResult, LeaderboardEntry, Squad, Tournament, HistoryEntry } from './types'

async function req<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`/api${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || `Request failed: ${res.status}`)
  }
  if (res.status === 204) return undefined as unknown as T
  return res.json()
}

export const api = {
  getPlayers: (params: { country?: string; role?: string; search?: string } = {}) => {
    const qs = new URLSearchParams(Object.entries(params).filter(([, v]) => v) as [string, string][])
    const suffix = qs.toString() ? `?${qs.toString()}` : ''
    return req<Player[]>(`/players${suffix}`)
  },
  getMeta: () => req<{ countries: string[]; roles: string[]; eras: number[]; count: number }>('/players/meta'),
  getTournaments: () => req<Tournament[]>('/tournaments'),
  rollSquad: (tournament: string, excludeKeys: string[]) => {
    const params = new URLSearchParams({ tournament })
    if (excludeKeys.length) params.set('exclude', excludeKeys.join(','))
    return req<Squad>(`/draft/roll?${params.toString()}`)
  },
  // Full squad+player data for the whole tournament pool, fetched once so
  // rolling/rerolling can happen entirely in memory (no per-attempt
  // round-trip - a constrained squad pool could otherwise need many
  // sequential retries to find a squad with an eligible pick).
  getSquadPool: (tournament: string) => req<Squad[]>(`/draft/squads?tournament=${tournament}`),
  createUser: (username: string) => req<User>('/users', { method: 'POST', body: JSON.stringify({ username }) }),
  getUser: (username: string, tournament?: string) =>
    req<User>(`/users/${username}${tournament ? `?tournament=${tournament}` : ''}`),
  submitDraft: (payload: {
    username: string
    name: string
    player_ids: number[]
    captain_id: number | null
    tournament: string
  }) => req<{ id: number }>('/drafts', { method: 'POST', body: JSON.stringify(payload) }),
  getDraft: (username: string, tournament: string) =>
    req<DraftDetail | null>(`/drafts/${username}?tournament=${tournament}`),
  simulate: (draft_id: number) => req<MatchResult>('/simulate', { method: 'POST', body: JSON.stringify({ draft_id }) }),
  getLeaderboard: (tournament: string) => req<LeaderboardEntry[]>(`/leaderboard?tournament=${tournament}`),
  getMatchHistory: (username: string, tournament: string) =>
    req<HistoryEntry[]>(`/matches/${username}?tournament=${tournament}`),
}
