const FLAGS: Record<string, string> = {
  India: '🇮🇳',
  Australia: '🇦🇺',
  'West Indies': '🏝️',
  England: '🏴',
  Pakistan: '🇵🇰',
  'South Africa': '🇿🇦',
  'Sri Lanka': '🇱🇰',
  'New Zealand': '🇳🇿',
  Zimbabwe: '🇿🇼',
  Bangladesh: '🇧🇩',
  Afghanistan: '🇦🇫',
  Brazil: '🇧🇷',
  Argentina: '🇦🇷',
  Germany: '🇩🇪',
  France: '🇫🇷',
  Spain: '🇪🇸',
  Italy: '🇮🇹',
  Netherlands: '🇳🇱',
  Uruguay: '🇺🇾',
  Portugal: '🇵🇹',
  Croatia: '🇭🇷',
  Belgium: '🇧🇪',
  Hungary: '🇭🇺',
  Colombia: '🇨🇴',
  Nigeria: '🇳🇬',
  'South Korea': '🇰🇷',
  Ghana: '🇬🇭',
}

export function flagFor(country: string): string {
  return FLAGS[country] || '🏳️'
}
