import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js';

type Slot = 'armor' | 'weapon' | 'edge' | 'pendant' | 'aura';
type Item = { slug: string; title: string; slot: Slot; rank: string; rarity: string; img: string | null; glb: string | null; mode: 'model' | 'sprite' | 'aura' };
const SLOTS: Slot[] = ['armor', 'weapon', 'edge', 'pendant', 'aura'];
const items: Item[] = JSON.parse(document.getElementById('lab-data')!.textContent || '[]');
const bySlug = new Map(items.map(i => [i.slug, i]));
const $ = <T extends HTMLElement>(id: string) => document.getElementById(id) as T;
const canvas = $<HTMLCanvasElement>('lab-canvas');
const loadingEl = $('lab-loading');

// ---------- scène ----------
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
const scene = new THREE.Scene();
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
scene.environmentIntensity = 0.55;
const key = new THREE.DirectionalLight(0xffffff, 0.9); key.position.set(2, 3, 3); scene.add(key);
const rim = new THREE.DirectionalLight(0x8b7cff, 1.2); rim.position.set(-3, 2, -2); scene.add(rim);
const camera = new THREE.PerspectiveCamera(36, 1, 0.1, 50);
const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true; controls.enablePan = false; controls.minDistance = 1.6; controls.maxDistance = 8;
controls.target.set(0, 0.35, 0); controls.autoRotate = true; controls.autoRotateSpeed = 1.6;
controls.maxPolarAngle = Math.PI * 0.62; controls.minPolarAngle = Math.PI * 0.25;
const HOME = new THREE.Vector3(2.3, 1.0, 4.1);
camera.position.copy(HOME);

// ---------- mannequin (original, style blocky) ----------
const skinMat = new THREE.MeshStandardMaterial({ color: 0x8798b5, roughness: 0.7, metalness: 0.05 });
const darkMat = new THREE.MeshStandardMaterial({ color: 0x1b2230, roughness: 0.8 });
const man = new THREE.Group(); scene.add(man);
const box = (w: number, h: number, d: number, x: number, y: number, z: number, m = skinMat) => {
  const g = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), m); g.position.set(x, y, z); man.add(g); return g;
};
box(0.26, 0.9, 0.26, -0.16, -0.45, 0); box(0.26, 0.9, 0.26, 0.16, -0.45, 0);      // jambes
box(0.64, 1.0, 0.34, 0, 0.5, 0);                                                  // torse
box(0.34, 0.2, 0.22, -0.5, 0.62, 0); box(0.34, 0.2, 0.22, 0.5, 0.62, 0);          // bras (T)
box(0.14, 0.08, 0.14, 0, 1.04, 0);                                                // cou
const head = box(0.34, 0.34, 0.34, 0, 1.25, 0);
box(0.05, 0.07, 0.01, -0.08, 1.27, 0.171, darkMat); box(0.05, 0.07, 0.01, 0.08, 1.27, 0.171, darkMat); // yeux
// sol
const floor = new THREE.Mesh(new THREE.CircleGeometry(1.2, 64), new THREE.MeshStandardMaterial({ color: 0x131a26, roughness: 0.9, transparent: true, opacity: 0.55 }));
floor.rotation.x = -Math.PI / 2; floor.position.y = -0.905; scene.add(floor);
const ring = new THREE.Mesh(new THREE.RingGeometry(1.1, 1.2, 64), new THREE.MeshBasicMaterial({ color: 0x8b7cff, transparent: true, opacity: 0.6 }));
ring.rotation.x = -Math.PI / 2; ring.position.y = -0.9; scene.add(ring);

