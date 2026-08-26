import type { Player } from '../types'

const ROLE_LABEL: Record<string, string> = { BAT: 'Batter', BOWL: 'Bowler', AR: 'All-rounder', WK: 'Wicketkeeper' }

export default function PlayerCard({
  player,
  selected,
  onToggle,
  disabled,
  isCaptain,
  onMakeCaptain,
}: {
  player: Player
  selected: boolean
  onToggle: () => void
  disabled?: boolean
  isCaptain?: boolean
  onMakeCaptain?: () => void
}) {
  return (
    <div className={`player-card role-${player.role} ${selected ? 'selected' : ''}`}>
      <div className="player-card-top">
        <span className={`role-badge role-${player.role}`}>{player.role}</span>
        <span className="credit">{player.credit.toFixed(1)} cr</span>
      </div>
      <div className="player-name">{player.name}</div>
      <div className="player-meta">
        {player.country} &middot; {player.era}
      </div>
      <div className="player-stats">
        {player.batting && (
          <span>
            Bat {player.batting.avg.toFixed(1)} avg / {player.batting.sr.toFixed(0)} SR
          </span>
        )}
        {player.bowling && (
          <span>
            Bowl {player.bowling.avg.toFixed(1)} avg / {player.bowling.econ.toFixed(1)} econ
          </span>
        )}
      </div>
      <div className="player-card-actions">
        <button
          className={selected ? 'btn-remove' : 'btn-add'}
          onClick={onToggle}
          disabled={disabled && !selected}
          title={ROLE_LABEL[player.role]}
        >
          {selected ? 'Remove' : 'Add'}
        </button>
        {selected && onMakeCaptain && (
          <button className={`btn-captain ${isCaptain ? 'is-captain' : ''}`} onClick={onMakeCaptain}>
            {isCaptain ? '★ Captain' : 'Make captain'}
          </button>
        )}
      </div>
    </div>
  )
}
