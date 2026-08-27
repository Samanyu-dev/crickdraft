import type {
  SoccerPlayer,
  SoccerSquad,
  SoccerTournament,
  SoccerDraftDetail,
  SoccerUser,
  SoccerMatchResult,
  SoccerHistoryEntry,
  SoccerLeaderboardEntry,
} from './types'

async function req<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`/api/soccer${path}`, {
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

export const soccerApi = {
  getTournaments: () => req<SoccerTournament[]>('/tournaments'),
  rollSquad: (tournament: string, excludeKeys: string[]) => {
    const params = new URLSearchParams({ tournament })
    if (excludeKeys.length) params.set('exclude', excludeKeys.join(','))
    return req<SoccerSquad>(`/draft/roll?${params.toString()}`)
  },
  createUser: (username: string) => req<SoccerUser>('/users', { method: 'POST', body: JSON.stringify({ username }) }),
  getUser: (username: string, tournament?: string) =>
    req<SoccerUser>(`/users/${username}${tournament ? `?tournament=${tournament}` : ''}`),
  submitDraft: (payload: {
    username: string
    name: string
    player_ids: number[]
    captain_id: number | null
    tournament: string
  }) => req<{ id: number }>('/drafts', { method: 'POST', body: JSON.stringify(payload) }),
  getDraft: (username: string, tournament: string) =>
    req<SoccerDraftDetail | null>(`/drafts/${username}?tournament=${tournament}`),
  simulate: (draft_id: number) =>
    req<SoccerMatchResult>('/simulate', { method: 'POST', body: JSON.stringify({ draft_id }) }),
  getLeaderboard: (tournament: string) => req<SoccerLeaderboardEntry[]>(`/leaderboard?tournament=${tournament}`),
  getMatchHistory: (username: string, tournament: string) =>
    req<SoccerHistoryEntry[]>(`/matches/${username}?tournament=${tournament}`),
}

export type { SoccerPlayer }
