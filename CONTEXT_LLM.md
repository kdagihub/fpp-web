# FPP — Contexte complet pour nouveau LLM (avril 2026)

> Ce document résume l'état actuel du projet pour reprendre le développement dans une nouvelle conversation.

---

## 1. Projet

**FPP** = Front Patriotique Panafricain — Plateforme web complète pour un parti politique en Côte d'Ivoire.

**Repo** : `https://github.com/kdagihub/fpp-web.git`
**Branche active** : `documents` (la plus avancée)
**Autres branches** : `develop`, `main`

**Production** :
- Frontend : `https://fpp-ci.online` (Nginx, Dokploy)
- Backend API : `https://api.fpp-ci.online/api/` (Django/Daphne, Dokploy)

**Dev local** :
- Backend Docker : `http://localhost:8000/api/`
- Frontend Vite : `http://localhost:5173`

---

## 2. Architecture technique

### Backend (Django 5 + DRF)
| Composant | Détail |
|-----------|--------|
| Framework | Django 5 + Django REST Framework |
| Auth | JWT via cookies httpOnly (access + refresh) |
| DB | PostgreSQL |
| Cache/Queue | Redis (Celery, Channels, DRF throttling) |
| Serveur | Daphne (ASGI) |
| PDF | WeasyPrint |
| Email | Django EmailMultiAlternatives + templates HTML |
| Déploiement | Dokploy (Docker) : backend, celery-worker, celery-beat, postgres, redis, frontend |

### Frontend (Vue 3 SPA)
| Composant | Détail |
|-----------|--------|
| Framework | Vue 3 (Composition API + `<script setup>` + TypeScript) |
| Build | Vite |
| Routing | Vue Router (createWebHistory, beforeEach guards, meta permissions) |
| State | Pinia (`useAuthStore`, `useSettingsStore`) |
| UI | PrimeVue (Tag, etc.) + Tailwind CSS v4 (variables CSS custom) |
| Icons | Lucide Vue Next |
| HTTP | Axios (withCredentials, interceptor refresh JWT) |
| Rich text | TipTap (articles) |
| Date | dayjs (locale fr) |

### Design System
- **Palette 60-30-10** : blanc/fond clair 60%, noir/texte 30%, vert accent `#16A34A` 10%
- **Typo** : Outfit (titres), Work Sans (corps)
- **Variables CSS** : `--color-primary`, `--color-accent`, `--color-muted`, `--color-border`, `--color-surface`, `--color-accent-light`, `--color-accent-hover`
- **Light mode uniquement**, pas de dark mode
- **Mobile-first responsive** (Tailwind breakpoints sm/md/lg)

---

## 3. Structure des fichiers clés

```
fpp-web/
├── backend/
│   ├── apps/
│   │   ├── accounts/          # Modèle User, tasks email
│   │   ├── api/
│   │   │   ├── urls.py        # Toutes les routes API
│   │   │   ├── permissions.py # Permissions custom DRF
│   │   │   ├── throttle.py    # Throttling custom
│   │   │   ├── serializers/   # auth, content, members, membership, bureau, contact, site_settings
│   │   │   └── views/         # auth, content, members, membership, bureau, contact, dashboard, pdf, share, audit, site_settings
│   │   ├── content/
│   │   │   └── models.py      # Article, Category, MediaContent, Event, ProgramSection, ProgramItem, Document
│   │   └── emergency/         # Purge d'urgence
│   ├── config/settings/       # base.py, production.py
│   └── templates/
│       ├── emails/            # base.html + tous les templates email (avec logo)
│       └── pdf/               # fiches inscription/adhésion
├── frontend/
│   ├── src/
│   │   ├── api/index.ts       # Axios instance + interceptor refresh
│   │   ├── stores/            # auth.ts, settings.ts
│   │   ├── router/index.ts    # Routes + guards
│   │   ├── types/index.ts     # Interfaces TypeScript
│   │   ├── layouts/           # PublicLayout, AdminLayout, MemberLayout
│   │   ├── components/        # SplashScreen, ShareDialog, WelcomeModal
│   │   └── views/
│   │       ├── public/        # Home, About, News, Contact, Join, Programme, Agenda, FppTv, Documents, CGU, Privacy
│   │       ├── auth/          # Login, VerifyEmail, PasswordReset
│   │       ├── member/        # Dashboard, Profile, Card, Settings, Join
│   │       └── admin/         # Dashboard, Members, Articles, Media, Contacts, Documents, Bureau, Settings, AuditLog, Emergency, VerifyMatricule
│   └── nginx.conf             # Config Nginx frontend (SPA fallback, X-Frame-Options SAMEORIGIN)
├── FRONTEND_CONTEXT.md        # Contexte initial détaillé (API ref, design system, pages à construire)
├── DEPLOY.md                  # Guide déploiement Dokploy complet
└── docker-compose.yml
```

---

