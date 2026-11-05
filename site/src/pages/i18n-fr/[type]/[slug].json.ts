import type { APIRoute } from 'astro';
import { byId } from '../../../lib/db';
import { frFile, frList } from '../../../lib/fr';
import { renderHtml } from '../../../lib/links';
export function getStaticPaths() { return frList().map(p => ({ params: p })); }
const blocksHtml = (blocks: any[], fr: Record<string, string> = {}) => blocks.map((b, i) => {
  if (b.type === 'heading') return `<h${b.level}${b.id ? ` id="${b.id}"` : ''}>${fr[i] ?? b.text}</h${b.level}>`;
  if (b.type === 'model' || b.type === 'image') return '';
  return renderHtml(fr[i] ?? b.html ?? '');
}).join('\n');
export const GET: APIRoute = ({ params }) => {
  const e = byId.get(`${params.type}/${params.slug}`)!; const f = frFile(params.type!, params.slug!)!;
  const sections = e.sections.filter(s => s.blocks.length || s.heading);
  const out = { summary: f.summary ?? null, sections: sections.map((s, i) => ({ heading: s.heading ? (f.headings?.[s.id ?? `#${i}`] ?? null) : null, html: blocksHtml(s.blocks, f.blocks?.[s.id ?? `#${i}`] ?? {}) })) };
  return new Response(JSON.stringify(out), { headers: { 'Content-Type': 'application/json' } });
};
