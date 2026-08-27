export type Role = 'BAT' | 'BOWL' | 'AR' | 'WK'

export interface Player {
  id: number
  name: string
  country: string
  era: number
  squad_name: string
  role: Role
  batting: { avg: number; sr: number } | null
  bowling: { avg: number; econ: number; sr: number } | null
  rating: number
  credit: number
  consistency: number
}

export interface Squad {
  key: string
  country: string
  era: number
  squad_name: string
  players: Player[]
}

export interface DraftDetail {
  id: number
  user_id: number
  name: string
  captain_id: number | null
  players: Player[]
}

export interface User {
  id: number
  username: string
  total_points: number
  matches_played: number
  wins: number
  losses: number
}

export interface PlayerPerformance {
  id: number
  name: string
  role: Role
  runs: number
  wickets: number
  points: number
  captain: boolean
}

export interface MatchResult {
  opponent_name: string
  team_score: number
  opponent_score: number
  result: 'W' | 'L'
  scorecard: { team: PlayerPerformance[]; opponent: PlayerPerformance[] }
}

export interface SimulateResponse {
  username: string
  rounds: number
  results: MatchResult[]
  totals: { total_points: number; matches_played: number; wins: number; losses: number }
}

export interface LeaderboardEntry {
  username: string
  total_points: number
  matches_played: number
  wins: number
  losses: number
  win_pct: number
}
