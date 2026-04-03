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



###### 
Pour activer en production

1.Rebuild l'image backend (inclut pyzipper + migration + nouvelle app)

2.Redéployer sur Dokploy

3.La migration 0004 s'exécutera automatiquement au démarrage (web)

4.Ajouter EMERGENCY_EMAILS=email1,email2,... dans les variables Dokploy (backend + celery)

5.Exécuter python manage.py setup_periodic_tasks pour enregistrer la tâche de rotation

6.Marquer le(s) utilisateur(s) autorisé(s) : User.objects.filter(email="...").update(is_emergency_user=True) via le shell Django

/admin/emergency/status/ - url admin

Pour accéder à la vue d'état des codes d'urgence en production, il suffit d'aller sur https://api.fpp-ci.online/admin/emergency/status/.