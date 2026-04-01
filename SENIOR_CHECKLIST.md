# Checklist Senior — Lacunes à combler

Audit réalisé sur le Bloc 1 (Authentification API).
Chaque item est classé par axe, priorisé, et référence le fichier concerné.

---

## 1. Transactions DB / Atomicité

- [ ] **Register atomique** — Envelopper la création `User` + `MemberProfile` dans `transaction.atomic()` pour éviter les users orphelins si le MemberProfile échoue
  - Fichier : `apps/api/serializers/auth.py` → `RegisterSerializer.create()`
  - Priorité : **CRITIQUE**

- [ ] **Login atomique** — Envelopper la création `RefreshToken` + `UserSession` + `AuditLog` dans `transaction.atomic()`
  - Fichier : `apps/api/views/auth.py` → `LoginView.post()`
  - Priorité : **HAUTE**

- [ ] **Logout atomique** — Envelopper `token.blacklist()` + `UserSession.update()` + `AuditLog` dans `transaction.atomic()`
  - Fichier : `apps/api/views/auth.py` → `LogoutView.post()`
  - Priorité : **HAUTE**

- [ ] **Password change atomique** — Envelopper `set_password()` + `OutstandingToken.delete()` dans `transaction.atomic()`
  - Fichier : `apps/api/views/auth.py` → `PasswordChangeView.post()`
  - Priorité : **HAUTE**

- [ ] **Password reset confirm atomique** — Même pattern
  - Fichier : `apps/api/views/auth.py` → `PasswordResetConfirmView.post()`
  - Priorité : **HAUTE**

- [ ] **Race condition matricule** — Utiliser `select_for_update()` ou `F()` expression pour la génération séquentielle du matricule afin d'éviter les doublons en cas d'inscriptions simultanées
  - Fichier : `apps/members/models.py` → `_generate_matricule()`
  - Priorité : **HAUTE**

---

## 2. Celery — Tâches asynchrones

- [ ] **Créer `apps/core/tasks.py`** — Tâches transversales
  - `send_email_task(subject, body, recipients)` — wrapper générique d'envoi d'email
  - `log_audit_async(user_id, action, entity_type, entity_id, changes, ip, ua)` — écriture AuditLog déportée
  - Priorité : **HAUTE**

- [ ] **Créer `apps/accounts/tasks.py`** — Tâches liées aux comptes
  - `send_password_reset_email(user_id, uid, token)` — envoi de l'email de reset
  - `send_welcome_email(user_id)` — email de bienvenue post-inscription
  - `notify_admins_new_registration(user_id)` — notification aux admins
  - Priorité : **HAUTE**

- [ ] **Créer `apps/user_sessions/tasks.py`** — Tâches périodiques sessions
  - `cleanup_expired_sessions()` — fermer les UserSession inactives depuis > 24h (périodique, quotidienne à 3h)
  - Priorité : **MOYENNE**

- [ ] **Créer `apps/api/tasks.py`** — Tâches liées aux tokens
  - `flush_expired_blacklisted_tokens()` — purger les tokens expirés de `token_blacklist` (périodique, quotidienne à 4h)
  - Priorité : **MOYENNE**

