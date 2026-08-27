import type { Player, DraftDetail, User, MatchResult, LeaderboardEntry, Squad } from './types'

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
  rollSquad: (excludeKeys: string[]) => {
    const qs = excludeKeys.length ? `?exclude=${encodeURIComponent(excludeKeys.join(','))}` : ''
    return req<Squad>(`/draft/roll${qs}`)
  },
  createUser: (username: string) => req<User>('/users', { method: 'POST', body: JSON.stringify({ username }) }),
  getUser: (username: string) => req<User>(`/users/${username}`),
  submitDraft: (payload: { username: string; name: string; player_ids: number[]; captain_id: number | null }) =>
    req<{ id: number }>('/drafts', { method: 'POST', body: JSON.stringify(payload) }),
  getDraft: (username: string) => req<DraftDetail | null>(`/drafts/${username}`),
  simulate: (draft_id: number) => req<MatchResult>('/simulate', { method: 'POST', body: JSON.stringify({ draft_id }) }),
  getLeaderboard: () => req<LeaderboardEntry[]>('/leaderboard'),
}