## 4. Modules fonctionnels — État actuel

### ✅ Site public
| Page | Route | État |
|------|-------|------|
| Accueil | `/` | ✅ Complet (hero, stats, actualités, CTA) |
| À propos | `/a-propos` | ✅ Complet |
| Actualités | `/actualites` | ✅ Liste paginée + détail + partage social |
| Programme | `/programme` | ✅ Complet |
| Agenda | `/agenda` | ✅ Complet |
| FPP-TV | `/fpp-tv` | ✅ Complet (vidéos YouTube/plateforme) |
| Documents | `/documents` | ✅ Complet (grille/liste toggle, aperçu PDF natif, filtres catégorie, modal preview) |
| Adhérer | `/adherer` | ✅ Inscription 2 phases (compte + demande adhésion) |
| Contact | `/contact` | ✅ Formulaire + coordonnées |
| CGU / Privacy | `/cgu`, `/politique-confidentialite` | ✅ Complet |

### ✅ Espace membre (`/mon-espace/...`)
| Page | État |
|------|------|
| Dashboard | ✅ Aperçu profil + statut adhésion |
| Profil | ✅ Infos + suivi demande adhésion |
| Carte membre | ✅ Carte virtuelle recto/verso |
| Paramètres | ✅ Changement mot de passe |
| Adhésion | ✅ Formulaire demande |
| Actualités / Agenda / Programme / FPP-TV / Documents | ✅ Même contenu que public |

### ✅ Dashboard admin (`/admin/...`)
| Module | Route admin | État |
|--------|-------------|------|
| Dashboard | `/admin/dashboard` | ✅ KPI + graphiques (Chart.js) |
| Membres | `/admin/membres` | ✅ DataTable, filtres, export, fiche détaillée, changement statut |
| Articles | `/admin/articles` | ✅ CRUD, éditeur TipTap, catégories, brouillon/publié, prévisualisation modal |
| FPP-TV/Médias | `/admin/fpp-tv` | ✅ CRUD médias (YouTube, Facebook, etc.), auto-détection plateforme |
| Contacts | `/admin/contacts` | ✅ Liste, lu/non-lu, export CSV |
| Documents | `/admin/documents` | ✅ CRUD, aperçu dans formulaire, modal vue détaillée avec preview PDF/image |
| Bureau National | `/admin/bureau` | ✅ Gestion des membres du bureau |
| Paramètres | `/admin/parametres` | ✅ Tous les champs site |
| Vérification matricule | `/admin/verification-matricule` | ✅ |
| Journal d'audit | `/admin/audit` | ✅ Filtrable |
| Purge d'urgence | `/admin/urgence` | ✅ Réservé emergency_user |

### ✅ Fonctionnalités transversales
- **Splash screen** : écran "gate" animé avec logo FPP, devise, slogan, rotation de 4 vidéos (random par session via sessionStorage/localStorage)
- **Partage social** : ShareDialog (Facebook, Twitter/X, WhatsApp, copie lien) sur articles, événements, programme
- **Logo dans emails** : logo FPP injecté dans tous les templates email via `_send_html_email`
- **PDF** : fiches inscription/adhésion vierges, carte membre admin
- **Navigation publique** : dropdown "Le Parti" (Présentation + Documents & Ressources), FPP-TV en item top-level
- **Auth** : JWT cookies httpOnly, refresh automatique, guards de permission par route

---

## 5. API — Endpoints récents (module Documents)

```
GET    /api/public/documents/                    # Liste docs publics (is_public=True), filtres: category, search
POST   /api/public/documents/<uuid>/download/    # Incrémente compteur DL
GET    /api/public/documents/<uuid>/preview/     # Sert le fichier inline (@xframe_options_exempt) pour aperçu iframe

GET    /api/admin/documents/                     # Liste tous les docs (filtres: category, is_public, search)
POST   /api/admin/documents/                     # Créer (FormData: title, description, category, is_public, file)
GET    /api/admin/documents/<uuid>/              # Détail
PATCH  /api/admin/documents/<uuid>/              # Modifier
DELETE /api/admin/documents/<uuid>/              # Supprimer
GET    /api/admin/documents/<uuid>/preview/      # Aperçu admin (auth required, @xframe_options_exempt)
```

**Modèle Document** : title, description, file (FileField), category (statuts/rapport/communique/formulaire/autre), is_public, uploaded_by (FK User), download_count, file_size. Permission : `can_manage_documents`.

---

## 6. Points techniques importants

### X-Frame-Options & aperçu documents
- Django `XFrameOptionsMiddleware` bloque l'embedding par défaut (protection clickjacking)
- Endpoints `/preview/` utilisent `@xframe_options_exempt` pour permettre les iframes PDF
- Seuls les endpoints de prévisualisation de fichiers bruts sont exemptés (aucun risque)

