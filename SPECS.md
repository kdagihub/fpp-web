# FPP — Spécifications Techniques Détaillées

## 1. Acteurs du système

| Acteur | Code | Description |
|--------|------|-------------|
| Visiteur | `VISITOR` | Utilisateur non authentifié, consulte le site public |
| Partisan | `PARTISAN` | Membre inscrit via le formulaire d'adhésion, compte actif |
| Responsable local | `LOCAL_LEADER` | Gère les membres de sa zone géographique (Phase 2) |
| Administrateur | `ADMIN` | Gestion complète : membres, contenus, dashboard |
| Super Admin | `SUPER_ADMIN` | Accès total, gestion des rôles, paramètres système |

---

## 2. Cas d'usage (Use Cases)

### 2.1 Site public

| ID | Cas d'usage | Acteur | Description |
|----|-------------|--------|-------------|
| UC-01 | Consulter l'accueil | VISITOR | Voir bannière, message du président, stats, actualités récentes, CTA adhésion |
| UC-02 | Consulter "Le Parti" | VISITOR | Lire histoire, vision, idéologie, valeurs, organisation |
| UC-03 | Consulter le programme | VISITOR | Lire la vision politique et les axes programmatiques |
| UC-04 | Lister les actualités | VISITOR | Voir la liste paginée des articles publiés |
| UC-05 | Lire un article | VISITOR | Consulter le détail d'un article avec partage réseaux sociaux |
| UC-06 | Adhérer au parti | VISITOR | Remplir le formulaire d'adhésion et soumettre sa candidature |
| UC-07 | Contacter le parti | VISITOR | Envoyer un message via le formulaire de contact |
| UC-08 | Partager un article | VISITOR | Partager sur Facebook, Twitter, WhatsApp |

### 2.2 Authentification

| ID | Cas d'usage | Acteur | Description |
|----|-------------|--------|-------------|
| UC-10 | S'inscrire (adhérer) | VISITOR | Créer un compte via le formulaire d'adhésion |
| UC-11 | Se connecter | PARTISAN, ADMIN | Authentification par email/matricule + mot de passe |
| UC-12 | Se déconnecter | PARTISAN, ADMIN | Suppression du JWT cookie |
| UC-13 | Réinitialiser mot de passe | PARTISAN, ADMIN | Demande de reset par email |
| UC-14 | Changer mot de passe | PARTISAN, ADMIN | Modification depuis le profil |
| UC-15 | Consulter son profil | PARTISAN, ADMIN | Voir et modifier ses informations personnelles |

### 2.3 Backoffice — Gestion des membres

| ID | Cas d'usage | Acteur | Description |
|----|-------------|--------|-------------|
| UC-20 | Voir le dashboard | ADMIN | Stats : total adhésions, récentes, par ville, articles publiés, évolution |
| UC-21 | Lister les membres | ADMIN | Liste paginée avec recherche et filtres |
| UC-22 | Rechercher un membre | ADMIN | Par nom, prénom, téléphone, email, ville, commune, matricule |
| UC-23 | Filtrer les membres | ADMIN | Par statut, sexe, ville, commune, rôle, date d'inscription |
| UC-24 | Voir fiche membre | ADMIN | Détail complet d'un adhérent + ses rôles + historique |
| UC-25 | Modifier un membre | ADMIN | Mise à jour des informations |
| UC-26 | Changer statut adhésion | ADMIN | Valider, suspendre, rejeter une adhésion |
| UC-27 | Exporter les membres | ADMIN | Export Excel/CSV avec filtres appliqués |

### 2.4 Backoffice — Gestion des contenus

| ID | Cas d'usage | Acteur | Description |
|----|-------------|--------|-------------|
| UC-30 | Créer un article | ADMIN | Titre, résumé, contenu, image, catégorie |
| UC-31 | Modifier un article | ADMIN | Mise à jour des champs |
| UC-32 | Publier/dépublier | ADMIN | Changer le statut de publication |
| UC-33 | Supprimer un article | ADMIN | Suppression logique (soft delete) |
| UC-34 | Gérer les catégories | ADMIN | CRUD des catégories d'articles |
| UC-35 | Prévisualiser un article | ADMIN | Voir le rendu avant publication |

### 2.5 Backoffice — Messages de contact

| ID | Cas d'usage | Acteur | Description |
|----|-------------|--------|-------------|
| UC-40 | Lister les messages | ADMIN | Liste paginée avec statut lu/non lu |
| UC-41 | Lire un message | ADMIN | Détail du message, marquage automatique comme lu |
| UC-42 | Exporter les messages | ADMIN | Export CSV |

### 2.6 Backoffice — Gestion des rôles

