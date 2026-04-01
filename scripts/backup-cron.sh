#!/bin/bash
# ============================================================================
# FPP — Boucle de backup (tourne en continu dans le conteneur)
# Exécute une sauvegarde toutes les 24h à 2h du matin
# ============================================================================

set -e

echo "[backup-cron] Démarrage du service de sauvegarde automatique..."

while true; do
    CURRENT_HOUR=$(date +%H)

    if [ "$CURRENT_HOUR" = "02" ]; then
        /scripts/backup.sh
        sleep 3600
    fi

    sleep 1800
done
