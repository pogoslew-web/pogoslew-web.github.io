import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js';

type Item = { slug: string; title: string; slot: 'armor' | 'weapon' | 'pendant'; rank: string; rarity: string; img: string | null; glb: string };
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
controls.enableDamping = true; controls.enablePan = false; controls.minDistance = 1.6; controls.maxDistance = 6;
controls.target.set(0, 0.55, 0); controls.autoRotate = true; controls.autoRotateSpeed = 1.6;
controls.maxPolarAngle = Math.PI * 0.62; controls.minPolarAngle = Math.PI * 0.25;
const HOME = new THREE.Vector3(1.9, 1.0, 3.2);
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
const PLACE: Record<string, (o: THREE.Object3D) => void> = {
  armor: o => { o.position.set(0, 0, 0); },
  weapon: o => { o.position.set(0.7, 0.5, 0.02); o.rotation.set(0.15, 0, -0.12); },   // tenue à la main droite, lame vers le haut
  pendant: o => { o.position.set(0, 0.78, 0.2); o.rotation.set(0, 0, 0); o.scale.setScalar(1); },
};
const worn: Record<string, { slug: string; obj: THREE.Object3D } | undefined> = {};
const state = { armor: '', weapon: '', pendant: '' } as Record<string, string>;
let slot: 'armor' | 'weapon' | 'pendant' = 'armor';

async function equip(s: 'armor' | 'weapon' | 'pendant', slug: string) {
  worn[s] && man.remove(worn[s]!.obj); worn[s] = undefined; state[s] = '';
  if (slug) {
    const it = bySlug.get(slug)!; state[s] = slug;
    loadingEl.hidden = false;
    try {
      const base = await load(it.glb); if (state[s] !== slug) return;
      const obj = base.clone(true); PLACE[s](obj); man.add(obj); worn[s] = { slug, obj };
    } catch { state[s] = ''; loadingEl.textContent = 'Could not load this 3D model.'; setTimeout(() => (loadingEl.textContent = 'Loading 3D…'), 2500); }
    loadingEl.hidden = true;
  }
  paint(); writeHash();
}

// ---------- interface ----------
const grid = $('lab-grid'), search = $<HTMLInputElement>('lab-search'), empty = $('lab-empty'), eqEl = $('lab-equipped');
function paint() {
  const q = search.value.trim().toLowerCase();
  const list = items.filter(i => i.slot === slot && (!q || i.title.toLowerCase().includes(q) || i.rank.toLowerCase().includes(q)));
  grid.innerHTML = list.map(i => `<button type="button" class="lab-item" role="listitem" data-slug="${i.slug}" aria-pressed="${state[slot] === i.slug}" title="${i.title}">
    ${i.img ? `<img src="${i.img}" alt="" width="64" height="64" loading="lazy">` : '<span class="thumb"></span>'}
    <span class="nm">${i.title}</span>${i.rank ? `<span class="rk">${i.rank}</span>` : ''}</button>`).join('');
  empty.hidden = list.length > 0;
  const names = (['armor', 'weapon', 'pendant'] as const).filter(s => state[s]).map(s => { const it = bySlug.get(state[s])!; return `<span class="lab-tag"><a href="/cosmetics/${it.slug}/">${it.title}</a><button type="button" data-clear="${s}" aria-label="Remove ${it.title}">×</button></span>`; });
  eqEl.innerHTML = names.length ? `<span class="faint">Wearing</span> ${names.join('')} <button type="button" class="btn btn-ghost btn-sm" id="lab-clear">Remove all</button>` : '<span class="faint">Nothing equipped yet. Pick a cosmetic below.</span>';
}
grid.addEventListener('click', e => { const b = (e.target as HTMLElement).closest<HTMLButtonElement>('.lab-item'); if (!b) return; const slug = b.dataset.slug!; equip(slot, state[slot] === slug ? '' : slug); });
eqEl.addEventListener('click', e => { const t = e.target as HTMLElement; const c = t.closest<HTMLElement>('[data-clear]'); if (c) equip(c.dataset.clear as any, ''); if (t.id === 'lab-clear') { (['armor', 'weapon', 'pendant'] as const).forEach(s => equip(s, '')); } });
document.querySelectorAll<HTMLButtonElement>('.lab-tabs [data-slot]').forEach(b => b.addEventListener('click', () => {
  slot = b.dataset.slot as any; document.querySelectorAll('.lab-tabs [data-slot]').forEach(x => x.setAttribute('aria-pressed', String(x === b))); paint();
}));
search.addEventListener('input', paint);
const spin = $('lab-spin');
spin.addEventListener('click', () => { controls.autoRotate = !controls.autoRotate; spin.setAttribute('aria-pressed', String(controls.autoRotate)); });
const view = (x: number, z: number) => { controls.autoRotate = false; spin.setAttribute('aria-pressed', 'false'); camera.position.set(x, 1.0, z); controls.update(); };
$('lab-view-front').addEventListener('click', () => view(0, 3.4));
$('lab-view-back').addEventListener('click', () => view(0, -3.4));
$('lab-reset').addEventListener('click', () => { camera.position.copy(HOME); controls.autoRotate = true; spin.setAttribute('aria-pressed', 'true'); controls.update(); });
const SKINS = [['#8798b5', 'Steel'], ['#d9b48f', 'Sand'], ['#9a6648', 'Bronze'], ['#5b4636', 'Umber'], ['#6fb27c', 'Jade'], ['#9a8aea', 'Violet']];
const skinsEl = $('lab-skins');
skinsEl.innerHTML = SKINS.map(([c, n], i) => `<button type="button" class="swatch" role="radio" aria-checked="${i === 0}" aria-label="${n}" title="${n}" data-c="${c}" style="background:${c}"></button>`).join('');
skinsEl.addEventListener('click', e => { const b = (e.target as HTMLElement).closest<HTMLButtonElement>('.swatch'); if (!b) return; skinMat.color.set(b.dataset.c!); skinsEl.querySelectorAll('.swatch').forEach(x => x.setAttribute('aria-checked', String(x === b))); });
// lien partageable : #armor=slug&weapon=slug&pendant=slug
function writeHash() { const p = new URLSearchParams(); (['armor', 'weapon', 'pendant'] as const).forEach(s => state[s] && p.set(s, state[s])); try { history.replaceState(null, '', p.toString() ? `#${p}` : location.pathname + location.search); } catch {} }
const initial = new URLSearchParams(location.hash.slice(1));
(['armor', 'weapon', 'pendant'] as const).forEach(s => { const v = initial.get(s); if (v && bySlug.get(v)?.slot === s) equip(s, v); });
paint();

// ---------- rendu ----------
function resize() { const r = canvas.getBoundingClientRect(); if (!r.width) return; renderer.setSize(r.width, r.height, false); camera.aspect = r.width / r.height; camera.updateProjectionMatrix(); }
new ResizeObserver(resize).observe(canvas); resize();
let visible = true; new IntersectionObserver(([en]) => (visible = en.isIntersecting)).observe(canvas);
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches; if (reduce) { controls.autoRotate = false; spin.setAttribute('aria-pressed', 'false'); }
renderer.setAnimationLoop(() => { if (!visible || document.hidden) return; controls.update(); renderer.render(scene, camera); });
loadingEl.hidden = true;
