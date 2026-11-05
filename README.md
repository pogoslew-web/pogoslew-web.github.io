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

## Déploiement GitHub Pages
Le workflow `.github/workflows/pages.yml` construit et publie `site/dist`. Le site utilise des chemins absolus (`/classes/...`) : il doit être servi à la racine d'un domaine, donc dépôt nommé `<utilisateur>.github.io` (ou domaine personnalisé). Settings → Pages → Source : GitHub Actions.
