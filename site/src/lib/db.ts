import fs from 'node:fs';
import path from 'node:path';

const ROOT = path.resolve(process.cwd(), '..');
const DB = path.join(ROOT, 'db');
const rd = (p: string) => JSON.parse(fs.readFileSync(p, 'utf8'));

export interface Block { type: string; text?: string; html?: string; src?: string; alt?: string; level?: number; id?: string | null; headers?: string[]; rows?: any[] }
export interface Section { id: string | null; heading: string | null; blocks: Block[] }
export interface Entity {
  id: string; type: string; slug: string; title: string; summary: string | null; rarity: string | null;
  is_overview: boolean; image: string | null; infobox: { key: string; value: string; html: string }[];
  sections: Section[]; media: { src: string; alt?: string; kind: string }[];
  related: { text: string; href: string; img?: string | null }[]; toc: { id: string; text: string }[];
  last_edited: string | null; last_edited_by: string | null; incomplete_at_source: boolean;
  source: { url: string; path: string }; links_to: string[]; linked_from: string[];
}
export interface Category {
  id: string; label: string; family: string; description: string | null; declared_count: number | null;
  count: number; has_overview: boolean; source: { url: string }; order: string[];
}

export const categories: Category[] = rd(path.join(DB, 'categories.json'));
export const codes: any[] = rd(path.join(DB, 'codes.json'));
export const home: any = rd(path.join(DB, 'home.json'));
export const assetMap: Record<string, string> = rd(path.join(process.cwd(), 'src/data/asset-map.json'));

const all: Entity[] = [];
for (const t of fs.readdirSync(path.join(DB, 'entities'))) {
  for (const f of fs.readdirSync(path.join(DB, 'entities', t))) all.push(rd(path.join(DB, 'entities', t, f)));
}
export const entities = all;
export const byId = new Map(all.map(e => [e.id, e]));
export const byPath = new Map(all.map(e => [e.source.path, e]));

export const FAMILIES = ['Gameplay', 'Progression', 'Database', 'World', 'Guides', 'Extra'] as const;
export const FAMILY_BLURB: Record<string, string> = {
  Gameplay: 'Classes, skills, weapon arts, passives and the core systems.',
  Progression: 'Ranks, titles and badges: the road to the top.',
  Database: 'Every item and cosmetic with its stats.',
  World: 'Rifts, dungeons, places and the monsters inside.',
  Guides: 'Step-by-step guides for new and returning hunters.',
  Extra: 'Events, passes, shop, glossary, formulas and odds.',
};
export const catById = new Map(categories.map(c => [c.id, c]));
export const catLabel = (t: string) => (t === 'news' ? 'Announcements' : catById.get(t)?.label ?? t);
export const entityHref = (e: Pick<Entity, 'type' | 'slug'>) => `/${e.type}/${e.slug}/`;
export const catHref = (id: string) => `/${id}/`;

/** Image d'origine -> URL locale (null si la ressource n'a pas pu être récupérée). */
export const asset = (src?: string | null) => (src ? assetMap[src] ?? null : null);

export const entitiesOf = (type: string, includeOverview = false) =>
  all.filter(e => e.type === type && (includeOverview || !e.is_overview) && !(e.type === 'odds' && e.slug === 'index'));

/** Ordre d'origine ("most viewed" au moment de la capture). */
export function popularityRank(): Map<string, number> {
  const m = new Map<string, number>();
  for (const c of categories) c.order.forEach((p, i) => m.set(p, i));
  return m;
}

export function parseDate(s?: string | null): number {
  if (!s) return 0;
  const t = Date.parse(s.replace(/(\d)(st|nd|rd|th),/, '$1,'));
  return Number.isNaN(t) ? 0 : t;
}

/** Facettes de filtre par catégorie : champs réels des infobox. */
export const FACETS: Record<string, string[]> = {
  badges: ['Rank / rarity', 'Group'], classes: ['Role', 'Difficulty', 'Rank / rarity'],
  cosmetics: ['Kind', 'Rarity', 'Rank / rarity', 'Tradeable'], dungeons: ['Hazard'],
  items: ['Kind', 'Tradeable'], monsters: ['Kind', 'Rank'], passives: ['Tree', 'Tier'],
  products: ['Kind', 'Gift'], ranks: ['Trial'], rifts: ['Rank'], skills: ['Class', 'Element'],
  titles: ['Category', 'Rank / rarity', 'Kept'], 'weapon-arts': ['Element', 'Class'],
  passes: [], places: [], events: [], guides: [], systems: [], formulas: [], glossary: [], odds: [],
};

export interface ClassCard { name?: string; desc: string; stats: string[]; on: string[]; weapons: string[]; armor: string[]; trees: string[]; rule: string; unlock: string; unlock_status: string }
export const classCards: Record<string, ClassCard> = rd(path.join(DB, 'overlays/class_cards.json')).classes;
export const classCardsMeta: any = rd(path.join(DB, 'overlays/class_cards.json'));
export const gearSuggestions: any = rd(path.join(DB, 'suggestions.json'));
