import type { Player } from './types'
import type { SoccerPlayer } from './soccer/types'
import type { PlayerCardStat } from './components/PlayerCard'

export function cricketCardStats(p: Player): PlayerCardStat[] {
  return [
    { label: 'BAT AVG', value: p.batting ? p.batting.avg.toFixed(0) : '-' },
    { label: 'BAT SR', value: p.batting ? p.batting.sr.toFixed(0) : '-' },
    { label: 'BOWL AVG', value: p.bowling ? p.bowling.avg.toFixed(0) : '-' },
    { label: 'ECON', value: p.bowling ? p.bowling.econ.toFixed(1) : '-' },
    { label: 'FIELD', value: p.fielding.toFixed(0) },
    { label: 'MORALE', value: p.morale.toFixed(0) },
  ]
}

export function soccerCardStats(p: SoccerPlayer): PlayerCardStat[] {
  return [
    { label: 'ATK', value: p.attack.toFixed(0) },
    { label: 'DEF', value: p.defense.toFixed(0) },
    { label: 'PAS', value: p.passing.toFixed(0) },
    { label: 'PAC', value: p.pace.toFixed(0) },
    { label: 'MOR', value: p.morale.toFixed(0) },
    { label: 'RTG', value: p.rating.toFixed(0) },
  ]
}
