# Overrank Atlas
Reconstruction indépendante du wiki Overrank (Astro 5, statique). Contenus et images © AwaitLab — dépôt privé, `noindex`.

## Lancer en local
```
cd site
npm install
node scripts/prepare.mjs      # copie les assets, génère l'index de recherche
npm run dev                   # http://localhost:4321
npm run build                 # sortie : site/dist
```
## Mettre à jour depuis le site d'origine
`./update.sh` (Python 3 + `pip install beautifulsoup4 lxml`), ou `./update.sh --no-crawl`.
Rapports : `db/integrity.json`, `db/dist_check.json`, page `/integrity/`. Détails : `REPORT.md`.
## Structure
`db/` base de données JSON · `assets/` images/3D dédupliquées · `tools/` crawl→extraction→vérif · `site/` Astro · `tests/` Playwright.
