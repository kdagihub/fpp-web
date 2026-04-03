# FPP — Guide de déploiement Dokploy

## Architecture cible

```
fpp-ci.online (frontend) ──► nginx ──► /api/ ──► api.fpp-ci.online (backend)
                                       /media/ ──► backend media files

Services Dokploy :
┌──────────────────────────────────────────────────────────────┐
│  1. fpp-postgres      (Database PostgreSQL)                   │
│  2. fpp-redis         (Database Redis)                        │
│  3. fpp-backend       (Application — Daphne)    PROCESS_TYPE=web            │
│  4. fpp-celery-worker (Application — Worker)    PROCESS_TYPE=celery-worker  │
│  5. fpp-celery-beat   (Application — Beat)      PROCESS_TYPE=celery-beat    │
│  6. fpp-frontend      (Application — Nginx)                   │
└──────────────────────────────────────────────────────────────┘

Même image Docker (ciacems/fpp:backend-v1) pour les services 3, 4, 5.
Le PROCESS_TYPE détermine le rôle — aucune commande à mettre dans Advanced.
```

---

## Étape 1 — Build & Push des images

> Prérequis : `docker login` sur Docker Hub et `docker buildx` configuré.

### Backend

```bash
docker buildx build --push \
  -t ciacems/fpp:backend-v1 \
  -f backend/Dockerfile.prod \
  ./backend
```

### Frontend

```bash
docker buildx build --push \
  --build-arg VITE_API_BASE_URL=https://api.fpp-ci.online/api \
  --build-arg VITE_SITE_NAME="FPP - Front Patriotique Panafricain" \
  -t ciacems/fpp:frontend-v1 \
  -f frontend/Dockerfile.prod \
  ./frontend
```

---

## Étape 2 — Créer les Databases dans Dokploy

### 2.1 PostgreSQL

| Champ             | Valeur                  |
|-------------------|-------------------------|
| Name              | `fpp-postgres`          |
| Docker Image      | `postgres:16-alpine`    |
| Database Name     | `fpp_db`                |
| Database User     | `fpp_user`              |
| Database Password | *(mot de passe fort)*   |

> Après création, noter le **hostname interne** Dokploy (ex: `fpp-postgres`).

### 2.2 Redis

| Champ        | Valeur             |
|--------------|--------------------|
| Name         | `fpp-redis`        |
| Docker Image | `redis:7-alpine`   |

> Après création, noter le **hostname interne** (ex: `fpp-redis`).

---

## Étape 3 — Créer les Applications dans Dokploy

### 3.1 Backend (Django/Daphne)

| Champ      | Valeur                       |
|------------|------------------------------|
| Name       | `fpp-backend`                |
| Type       | Docker (External Registry)   |
| Image      | `ciacems/fpp:backend-v1`    |
| Port       | `8000`                       |

**Variables d'environnement :**

```env
# ── Django ──
DJANGO_SETTINGS_MODULE=config.settings.production
DJANGO_SECRET_KEY=<GÉNÉRER: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())">
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=api.fpp-ci.online,fpp-backend

# ── PostgreSQL (utiliser le hostname interne Dokploy) ──
POSTGRES_DB=fpp_db
POSTGRES_USER=fpp_user
POSTGRES_PASSWORD=<MOT_DE_PASSE_POSTGRES>
POSTGRES_HOST=<HOSTNAME_INTERNE_POSTGRES>
POSTGRES_PORT=5432

# ── Redis (utiliser le hostname interne Dokploy) ──
REDIS_URL=redis://<HOSTNAME_INTERNE_REDIS>:6379/0

# ── JWT ──
JWT_ACCESS_TOKEN_LIFETIME=15
JWT_REFRESH_TOKEN_LIFETIME=10080

# ── CORS ──
CORS_ALLOWED_ORIGINS=https://fpp-ci.online,https://www.fpp-ci.online

# ── Media ──
MEDIA_ROOT=/app/media

# ── Matricule ──
MATRICULE_SECRET_KEY=<GÉNÉRER: python -c "import secrets; print(secrets.token_hex(32))">

# ── Email (Hostinger SMTP) ──
EMAIL_HOST=smtp.hostinger.com
EMAIL_PORT=465
EMAIL_HOST_USER=info@fpp-ci.online
EMAIL_HOST_PASSWORD=<MOT_DE_PASSE_EMAIL>
EMAIL_USE_TLS=False
EMAIL_USE_SSL=True
DEFAULT_FROM_EMAIL=info@fpp-ci.online
SERVER_EMAIL=info@fpp-ci.online
CONTACT_DEST_EMAIL=info@fpp-ci.online

# ── Frontend ──
FRONTEND_URL=https://fpp-ci.online
```

