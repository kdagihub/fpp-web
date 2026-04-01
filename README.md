# fpp-web

# Tout démarrer
docker compose up -d

# Tout arrêter
docker compose down

# Voir les logs
docker compose logs -f backend

# Lancer une commande Django
docker compose run --rm backend python manage.py <commande>

# Backup manuel
docker compose exec backup /scripts/backup.sh


 #### GENERER DES SECRET KEY ######

# Tout générer (Django key + mot de passe DB)
python scripts/generate_secrets.py

# Juste une SECRET_KEY Django
python scripts/generate_secrets.py --key-only

# Juste un mot de passe base de données
python scripts/generate_secrets.py --password-only

# Longueur personnalisée (ex: 64 caractères)
python scripts/generate_secrets.py --length 64
python scripts/generate_secrets.py --key-only --length 100