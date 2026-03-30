#!/bin/bash
# ============================================================================
# FPP — Sauvegarde PostgreSQL automatique
# Lancé quotidiennement par le conteneur backup (via cron ou boucle)
# Rétention : 7 jours — les backups plus anciens sont supprimés
# ============================================================================

set -e

BACKUP_DIR="/backups"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
FILENAME="${POSTGRES_DB:-fpp_db}_${TIMESTAMP}.sql.gz"
RETENTION_DAYS=7

echo "[backup] Sauvegarde de ${POSTGRES_DB} vers ${BACKUP_DIR}/${FILENAME}..."

PGPASSWORD="${POSTGRES_PASSWORD}" pg_dump \
    -h "${POSTGRES_HOST:-db}" \
    -p "${POSTGRES_PORT:-5432}" \
    -U "${POSTGRES_USER:-fpp_user}" \
    -d "${POSTGRES_DB:-fpp_db}" \
    --no-owner \
    --no-privileges \
    | gzip > "${BACKUP_DIR}/${FILENAME}"

echo "[backup] Sauvegarde terminée : ${FILENAME} ($(du -h "${BACKUP_DIR}/${FILENAME}" | cut -f1))"

echo "[backup] Suppression des backups de plus de ${RETENTION_DAYS} jours..."
find "${BACKUP_DIR}" -name "*.sql.gz" -mtime +${RETENTION_DAYS} -delete

REMAINING=$(find "${BACKUP_DIR}" -name "*.sql.gz" | wc -l)
echo "[backup] ${REMAINING} backup(s) restant(s)."
