import { getRarityStyle } from '../rarityTiers'
import { flagFor } from '../countryFlags'

export interface PlayerCardStat {
  label: string
  value: string | number
}

export interface PlayerCardProps {
  name: string
  role: string
  country: string
  era: number
  rating: number
  rarity: string
  credit: number
  stats: PlayerCardStat[]
  onClick?: () => void
  disabled?: boolean
  disabledReason?: string
  badge?: string
}

function initials(name: string): string {
  const parts = name.trim().split(/\s+/)
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase()
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
}

export default function PlayerCard({
  name,
  role,
  country,
  era,
  rating,
  rarity,
  credit,
  stats,
  onClick,
  disabled,
  disabledReason,
  badge,
}: PlayerCardProps) {
  const tier = getRarityStyle(rarity)
  const Tag = onClick ? 'button' : 'div'

  return (
    <Tag
      className={`player-card rarity-${rarity.toLowerCase()} ${tier.shimmer ? 'player-card-shimmer' : ''}`}
      onClick={onClick}
      disabled={onClick ? disabled : undefined}
      title={disabledReason}
      style={{
        background: tier.cardBg,
        borderColor: tier.cardBorder,
        color: tier.cardText,
        boxShadow: `0 0 18px ${tier.glow}, 0 6px 14px rgba(0,0,0,0.45)`,
      }}
    >
      <div className="player-card-top">
        <div className="player-card-rating">
          <span className="player-card-rating-num">{rating.toFixed(0)}</span>
          <span className="player-card-role">{role}</span>
        </div>
        <div className="player-card-flag" title={`${country} · ${era}`}>
          {flagFor(country)}
        </div>
      </div>

      <div className="player-card-avatar" style={{ borderColor: tier.cardBorder, color: tier.cardText }}>
        {initials(name)}
      </div>

      <div className="player-card-name" style={{ borderColor: tier.cardBorder }}>
        {name}
      </div>
      <div className="player-card-origin" style={{ color: tier.cardTextDim }}>
        {country} · {era}
      </div>

      <div className="player-card-stats" style={{ borderColor: tier.cardBorder }}>
        {stats.map((s) => (
          <div key={s.label} className="player-card-stat">
            <span className="player-card-stat-value">{s.value}</span>
            <span className="player-card-stat-label">{s.label}</span>
          </div>
        ))}
      </div>

      <div className="player-card-footer" style={{ borderColor: tier.cardBorder }}>
        <span className="player-card-rarity-tag">{tier.name}</span>
        <span className="player-card-credit">{credit.toFixed(1)} cr</span>
      </div>

      {badge && <div className="player-card-badge">{badge}</div>}
      {disabled && disabledReason && <div className="player-card-disabled-reason">{disabledReason}</div>}
    </Tag>
  )
}