// ---------- cosmétiques ----------
const loader = new GLTFLoader();
const cache = new Map<string, Promise<THREE.Object3D>>();
const load = (url: string) => { if (!cache.has(url)) cache.set(url, new Promise((res, rej) => loader.load(url, g => res(g.scene), undefined, rej))); return cache.get(url)!; };
// repères du mannequin : torse y 0→1, main droite (0.67, 0.62), poitrine z=0.17
const HAND = new THREE.Vector3(0.68, 0.62, 0.02);
const texLoader = new THREE.TextureLoader();
const texCache = new Map<string, Promise<THREE.Texture>>();
const loadTex = (url: string) => { if (!texCache.has(url)) texCache.set(url, new Promise((res, rej) => texLoader.load(url, t => { t.colorSpace = THREE.SRGBColorSpace; res(t); }, undefined, rej))); return texCache.get(url)!; };
const pixels = (t: THREE.Texture, n = 96) => { const im = t.image as HTMLImageElement; const c = document.createElement('canvas'); c.width = c.height = n; const x = c.getContext('2d', { willReadFrequently: true })!; x.drawImage(im, 0, 0, n, n); return x.getImageData(0, 0, n, n).data; };

/** Enveloppe un objet 3D : le centre sur l'origine, puis applique échelle/position voulues. */
function wrap(obj: THREE.Object3D, fit: (size: THREE.Vector3) => number, at: (size: THREE.Vector3) => THREE.Vector3, upright = false) {
  const g = new THREE.Group(); const inner = new THREE.Group(); inner.add(obj); g.add(inner);
  if (upright) { // l'axe le plus long doit être vertical
    const b0 = new THREE.Box3().setFromObject(obj), z0 = b0.getSize(new THREE.Vector3());
    if (z0.x > z0.y * 1.15 && z0.x >= z0.z) inner.rotation.z = Math.PI / 2; else if (z0.z > z0.y * 1.15) inner.rotation.x = Math.PI / 2;
  }
  inner.updateMatrixWorld(true);
  const box = new THREE.Box3().setFromObject(inner), size = box.getSize(new THREE.Vector3()), ctr = box.getCenter(new THREE.Vector3());
  inner.position.sub(ctr); const sc = fit(size); g.scale.setScalar(sc); g.position.copy(at(size.clone().multiplyScalar(sc)));
  return g;
}
// épaisseur simulée : le visuel officiel (image) est empilé en fines tranches
function slab(tex: THREE.Texture, w: number, h: number, depth: number, layers = 9) {
  const g = new THREE.Group();
  for (let i = 0; i < layers; i++) {
    const m = new THREE.MeshStandardMaterial({ map: tex, alphaTest: 0.5, side: THREE.DoubleSide, roughness: 0.6, metalness: 0.1, color: i === 0 || i === layers - 1 ? 0xffffff : 0x8a8f9c });
    const p = new THREE.Mesh(new THREE.PlaneGeometry(w, h), m); p.position.z = (i / (layers - 1) - 0.5) * depth; g.add(p);
  }
  return g;
}
/** angle de l'axe principal + sens (le côté le plus « lourd » de l'image = lame/haut) pour redresser une arme en 2D */
function uprightAngle(t: THREE.Texture) {
  const d = pixels(t); const n = 96; let sx = 0, sy = 0, c = 0; const pts: [number, number][] = [];
  for (let y = 0; y < n; y++) for (let x = 0; x < n; x++) if (d[(y * n + x) * 4 + 3] > 40) { pts.push([x, n - y]); sx += x; sy += n - y; c++; }
  if (!c) return 0; const mx = sx / c, my = sy / c; let a = 0, b = 0, cc = 0;
  pts.forEach(([x, y]) => { a += (x - mx) ** 2; b += (y - my) ** 2; cc += (x - mx) * (y - my); });
  const th = 0.5 * Math.atan2(2 * cc, a - b); // axe principal
  const ux = Math.cos(th), uy = Math.sin(th); let pos = 0, neg = 0, far = 0, farSign = 1;
  pts.forEach(([x, y]) => { const p = (x - mx) * ux + (y - my) * uy; if (p > 0) pos++; else neg++; if (Math.abs(p) > far) { far = Math.abs(p); farSign = Math.sign(p) || 1; } });
  const dir = pos >= neg ? 1 : -1; // sens de la lame
  const ang = Math.atan2(uy * dir, ux * dir); // direction de la lame
  return Math.PI / 2 - ang; // rotation à appliquer pour que la lame pointe vers le haut
}
function palette(t: THREE.Texture) { // couleur dominante, saturée, de l'image officielle
  const d = pixels(t, 64); let r = 0, g = 0, b = 0, w = 0, rs = 0, gs = 0, bs = 0, ws = 0;
  for (let i = 0; i < d.length; i += 4) { const a = d[i + 3] / 255; if (a < 0.15) continue; const mx = Math.max(d[i], d[i + 1], d[i + 2]), mn = Math.min(d[i], d[i + 1], d[i + 2]); const sat = mx ? (mx - mn) / mx : 0; const wt = a * (0.2 + mx / 255);
    r += d[i] * wt; g += d[i + 1] * wt; b += d[i + 2] * wt; w += wt; const sw = wt * sat * sat; rs += d[i] * sw; gs += d[i + 1] * sw; bs += d[i + 2] * sw; ws += sw; }
  const c = ws > w * 0.02 ? [rs / ws, gs / ws, bs / ws] : [r / w, g / w, b / w];
  return new THREE.Color(c[0] / 255, c[1] / 255, c[2] / 255);
}
// aura : anneau au sol + particules en spirale, aux couleurs de l'image officielle (effet simulé)
function makeAura(col: THREE.Color) {
  const g = new THREE.Group(); const N = 260; const pos = new Float32Array(N * 3); const seed = new Float32Array(N * 3);
  for (let i = 0; i < N; i++) { seed[i * 3] = Math.random(); seed[i * 3 + 1] = Math.random() * Math.PI * 2; seed[i * 3 + 2] = 0.55 + Math.random() * 0.4; }
  const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  const mat = new THREE.PointsMaterial({ color: col, size: 0.045, transparent: true, opacity: 0.9, blending: THREE.AdditiveBlending, depthWrite: false });
  const pts = new THREE.Points(geo, mat); pts.frustumCulled = false; g.add(pts);
  const disc = new THREE.Mesh(new THREE.RingGeometry(0.5, 1.0, 64), new THREE.MeshBasicMaterial({ color: col, transparent: true, opacity: 0.35, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide }));
  disc.rotation.x = -Math.PI / 2; disc.position.y = -0.89; g.add(disc);
  g.userData.tick = (t: number) => { for (let i = 0; i < N; i++) { const p = (seed[i * 3] + t * 0.12) % 1, a = seed[i * 3 + 1] + t * 0.8 + p * 3; const r = seed[i * 3 + 2] * (1 - p * 0.35); pos[i * 3] = Math.cos(a) * r; pos[i * 3 + 1] = -0.88 + p * 2.5; pos[i * 3 + 2] = Math.sin(a) * r; } geo.attributes.position.needsUpdate = true; mat.opacity = 0.75 + Math.sin(t * 2) * 0.15; disc.scale.setScalar(1 + Math.sin(t * 2) * 0.04); };
  return g;
}
const HAND_SLOTS: Slot[] = ['weapon', 'edge'];
const worn: Partial<Record<Slot, { slug: string; obj: THREE.Object3D }>> = {};
const state = { armor: '', weapon: '', edge: '', pendant: '', aura: '' } as Record<Slot, string>;
let slot: Slot = 'armor';
const auras: THREE.Object3D[] = [];

