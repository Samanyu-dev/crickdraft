export type SoccerRole = 'GK' | 'DEF' | 'MID' | 'FWD'

export interface SoccerPlayer {
  id: number
  name: string
  country: string
  era: number
  squad_name: string
  role: SoccerRole
  attack: number
  defense: number
  passing: number
  pace: number
  morale: number
  rating: number
  credit: number
}

export interface SoccerSquad {
  key: string
  country: string
  era: number
  squad_name: string
  players: SoccerPlayer[]
}

export interface SoccerTournament {
  slug: string
  name: string
  tagline: string
  era_min: number | null
  era_max: number | null
}

export interface SoccerDraftDetail {
  id: number
  user_id: number
  tournament: string
  name: string
  captain_id: number | null
  players: SoccerPlayer[]
}

export interface SoccerUser {
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

export interface SoccerPlayerPerformance {
  id: number
  name: string
  role: SoccerRole
  goals: number
  points: number
  captain: boolean
}

export interface SoccerMatchEvent {
  minute: number
  side: 'team' | 'opponent'
  event: 'goal' | 'chance' | 'quiet'
  scorer: string | null
  score_team: number
  score_opponent: number
}

export interface SoccerMatchResult {
  username: string
  tournament: string
  result: 'W' | 'L' | 'D'
  opponent_name: string
  opponent_rating: number
  team_goals: number
  opponent_goals: number
  timeline: SoccerMatchEvent[]
  scorecard: { team: SoccerPlayerPerformance[]; opponent: SoccerPlayerPerformance[] }
  elo_before: number
  elo_after: number
  elo_delta: number
  totals: { elo_rating: number; matches_played: number; wins: number; losses: number; draws: number }
  matches_today: number
  matches_remaining_today: number
}

export interface SoccerHistoryEntry {
  opponent_name: string
  opponent_rating: number
  result: 'W' | 'L' | 'D'
  team_goals: number
  opponent_goals: number
  elo_before: number
  elo_after: number
  elo_delta: number
  scorecard: { team: SoccerPlayerPerformance[]; opponent: SoccerPlayerPerformance[] }
  played_at?: string
}

export interface SoccerLeaderboardEntry {
  username: string
  elo_rating: number
  matches_played: number
  wins: number
  losses: number
  draws: number
  win_pct: number
}
