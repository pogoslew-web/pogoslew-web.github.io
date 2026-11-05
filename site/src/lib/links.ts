import { asset, byPath } from './db';

const ORIGIN = 'https://overrank.awaitlab.com';

/** Réécrit un lien interne de l'ancien site vers une URL du nouveau site (ou garde l'original si hors périmètre). */
export function mapHref(href: string): { href: string; external: boolean } {
  if (!href || href.startsWith('#') || href.startsWith('mailto:')) return { href, external: false };
  if (/^https?:\/\//.test(href)) return { href, external: true };
  const [pathAndQuery, hash] = href.split('#');
  const p = pathAndQuery.split('?')[0].replace(/\/$/, '');
  const h = hash ? '#' + hash : '';
  const e = byPath.get(p);
  if (e) {
    if (e.type === 'odds' && e.slug === 'index') return { href: '/odds/' + h, external: false };
    if (e.type === 'news' && e.slug === 'index') return { href: '/news/' + h, external: false };
    return { href: `/${e.type}/${e.slug}/` + h, external: false };
  }
  let m = p.match(/^\/en\/w\/overrank\/([^/]+)$/);
  if (m) return { href: `/${m[1]}/` + h, external: false };
  if (p === '/en/w/overrank' || p === '/en') return { href: '/', external: false };
  if (p === '/en/news') return { href: '/news/', external: false };
  if (p === '/en/w/overrank/leaderboards') return { href: '/leaderboards/', external: false };
  return { href: ORIGIN + href, external: true };
}

const RAW_IMG = /(src)="(\/[^"]+)"/g;
const RAW_HREF = /href="([^"]*)"/g;

/** HTML nettoyé issu de l'extraction -> HTML du nouveau site (liens, images, tableaux). */
export function renderHtml(html: string): string {
  let out = html
    .replace(RAW_IMG, (_m, _a, src) => {
      const local = asset(src);
      return local ? `src="${local}" loading="lazy" decoding="async"` : `src="" data-missing="${src}"`;
    })
    .replace(RAW_HREF, (_m, href) => {
      const { href: h, external } = mapHref(href);
      return external ? `href="${h}" target="_blank" rel="noopener noreferrer"` : `href="${h}"`;
    });
  out = out.replace(/<table/g, '<div class="table-wrap" tabindex="0"><table class="data-table"').replace(/<\/table>/g, '</table></div>');
  return out;
}

export const originalUrl = (p: string) => ORIGIN + p;