- [ ] **Brancher les tâches dans les vues** — Remplacer les appels synchrones
  - `PasswordResetView` : appeler `send_password_reset_email.delay()` au lieu de `pass`
  - `RegisterView` : appeler `send_welcome_email.delay()` + `notify_admins_new_registration.delay()`
  - Évaluer si `AuditMixin.log_action()` doit appeler `log_audit_async.delay()` (trade-off : on perd la garantie d'écriture immédiate)
  - Priorité : **HAUTE**

- [ ] **Enregistrer les tâches périodiques** — Via `django_celery_beat` dans le Django admin ou via une commande `setup_periodic_tasks`
  - Priorité : **MOYENNE**

---

## 3. Cache Redis — Stratégie d'invalidation

- [ ] **Cache sur `GET /api/auth/me/`** — Clé `user_profile:{user_id}`, TTL 5 min, invalidation sur `PATCH /api/auth/me/`
  - Fichier : `apps/api/views/auth.py` → `MeView`
  - Priorité : **MOYENNE**

- [ ] **Cache sur les listes publiques** (articles, catégories) — Clé avec paramètres de pagination/filtre, TTL 2 min, invalidation sur CREATE/UPDATE/DELETE
  - Fichier : vues futures des blocs Content
  - Priorité : **MOYENNE**

- [ ] **Séparer les bases Redis** — Celery broker sur `/0`, Channels sur `/2`, cache sur `/1` (actuellement Celery et Channels partagent `/0`)
  - Fichier : `config/settings/base.py` → `CHANNEL_LAYERS`, `CELERY_BROKER_URL`
  - Priorité : **BASSE**

- [ ] **Cache des permissions user** — `user.has_perm()` fait une requête DB à chaque appel. Cacher les permissions du user dans Redis avec invalidation au changement de groupe
  - Priorité : **BASSE** (peu d'impact tant que < 1000 users actifs)

---

## 4. Idempotence

- [ ] **Token refresh idempotent** — Si le frontend envoie 2x le même refresh token (réseau instable), le 2e appel échoue et déconnecte le user. Solutions possibles :
  - Grace period : après blacklist d'un refresh, garder le nouveau access/refresh en cache Redis pendant 30s. Si le même ancien refresh arrive, retourner les mêmes nouveaux tokens depuis le cache
  - Fichier : `apps/api/views/auth.py` → `CookieTokenRefreshView`
  - Priorité : **HAUTE** (surtout pour le mobile Flutter)

- [ ] **Login idempotent** — 2 appels = 2 UserSession. Ajouter une vérification : si une session active existe pour le même user-agent + IP, réutiliser la session au lieu d'en créer une nouvelle
  - Fichier : `apps/api/views/auth.py` → `_create_session()`
  - Priorité : **MOYENNE**

- [ ] **Register idempotent** — 2 appels avec le même email : le 2e retourne une erreur de validation. C'est correct mais l'erreur devrait être un 409 Conflict plutôt qu'un 400
  - Fichier : `apps/api/serializers/auth.py` → `RegisterSerializer.validate_email()`
  - Priorité : **BASSE**

---

## 5. Optimisation des requêtes (N+1, select_related, prefetch_related)

- [ ] **N+1 sur `GET /api/auth/me/`** — Le user est récupéré sans `select_related("member_profile")`. DRF fait une requête lazy pour le profil membre
  - Fichier : `apps/api/views/auth.py` → `MeView.get()` — utiliser `User.objects.select_related("member_profile").get(pk=request.user.pk)` au lieu de `request.user`
  - Priorité : **HAUTE**

- [ ] **Vues futures (membres, articles, etc.)** — Systématiquement utiliser `select_related` (FK/O2O) et `prefetch_related` (M2M/reverse FK) dans les querysets des ListAPIView
  - Priorité : **HAUTE**

- [ ] **Ajouter `django-debug-toolbar`** en local pour détecter visuellement les N+1
  - Fichier : `config/settings/local.py`
  - Priorité : **MOYENNE**

---

## 6. Sécurité — Renforcements

- [ ] **Throttle par compte cible** sur le login — En plus du throttle par IP (5/min), ajouter un throttle par email cible (10 tentatives/heure par email) pour contrer les botnets
  - Fichier : `apps/api/throttle.py` + `apps/api/views/auth.py`
  - Priorité : **HAUTE**

- [ ] **Validation taille des champs texte libres** — `motivation` (TextField) n'a pas de `max_length`. Un user pourrait envoyer 10 Mo. Ajouter `MaxLengthValidator` ou `max_length` dans le serializer
  - Fichier : `apps/api/serializers/auth.py` → `RegisterSerializer.motivation`
  - Priorité : **MOYENNE**

- [ ] **CSRF double-submit pour les cookies JWT** — Les vues DRF exemptent le CSRF par défaut. Ajouter un custom middleware ou utiliser `X-CSRFToken` header pour les mutations quand l'auth est par cookie
  - Fichier : nouveau middleware ou configuration DRF
  - Priorité : **MOYENNE**

- [ ] **Audit des accès admin** — Logger les accès au Django admin dans l'AuditLog (signal `user_logged_in` de Django)
  - Fichier : `apps/core/signals.py`
  - Priorité : **BASSE**

---

## 7. HTTP / REST — Bonnes pratiques

- [ ] **Versioning API** — Préfixer toutes les routes par `/api/v1/`. Si le contrat change, créer `/api/v2/` sans casser les clients existants
  - Fichier : `config/urls.py` + `apps/api/urls.py`
  - Priorité : **HAUTE**

- [ ] **Error handler custom** — DRF retourne des formats d'erreur différents (validation vs permission vs 500). Créer un `EXCEPTION_HANDLER` custom qui retourne toujours `{"detail": ..., "code": ..., "errors": {...}}`
  - Fichier : nouveau `apps/api/exceptions.py` + `base.py` → `REST_FRAMEWORK["EXCEPTION_HANDLER"]`
  - Priorité : **MOYENNE**

- [ ] **Health check endpoint** — `GET /api/health/` qui vérifie DB + Redis + Celery, retourne 200 ou 503. Utile pour Docker healthcheck et monitoring
  - Fichier : `apps/api/views/health.py` + `apps/api/urls.py`
  - Priorité : **MOYENNE**

---

## 8. Design Patterns — Architecture

- [ ] **Service Layer** — Extraire la logique métier des serializers/views vers des services dédiés (`apps/accounts/services.py` avec `AccountService.register()`, `AccountService.login()`, etc.)
  - Priorité : **MOYENNE** (à faire avant que le code grossisse)

- [ ] **Custom Managers** — Ajouter des méthodes aux managers pour les requêtes courantes :
  - `UserSession.objects.active()` → `.filter(is_active=True)`
  - `MemberProfile.objects.pending()` → `.filter(membership_status="pending")`
  - `AuditLog.objects.for_user(user)` → `.filter(user=user)`
  - Priorité : **BASSE**

- [ ] **Django Signals** — Déclencher des actions post-événement (email bienvenue, notification admin) via signals plutôt que dans les vues, pour découpler la logique
  - Fichier : `apps/accounts/signals.py` + `apps/accounts/apps.py` → `ready()`
  - Priorité : **BASSE**

---

## 9. Pagination avancée

- [ ] **CursorPagination pour les grandes listes** — `PageNumberPagination` exécute `COUNT(*)` à chaque page (lent sur 100k+ lignes). Proposer `CursorPagination` comme alternative pour les listes admin (membres, audit logs)
  - Fichier : `apps/api/pagination.py`
  - Priorité : **BASSE** (pertinent uniquement à grande échelle)

---

## 10. Scalabilité — Préparation production

- [ ] **Multiple workers Daphne/Gunicorn** — Actuellement 1 seul process Daphne. En prod, configurer Gunicorn avec 4-8 workers pour les endpoints REST, et Daphne uniquement pour les WebSockets
  - Fichier : `docker-compose.yml` → commande backend, ou `Procfile`
  - Priorité : **MOYENNE** (avant mise en production)

- [ ] **Connection pooling PostgreSQL** — Utiliser `django-db-connection-pool` ou `pgbouncer` pour éviter d'ouvrir une connexion DB par requête
  - Priorité : **BASSE** (pertinent > 200 requêtes/s)

---

## Ordre de priorité recommandé

### Phase 1 — Corrections critiques (avant de continuer les blocs)
1. Transactions atomiques sur toutes les vues auth
2. Race condition matricule
3. Créer les fichiers `tasks.py` et brancher le reset password sur Celery
4. Idempotence du token refresh (grace period)

### Phase 2 — Renforcements (pendant les blocs suivants)
5. Versioning API `/api/v1/`
6. Error handler custom
7. N+1 fix sur `/api/auth/me/`
8. Throttle par compte cible sur le login
9. Validation taille des inputs texte
10. Tâches périodiques Celery (cleanup sessions, purge tokens)

### Phase 3 — Optimisations (avant production)
11. Cache Redis sur les endpoints fréquents
12. Health check endpoint
13. Service Layer
14. Multiple workers Gunicorn
15. Séparation bases Redis
16. CursorPagination




J'ai tout analysé. Voici l'explication complète et l'audit de sécurité JWT.

---

## JWT vs Session — Explication concrète pour le projet FPP

### Session Authentication (classique Django)

```
Login → Le serveur crée une entrée en base (session table)
      → Le serveur envoie un cookie "sessionid=abc123" au navigateur
      → À chaque requête, le navigateur envoie ce cookie
      → Le serveur lit "abc123", cherche en base la session, trouve le user
```

**Avantages :**
- Simple, natif Django
- Facile à révoquer (supprimer la ligne en base = déconnexion immédiate)
- Un seul cookie opaque (pas de données sensibles côté client)

**Inconvénients :**
- **Chaque requête** = 1 requête DB pour lire la session → scalabilité limitée
- **Stateful** : le serveur doit stocker l'état. Si tu as 3 serveurs derrière un load balancer, il faut un "sticky session" ou un store Redis partagé
- **Pas adapté aux apps mobile** : Flutter/mobile ne gère pas nativement les cookies de session Django

### JWT Authentication (notre choix)

```
Login → Le serveur génère 2 tokens signés (access 15min + refresh 7j)
      → Les tokens contiennent le user_id encodé + signé cryptographiquement
      → À chaque requête, le serveur vérifie la signature (pas de DB)
      → Le refresh token permet de renouveler l'access token
```

**Avantages :**
- **Stateless** : pas besoin de chercher en base à chaque requête → bien plus performant
- **Scalable** : 10 serveurs peuvent vérifier le même JWT indépendamment
- **Multi-plateforme** : fonctionne pour le web (Vue.js), le mobile (Flutter), et les API tierces
- **Cross-domain** : le frontend sur `fpp-ci.online` et l'API sur `api.fpp-ci.online` peuvent communiquer

**Inconvénients :**
- Révocation complexe (d'où le blacklist qu'on utilise)
- Si mal stocké (localStorage), vulnérable au XSS

### Pourquoi JWT est le bon choix pour FPP

Ton architecture = **frontend séparé** (Vue.js sur `fpp-ci.online`) + **API** (Django sur `api.fpp-ci.online`) + **future app Flutter**. C'est exactement le cas d'usage pour JWT. L'auth session ne fonctionnerait pas bien en cross-domain.

---

## Audit sécurité de notre implémentation JWT — Résultat

| Critère de sécurité | Statut | Implémentation |
|---|---|---|
| **Tokens en cookies httpOnly** | **OK** | `AUTH_COOKIE_HTTP_ONLY: True` dans `set_jwt_cookies()` — JavaScript ne peut PAS lire les tokens |
| **Flag Secure (HTTPS only)** | **OK** | `AUTH_COOKIE_SECURE: True` en prod, `False` en local |
| **SameSite=Lax** | **OK** | Protège contre les CSRF simples (formulaires cross-site) |
| **Refresh token path restreint** | **OK** | `AUTH_COOKIE_REFRESH_PATH: /api/auth/token/refresh/` — le cookie refresh n'est envoyé QUE vers cet endpoint |
| **Rotation des refresh tokens** | **OK** | `ROTATE_REFRESH_TOKENS: True` — chaque refresh génère un nouveau refresh |
| **Blacklist après rotation** | **OK** | `BLACKLIST_AFTER_ROTATION: True` — l'ancien refresh est invalidé |
| **Access token courte durée** | **OK** | 15 minutes (`JWT_ACCESS_TOKEN_LIFETIME=15`) |
| **Grace period idempotence** | **OK** | `CookieTokenRefreshView` avec cache Redis 30s pour réseau instable |
| **Logout = blacklist + session fermée** | **OK** | `LogoutView` blacklist le token + ferme la `UserSession` |
| **Password change = révoque tout** | **OK** | `PasswordChangeView` supprime tous les `OutstandingToken` |
| **Fallback header Authorization** | **OK** | `CookieJWTAuthentication` — cookie d'abord, puis header (pour Flutter/tests) |

**Verdict : notre JWT est correctement sécurisé.** Les tokens sont bien dans des cookies `httpOnly` + `Secure` + `SameSite=Lax`, ce qui est la configuration recommandée par l'OWASP pour les SPA.

---

## Bilan des phases SENIOR_CHECKLIST

| Phase | Statut |
|---|---|
| **Phase 1** — Transactions atomiques, race condition, Celery tasks, idempotence refresh | **TERMINEE** |
| **Phase 2** — Versioning API, error handler, N+1, throttle avancé, validation, tâches périodiques | **A FAIRE** |
| **Phase 3** — Cache Redis, health check, service layer, workers Gunicorn, Redis séparation | **A FAIRE** |

Concernant ta question "est-ce qu'on peut passer à autre chose" : **oui**. Le système d'authentification est complet et sécurisé. On peut maintenant attaquer les APIs du cahier des charges (Plan.md) tout en intégrant progressivement les items de Phase 2 du checklist *au fur et à mesure*.

La prochaine étape logique selon le cahier des charges serait d'implémenter les **APIs du MVP** :

1. **Content (Blog/Actualités)** — CRUD articles, catégories, publication
2. **Contact** — formulaire de contact, gestion messages
3. **Dashboard admin** — statistiques (nombre membres, adhésions récentes, répartition par ville)
4. **Members admin** — liste paginée, filtres, recherche, export Excel/CSV

Veux-tu qu'on attaque ces blocs ? Si oui, par lequel souhaites-tu commencer ?