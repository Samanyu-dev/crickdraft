import { getRank } from '../rankTiers'

export default function RankBadge({ elo, size = 'md' }: { elo: number; size?: 'sm' | 'md' | 'lg' }) {
  const rank = getRank(elo)
  return (
    <span
      className={`rank-badge rank-badge-${size}`}
      style={{
        color: rank.color,
        borderColor: rank.color,
        boxShadow: `0 0 16px ${rank.glow}`,
      }}
    >
      {rank.name}
    </span>
  )
}