**Volumes (persistants) :**

| Mount Path     | Description           |
|----------------|-----------------------|
| `/app/media`   | Fichiers médias       |
| `/app/staticfiles` | Fichiers statiques |

**Domaine :** `api.fpp-ci.online` → port `8000`, HTTPS activé.

---

### 3.2 Celery Worker

| Champ      | Valeur                       |
|------------|------------------------------|
| Name       | `fpp-celery-worker`          |
| Type       | Docker (External Registry)   |
| Image      | `ciacems/fpp:backend-v1`    |

**Variables d'environnement :**
Identiques au backend + ajouter :

```env
PROCESS_TYPE=celery-worker
```

**Volumes :**

| Mount Path   | Description                         |
|--------------|-------------------------------------|
| `/app/media` | Même volume que le backend (partagé)|

> Pas de domaine ni de port exposé.

---

### 3.3 Celery Beat

| Champ      | Valeur                       |
|------------|------------------------------|
| Name       | `fpp-celery-beat`            |
| Type       | Docker (External Registry)   |
| Image      | `ciacems/fpp:backend-v1`    |

**Variables d'environnement :**
Identiques au backend + ajouter :

```env
PROCESS_TYPE=celery-beat
```

> Pas de volume, domaine, ni port nécessaire.

---

### 3.4 Backup PostgreSQL (Dokploy → Cloudflare R2)

Pas de conteneur supplémentaire — utiliser le **backup intégré de Dokploy** vers Cloudflare R2.

**Étape 1 — Créer la destination S3 dans Dokploy :**

Dokploy → **S3 Destinations** → **Add Destination** :

| Champ            | Valeur                                                          |
|------------------|-----------------------------------------------------------------|
| Name             | `FPP R2 Backups`                                                |
| Provider         | `Cloudflare R2 Storage`                                         |
| Access Key Id    | *(même clé API R2 que monajent)*                                |
| Secret Access Key| *(même secret que monajent)*                                    |
| Bucket           | `fpp-backups`                                                   |
| Region           | `auto`                                                          |
| Endpoint         | `https://478a04a0573a507a104004d51faea431.r2.cloudflarestorage.com` |

> Vérifier que le token R2 (`monajent-back`) a bien le bucket `fpp-backups`
> dans ses autorisations (Cloudflare → R2 → API Tokens → Edit).

**Étape 2 — Configurer le backup PostgreSQL :**

`fppostgres` → **Backups** → **Create Backup** :

| Champ                | Valeur                       |
|----------------------|------------------------------|
| Destination          | `FPP R2 Backups`             |
| Database             | `fppostgres`                 |
| Schedule             | `0 2 * * *`                  |
| Prefix Destination   | `pg/`                        |
| Keep the latest      | `7`                          |
| Enabled              | Activé                       |

**Étape 3 — Valider** : lancer un backup manuel pour vérifier.

> Les scripts `scripts/backup.sh` restent dans le repo comme solution de secours.

---

### 3.5 Frontend (Nginx + Vue)

| Champ      | Valeur                       |
|------------|------------------------------|
| Name       | `fpp-frontend`               |
| Type       | Docker (External Registry)   |
| Image      | `ciacems/fpp:frontend-v1`   |
| Port       | `80`                         |

**Domaine :** `fpp-ci.online` → port `80`, HTTPS activé.

> **Important :** Le `nginx.conf` intégré dans l'image proxy les requêtes `/api/` et `/media/`
> vers `fpp-backend:8000`. Vérifier que le hostname interne Dokploy du backend
> correspond bien à `fpp-backend`. Sinon, adapter `nginx.conf` avant le build.

---

## Étape 4 — Vérification du hostname réseau

Tous les services Dokploy sur le même projet partagent un réseau Docker interne.
Les hostnames utilisés dans `nginx.conf` (`fpp-backend`) doivent correspondre au
**App Name** du service backend dans Dokploy.

Pour vérifier :

1. Dans Dokploy, aller dans les paramètres du service `fpp-backend`
2. Chercher le "Service Name" ou "Container Name" — c'est le hostname réseau
3. Si différent de `fpp-backend`, modifier `nginx.conf` et rebuild le frontend

---

