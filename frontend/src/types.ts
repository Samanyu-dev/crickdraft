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
  fielding: number
  morale: number
  rating: number
  credit: number
  consistency: number
  position_min: number
  position_max: number
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
  elo_rating: number
  matches_played: number
  wins: number
  losses: number
  matches_today: number
  matches_remaining_today: number
}

export interface PlayerPerformance {
  id: number
  name: string
  role: Role
  runs: number
  balls: number
  how_out: string
  wickets: number
  overs?: number
  runs_conceded?: number
  points: number
  captain: boolean
}

export interface OverEvent {
  over: number
  bowler: string
  balls: string[]
  score: number
  wickets: number
}

export interface MatchResult {
  username: string
  result: 'W' | 'L'
  opponent_name: string
  opponent_rating: number
  team_score: number
  opponent_score: number
  team_wickets: number
  opponent_wickets: number
  team_overs: number
  opponent_overs: number
  team_timeline: OverEvent[]
  opponent_timeline: OverEvent[]
  scorecard: { team: PlayerPerformance[]; opponent: PlayerPerformance[] }
  elo_before: number
  elo_after: number
  elo_delta: number
  totals: { elo_rating: number; matches_played: number; wins: number; losses: number }
  matches_today: number
  matches_remaining_today: number
}

export interface LeaderboardEntry {
  username: string
  elo_rating: number
  matches_played: number
  wins: number
  losses: number
  win_pct: number
}
