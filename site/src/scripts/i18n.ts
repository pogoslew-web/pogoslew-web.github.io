import { exact, rules, frDate } from '../i18n/fr';
type Lang = 'en' | 'fr';
const SKIP_TEXT = 'script,style,textarea,[data-i18n-skip]';
const root = document.documentElement;
const origText = new Map<Text, string>();
const lastTr = new WeakMap<Text, string>();
const origAttr = new Map<Element, Record<string, string>>();
const ATTRS = ['placeholder', 'aria-label', 'title'];
let lang: Lang = 'en';

const translate = (raw: string): string | null => {
  const t = raw.replace(/\s+/g, ' ').trim(); if (!t) return null;
  let r: string | undefined = exact[t];
  if (r === undefined) for (const [re, f] of rules) { const m = t.match(re); if (m) { const x = f(m); if (x) { r = x; break; } } }
  if (r === undefined && /\d{4}/.test(t)) { const d = frDate(t); if (d !== t) r = d; }
  return r ?? null;
};
const skipNode = (n: Node) => {
  const el = n.parentElement; if (!el) return true;
  if (el.closest(SKIP_TEXT)) return true;
  // texte rédactionnel du wiki : traduit par fichier de page, pas par dictionnaire (sauf tableaux)
  if (el.closest('.acc-body, .prose') && !el.closest('table')) return true;
  return false;
};
function doText(n: Text) {
  if (skipNode(n)) return;
  const cur = n.nodeValue ?? '';
  if (lastTr.get(n) === cur) return;
  const r = translate(cur); if (r === null) return;
  const lead = cur.match(/^\s*/)![0], trail = cur.match(/\s*$/)![0];
  if (!origText.has(n)) origText.set(n, cur);
  const out = lead + r + trail; lastTr.set(n, out); n.nodeValue = out;
}
function doAttrs(el: Element) {
  if (el.closest('[data-i18n-skip]')) return;
  for (const a of ATTRS) {
    const v = el.getAttribute(a); if (!v) continue;
    const r = translate(v); if (r === null) continue;
    const o = origAttr.get(el) ?? {}; if (!(a in o)) o[a] = v; origAttr.set(el, o); el.setAttribute(a, r);
  }
}
function apply(scope: Node) {
  if (scope.nodeType === 3) { doText(scope as Text); return; }
  if (scope.nodeType !== 1) return;
  const el = scope as Element;
  const w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT); let n: Node | null;
  while ((n = w.nextNode())) doText(n as Text);
  doAttrs(el); el.querySelectorAll('[placeholder],[aria-label],[title]').forEach(doAttrs);
}
function restore() {
  origText.forEach((v, n) => { if (n.isConnected) n.nodeValue = v; }); origText.clear();
  origAttr.forEach((o, el) => { if (el.isConnected) for (const a in o) el.setAttribute(a, o[a]); }); origAttr.clear();
}
let obs: MutationObserver | null = null;
function watch(on: boolean) {
  obs?.disconnect(); obs = null; if (!on) return;
  obs = new MutationObserver(ms => { for (const m of ms) { if (m.type === 'childList') m.addedNodes.forEach(n => apply(n)); else if (m.type === 'characterData') apply(m.target); else if (m.type === 'attributes') doAttrs(m.target as Element); } });
  obs.observe(document.body, { childList: true, subtree: true, characterData: true, attributes: true, attributeFilter: ATTRS });
}
export function getLang(): Lang { return lang; }
export function setLang(l: Lang, persist = true) {
  lang = l; root.lang = l; root.dataset.lang = l;
  if (persist) try { localStorage.setItem('lang', l); } catch {}
  watch(false); restore();
  if (l === 'fr') { apply(document.body); watch(true); document.title = translateTitle(document.title); }
  document.querySelectorAll<HTMLElement>('[data-set-lang]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.setLang === l)));
  document.dispatchEvent(new CustomEvent('langchange', { detail: l }));
}
const titleOrig = document.title;
function translateTitle(t: string) { const base = titleOrig; const parts = base.split(' · '); const out = parts.map(p => translate(p) ?? p); return out.join(' · '); }
function initial(): Lang { try { const s = localStorage.getItem('lang'); if (s === 'fr' || s === 'en') return s; } catch {} return /^fr\b/i.test(navigator.language) ? 'fr' : 'en'; }
document.querySelectorAll<HTMLElement>('[data-set-lang]').forEach(b => b.addEventListener('click', () => setLang(b.dataset.setLang as Lang)));
(window as any).__setLang = setLang;
setLang(initial(), false);
// les scripts de page peuvent s'exécuter avant celui-ci : on ré-annonce la langue une fois le DOM prêt
const announce = () => document.dispatchEvent(new CustomEvent('langchange', { detail: lang }));
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', announce); else setTimeout(announce, 0);
