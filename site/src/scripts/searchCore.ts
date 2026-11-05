import MiniSearch from 'minisearch';

export interface Rec { id: string; t: string; tl: string; n: string; d: string; r: string; k: string; b: string; i: string | null; h: string }
let ready: Promise<{ ms: MiniSearch<Rec>; recs: Rec[] }> | null = null;

export function loadIndex() {
  ready ??= fetch('/search-index.json')
    .then(r => { if (!r.ok) throw new Error('index ' + r.status); return r.json() as Promise<Rec[]>; })
    .then(recs => {
      const ms = new MiniSearch<Rec>({
        fields: ['n', 'd', 'r', 'k', 'tl', 'b'],
        storeFields: ['id', 't', 'tl', 'n', 'd', 'r', 'i', 'h'],
        searchOptions: { boost: { n: 6, tl: 2, d: 2, r: 2, k: 1.5, b: 0.6 }, prefix: true, fuzzy: (term) => (term.length > 4 ? 0.2 : 0), combineWith: 'AND' },
      });
      ms.addAll(recs);
      return { ms, recs };
    });
  return ready;
}

// Priorité de type : une recherche "reaper" doit montrer la classe avant ses cosmétiques.
const TYPE_W: Record<string, number> = { classes: 1.3, guides: 1.2, skills: 1.15, rifts: 1.12, monsters: 1.1, items: 1.1, 'weapon-arts': 1.08, passives: 1.05, ranks: 1.12, systems: 1.08, dungeons: 1.1, places: 1.05, glossary: 1.02, formulas: 1.02, odds: 1.02, events: 1.0, passes: 0.95, titles: 0.88, badges: 0.88, news: 0.9, products: 0.82, cosmetics: 0.78 };
const norm = (s: string) => s.toLowerCase().replace(/[^a-z0-9\u00C0-\u024F]+/g, ' ').trim();
export function rerank<T extends { t: string; n: string; score?: number }>(res: T[], q: string): T[] {
  const nq = norm(q);
  return res.map(r => {
    const nt = norm(r.n); let s = (r.score ?? 0) * (TYPE_W[r.t] ?? 1);
    if (nt === nq) s += 1000; else if (nt.startsWith(nq + ' ') || nt.startsWith(nq)) s *= 1.25; else if (nt.split(' ').includes(nq)) s *= 1.08;
    return { r, s };
  }).sort((a, b) => b.s - a.s).map(x => x.r);
}

export async function runSearch(q: string, type?: string | null, limit = 60): Promise<Rec[]> {
  const { ms } = await loadIndex();
  const query = q.trim();
  if (!query) return [];
  let res = ms.search(query);
  if (!res.length) res = ms.search(query, { combineWith: 'OR', fuzzy: 0.25 });
  let out = rerank(res.map(r => r as unknown as Rec & { score?: number }), query);
  if (type) out = out.filter(r => r.t === type);
  return out.slice(0, limit);
}

export const esc = (s: string) => s.replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]!));
export function mark(text: string, q: string) {
  const t = esc(text);
  const words = q.trim().split(/\s+/).filter(w => w.length > 1).map(w => w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
  if (!words.length) return t;
  return t.replace(new RegExp('(' + words.join('|') + ')', 'ig'), '<mark>$1</mark>');
}
