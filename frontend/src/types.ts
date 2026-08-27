export type Role = 'BAT' | 'BOWL' | 'AR' | 'WK'
export type Format = 'T20' | 'ODI' | 'TEST'

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
  rarity: string
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

export interface Tournament {
  slug: string
  name: string
  tagline: string
  format: Format
  overs: number
  innings_per_side: number
  era_min: number | null
  era_max: number | null
}

export interface DraftDetail {
  id: number
  user_id: number
  tournament: string
  name: string
  captain_id: number | null
  players: Player[]
}

export interface User {
  id: number
  username: string
  tournament: string
  elo_rating: number
  matches_played: number
  wins: number
  losses: number
  draws: number
  matches_today: number
  matches_remaining_today: number
  rank: number | null
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

export interface InningsResult {
  side: 'team' | 'opponent'
  seq: number
  score: number
  wickets: number
  overs: number
  timeline: OverEvent[]
}

export interface MatchResult {
  username: string
  tournament: string
  format: Format
  result: 'W' | 'L' | 'D'
  opponent_name: string
  opponent_rating: number
  team_total: number
  opponent_total: number
  innings: InningsResult[]
  scorecard: { team: PlayerPerformance[]; opponent: PlayerPerformance[] }
  elo_before: number
  elo_after: number
  elo_delta: number
  totals: { elo_rating: number; matches_played: number; wins: number; losses: number; draws: number }
  matches_today: number
  matches_remaining_today: number
}

export interface HistoryEntry {
  opponent_name: string
  opponent_rating: number
  result: 'W' | 'L' | 'D'
  team_total: number
  opponent_total: number
  elo_before: number
  elo_after: number
  elo_delta: number
  scorecard: { team: PlayerPerformance[]; opponent: PlayerPerformance[] }
  played_at?: string
}

export interface LeaderboardEntry {
  username: string
  elo_rating: number
  matches_played: number
  wins: number
  losses: number
  draws: number
  win_pct: number
}