async function build(it: Item): Promise<THREE.Object3D> {
  if (it.mode === 'model') {
    const base = (await load(it.glb!)).clone(true);
    if (it.slot === 'armor') return wrap(base, s => Math.min(1.12 / s.y, 1.4 / s.x), s => new THREE.Vector3(0, 0.52, 0));
    if (it.slot === 'pendant') return wrap(base, s => 0.26 / Math.max(s.x, s.y, s.z), s => new THREE.Vector3(0, 0.8, 0.17 + s.z / 2));
    // arme / edge : dimension la plus longue ramenée à ~0.95 (en gardant une partie de la différence de taille), poignée à la main
    const g = wrap(base, s => Math.pow(0.95 / Math.max(s.x, s.y, s.z), 0.65), s => new THREE.Vector3(HAND.x, HAND.y + s.y * 0.2, HAND.z), true);
    g.rotation.z = -0.12; return g;
  }
  const tex = await loadTex(it.img!);
  if (it.mode === 'aura') return makeAura(palette(tex));
  const asp = (tex.image as HTMLImageElement).width / (tex.image as HTMLImageElement).height || 1;
  if (it.slot === 'armor') { const w = 1.36, h = w / asp; const s = slab(tex, w, h, 0.05); s.position.set(0, 0.52, 0.19); return s; }
  if (it.slot === 'pendant') { const w = 0.3, s = slab(tex, w, w / asp, 0.03, 5); s.position.set(0, 0.8, 0.2); return s; }
  // arme / edge : visuel redressé, lame vers le haut, tenu à la main
  const ang = uprightAngle(tex); const len = 1.15; const s = slab(tex, len, len / asp, 0.07);
  const holder = new THREE.Group(); s.rotation.z = ang; holder.add(s);
  const b = new THREE.Box3().setFromObject(holder); const sz = b.getSize(new THREE.Vector3()), ctr = b.getCenter(new THREE.Vector3());
  const k = 0.95 / Math.max(sz.x, sz.y); s.position.sub(ctr); holder.scale.setScalar(k); holder.position.set(HAND.x, HAND.y + sz.y * k * 0.2, HAND.z); holder.rotation.z = -0.12; return holder;
}
async function equip(s: Slot, slug: string) {
  if (HAND_SLOTS.includes(s) && slug) HAND_SLOTS.filter(o => o !== s).forEach(o => { if (state[o]) clear(o); });
  clear(s);
  if (slug) {
    const it = bySlug.get(slug)!; state[s] = slug;
    loadingEl.hidden = false;
    try {
      const obj = await build(it); if (state[s] !== slug) return;
      man.add(obj); worn[s] = { slug, obj }; if (obj.userData.tick) auras.push(obj);
    } catch { state[s] = ''; loadingEl.textContent = 'Could not load this preview.'; setTimeout(() => (loadingEl.textContent = 'Loading 3D…'), 2500); }
    loadingEl.hidden = true;
  }
  paint(); writeHash();
}
function clear(s: Slot) { const w = worn[s]; if (w) { man.remove(w.obj); const i = auras.indexOf(w.obj); if (i >= 0) auras.splice(i, 1); } worn[s] = undefined; state[s] = ''; }

