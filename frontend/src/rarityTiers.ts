export interface RarityTier {
  name: string
  color: string
  glow: string
  cardBg: string
  cardBorder: string
  cardText: string
  cardTextDim: string
  shimmer?: boolean
}

// Mirrors backend rarity_for() thresholds in gen_players.py (both sports) -
// keep the names/order in sync if those thresholds ever change.
export const RARITY_STYLE: Record<string, RarityTier> = {
  Common: {
    name: 'Common',
    color: '#b08d5c',
    glow: 'rgba(176,141,92,0.3)',
    cardBg: 'linear-gradient(160deg, #8a6539 0%, #55391d 55%, #3c2712 100%)',
    cardBorder: '#c9a05f',
    cardText: '#f6ead4',
    cardTextDim: 'rgba(246,234,212,0.7)',
  },
  Uncommon: {
    name: 'Uncommon',
    color: '#aab4bd',
    glow: 'rgba(170,180,189,0.35)',
    cardBg: 'linear-gradient(160deg, #c3cad1 0%, #838d97 55%, #565f68 100%)',
    cardBorder: '#e4e9ed',
    cardText: '#1c2126',
    cardTextDim: 'rgba(28,33,38,0.68)',
  },
  Rare: {
    name: 'Rare',
    color: '#5aa9c9',
    glow: 'rgba(90,169,201,0.4)',
    cardBg: 'linear-gradient(160deg, #4f9fd6 0%, #235f8c 55%, #123650 100%)',
    cardBorder: '#8fd3f4',
    cardText: '#f2fbff',
    cardTextDim: 'rgba(242,251,255,0.72)',
  },
  Epic: {
    name: 'Epic',
    color: '#a37fd6',
    glow: 'rgba(163,127,214,0.45)',
    cardBg: 'linear-gradient(160deg, #8b5fd1 0%, #4d2f8a 55%, #2c1a54 100%)',
    cardBorder: '#d4b6ff',
    cardText: '#f9f4ff',
    cardTextDim: 'rgba(249,244,255,0.72)',
  },
  Legendary: {
    name: 'Legendary',
    color: '#e0a83a',
    glow: 'rgba(224,168,58,0.55)',
    cardBg: 'linear-gradient(160deg, #ffdd88 0%, #d9a832 45%, #93650f 100%)',
    cardBorder: '#fff1c4',
    cardText: '#3a2405',
    cardTextDim: 'rgba(58,36,5,0.72)',
  },
  Legend: {
    name: 'Legend',
    color: '#ff9ec4',
    glow: 'rgba(255,158,196,0.7)',
    cardBg: 'linear-gradient(160deg, #fff9f0 0%, #ffd3e8 45%, #ffb6d8 75%, #f7c9ff 100%)',
    cardBorder: '#ffffff',
    cardText: '#5a1440',
    cardTextDim: 'rgba(90,20,64,0.75)',
    shimmer: true,
  },
}

export function getRarityStyle(rarity: string): RarityTier {
  return RARITY_STYLE[rarity] || RARITY_STYLE.Common
}
