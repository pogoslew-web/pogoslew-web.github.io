# Overrank Atlas — rapport de reconstruction

Source : https://overrank.awaitlab.com/ (crawl poli, 0,6 s/page, le 05/11/2026).

## Contrôle d'intégrité (mesuré, voir /integrity/ et db/*.json)
| Indicateur | Valeur |
|---|---|
| Pages en périmètre découvertes / récupérées | 1160 / 1160 (0 échec) |
| Pages intégrées comme contenu | 1135 (+24 pages d'index/accueil) |
| Pages HTML construites | 1163 |
| Différences source → base (mots + nombres, 1135 pages) | 0 |
| Pages spéciales (Odds 78 sections, News 8 articles…) | 0 manquant |
| Nombres retrouvés dans le site construit | 13 456 / 13 456 |
| Liens internes vérifiés | 86 373, 0 cassé |
| Images/ressources | 2090 référencées, 1961 fichiers uniques, 0 échec, 0 manquant |
| Pages signalées « incomplètes à la source » | 55 (conservées telles quelles) |

## Limites assumées
- Classements joueurs (leaderboards) : pseudos non copiés (données personnelles vivantes).
- Registre / pages /players, /login, /forum, /legal : hors périmètre (connexion ou non-contenu).
- Calculateur de drops (Odds) : tables reproduites, pas l'outil interactif d'origine.
- Contenus masqués « ??? » présents dans la charge technique de Next.js : volontairement NON extraits.
- Les 678 formulaires /edit sont exclus (aucun contenu).
- Images et textes © AwaitLab : le site est livré en `noindex` + `Disallow: /`. Obtenir l'autorisation avant toute publication.
- Je ne peux pas prouver « 100 % » au sens absolu : le site d'origine n'a pas de sitemap ; la complétude = tout ce qui est atteignable par liens depuis l'accueil.

## Relancer / mettre à jour
`./update.sh` (crawl → extraction → base → assets → vérifs → build). `./update.sh --no-crawl` pour rebâtir seulement.
Site : `cd site && npx astro dev` ; sortie statique : `site/dist/`.
Indexation : build avec `PUBLIC_INDEXABLE=1` et retirer public/robots.txt Disallow.