## Étape 5 — Ordre de déploiement

```
1. fpp-postgres       ──► Attendre que la DB soit prête
2. fpp-redis          ──► Attendre que Redis soit prêt
3. fpp-backend        ──► Migrations + collectstatic + Daphne
4. fpp-celery-worker  ──► Se connecte à la même DB + Redis
5. fpp-celery-beat    ──► Se connecte à la même DB + Redis
6. fpp-frontend       ──► Se connecte au backend via réseau interne

+ Activer le backup intégré Dokploy sur fpp-postgres (schedule: 0 2 * * *)
```

---

## Étape 6 — Post-déploiement

### Créer le superuser

Se connecter au terminal du conteneur `fpp-backend` dans Dokploy :

```bash
python manage.py createsuperuser
```

### Vérifier les services

```bash
# Depuis le terminal du backend
python manage.py check --deploy

# Tester l'envoi d'email
python manage.py shell -c "
from django.core.mail import send_mail
send_mail('Test FPP', 'Déploiement OK', 'info@fpp-ci.online', ['votre@email.com'])
"
```

### Vérifier les URLs

| URL                                | Attendu                     |
|------------------------------------|-----------------------------|
| `https://fpp-ci.online`            | Frontend Vue (page d'accueil) |
| `https://api.fpp-ci.online/api/public/settings/` | JSON config site |
| `https://api.fpp-ci.online/admin/` | Django admin                 |

---

## Commandes utiles — Rebuild & Redéploiement

### Rebuild backend uniquement

```bash
docker buildx build --push \
  -t ciacems/fpp:backend-v1 \
  -f backend/Dockerfile.prod \
  ./backend
```

Puis dans Dokploy → Redeploy : `fpp-backend`, `fpp-celery-worker`, `fpp-celery-beat`.

### Rebuild frontend uniquement

```bash
docker buildx build --push \
  --build-arg VITE_API_BASE_URL=https://api.fpp-ci.online/api \
  --build-arg VITE_SITE_NAME="FPP - Front Patriotique Panafricain" \
  -t ciacems/fpp:frontend-v1 \
  -f frontend/Dockerfile.prod \
  ./frontend
```

Puis dans Dokploy → `fpp-frontend` → Redeploy.

### Rebuild tout

```bash
# Backend + Celery
docker buildx build --push \
  -t ciacems/fpp:backend-v1 \
  -f backend/Dockerfile.prod \
  ./backend

# Frontend
docker buildx build --push \
  --build-arg VITE_API_BASE_URL=https://api.fpp-ci.online/api \
  --build-arg VITE_SITE_NAME="FPP - Front Patriotique Panafricain" \
  -t ciacems/fpp:frontend-v1 \
  -f frontend/Dockerfile.prod \
  ./frontend
```

Puis Redeploy les 4 services applicatifs dans Dokploy.

---

## DNS requis (chez Hostinger ou autre)

| Type  | Nom               | Valeur              | TTL  |
|-------|--------------------|---------------------|------|
| A     | `fpp-ci.online`    | IP du serveur Dokploy | 300 |
| A     | `api.fpp-ci.online`| IP du serveur Dokploy | 300 |
| CNAME | `www`              | `fpp-ci.online`     | 300  |

---

## Backups — Vérification & Restauration

### Vérifier les backups

Via l'interface Dokploy : `fpp-postgres` → **Backups** → historique des sauvegardes.

### Restaurer un backup

Via Dokploy : sélectionner le backup souhaité → **Restore**.

Ou manuellement depuis le terminal `fpp-backend` :

```bash
gunzip -c backup_file.sql.gz | \
  PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB
```

### Sauvegarder les médias

Les fichiers médias (photos, documents) sont dans le volume `/app/media`.
Pour une sauvegarde complète, copier aussi ce volume périodiquement.

---

## Troubleshooting

| Problème | Solution |
|----------|----------|
| `502 Bad Gateway` sur `/api/` | Vérifier que `fpp-backend` est démarré et que le hostname dans `nginx.conf` est correct |
| Cookies JWT non envoyés | Vérifier que `CORS_ALLOWED_ORIGINS` inclut le domaine frontend et que HTTPS est actif |
| Emails non envoyés | Vérifier les credentials SMTP et que le service `fpp-celery` tourne |
| Migrations échouent | Vérifier la connectivité PostgreSQL (hostname, port, credentials) |
| Media files 404 | Vérifier que le volume `/app/media` est monté et partagé entre backend et celery |
