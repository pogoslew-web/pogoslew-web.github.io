const TIERS: Record<string, string> = {
  EX: 'ex', 'S+': 'splus', S: 's', A: 'a', B: 'b', C: 'c', D: 'd', E: 'e', 'SP (exclusive)': 'sp', Nation: 'ex',
  Mythical: 'mythic', Mythic: 'mythic', Legendary: 'legendary', Epic: 'epic', Rare: 'rare', Limited: 'limited',
  Extreme: 'extreme', Hard: 'hard', Normal: 'normal', Easy: 'easy', Common: 'normal', Uncommon: 'easy',
};
/** Classe CSS de badge pour une valeur de rareté/grade connue (sinon neutre). */
export const tierClass = (v?: string | null) => (v && TIERS[v] ? `tier-${TIERS[v]}` : 'tier-none');
