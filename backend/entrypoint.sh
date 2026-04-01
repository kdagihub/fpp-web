#!/bin/bash
set -e

# ============================================================================
# FPP Backend — Entrypoint
# Attend PostgreSQL, lance les migrations, collectstatic, puis le serveur.
# ============================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# ---------------------------------------------------------------------------
# 1. Attendre que PostgreSQL soit prêt
# ---------------------------------------------------------------------------
echo -e "${YELLOW}[entrypoint] Attente de PostgreSQL (${POSTGRES_HOST}:${POSTGRES_PORT})...${NC}"

MAX_RETRIES=30
RETRY_COUNT=0

while ! python -c "
import socket, sys
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(5)
try:
    s.connect(('${POSTGRES_HOST:-db}', ${POSTGRES_PORT:-5432}))
    s.close()
except (OSError, ConnectionRefusedError):
    sys.exit(1)
" 2>/dev/null; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ "$RETRY_COUNT" -ge "$MAX_RETRIES" ]; then
        echo -e "${RED}[entrypoint] PostgreSQL non disponible après ${MAX_RETRIES} tentatives. Abandon.${NC}"
        exit 1
    fi
    echo -e "${YELLOW}[entrypoint] PostgreSQL non prêt — tentative ${RETRY_COUNT}/${MAX_RETRIES}...${NC}"
    sleep 2
done

echo -e "${GREEN}[entrypoint] PostgreSQL est prêt.${NC}"

# ---------------------------------------------------------------------------
# 2. Migrations (uniquement pour le service principal, pas les workers Celery)
# ---------------------------------------------------------------------------
if [ "$1" = "daphne" ] || [ "$1" = "gunicorn" ]; then
    echo -e "${YELLOW}[entrypoint] Application des migrations...${NC}"
    python manage.py migrate --noinput

    echo -e "${YELLOW}[entrypoint] Collecte des fichiers statiques...${NC}"
    python manage.py collectstatic --noinput --clear 2>/dev/null || true

    echo -e "${GREEN}[entrypoint] Backend prêt.${NC}"
fi

# ---------------------------------------------------------------------------
# 3. Lancer la commande passée (daphne, celery, etc.)
# ---------------------------------------------------------------------------
exec "$@"
