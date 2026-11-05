import fs from 'node:fs';
import path from 'node:path';
const DIR = path.resolve(process.cwd(), '..', 'db', 'i18n', 'fr');
export interface FrFile { summary?: string; headings?: Record<string, string>; blocks?: Record<string, Record<string, string>> }
export const frFile = (type: string, slug: string): FrFile | null => {
  const p = path.join(DIR, type, `${slug}.json`);
  return fs.existsSync(p) ? JSON.parse(fs.readFileSync(p, 'utf8')) : null;
};
export const frList = (): { type: string; slug: string }[] => {
  if (!fs.existsSync(DIR)) return [];
  return fs.readdirSync(DIR).flatMap(t => fs.readdirSync(path.join(DIR, t)).filter(f => f.endsWith('.json')).map(f => ({ type: t, slug: f.slice(0, -5) })));
};
