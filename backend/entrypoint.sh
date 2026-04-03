#!/bin/bash
set -e

MAX_RETRIES=30
PROCESS_TYPE=${PROCESS_TYPE:-web}

echo "🔧 PROCESS_TYPE = ${PROCESS_TYPE}"

# ---------------------------------------------------------------------------
# 1. Attendre PostgreSQL
# ---------------------------------------------------------------------------
echo "⏳ Attente de PostgreSQL (${POSTGRES_HOST:-db}:${POSTGRES_PORT:-5432})..."
retries=0
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
    retries=$((retries + 1))
    if [ $retries -ge $MAX_RETRIES ]; then
        echo "❌ PostgreSQL injoignable après ${MAX_RETRIES} tentatives"
        exit 1
    fi
    echo "⏳ PostgreSQL non prêt — tentative ${retries}/${MAX_RETRIES}..."
    sleep 2
done
echo "✅ PostgreSQL prêt"

# ---------------------------------------------------------------------------
# 2. Attendre Redis
# ---------------------------------------------------------------------------
if [ -n "$REDIS_URL" ]; then
    echo "⏳ Attente de Redis..."
    retries=0
    while ! python -c "
import os, redis
redis.from_url(os.environ['REDIS_URL'], socket_connect_timeout=2).ping()
" 2>/dev/null; do
        retries=$((retries + 1))
        if [ $retries -ge $MAX_RETRIES ]; then
            echo "❌ Redis injoignable après ${MAX_RETRIES} tentatives"
            exit 1
        fi
        sleep 2
    done
    echo "✅ Redis prêt"
fi

# ---------------------------------------------------------------------------
# 3. Lancer le processus selon PROCESS_TYPE
# ---------------------------------------------------------------------------
case "$PROCESS_TYPE" in
    celery-worker)
        echo "🚀 Démarrage Celery Worker"
        exec celery -A config worker -l info --concurrency=2 --hostname=worker1@%h
        ;;
    celery-beat)
        echo "🚀 Démarrage Celery Beat"
        exec celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
        ;;
    web)
        echo "⏳ Migrations..."
        python manage.py migrate --noinput
        echo "⏳ Collectstatic..."
        python manage.py collectstatic --noinput --clear 2>/dev/null || true
        echo "🚀 Démarrage Daphne sur 0.0.0.0:8000"
        exec daphne -b 0.0.0.0 -p 8000 --proxy-headers config.asgi:application
        ;;
    *)
        echo "❌ PROCESS_TYPE inconnu : ${PROCESS_TYPE}"
        echo "   Valeurs acceptées : web, celery-worker, celery-beat"
        exit 1
        ;;
esac