// ---------- interface ----------
const grid = $('lab-grid'), search = $<HTMLInputElement>('lab-search'), empty = $('lab-empty'), eqEl = $('lab-equipped');
function paint() {
  const q = search.value.trim().toLowerCase();
  const list = items.filter(i => i.slot === slot && (!q || i.title.toLowerCase().includes(q) || i.rank.toLowerCase().includes(q)));
  grid.innerHTML = list.map(i => `<button type="button" class="lab-item" role="listitem" data-slug="${i.slug}" aria-pressed="${state[slot] === i.slug}" title="${i.title}">
    ${i.img ? `<img src="${i.img}" alt="" width="64" height="64" loading="lazy">` : '<span class="thumb"></span>'}
    <span class="nm">${i.title}</span>${i.rank ? `<span class="rk">${i.rank}</span>` : ''}</button>`).join('');
  empty.hidden = list.length > 0;
  const names = SLOTS.filter(s => state[s]).map(s => { const it = bySlug.get(state[s])!; return `<span class="lab-tag"><a href="/cosmetics/${it.slug}/">${it.title}</a><button type="button" data-clear="${s}" aria-label="Remove ${it.title}">×</button></span>`; });
  eqEl.innerHTML = names.length ? `<span class="faint">Wearing</span> ${names.join('')} <button type="button" class="btn btn-ghost btn-sm" id="lab-clear">Remove all</button>` : '<span class="faint">Nothing equipped yet. Pick a cosmetic below.</span>';
}
grid.addEventListener('click', e => { const b = (e.target as HTMLElement).closest<HTMLButtonElement>('.lab-item'); if (!b) return; const slug = b.dataset.slug!; equip(slot, state[slot] === slug ? '' : slug); });
eqEl.addEventListener('click', e => { const t = e.target as HTMLElement; const c = t.closest<HTMLElement>('[data-clear]'); if (c) equip(c.dataset.clear as Slot, ''); if (t.id === 'lab-clear') { SLOTS.forEach(s => equip(s, '')); } });
document.querySelectorAll<HTMLButtonElement>('.lab-tabs [data-slot]').forEach(b => b.addEventListener('click', () => {
  slot = b.dataset.slot as Slot; document.querySelectorAll('.lab-tabs [data-slot]').forEach(x => x.setAttribute('aria-pressed', String(x === b))); paint();
}));
search.addEventListener('input', paint);
const spin = $('lab-spin');
spin.addEventListener('click', () => { controls.autoRotate = !controls.autoRotate; spin.setAttribute('aria-pressed', String(controls.autoRotate)); });
const view = (x: number, z: number) => { controls.autoRotate = false; spin.setAttribute('aria-pressed', 'false'); camera.position.set(x, 1.0, z); controls.update(); };
$('lab-view-front').addEventListener('click', () => view(0, 4.3));
$('lab-view-back').addEventListener('click', () => view(0, -4.3));
$('lab-reset').addEventListener('click', () => { camera.position.copy(HOME); controls.autoRotate = true; spin.setAttribute('aria-pressed', 'true'); controls.update(); });
const SKINS = [['#8798b5', 'Steel'], ['#d9b48f', 'Sand'], ['#9a6648', 'Bronze'], ['#5b4636', 'Umber'], ['#6fb27c', 'Jade'], ['#9a8aea', 'Violet']];
const skinsEl = $('lab-skins');
skinsEl.innerHTML = SKINS.map(([c, n], i) => `<button type="button" class="swatch" role="radio" aria-checked="${i === 0}" aria-label="${n}" title="${n}" data-c="${c}" style="background:${c}"></button>`).join('');
skinsEl.addEventListener('click', e => { const b = (e.target as HTMLElement).closest<HTMLButtonElement>('.swatch'); if (!b) return; skinMat.color.set(b.dataset.c!); skinsEl.querySelectorAll('.swatch').forEach(x => x.setAttribute('aria-checked', String(x === b))); });
// lien partageable : #armor=slug&weapon=slug&pendant=slug
function writeHash() { const p = new URLSearchParams(); SLOTS.forEach(s => state[s] && p.set(s, state[s])); try { history.replaceState(null, '', p.toString() ? `#${p}` : location.pathname + location.search); } catch {} }
const initial = new URLSearchParams(location.hash.slice(1));
SLOTS.forEach(s => { const v = initial.get(s); if (v && bySlug.get(v)?.slot === s) equip(s, v); });
paint();

// ---------- rendu ----------
function resize() { const r = canvas.getBoundingClientRect(); if (!r.width) return; renderer.setSize(r.width, r.height, false); camera.aspect = r.width / r.height; camera.updateProjectionMatrix(); }
new ResizeObserver(resize).observe(canvas); resize();
let visible = true; new IntersectionObserver(([en]) => (visible = en.isIntersecting)).observe(canvas);
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches; if (reduce) { controls.autoRotate = false; spin.setAttribute('aria-pressed', 'false'); }
renderer.setAnimationLoop(t => { if (!visible || document.hidden) return; auras.forEach(a => a.userData.tick(t / 1000)); controls.update(); renderer.render(scene, camera); });
loadingEl.hidden = true;
