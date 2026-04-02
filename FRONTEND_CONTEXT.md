# FPP — Contexte complet pour le développement Frontend

> Ce document contient TOUT le contexte nécessaire pour reprendre le développement du frontend Vue.js du projet FPP. À passer au LLM en début de nouvelle conversation.

---

## 1. Vue d'ensemble du projet

**FPP** = Front Patriotique Panafricain — Plateforme web pour un parti politique en Côte d'Ivoire.

**Architecture** : Backend Django (API REST) + Frontend Vue.js (SPA) + Future app Flutter.
- Backend : `http://localhost:8000/api/` (dev) / `https://api-fpp.monajent.com` (prod)
- Frontend : `http://localhost:5173` (dev Vite) / `https://fpp.monajent.com` (prod)

**Le backend est 100% terminé et testé.** Tous les endpoints fonctionnent. Il ne reste que le frontend à construire.

---

## 2. Stack frontend à utiliser

| Outil | Version | Rôle |
|-------|---------|------|
| **Vue 3** | latest | Framework (Composition API + `<script setup>`) |
| **Vite** | latest | Build tool |
| **Vue Router** | latest | Routing |
| **Pinia** | latest | State management |
| **Tailwind CSS** | v4 | Styling (aligné avec le design system) |
| **PrimeVue** | v4 | Composants UI (DataTable, Dialog, Toast, InputText, etc.) |
| **Lucide Vue** | latest | Icônes SVG |
| **Axios** | latest | HTTP client (avec interceptor pour le refresh JWT) |

**Dossier frontend** : `fpp-web/frontend/` (à créer à côté de `fpp-web/backend/`)

---

## 3. Design System — Résumé

Source complète : `design-system/fpp/MASTER.md`

### Palette (règle 60-30-10)
- **60%** : Blanc `#FFFFFF` + fond clair `#F6F7F6`
- **30%** : Noir `#111111` + texte secondaire `#52594F`
- **10%** : Vert accent `#16A34A` (CTA, liens, badges, focus)
- Vert hover : `#138A3E`
- Vert léger (bg badges) : `#DCFCE7`
- Bordures : `#E0E5E0`
- Sémantique : error `#DC2626`, warning `#D97706`, info `#2563EB`, success = accent

**IMPORTANT** : Tous les gris sont teintés vers le vert (hue 145). Pas de gris pur.

### Typographie
- **Titres** : Outfit (500, 600, 700) — `font-heading`
- **Corps** : Work Sans (300, 400, 500) — `font-body`
- Échelle major third (1.25) : xs 12px → 4xl 48px
- Max-width texte : `65ch`

```
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@500;600;700&family=Work+Sans:wght@300;400;500&display=swap');
```

### Espacement (base 4px)
xs=4px, sm=8px, md=12px, base=16px, lg=24px, xl=32px, 2xl=48px, 3xl=64px, 4xl=96px

### Composants
- Boutons : primaire (vert), secondaire (noir outline), ghost (vert texte)
- Cards : bg white, border 1px `#E0E5E0`, radius 12px, hover shadow
- Inputs : border 1.5px, radius 8px, focus ring vert
- Navbar : sticky, white bg, border-bottom, 64px height

### Motion
- Fast : 150ms (hover, focus)
- Normal : 200ms (transitions standard)
- Slow : 300ms (entrées, apparitions)
- Easing : `cubic-bezier(0.4, 0, 0.2, 1)`
- **PAS de bounce/elastic**
- Respecter `prefers-reduced-motion`

### Anti-patterns INTERDITS
- ❌ Dark mode
- ❌ Dégradés violet-bleu
- ❌ Gris pur sans teinte
- ❌ Polices Inter, Roboto, Arial
- ❌ Emojis comme icônes
- ❌ Cards dans des cards
- ❌ Glassmorphism décoratif
- ❌ Bounce/elastic easing

### Thème = Light mode uniquement

---

## 4. Personnalité de marque