### Détection des formats de fichiers (frontend)
```typescript
function getExt(url: string): string {
  const clean = url.split('?')[0]!.split('#')[0]!.replace(/\/+$/, '')
  return (clean.split('.').pop() ?? '').toLowerCase()
}
```
Types supportés : pdf, image (jpg/png/webp/gif), spreadsheet (xls/xlsx/csv), word (doc/docx), archive (zip/rar), code, autre.

### Rate Limiting
- `AnonBurstThrottle` + `UserBurstThrottle` dans `DEFAULT_THROTTLE_CLASSES`
- Commande management `flush_throttle` pour vider le cache Redis
- Rates augmentées pour éviter les 429 sur les pages publiques

### Splash Screen vidéo
- 4 vidéos en rotation (splash0-3.mp4 dans `assets/img/`)
- Sélection aléatoire via `sessionStorage` (consistant dans la session) + `localStorage` (différent entre sessions)
- Écran "gate" avec interaction utilisateur requise pour activer l'audio (politique navigateur)

---

## 7. Permissions backend (groupes)

| Permission | Description |
|-----------|-------------|
| `can_view_dashboard` | Voir le tableau de bord admin |
| `can_view_members` | Voir la liste des membres |
| `can_manage_members` | Modifier les membres |
| `can_validate_membership` | Valider/rejeter les adhésions |
| `can_export_members` | Exporter les membres |
| `can_create_article` | Créer des articles |
| `can_edit_article` | Modifier des articles |
| `can_delete_article` | Supprimer des articles |
| `can_manage_categories` | Gérer les catégories |
| `can_manage_media` | Gérer les médias FPP-TV |
| `can_manage_contacts` | Gérer les messages de contact |
| `can_manage_events` | Gérer les événements |
| `can_manage_program` | Gérer le programme |
| `can_manage_documents` | Gérer les documents |
| `can_manage_settings` | Gérer les paramètres du site |
| `can_view_audit_log` | Voir le journal d'audit |
| `can_export_contacts` | Exporter les contacts |

---

## 8. Utilisateurs de test

| Email | Mot de passe | Rôle |
|-------|-------------|------|
| admin@fpp-ci.online | Admin@FPP2026 | Superuser (toutes perms) |
| gestionnaire@fpp-ci.online | Gest@FPP2026 | Gestionnaire |
| editeur@fpp-ci.online | Edit@FPP2026 | Éditeur |
| partisan@fpp-ci.online | Part@FPP2026 | User normal |

---

## 9. Docker / Déploiement

```bash
cd fpp-web
docker compose up -d                              # Dev local
docker compose exec backend python manage.py ...  # Commandes Django
```

Production via **Dokploy** avec 6 services Docker (postgres, redis, backend/daphne, celery-worker, celery-beat, frontend/nginx). Voir `DEPLOY.md` pour le guide complet.

---

## 10. Historique Git (branche documents)

```
00c014b feat: module Documents complet (backend + frontend admin & public)
cb2a6c8 feat: logo dans les emails, splashscreen premium avec rotation vidéos
58035dd fix: correctifs API media/articles, rate limiting, prévisualisation articles admin
cf7001f feat: modules admin FPP TV, Contacts, Articles + correctifs KPI mobile + partage réseaux sociaux
b2eab9b Dashboard admin avancé avant première rencontre du FPP
87b77b2 feat: procédure d'urgence, contenu politique réel, améliorations UX
b26dcc3 feat: déploiement production Dokploy + contenu public complet
f3ab279 Passage au frontend
c5f9f0f feat: inscription 2 phases, matricule HMAC, vérification email, SMTP Hostinger
608332a Config initial terminé passage à optimisation de l'architecture et du code
4b83a10 Configuration de base du projet
9c53dae Initial commit
```

---

## 11. Fichiers de référence

| Fichier | Contenu |
|---------|---------|
| `FRONTEND_CONTEXT.md` | Contexte initial détaillé (API complète, design system, pages à construire) |
| `DEPLOY.md` | Guide déploiement Dokploy pas-à-pas |
| `CONTEXT_LLM.md` | Ce fichier — bilan actuel pour nouveau LLM |
| `backend/apps/api/urls.py` | Toutes les routes API (215 lignes) |
| `backend/apps/api/views/content.py` | Vues content les plus volumineuses (1023 lignes) |
| `backend/apps/content/models.py` | Modèles Article, MediaContent, Event, Program, Document (333 lignes) |
| `frontend/src/router/index.ts` | Toutes les routes frontend + guards (277 lignes) |
| `frontend/src/types/index.ts` | Interfaces TypeScript complètes (431 lignes) |

---

## 12. Prochaines étapes potentielles

- Merge branche `documents` → `develop` → `main`
- Déploiement de la migration `0005_add_document_model` en production
- Tests end-to-end sur les modules récents
- Optimisations performance (lazy loading images, bundle splitting)
- SEO meta tags sur les pages publiques
- PWA / manifest pour installation mobile
