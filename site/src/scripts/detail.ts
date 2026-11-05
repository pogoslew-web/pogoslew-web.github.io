if (document.querySelector('model-viewer')) import('@google/model-viewer');
// traduction française du texte rédactionnel (fichier par page, si disponible)
const art = document.querySelector<HTMLElement>('article[data-fr]');
if (art) {
  const frUrl = art.dataset.fr!; let cache: any = null; const orig = new Map<HTMLElement, string>(); let origSub: string | null = null; let note: HTMLElement | null = null;
  const sub = document.querySelector<HTMLElement>('.detail-head .sub');
  const secEls = () => [...art.querySelectorAll<HTMLElement>('[data-i]')];
  const toFr = async () => {
    try { cache ??= await (await fetch(frUrl)).json(); } catch { return; }
    if (document.documentElement.lang !== 'fr') return;
    secEls().forEach(el => {
      const d = cache.sections[Number(el.dataset.i)]; if (!d) return;
      const body = el.matches('details') ? el.querySelector<HTMLElement>('.acc-body')! : el;
      if (!orig.has(body)) orig.set(body, body.innerHTML);
      body.innerHTML = d.html;
      if (d.heading && el.matches('details')) { const sm = el.querySelector('summary')!; if (!sm.dataset.en) sm.dataset.en = sm.textContent ?? ''; sm.textContent = d.heading; }
    });
    if (cache.summary && sub) { origSub ??= sub.textContent; sub.textContent = cache.summary; }
    if (!note) { note = document.createElement('div'); note.className = 'i18n-note'; note.innerHTML = '<span><b>Traduction française automatique</b> du texte du wiki original. Les noms du jeu restent en anglais, comme en jeu.</span>'; art.insertBefore(note, art.querySelector('.sections')); }
  };
  const toEn = () => {
    orig.forEach((h, el) => (el.innerHTML = h)); orig.clear();
    art.querySelectorAll<HTMLElement>('summary[data-en]').forEach(sm => { sm.textContent = sm.dataset.en!; delete sm.dataset.en; });
    if (origSub !== null && sub) { sub.textContent = origSub; origSub = null; }
    note?.remove(); note = null;
  };
  const sync = () => (document.documentElement.lang === 'fr' ? toFr() : toEn());
  document.addEventListener('langchange', sync); sync();
}
const secs = [...document.querySelectorAll<HTMLDetailsElement>('details[data-sec]')];
// mobile : seules les deux premières sections restent ouvertes ; tout reste accessible
if (matchMedia('(max-width: 719px)').matches && secs.length > 3) secs.slice(2).forEach(s => (s.open = false));
const openHash = () => { const id = decodeURIComponent(location.hash.slice(1)); if (!id) return; const t = document.getElementById(id); const d = t?.closest('details[data-sec]') as HTMLDetailsElement | null; if (d) { d.open = true; t!.scrollIntoView(); } };
addEventListener('hashchange', openHash); openHash();
document.getElementById('expand-all')?.addEventListener('click', () => secs.forEach(s => (s.open = true)));
document.getElementById('collapse-all')?.addEventListener('click', () => secs.forEach(s => (s.open = false)));
document.querySelectorAll<HTMLAnchorElement>('.toc-chips a, .toc a').forEach(a => a.addEventListener('click', () => { const t = document.getElementById(a.hash.slice(1)) as HTMLDetailsElement | null; if (t && 'open' in t) t.open = true; }));
// surlignage du sommaire
const links = [...document.querySelectorAll<HTMLAnchorElement>('.toc a')];
if ('IntersectionObserver' in window && links.length) {
  const io = new IntersectionObserver(es => { es.forEach(en => { if (en.isIntersecting) links.forEach(l => l.setAttribute('aria-current', String(l.hash === '#' + en.target.id))); }); }, { rootMargin: '-20% 0px -70% 0px' });
  secs.forEach(s => io.observe(s));
}
document.getElementById('copy-link')?.addEventListener('click', async ev => { const b = ev.currentTarget as HTMLButtonElement; try { await navigator.clipboard.writeText(location.href.split('#')[0]); b.textContent = 'Link copied'; setTimeout(() => (b.textContent = 'Copy link'), 1600); } catch { b.textContent = 'Copy failed'; } });
export {};
