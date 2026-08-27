export interface RankTier {
  name: string
  color: string
  glow: string
  min: number
}

// Cricket's own ladder: village maidan up through international legend.
export const RANK_TIERS: RankTier[] = [
  { name: 'Maidan', min: 0, color: '#9c8a63', glow: 'rgba(156,138,99,0.35)' },
  { name: 'Club', min: 1000, color: '#7fb069', glow: 'rgba(127,176,105,0.35)' },
  { name: 'District', min: 1150, color: '#5aa9c9', glow: 'rgba(90,169,201,0.35)' },
  { name: 'State', min: 1300, color: '#a37fd6', glow: 'rgba(163,127,214,0.35)' },
  { name: 'National', min: 1450, color: '#e0a83a', glow: 'rgba(224,168,58,0.4)' },
  { name: 'International', min: 1600, color: '#e0537a', glow: 'rgba(224,83,122,0.4)' },
  { name: 'Legend', min: 1800, color: '#e8c877', glow: 'rgba(232,200,119,0.55)' },
]

export function getRank(elo: number): RankTier {
  let current = RANK_TIERS[0]
  for (const t of RANK_TIERS) {
    if (elo >= t.min) current = t
  }
  return current
}
