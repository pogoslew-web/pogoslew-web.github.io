#!/usr/bin/env bash
# Rafraîchit tout depuis le site original, vérifie, reconstruit. Usage : ./update.sh [--no-crawl]
set -euo pipefail
cd "$(dirname "$0")"
if [ "${1:-}" != "--no-crawl" ]; then
  rm -f raw/inventory.json            # force la reprise propre de l'inventaire
  python3 -I tools/crawl2.py "$PWD/raw"      # crawl poli (0,6 s / page), reprend les pages déjà sur disque
fi
python3 -I tools/extract.py
python3 -I tools/extract_hubs.py
rm -rf db/entities db/categories.json
python3 -I tools/normalize.py
python3 -I tools/extras.py
python3 -I tools/dl_assets.py          # ne télécharge que les ressources nouvelles
python3 -I tools/verify.py             # source -> base
( cd site && npm ci --silent && node scripts/prepare.mjs && npx astro build )
python3 -I tools/verify_dist.py        # base -> site construit
( cd site && npx astro build )         # reconstruit pour intégrer le rapport final
echo "OK. Rapport : db/integrity.json, db/dist_check.json, page /integrity/"
