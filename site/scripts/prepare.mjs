// Prépare les ressources du site : copie les images dédoublonnées, produit la carte d'assets et l'index de recherche.
import fs from 'node:fs'; import path from 'node:path';
const ROOT = path.resolve(process.cwd(), '..');
const man = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/assets_manifest.json'), 'utf8'));
fs.mkdirSync('public/assets', { recursive: true });
const map = {}; let copied = 0, failed = 0;
for (const [orig, e] of Object.entries(man)) {
  if (e.status !== 200 || !e.file) { failed++; continue; }
  const name = path.basename(e.file);
  const dst = path.join('public/assets', name);
  if (!fs.existsSync(dst)) { fs.copyFileSync(path.join(ROOT, 'assets', e.file), dst); copied++; }
  map[orig] = '/assets/' + name;
}
fs.writeFileSync('src/data/asset-map.json', JSON.stringify(map));
console.log(`assets: ${Object.keys(map).length} mapped, ${copied} copied, ${failed} unavailable`);

// index de recherche
const ents = [];
for (const t of fs.readdirSync(path.join(ROOT, 'db/entities'))) {
  for (const f of fs.readdirSync(path.join(ROOT, 'db/entities', t))) ents.push(JSON.parse(fs.readFileSync(path.join(ROOT, 'db/entities', t, f), 'utf8')));
}
const cats = JSON.parse(fs.readFileSync(path.join(ROOT, 'db/categories.json'), 'utf8'));
const label = Object.fromEntries(cats.map(c => [c.id, c.label])); label.news = 'Announcements';
const popRank = {};
for (const c of cats) c.order.forEach((p, i) => { popRank[p] = i; });
const strip = s => (s || '').replace(/\s+/g, ' ').trim();
const idx = [];
for (const e of ents) {
  if (e.type === 'news' && e.slug === 'index') continue;
  if (e.type === 'odds' && e.slug === 'index') continue;
  const body = strip(e.sections.flatMap(s => s.blocks.map(b => b.text || '')).join(' ')).slice(0, 500);
  const keys = e.infobox.map(i => i.value).join(' ');
  const img = e.image ? map[e.image] || null : null;
  idx.push({ id: e.id, t: e.type, tl: label[e.type] || e.type, n: e.title, d: e.summary || '', r: e.rarity || '', k: keys, b: body, i: img, h: `/${e.type}/${e.slug}/` });
}
fs.writeFileSync('public/search-index.json', JSON.stringify(idx));
console.log('search index:', idx.length, 'records');