| ID | Cas d'usage | Acteur | Description |
|----|-------------|--------|-------------|
| UC-50 | Lister les rôles du parti | ADMIN | Voir tous les rôles existants |
| UC-51 | Créer un rôle | SUPER_ADMIN | Définir un nouveau rôle avec nom, description, niveau |
| UC-52 | Modifier un rôle | SUPER_ADMIN | Mettre à jour les informations d'un rôle |
| UC-53 | Assigner un rôle à un membre | ADMIN | Affecter un rôle (avec zone optionnelle) |
| UC-54 | Retirer un rôle à un membre | ADMIN | Désactiver une affectation (conserve l'historique) |
| UC-55 | Voir l'historique des rôles d'un membre | ADMIN | Tracer toutes les affectations passées et présentes |
| UC-56 | Gérer les groupes de permissions | SUPER_ADMIN | Créer/modifier les groupes Django (contrôle d'accès API) |

### 2.7 Backoffice — Monitoring des sessions

| ID | Cas d'usage | Acteur | Description |
|----|-------------|--------|-------------|
| UC-57 | Voir les utilisateurs connectés | ADMIN | Liste des sessions actives en temps réel |
| UC-58 | Voir l'historique des connexions | ADMIN | Historique complet : qui, quand, d'où, quel appareil |
| UC-59 | Déconnecter une session à distance | SUPER_ADMIN | Forcer la fin d'une session d'un utilisateur |

### 2.8 Backoffice — Journal d'audit

| ID | Cas d'usage | Acteur | Description |
|----|-------------|--------|-------------|
| UC-60 | Consulter le journal d'audit | SUPER_ADMIN | Voir toutes les actions effectuées sur la plateforme |
| UC-61 | Filtrer le journal | SUPER_ADMIN | Par utilisateur, type d'action, entité, date |

---

## 3. User Stories

### 3.1 Visiteur

```
US-01 : En tant que visiteur, je veux voir la page d'accueil du parti
        pour comprendre rapidement son identité et ses valeurs.

US-02 : En tant que visiteur, je veux lire les actualités du parti
        pour suivre ses actions et prises de position.

US-03 : En tant que visiteur, je veux adhérer en ligne
        pour rejoindre le parti sans me déplacer.
        Critères d'acceptation :
        - Le formulaire contient : nom, prénom, email, téléphone, sexe,
          date de naissance, ville, commune, quartier, profession, adresse, motivation
        - Validation côté client ET serveur
        - Détection de doublons (email, téléphone)
        - Message de confirmation après soumission
        - Notification admin (email ou dashboard)

US-04 : En tant que visiteur, je veux contacter le parti
        pour poser une question ou faire une remarque.

US-05 : En tant que visiteur, je veux partager un article sur les réseaux sociaux
        pour diffuser les actions du parti.
```

### 3.2 Partisan (membre inscrit)

```
US-10 : En tant que partisan, je veux me connecter avec mon email et mot de passe
        pour accéder à mon espace personnel.

US-11 : En tant que partisan, je veux consulter mon profil
        pour vérifier mes informations d'adhésion et mes rôles.

US-12 : En tant que partisan, je veux modifier mon mot de passe
        pour sécuriser mon compte.

US-13 : En tant que partisan, je veux réinitialiser mon mot de passe
        si je l'ai oublié, via un lien envoyé par email.
```

### 3.3 Administrateur

```
US-20 : En tant qu'admin, je veux voir un tableau de bord
        avec les KPI du parti (total membres, adhésions récentes,
        répartition géographique, articles publiés).

US-21 : En tant qu'admin, je veux rechercher un membre par nom, téléphone ou matricule
        pour retrouver rapidement sa fiche.

US-22 : En tant qu'admin, je veux filtrer les membres par statut, localisation et rôle
        pour avoir une vue segmentée de la base.

US-23 : En tant qu'admin, je veux valider ou rejeter une demande d'adhésion
        pour contrôler les entrées dans le parti.

US-24 : En tant qu'admin, je veux exporter la liste des membres en Excel
        pour l'exploiter hors plateforme.

US-25 : En tant qu'admin, je veux créer et publier un article
        pour communiquer les actions du parti.

US-26 : En tant qu'admin, je veux gérer les messages de contact
        pour répondre aux sollicitations du public.

US-27 : En tant qu'admin, je veux assigner un rôle à un membre
        pour structurer l'organisation du parti.

US-28 : En tant qu'admin, je veux consulter le journal d'audit
        pour tracer qui a fait quoi et quand sur la plateforme.
```

---

## 4. Modèle Conceptuel de Données (MCD)

### 4.0 Modèle abstrait de base

Toutes les tables héritent d'un modèle abstrait `TimeStampedModel` :

| Champ | Type | Description |
|-------|------|-------------|
| created_at | DateTimeField | auto_now_add — date de création |
| updated_at | DateTimeField | auto_now — date de dernière modification |

Cela garantit la **traçabilité temporelle** sur l'intégralité des entités.

### 4.1 Diagramme textuel

```
┌────────────────────┐
│  TimeStampedModel   │  (abstrait — hérité par TOUTES les tables)
│────────────────────│
│ created_at         │
│ updated_at         │
└────────────────────┘

┌─────────────────────┐       ┌──────────────────────┐
│      User            │       │     MemberProfile     │
│─────────────────────│       │──────────────────────│
│ id (PK, UUID)       │       │ id (PK, UUID)        │
│ email (unique)      │──1:1──│ user (FK → User)     │
│ phone (unique)      │       │ matricule (unique)   │
│ first_name          │       │ sex                  │
│ last_name           │       │ date_of_birth        │
│ is_active           │       │ profession           │
│ is_staff            │       │ address              │
│ date_joined         │       │ region               │
│ password            │       │ city                 │
│ groups (M2M Django) │       │ commune              │
│ created_at ⏱        │       │ neighborhood         │
│ updated_at ⏱        │       │ motivation           │
└─────────────────────┘       │ membership_status    │
         │                    │ membership_date      │
         │ 1:N                │ registration_source  │
         ▼                    │ photo                │
┌─────────────────────┐       │ created_at ⏱         │
│   UserPartyRole      │       │ updated_at ⏱         │
│─────────────────────│       └──────────────────────┘
│ id (PK, UUID)       │
│ user (FK → User)    │       ┌──────────────────────┐
│ role (FK → Role)  ──│──N:1──│     PartyRole         │
│ zone (FK → Zone)    │       │──────────────────────│
│ assigned_by (FK)    │       │ id (PK, UUID)        │
│ is_active           │       │ name (unique)        │
│ ended_at            │       │ slug (unique)        │
│ created_at ⏱        │       │ description          │
│ updated_at ⏱        │       │ level                │
└─────────────────────┘       │ is_active            │
                              │ created_at ⏱         │
                              │ updated_at ⏱         │
                              └──────────────────────┘

┌─────────────────────┐       ┌──────────────────────┐
│      Zone            │       │     Article           │
│─────────────────────│       │──────────────────────│
│ id (PK, UUID)       │       │ id (PK, UUID)        │
│ name                │       │ title                │
│ type                │       │ slug (unique)        │
│ parent (FK self)    │       │ summary              │
│ is_active           │       │ content              │
│ created_at ⏱        │       │ cover_image          │
│ updated_at ⏱        │       │ status               │
└─────────────────────┘       │ author (FK → User)   │
                              │ category (FK)        │
┌─────────────────────┐       │ is_featured          │
│     Category         │       │ published_at         │
│─────────────────────│       │ deleted_at (soft)    │
│ id (PK, UUID)       │       │ created_at ⏱         │
│ name (unique)       │──1:N──│ updated_at ⏱         │
│ slug (unique)       │       └──────────────────────┘
│ description         │
│ is_active           │
│ created_at ⏱        │
│ updated_at ⏱        │
└─────────────────────┘

┌─────────────────────┐       ┌──────────────────────┐
│   ContactMessage     │       │    SiteSettings       │
│─────────────────────│       │──────────────────────│
│ id (PK, UUID)       │       │ id (PK)              │
│ name                │       │ site_name            │
│ email               │       │ slogan               │
│ phone               │       │ president_name       │
│ subject             │       │ president_message    │
│ message             │       │ president_photo      │
│ is_read             │       │ whatsapp_number      │
│ read_at             │       │ contact_email        │
│ created_at ⏱        │       │ address              │
│ updated_at ⏱        │       │ facebook_url         │
└─────────────────────┘       │ twitter_url          │
                              │ instagram_url        │
┌─────────────────────┐       │ youtube_url          │
│     AuditLog         │       │ logo                 │
│─────────────────────│       │ hero_image           │
│ id (PK, UUID)       │       │ hero_title           │
│ user (FK → User)    │       │ hero_subtitle        │
│ action              │       │ about_text           │
│ entity_type         │       │ vision_text          │
│ entity_id           │       │ values_text          │
│ changes (JSON)      │       │ created_at ⏱         │
│ ip_address          │       │ updated_at ⏱         │
│ created_at ⏱        │       └──────────────────────┘
└─────────────────────┘
```

### 4.2 Relations

| Relation | Type | Description |
|----------|------|-------------|
| User ↔ MemberProfile | 1:1 | Chaque user a un profil membre (créé à l'inscription) |
| User ↔ PartyRole | M:N via UserPartyRole | Un membre peut avoir plusieurs rôles, un rôle peut être porté par plusieurs membres |
| UserPartyRole → Zone | N:1 (optionnel) | Une affectation de rôle peut être liée à une zone géographique |
| UserPartyRole.assigned_by → User | N:1 | Qui a assigné le rôle |
| Zone → Zone (parent) | Auto-référence | Hiérarchie : région > district > commune > quartier |
| User → Article | 1:N | Un admin peut écrire plusieurs articles |
| Category → Article | 1:N | Une catégorie regroupe plusieurs articles |
| User → AuditLog | 1:N | Un utilisateur génère plusieurs entrées d'audit |
| User ↔ Group (Django) | M:N natif | Groupes de permissions pour le contrôle d'accès technique |
| SiteSettings | Singleton | Une seule ligne, contient les paramètres du site |

### 4.3 Détail des champs

#### TimeStampedModel (abstrait)

Hérité par **toutes les tables** du projet.

| Champ | Type | Contraintes | Description |
|-------|------|-------------|-------------|
| created_at | DateTimeField | auto_now_add | Date/heure de création de l'enregistrement |
| updated_at | DateTimeField | auto_now | Date/heure de dernière modification |

#### User (modèle personnalisé, hérite de AbstractBaseUser + TimeStampedModel)

| Champ | Type | Contraintes | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto | Identifiant unique |
| email | EmailField | unique, indexed | Email de connexion |
| phone | CharField(20) | unique, indexed | Numéro de téléphone |
| first_name | CharField(100) | required | Prénom |
| last_name | CharField(100) | required | Nom de famille |
| is_active | BooleanField | default=True | Compte actif |
| is_staff | BooleanField | default=False | Accès admin Django |
| date_joined | DateTimeField | auto_now_add | Date de création du compte |
| groups | ManyToManyField | Django natif | Groupes de permissions techniques |

> **Note :** Plus de champ `role`. Les rôles politiques sont dans `PartyRole` via `UserPartyRole`. Les permissions techniques sont dans les `Group` Django.

#### MemberProfile (hérite de TimeStampedModel)

| Champ | Type | Contraintes | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | — |
| user | OneToOneField(User) | cascade | Lien vers le compte |
| matricule | CharField(20) | unique, auto-generated | Ex: FPP-2026-00001 |
| sex | CharField(1) | choices: M/F | Sexe |
| date_of_birth | DateField | nullable | Date de naissance |
| profession | CharField(100) | nullable | Profession |
| address | TextField | nullable | Adresse complète |
| region | CharField(100) | nullable, indexed | Région |
| city | CharField(100) | indexed | Ville |
| commune | CharField(100) | indexed | Commune |
| neighborhood | CharField(100) | nullable | Quartier |
| motivation | TextField | nullable | Motivation d'adhésion |
| membership_status | CharField(20) | choices, default='pending' | Statut adhésion |
| membership_date | DateTimeField | nullable | Date de validation |
| registration_source | CharField(20) | choices, default='web' | Source d'inscription |
| photo | ImageField | nullable | Photo de profil (stockée sur disque) |

**Statuts d'adhésion :**

| Statut | Code | Description |
|--------|------|-------------|
| En attente | `pending` | Demande soumise, non validée |
| Validé | `validated` | Adhésion approuvée |
| Suspendu | `suspended` | Adhésion temporairement gelée |
| Rejeté | `rejected` | Adhésion refusée |

#### PartyRole (hérite de TimeStampedModel)

| Champ | Type | Contraintes | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | — |
| name | CharField(100) | unique | Nom du rôle (ex: Président, Trésorier) |
| slug | SlugField(120) | unique, auto | URL-friendly |
| description | TextField | nullable | Description du rôle |
| level | CharField(20) | choices | Niveau : national, regional, communal, local |
| is_active | BooleanField | default=True | Rôle actif/archivé |

**Niveaux possibles :**

| Niveau | Code | Exemple |
|--------|------|---------|
| National | `national` | Président, Secrétaire Général, Trésorier |
| Régional | `regional` | Responsable régional |
| Communal | `communal` | Responsable communal |
| Local | `local` | Chef de quartier, Coordinateur local |

#### UserPartyRole (table de liaison M2M — hérite de TimeStampedModel)

| Champ | Type | Contraintes | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | — |
| user | ForeignKey(User) | cascade, indexed | Le membre |
| role | ForeignKey(PartyRole) | cascade, indexed | Le rôle assigné |
| zone | ForeignKey(Zone) | nullable, SET_NULL | Zone géographique d'exercice |
| assigned_by | ForeignKey(User) | nullable, SET_NULL | Qui a assigné ce rôle |
| is_active | BooleanField | default=True | Affectation active |
| ended_at | DateTimeField | nullable | Date de fin d'affectation |

> **Contrainte unique :** `(user, role, zone)` — un membre ne peut pas avoir le même rôle deux fois dans la même zone.

> **Historique :** Pour retirer un rôle, on met `is_active=False` et on renseigne `ended_at`. L'enregistrement reste en base pour l'historique. `created_at` sert de date d'assignation.

#### Zone (hérite de TimeStampedModel)

| Champ | Type | Contraintes | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | — |
| name | CharField(100) | required | Nom de la zone |
| type | CharField(20) | choices | region, district, commune, quartier |
| parent | ForeignKey(self) | nullable, SET_NULL | Zone parente (hiérarchie) |
| is_active | BooleanField | default=True | Zone active |

> **Hiérarchie :** Région → District → Commune → Quartier. Chaque zone pointe vers sa zone parente.

#### Article (hérite de TimeStampedModel)

| Champ | Type | Contraintes | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | — |
| title | CharField(200) | required | Titre de l'article |
| slug | SlugField(220) | unique, auto from title | URL lisible |
| summary | TextField(500) | required | Résumé court |
| content | TextField | required | Contenu complet (HTML ou Markdown) |
| cover_image | ImageField | nullable | Image de couverture (stockée sur disque) |
| status | CharField(20) | choices, default='draft' | Statut publication |
| author | ForeignKey(User) | on_delete=SET_NULL, nullable | Auteur |
| category | ForeignKey(Category) | on_delete=SET_NULL, nullable | Catégorie |
| is_featured | BooleanField | default=False | Mis en avant sur l'accueil |
| published_at | DateTimeField | nullable | Date de publication |
| deleted_at | DateTimeField | nullable | Soft delete |

**Statuts de publication :**

| Statut | Code |
|--------|------|
| Brouillon | `draft` |
| Publié | `published` |
| Archivé | `archived` |

#### Category (hérite de TimeStampedModel)

| Champ | Type | Contraintes |
|-------|------|-------------|
| id | UUID | PK |
| name | CharField(100) | unique |
| slug | SlugField(120) | unique, auto |
| description | TextField | nullable |
| is_active | BooleanField | default=True |

#### ContactMessage (hérite de TimeStampedModel)

| Champ | Type | Contraintes |
|-------|------|-------------|
| id | UUID | PK |
| name | CharField(100) | required |
| email | EmailField | required |
| phone | CharField(20) | nullable |
| subject | CharField(200) | required |
| message | TextField | required |
| is_read | BooleanField | default=False |
| read_at | DateTimeField | nullable |

#### UserSession (supervision des sessions — hérite de TimeStampedModel)

| Champ | Type | Contraintes | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | — |
| user | ForeignKey(User) | cascade, indexed | Utilisateur connecté |
| session_key | CharField(64) | unique, indexed | Identifiant lié au refresh token |
| ip_address | GenericIPAddressField | nullable | IP de connexion |
| city | CharField(100) | nullable | Ville (géolocalisation IP) |
| country | CharField(100) | nullable | Pays (géolocalisation IP) |
| device | CharField(200) | nullable | Navigateur + OS (ex: "Chrome 120 / Windows 11") |
| device_type | CharField(20) | choices, default='desktop' | desktop, mobile, tablet |
| is_active | BooleanField | default=True, indexed | Session toujours active |
| last_activity | DateTimeField | auto_now, indexed | Dernière activité (mis à jour à chaque requête) |
| ended_at | DateTimeField | nullable | Fin de session (logout ou expiration) |

**Types d'appareil :**

| Type | Code |
|------|------|
| Ordinateur | `desktop` |
| Mobile | `mobile` |
| Tablette | `tablet` |
| Inconnu | `unknown` |

**Requêtes utiles :**

| Besoin | Requête |
|--------|---------|
| Utilisateurs connectés maintenant | `WHERE is_active=True AND last_activity > now() - 15min` |
| Sessions actives d'un utilisateur | `WHERE user=X AND is_active=True` |
| Historique des connexions | `ORDER BY created_at DESC` (created_at = heure de connexion) |
| Connectés par jour | `COUNT(DISTINCT user) GROUP BY DATE(created_at)` |
| Appareils les plus utilisés | `COUNT(*) GROUP BY device_type` |
| Connexions par pays/ville | `COUNT(*) GROUP BY country, city` |

**Implémentation :**

- **Création** : à chaque login réussi, une `UserSession` est créée avec les infos du `request` (IP, user agent)
- **Mise à jour** : un middleware Django met à jour `last_activity` à chaque requête authentifiée (avec throttle de 60s pour ne pas surcharger la DB)
- **Fin** : au logout, `is_active=False` et `ended_at` renseigné. Un celery beat marque les sessions inactives > 7 jours
- **Géolocalisation** : `geoip2` + base MaxMind GeoLite2 (gratuite, mise à jour mensuelle)
- **Parsing device** : `user-agents` (lib Python) pour extraire navigateur, OS, type d'appareil
- **Déconnexion à distance** : un admin peut forcer `is_active=False` sur une session d'un autre utilisateur

#### AuditLog (journal d'audit)

| Champ | Type | Contraintes | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | — |
| user | ForeignKey(User) | nullable, SET_NULL, indexed | Qui a effectué l'action |
| action | CharField(20) | choices, indexed | Type d'action |
| entity_type | CharField(50) | indexed | Modèle concerné (ex: 'MemberProfile', 'Article') |
| entity_id | UUIDField | indexed | ID de l'objet concerné |
| changes | JSONField | nullable | Snapshot des changements (ancien → nouveau) |
| ip_address | GenericIPAddressField | nullable | IP de l'utilisateur |
| user_agent | CharField(300) | nullable | Navigateur/client |
| created_at | DateTimeField | auto_now_add, indexed | Horodatage de l'action |

**Actions possibles :**

| Action | Code | Description |
|--------|------|-------------|
| Création | `create` | Nouvel enregistrement |
| Modification | `update` | Mise à jour de champs |
| Suppression | `delete` | Suppression (ou soft delete) |
| Changement de statut | `status_change` | Validation/suspension/rejet adhésion |
| Connexion | `login` | Connexion réussie |
| Déconnexion | `logout` | Déconnexion |
| Échec de connexion | `login_failed` | Tentative ratée |
| Assignation de rôle | `role_assign` | Nouveau rôle attribué |
| Retrait de rôle | `role_revoke` | Rôle retiré |
| Export | `export` | Export de données |

**Exemple de `changes` (JSON) :**

```json
{
  "membership_status": {
    "old": "pending",
    "new": "validated"
  },
  "membership_date": {
    "old": null,
    "new": "2026-03-22T14:30:00Z"
  }
}
```

#### SiteSettings (Singleton — hérite de TimeStampedModel)

| Champ | Type | Description |
|-------|------|-------------|
| site_name | CharField(200) | Nom du parti |
| slogan | CharField(300) | Slogan principal |
| president_name | CharField(200) | Nom du président |
| president_message | TextField | Message du président (accueil) |
| president_photo | ImageField | Photo du président |
| whatsapp_number | CharField(20) | Numéro WhatsApp |
| contact_email | EmailField | Email de contact |
| address | TextField | Adresse physique |
| facebook_url | URLField | Lien Facebook |
| twitter_url | URLField | Lien Twitter/X |
| instagram_url | URLField | Lien Instagram |
| youtube_url | URLField | Lien YouTube |
| logo | ImageField | Logo du parti |
| hero_image | ImageField | Image hero accueil |
| hero_title | CharField(200) | Titre hero |
| hero_subtitle | TextField | Sous-titre hero |
| about_text | TextField | Texte "À propos" |
| vision_text | TextField | Texte "Vision/Programme" |
| values_text | TextField | Texte "Valeurs" |

---

## 5. Permissions — Architecture à deux couches

### 5.1 Couche politique : PartyRole

Rôles **créés dynamiquement** depuis le dashboard. Représentent la structure organisationnelle du parti.

Un membre peut avoir **plusieurs rôles simultanément** (ex: Trésorier national + Responsable régional d'Abidjan).

L'historique est conservé : quand un rôle est retiré, `UserPartyRole.is_active = False` et `ended_at` est renseigné.

### 5.2 Couche technique : Django Groups + Permissions

Groupes de permissions pour le **contrôle d'accès à l'API**. Utilisés dans `permissions.py`.

| Groupe | Permissions | Cible |
|--------|-------------|-------|
| Éditeur | `can_create_article`, `can_edit_article`, `can_manage_categories` | Gestion du contenu uniquement |
| Gestionnaire | Éditeur + `can_manage_members`, `can_validate_membership`, `can_export_members`, `can_manage_contacts`, `can_view_dashboard` | Gestion complète courante |
| Super Admin | Gestionnaire + `can_manage_settings`, `can_assign_roles`, `can_manage_permissions`, `can_view_audit_log` | Accès total |

**Permissions granulaires :**

| Permission | Code | Entité |
|------------|------|--------|
| Créer un article | `content.can_create_article` | Article |
| Modifier un article | `content.can_edit_article` | Article |
| Supprimer un article | `content.can_delete_article` | Article |
| Gérer les catégories | `content.can_manage_categories` | Category |
| Voir les membres | `members.can_view_members` | MemberProfile |
| Gérer les membres | `members.can_manage_members` | MemberProfile |
| Valider une adhésion | `members.can_validate_membership` | MemberProfile |
| Exporter les membres | `members.can_export_members` | MemberProfile |
| Gérer les messages | `contact.can_manage_contacts` | ContactMessage |
| Exporter les messages | `contact.can_export_contacts` | ContactMessage |
| Voir le dashboard | `core.can_view_dashboard` | Dashboard |
| Gérer les paramètres | `site_settings.can_manage_settings` | SiteSettings |
| Assigner des rôles | `roles.can_assign_roles` | UserPartyRole |
| Gérer les permissions | `accounts.can_manage_permissions` | Group/Permission |
| Voir le journal d'audit | `audit.can_view_audit_log` | AuditLog |

---

## 6. API REST — Endpoints

### 6.1 Authentification

| Méthode | Endpoint | Description | Auth |
|---------|----------|-------------|------|
| POST | `/api/auth/register/` | Inscription (adhésion) | Non |
| POST | `/api/auth/login/` | Connexion (retourne JWT en cookie httponly) | Non |
| POST | `/api/auth/logout/` | Déconnexion (supprime cookie) | Oui |
| GET | `/api/auth/me/` | Profil de l'utilisateur connecté + rôles | Oui |
| PATCH | `/api/auth/me/` | Modifier son profil | Oui |
| POST | `/api/auth/password/change/` | Changer son mot de passe | Oui |
| POST | `/api/auth/password/reset/` | Demander un reset (envoie email) | Non |
| POST | `/api/auth/password/reset/confirm/` | Confirmer le reset avec token | Non |
| POST | `/api/auth/token/refresh/` | Rafraîchir le JWT | Cookie |

### 6.2 Public (pas d'auth)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/public/settings/` | Paramètres du site (nom, slogan, réseaux, etc.) |
| GET | `/api/public/articles/` | Articles publiés (paginés, filtrables par catégorie) |
| GET | `/api/public/articles/{slug}/` | Détail d'un article |
| GET | `/api/public/categories/` | Liste des catégories actives |
| POST | `/api/public/contact/` | Envoyer un message de contact |
| GET | `/api/public/stats/` | Stats publiques (nombre de membres, articles, etc.) |

### 6.3 Admin — Membres

| Méthode | Endpoint | Description | Permission |
|---------|----------|-------------|------------|
| GET | `/api/admin/dashboard/` | KPI du dashboard | `can_view_dashboard` |
| GET | `/api/admin/members/` | Liste membres paginée + filtres | `can_view_members` |
| GET | `/api/admin/members/{id}/` | Fiche détaillée membre + rôles + historique | `can_view_members` |
| PATCH | `/api/admin/members/{id}/` | Modifier un membre | `can_manage_members` |
| PATCH | `/api/admin/members/{id}/status/` | Changer statut adhésion | `can_validate_membership` |
| GET | `/api/admin/members/export/` | Export Excel/CSV | `can_export_members` |

### 6.4 Admin — Contenus

| Méthode | Endpoint | Description | Permission |
|---------|----------|-------------|------------|
| GET | `/api/admin/articles/` | Liste tous les articles | `can_create_article` |
| POST | `/api/admin/articles/` | Créer un article | `can_create_article` |
| GET | `/api/admin/articles/{id}/` | Détail article (admin) | `can_create_article` |
| PATCH | `/api/admin/articles/{id}/` | Modifier un article | `can_edit_article` |
| DELETE | `/api/admin/articles/{id}/` | Supprimer un article (soft) | `can_delete_article` |
| GET | `/api/admin/categories/` | Liste catégories | `can_manage_categories` |
| POST | `/api/admin/categories/` | Créer catégorie | `can_manage_categories` |
| PATCH | `/api/admin/categories/{id}/` | Modifier catégorie | `can_manage_categories` |
| DELETE | `/api/admin/categories/{id}/` | Supprimer catégorie | `can_manage_categories` |

### 6.5 Admin — Contacts

| Méthode | Endpoint | Description | Permission |
|---------|----------|-------------|------------|
| GET | `/api/admin/contacts/` | Messages de contact | `can_manage_contacts` |
| GET | `/api/admin/contacts/{id}/` | Détail message | `can_manage_contacts` |
| PATCH | `/api/admin/contacts/{id}/` | Marquer lu | `can_manage_contacts` |
| GET | `/api/admin/contacts/export/` | Export CSV messages | `can_export_contacts` |

### 6.6 Admin — Rôles

| Méthode | Endpoint | Description | Permission |
|---------|----------|-------------|------------|
| GET | `/api/admin/roles/` | Liste des rôles du parti | `can_assign_roles` |
| POST | `/api/admin/roles/` | Créer un rôle | `can_manage_permissions` |
| PATCH | `/api/admin/roles/{id}/` | Modifier un rôle | `can_manage_permissions` |
| GET | `/api/admin/members/{id}/roles/` | Rôles actifs d'un membre | `can_assign_roles` |
| GET | `/api/admin/members/{id}/roles/history/` | Historique complet des rôles | `can_assign_roles` |
| POST | `/api/admin/members/{id}/roles/` | Assigner un rôle à un membre | `can_assign_roles` |
| PATCH | `/api/admin/members/{id}/roles/{role_id}/` | Désactiver un rôle (retirer) | `can_assign_roles` |

### 6.7 Admin — Sessions

| Méthode | Endpoint | Description | Permission |
|---------|----------|-------------|------------|
| GET | `/api/admin/sessions/active/` | Sessions actives en ce moment | `can_view_dashboard` |
| GET | `/api/admin/sessions/` | Historique des sessions (paginé, filtrable) | `can_view_dashboard` |
| GET | `/api/admin/sessions/stats/` | Stats : connectés/jour, appareils, pays/villes | `can_view_dashboard` |
| DELETE | `/api/admin/sessions/{id}/` | Forcer la déconnexion d'une session | `can_manage_permissions` |
| GET | `/api/auth/me/sessions/` | Mes sessions actives (pour le partisan) | Authentifié |
| DELETE | `/api/auth/me/sessions/{id}/` | Déconnecter une de mes sessions | Authentifié |

### 6.8 Admin — Paramètres et audit

| Méthode | Endpoint | Description | Permission |
|---------|----------|-------------|------------|
| GET | `/api/admin/settings/` | Paramètres du site | `can_view_dashboard` |
| PATCH | `/api/admin/settings/` | Modifier paramètres | `can_manage_settings` |
| GET | `/api/admin/audit-log/` | Journal d'audit (paginé, filtrable) | `can_view_audit_log` |

---

## 7. Règles métier

### 7.1 Adhésion

- Le matricule est généré automatiquement au format `FPP-AAAA-NNNNN` (ex: FPP-2026-00042)
- La détection de doublons se fait sur `email` et `phone` (unicité en base)
- Le statut initial est `pending`, seul un utilisateur avec `can_validate_membership` peut le changer
- La `membership_date` est remplie automatiquement lors de la validation
- Un email de confirmation est envoyé au partisan après inscription (Celery)
- Une notification est créée dans le dashboard admin
- Tout changement de statut est tracé dans `AuditLog`

### 7.2 Articles

- Le `slug` est auto-généré depuis le `title` (avec dédoublonnage)
- La `published_at` est remplie automatiquement lors du passage en `published`
- La suppression est toujours un soft delete (`deleted_at` renseigné)
- Les articles `featured` sont affichés sur la page d'accueil
- Maximum 3 articles featured simultanément
- Toute création/modification/suppression est tracée dans `AuditLog`

### 7.3 Rôles

- Un membre peut avoir **plusieurs rôles actifs** simultanément
- Chaque rôle peut être lié à une **zone** (ou non, pour les rôles nationaux)
- Contrainte unique : `(user, role, zone)` — pas de doublon
- Retirer un rôle = `is_active=False` + `ended_at` renseigné (l'enregistrement reste)
- Toute assignation/retrait est tracé dans `AuditLog`

### 7.4 Audit

- Toute action de création, modification, suppression, changement de statut est journalisée
- Les connexions réussies et échouées sont journalisées
- Les exports de données sont journalisés
- Le journal est **en lecture seule** (pas de modification/suppression possible)
- Le `changes` JSON stocke un diff ancien/nouveau pour chaque champ modifié
- L'audit est réalisé via un **mixin Django** (`AuditMixin`) ou des **signals**

### 7.5 Sessions

- Une `UserSession` est créée à chaque login réussi
- `last_activity` est mis à jour par un middleware Django (throttlé à 1 update/60s par session)
- Au logout : `is_active=False`, `ended_at` renseigné
- Les sessions inactives > 7 jours sont marquées `is_active=False` par un Celery beat
- La géolocalisation utilise `geoip2` + base GeoLite2 de MaxMind (gratuite)
- Le parsing device utilise la lib Python `user-agents`
- Un utilisateur peut voir et révoquer ses propres sessions (comme Google/GitHub)
- Un SUPER_ADMIN peut révoquer n'importe quelle session

### 7.6 Analytics visiteurs publics (Umami)

Pour le comptage des visiteurs non authentifiés (pages vues, pays, appareils), **ne pas coder de solution custom**. Utiliser **Umami** (open source, auto-hébergé) :

- Ajouter un service `umami` au `docker-compose.yml` (image `ghcr.io/umami-software/umami`)
- Ajouter un script tracking de 2KB dans le `index.html` du frontend
- Dashboard analytics accessible sur un sous-domaine (ex: `analytics-fpp.monajent.com`)
- Pas de cookies, conforme RGPD, pas de données personnelles
- Métriques : visiteurs uniques/jour, pages vues, pays, appareils, sources de trafic

> **Pourquoi pas custom ?** Un système de tracking complet (fingerprinting, sessions anonymes, pages vues, bounce rate, sources) représente des semaines de développement. Umami fait tout ça out-of-the-box avec un seul conteneur Docker.

### 7.7 Médias

- Les fichiers sont stockés sur le filesystem hôte (volume Docker monté)
- Les chemins relatifs sont stockés en base
- Structure : `media/profiles/`, `media/articles/`, `media/site/`
- Les images sont validées côté serveur (type MIME, taille max 5 Mo)
- `django-cleanup` supprime automatiquement les anciens fichiers lors d'une mise à jour

### 7.6 Sécurité

- JWT en cookie HttpOnly avec SameSite=Lax
- Access token : 15 minutes, Refresh token : 7 jours
- Rate limiting : 5 req/min pour login, 3 req/min pour register, 20 req/min pour les API publiques
- Validation serveur systématique de tous les inputs
- Protection CSRF pour les cookies
- Permissions centralisées dans `permissions.py`
- Pas de token en localStorage

### 7.7 CORS

```python
CORS_ALLOWED_ORIGINS = [
    "https://fpp.monajent.com",       # Frontend prod
    "http://localhost:5173",           # Frontend dev (Vite)
    "http://localhost:3000",           # Flutter web dev
    "http://10.0.2.2:8000",           # Flutter emulator Android
]
```

---

## 8. Architecture technique

### 8.1 Services Docker

| Service | Image | Port | Description |
|---------|-------|------|-------------|
| `db` | postgres:16-alpine | 5432 | Base de données |
| `redis` | redis:7-alpine | 6379 | Broker Celery + cache |
| `backend` | custom (Daphne) | 8000 | API Django ASGI |
| `celery-worker` | custom | — | Worker Celery |
| `celery-beat` | custom | — | Scheduler tâches planifiées |
| `frontend` | custom (Nginx) | 80/443 | SPA Vue 3 servie par Nginx |
| `backup` | custom | — | Sauvegarde PostgreSQL quotidienne |
| `umami` | ghcr.io/umami-software/umami | 3000 | Analytics visiteurs publics (Phase 2) |

### 8.2 Structure backend (Django)

```
backend/
├── manage.py
├── requirements.txt
├── Dockerfile
├── entrypoint.sh
├── config/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── local.py
│   │   └── production.py
│   ├── urls.py
│   ├── asgi.py
│   ├── wsgi.py
│   └── celery.py
└── apps/
    ├── __init__.py
    ├── core/                  # TimeStampedModel, AuditLog, AuditMixin
    │   ├── models.py
    │   ├── mixins.py
    │   ├── middleware.py       # SessionActivityMiddleware
    │   ├── admin.py
    │   └── apps.py
    ├── accounts/              # User model, managers
    │   ├── models.py
    │   ├── managers.py
    │   ├── admin.py
    │   ├── signals.py
    │   └── apps.py
    ├── members/               # MemberProfile
    │   ├── models.py
    │   ├── admin.py
    │   └── apps.py
    ├── roles/                 # PartyRole, UserPartyRole
    │   ├── models.py
    │   ├── admin.py
    │   └── apps.py
    ├── zones/                 # Zone (hiérarchie géographique)
    │   ├── models.py
    │   ├── admin.py
    │   └── apps.py
    ├── content/               # Article, Category
    │   ├── models.py
    │   ├── admin.py
    │   └── apps.py
    ├── contact/               # ContactMessage
    │   ├── models.py
    │   ├── admin.py
    │   └── apps.py
    ├── site_settings/         # SiteSettings (singleton)
    │   ├── models.py
    │   ├── admin.py
    │   └── apps.py
    └── api/                   # API centralisée
        ├── urls.py
        ├── permissions.py
        ├── throttle.py
        ├── pagination.py
        ├── serializers/
        │   ├── __init__.py
        │   ├── auth.py
        │   ├── members.py
        │   ├── roles.py
        │   ├── content.py
        │   ├── contact.py
        │   └── site_settings.py
        └── views/
            ├── __init__.py
            ├── auth.py
            ├── members.py
            ├── roles.py
            ├── sessions.py
            ├── content.py
            ├── contact.py
            ├── dashboard.py
            ├── audit.py
            └── site_settings.py
```

### 8.3 Tâches Celery planifiées

| Tâche | Fréquence | Description |
|-------|-----------|-------------|
| `send_welcome_email` | À l'événement | Email de bienvenue après inscription |
| `notify_admin_new_member` | À l'événement | Notification dashboard nouvelle adhésion |
| `cleanup_expired_tokens` | Quotidien 3h | Supprimer les tokens JWT expirés |
| `generate_daily_stats` | Quotidien 1h | Calculer les stats du dashboard |
| `cleanup_old_audit_logs` | Mensuel | Archiver les logs d'audit > 1 an (optionnel) |
| `cleanup_inactive_sessions` | Quotidien 4h | Marquer les sessions inactives > 7 jours |

### 8.4 Optimisations requises

- `select_related` sur toutes les FK (Article → author, Article → category, MemberProfile → user, UserPartyRole → role, UserPartyRole → zone)
- `prefetch_related` sur les M2M (User → party roles)
- `Subquery` + `OuterRef` pour les comptages agrégés dans le dashboard
- Pagination par curseur pour les listes longues (membres, audit)
- Indexation sur : `email`, `phone`, `matricule`, `city`, `commune`, `membership_status`, `slug`, `entity_type`, `created_at` (AuditLog)
- Cache Redis pour les endpoints publics (settings, stats, articles) avec invalidation

---

## 9. Variables d'environnement

```env
# Django
DJANGO_SETTINGS_MODULE=config.settings.local
DJANGO_SECRET_KEY=change-me-in-production
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,api-fpp.monajent.com

# Database
POSTGRES_DB=fpp_db
POSTGRES_USER=fpp_user
POSTGRES_PASSWORD=change-me
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# JWT
JWT_ACCESS_TOKEN_LIFETIME=15
JWT_REFRESH_TOKEN_LIFETIME=10080

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Media
MEDIA_ROOT=/app/media

# Email (Celery)
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=noreply@fpp.com
EMAIL_HOST_PASSWORD=change-me
EMAIL_USE_TLS=True

# Frontend (build-time)
VITE_API_BASE_URL=http://localhost:8000/api
VITE_SITE_NAME=FPP - Front Patriotique Panafricain
```

---

## 10. Déploiement

### Domaines

| Service | URL |
|---------|-----|
| Frontend | https://fpp.monajent.com |
| Backend API | https://api-fpp.monajent.com |
| Admin Django | https://api-fpp.monajent.com/admin/ |

### Backups PostgreSQL

- Sauvegarde quotidienne à 2h du matin
- Rétention : 7 jours (suppression automatique des anciennes sauvegardes)
- Stockage : volume dédié sur l'hôte `/opt/backups/fpp/`
- Script dans le conteneur `backup` ou cron sur le VPS

---

## 11. Phases de développement

### Phase 1 — MVP (actuel)

- Site public complet (5 pages)
- Formulaire d'adhésion fonctionnel
- Backoffice admin (dashboard, membres, articles, messages)
- Auth JWT cookie httponly
- Système de rôles dynamique (PartyRole + UserPartyRole)
- Permissions granulaires (Django Groups)
- Journal d'audit
- Export Excel
- Docker compose local + prod

### Phase 2 — Structuration

- Gestion territoriale complète (Zones hiérarchiques)
- Affectation de rôles par zone
- Responsable local avec périmètre restreint
- Statistiques avancées par zone
- Notifications email
- Segmentation membres par zone

### Phase 3 — Extension

- Application mobile Flutter
- Espace membre sécurisé
- Carte de membre digitale
- Paiement Mobile Money
- Gestion événements
- CRM politique