- **3 mots** : Audacieux, Jeune, Panafricain
- **Émotions** : Espoir, Urgence, Énergie, Confiance
- **Ton** : Institutionnel mais accessible. Phrases courtes, orientées action
- **Référence visuelle** : [ONE.org Africa](https://www.one.org/africa/fr/)
- **Accessibilité** : WCAG AA (contraste 4.5:1, navigation clavier, focus visible)

---

## 5. Pages à construire — Site public

### 5.1 Page Accueil (`/`)
- Hero banner (image, titre, sous-titre, CTA "Adhérer")
- Message du président (photo + texte)
- Chiffres clés (total membres validés, articles publiés) → `GET /api/public/stats/`
- Valeurs du parti (section)
- Actualités récentes (3 articles featured) → `GET /api/public/articles/?featured=true`
- CTA d'adhésion final
- Footer (coordonnées, réseaux sociaux) → `GET /api/public/settings/`

### 5.2 Page Le Parti / À propos (`/a-propos`)
- Texte "about" → `GET /api/public/settings/` (champ `about_text`)
- Vision → champ `vision_text`
- Valeurs → champ `values_text`

### 5.3 Page Actualités (`/actualites`)
- Liste paginée des articles → `GET /api/public/articles/?page=X`
- Filtre par catégorie → `GET /api/public/articles/?category=slug`
- Sidebar : catégories → `GET /api/public/categories/`

### 5.4 Page Détail article (`/actualites/:slug`)
- Contenu complet → `GET /api/public/articles/{slug}/`
- Boutons partage (Facebook, Twitter/X, WhatsApp)
- Articles récents en sidebar ou "Lire aussi"

### 5.5 Page Adhérer (`/adherer`)
- **Étape 1** : Inscription compte → `POST /api/auth/register/`
  - Champs : email, password, password_confirm, first_name, last_name, sex, date_of_birth
  - Redirige vers page "Vérifiez votre email"
- **Étape 2** (après vérification email + login) : Demande d'adhésion → `POST /api/membership/request/`
  - Champs : id_document_type, id_document_number, id_document_scan, photo, city, commune, region, profession, neighborhood, address, motivation
  - Upload fichiers (multipart/form-data)
- Page de suivi : `GET /api/membership/status/`

### 5.6 Page Contact (`/contact`)
- Formulaire → `POST /api/public/contact/`
- Coordonnées du parti (WhatsApp, email, adresse) → depuis settings
- Liens réseaux sociaux

### 5.7 Pages Auth
- Login (`/login`) → `POST /api/auth/login/`
- Vérification email (`/verify-email?uid=X&token=Y`) → `POST /api/auth/verify-email/`
- Reset mot de passe (`/password-reset`) → `POST /api/auth/password/reset/`
- Confirmation reset (`/password-reset/confirm?uid=X&token=Y`) → `POST /api/auth/password/reset/confirm/`

---

## 6. Pages à construire — Backoffice admin (`/admin/...`)

### 6.1 Login admin (`/admin/login`)
- Formulaire email + mot de passe
- Redirige vers dashboard si déjà connecté

### 6.2 Dashboard (`/admin/dashboard`)
- KPI cards (total membres validés, en attente, articles publiés, contacts non lus)
- Graphique évolution adhésions → `GET /api/admin/dashboard/?period=30`
- Répartition par ville (top 10)
- Répartition par sexe
- → Endpoint : `GET /api/admin/dashboard/`

### 6.3 Gestion membres (`/admin/membres`)
- DataTable PrimeVue paginée, searchable, filtrable
- Filtres : statut, ville, commune, sexe, source
- Colonnes : matricule, nom, prénom, email, ville, statut
- Actions : voir fiche, changer statut
- Export Excel/CSV
- → `GET /api/admin/members/?page=X&search=Y&membership_status=Z`

### 6.4 Fiche membre (`/admin/membres/:id`)
- Toutes les infos + photo + scan pièce d'identité
- Rôles actifs
- Bouton changer statut → `PATCH /api/admin/members/{id}/status/`
- → `GET /api/admin/members/{id}/`

### 6.5 Gestion articles (`/admin/articles`)
- DataTable : titre, auteur, catégorie, statut, featured, date
- Boutons : créer, modifier, publier/dépublier, supprimer
- → `GET /api/admin/articles/`

### 6.6 Éditeur d'article (`/admin/articles/new` et `/admin/articles/:id/edit`)
- Formulaire : titre, résumé, contenu (éditeur riche), catégorie, image couverture, featured
- Statut : brouillon / publié
- → `POST /api/admin/articles/create/` ou `PATCH /api/admin/articles/{id}/`

### 6.7 Gestion contacts (`/admin/contacts`)
- Liste paginée avec filtre lu/non-lu
- Clic = détail + auto-marqué lu
- Export CSV
- → `GET /api/admin/contacts/`

### 6.8 Paramètres (`/admin/parametres`)
- Formulaire éditable : nom site, slogan, président, hero, réseaux sociaux, textes
- Upload logo, hero image, photo président
- → `GET /api/admin/settings/` + `PATCH /api/admin/settings/`

### 6.9 Journal d'audit (`/admin/audit`)
- DataTable filtrable par action, entité, utilisateur, date
- → `GET /api/admin/audit-log/?page=X&action=Y&entity_type=Z`

---

## 7. Référence API complète

Base URL : `http://localhost:8000/api/`

### Auth (cookies JWT httpOnly — pas de header Authorization côté web)
| Méthode | Endpoint | Auth | Description |
|---------|----------|------|-------------|
| POST | `/auth/register/` | Non | Inscription (retourne message, envoie email verif) |
| POST | `/auth/login/` | Non | Login (pose cookies access_token + refresh_token) |
| POST | `/auth/logout/` | Oui | Logout (blacklist token, supprime cookies) |
| GET | `/auth/me/` | Oui | Profil user + membership + roles |
| PATCH | `/auth/me/` | Oui | Modifier profil (first_name, last_name, phone, avatar) |
| POST | `/auth/password/change/` | Oui | Changer mot de passe |
| POST | `/auth/password/reset/` | Non | Demander reset (envoie email) |
| POST | `/auth/password/reset/confirm/` | Non | Confirmer reset (uid + token + new_password) |
| POST | `/auth/token/refresh/` | Cookie | Rafraîchir JWT (grace period 30s) |
| POST | `/auth/verify-email/` | Non | Vérifier email (uid + token) |
| POST | `/auth/resend-verification/` | Non | Renvoyer email verif |

### Membership
| POST | `/membership/request/` | Oui | Soumettre demande adhésion (multipart) |
| GET | `/membership/status/` | Oui | Voir statut de sa demande |

### Public (pas d'auth)
| GET | `/public/settings/` | Non | Paramètres du site |
| GET | `/public/articles/` | Non | Articles publiés (paginés). Query: `?category=slug&featured=true&search=X&page=X` |
| GET | `/public/articles/{slug}/` | Non | Détail article |
| GET | `/public/categories/` | Non | Catégories actives (avec article_count) |
| POST | `/public/contact/` | Non | Envoyer message contact |
| GET | `/public/stats/` | Non | Stats publiques (total_members, total_articles, total_categories) |

### Admin (auth + permissions)
| GET | `/admin/dashboard/` | can_view_dashboard | KPI complet |
| GET | `/admin/members/` | can_view_members | Liste paginée. Query: `?search=X&membership_status=X&city=X&sex=M&page=X` |
| GET | `/admin/members/{id}/` | can_view_members | Fiche détaillée + rôles |
| PATCH | `/admin/members/{id}/update/` | can_manage_members | Modifier infos |
| PATCH | `/admin/members/{id}/status/` | can_validate_membership | Body: `{"status":"validated","reason":"..."}` |
| GET | `/admin/members/export/` | can_export_members | CSV ou Excel (`?format=excel`) |
| POST | `/admin/membership/{id}/validate/` | is_staff | Body: `{"action":"validate"}` ou `{"action":"reject","reason":"..."}` |
| POST | `/admin/verify-matricule/` | is_staff | Body: `{"matricule":"FPP-..."}` |
| GET | `/admin/articles/` | can_create_article | Liste admin (draft + published) |
| POST | `/admin/articles/create/` | can_create_article | Créer article |
| GET | `/admin/articles/{id}/` | can_create_article | Détail |
| PATCH | `/admin/articles/{id}/` | can_edit_article | Modifier |
| DELETE | `/admin/articles/{id}/` | can_delete_article | Soft delete |
| GET/POST | `/admin/categories/` | can_manage_categories | Lister / Créer |
| PATCH/DELETE | `/admin/categories/{id}/` | can_manage_categories | Modifier / Supprimer |
| GET | `/admin/contacts/` | can_manage_contacts | Liste paginée. Query: `?is_read=true/false` |
| GET | `/admin/contacts/{id}/` | can_manage_contacts | Détail (auto-marque lu) |
| PATCH | `/admin/contacts/{id}/` | can_manage_contacts | Toggle lu/non-lu |
| GET | `/admin/contacts/export/` | can_export_contacts | Export CSV |
| GET | `/admin/settings/` | auth | Paramètres site |
| PATCH | `/admin/settings/` | can_manage_settings | Modifier paramètres |
| GET | `/admin/audit-log/` | can_view_audit_log | Journal paginé. Query: `?action=X&entity_type=X&user=uuid` |

### Format de pagination
```json
{
  "count": 42,
  "next": "http://localhost:8000/api/...?page=2",
  "previous": null,
  "results": [...]
}
```

---

## 8. Authentification côté frontend

### Mécanisme
- Les JWT sont stockés dans des **cookies httpOnly** (pas de localStorage).
- Le frontend n'a JAMAIS accès aux tokens directement.
- Axios doit envoyer `withCredentials: true` sur toutes les requêtes.
- Le cookie `access_token` est automatiquement envoyé par le navigateur.
- Le cookie `refresh_token` n'est envoyé qu'à `/api/auth/token/refresh/` (path restreint).

### Interceptor Axios recommandé
```js
// Si une requête retourne 401, tenter un refresh puis retry
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401 && !error.config._retry) {
      error.config._retry = true;
      try {
        await api.post('/auth/token/refresh/');
        return api(error.config);
      } catch {
        // Refresh échoué → déconnecter
        useAuthStore().logout();
        router.push('/login');
      }
    }
    return Promise.reject(error);
  }
);
```

### Store Auth (Pinia)
- `user` : objet user (depuis GET /auth/me/)
- `isAuthenticated` : boolean
- `isAdmin` : boolean (user.is_staff)
- `login(email, password)` → POST /auth/login/ puis GET /auth/me/
- `logout()` → POST /auth/logout/
- `fetchUser()` → GET /auth/me/ (appelé au mount de l'app)

---

## 9. Structure frontend recommandée

```
frontend/
├── index.html
├── vite.config.js
├── tailwind.config.js
├── package.json
├── public/
│   └── favicon.svg
├── src/
│   ├── main.js
│   ├── App.vue
│   ├── api/
│   │   └── index.js          # Instance Axios + interceptors
│   ├── stores/
│   │   ├── auth.js            # Store auth (user, login, logout)
│   │   └── settings.js        # Store settings (site_name, slogan, socials)
│   ├── router/
│   │   └── index.js           # Routes public + admin + guards
│   ├── composables/
│   │   ├── useApi.js           # Wrapper fetch paginé
│   │   └── useToast.js         # Notifications
│   ├── layouts/
│   │   ├── PublicLayout.vue    # Navbar + Footer (site public)
│   │   └── AdminLayout.vue     # Sidebar + Topbar (backoffice)
│   ├── components/
│   │   ├── common/             # Boutons, Cards, Inputs, Loader, EmptyState
│   │   ├── public/             # Hero, StatsCounter, ArticleCard, etc.
│   │   └── admin/              # DataTable wrappers, StatusBadge, etc.
│   └── views/
│       ├── public/
│       │   ├── HomeView.vue
│       │   ├── AboutView.vue
│       │   ├── NewsView.vue
│       │   ├── NewsDetailView.vue
│       │   ├── JoinView.vue
│       │   └── ContactView.vue
│       ├── auth/
│       │   ├── LoginView.vue
│       │   ├── VerifyEmailView.vue
│       │   ├── PasswordResetView.vue
│       │   └── PasswordResetConfirmView.vue
│       └── admin/
│           ├── DashboardView.vue
│           ├── MembersView.vue
│           ├── MemberDetailView.vue
│           ├── ArticlesView.vue
│           ├── ArticleEditorView.vue
│           ├── ContactsView.vue
│           ├── SettingsView.vue
│           └── AuditLogView.vue
```

---

## 10. Guards de navigation (Vue Router)

```js
// Public : accessible à tous
// Auth : accessible uniquement si NON connecté (login, register)
// Protected : accessible uniquement si connecté
// Admin : accessible uniquement si connecté + is_staff
// Permission : accessible si user a la permission spécifique
```

---

## 11. Variables d'environnement frontend

```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_SITE_NAME=FPP - Front Patriotique Panafricain
```

---

## 12. Utilisateurs de test (dans la base Docker actuelle)

| Email | Mot de passe | Rôle | Groupe |
|-------|-------------|------|--------|
| admin@fpp-ci.online | Admin@FPP2026 | Superuser + staff | Super Admin (toutes perms) |
| gestionnaire@fpp-ci.online | Gest@FPP2026 | Staff | Gestionnaire (membres, articles, contacts, dashboard) |
| editeur@fpp-ci.online | Edit@FPP2026 | Staff | Éditeur (articles + catégories uniquement) |
| partisan@fpp-ci.online | Part@FPP2026 | User normal | Aucun (accès public + profil) |

---

## 13. Docker — Backend déjà running

```bash
cd fpp-web
docker compose up -d       # Démarre tout (db, redis, backend, celery, backup)
docker compose logs -f backend   # Logs
```

Backend écoute sur `http://localhost:8000`. Pas besoin de rebuilder sauf si on modifie le backend.

---

## 14. Fichiers de référence du projet

| Fichier | Contenu |
|---------|---------|
| `Plan.md` | Cahier des charges fonctionnel complet |
| `SPECS.md` | Spécifications techniques (modèles, API, permissions, règles métier) |
| `SENIOR_CHECKLIST.md` | Checklist senior backend (Phase 1 terminée, Phases 2-3 à faire) |
| `design-system/fpp/MASTER.md` | Design system complet (palette, typo, composants, motion) |
| `.impeccable.md` | Contexte design (users, personnalité, principes) |
| `.cursorrules` | Règles Cursor persistantes |
| `backend/apps/api/urls.py` | Toutes les routes API |

---

## 15. Ordre de développement recommandé

### Phase A — Setup + Site public
1. Init projet Vite + Vue 3 + Tailwind + PrimeVue + Router + Pinia
2. Configurer Axios (withCredentials, interceptor refresh)
3. Layout public (Navbar + Footer) avec données de `GET /api/public/settings/`
4. Page Accueil (hero, stats, actualités, CTA)
5. Page Actualités (liste + détail)
6. Page À propos
7. Page Contact
8. Page Adhérer (inscription + demande adhésion)
9. Pages Auth (login, verify-email, password reset)

### Phase B — Backoffice admin
1. Layout admin (sidebar + topbar)
2. Dashboard (KPI + graphiques)
3. Gestion membres (DataTable + fiche + statut + export)
4. Gestion articles (DataTable + éditeur)
5. Gestion contacts
6. Paramètres du site
7. Journal d'audit

### Phase C — Polish
1. Responsive (375px, 768px, 1024px, 1440px)
2. Loading states, empty states, error states partout
3. Animations d'entrée (stagger 50ms)
4. SEO meta tags
5. PWA / manifest
