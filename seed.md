# Seeds de production — FPP

## Comment exécuter

```bash
# Depuis le conteneur backend
docker compose exec backend python manage.py shell < seed_bureau.py
docker compose exec backend python manage.py shell < seed_test_members.py
```

---

## 1. Seed — Membres du Bureau National

Ce script crée les 12 membres du bureau dans la table `BureauMember`.
Les photos peuvent être ajoutées ensuite via l'admin Django (`/admin/site_settings/bureaumember/`).

```python
"""seed_bureau.py — Membres du Bureau National FPP (production)"""
from apps.site_settings.models import BureauMember

bureau_members = [
    {"order": 1,  "full_name": "MAHI ZOUKOU",                   "title": "Vice-Président"},
    {"order": 2,  "full_name": "TRAORÉ Moussa",                 "title": "Secrétaire Général National"},
    {"order": 3,  "full_name": "ASSAOURÉ Kouadio",              "title": "Secrétaire National aux Affaires Financières"},
    {"order": 4,  "full_name": "BAMBA Gnaimmon",                 "title": "Secrétaire National à la Formation Idéologique et Politique"},
    {"order": 5,  "full_name": "KONÉ Peanguy Souleymane",       "title": "Secrétaire National à l'Organisation"},
    {"order": 6,  "full_name": "KONÉ Beh Arouna",               "title": "Secrétaire National à la Communication"},
    {"order": 7,  "full_name": "KOUASSI N'guessan",             "title": "Secrétaire National à la Mobilisation"},
    {"order": 8,  "full_name": "KOUAKOU Akissi",                "title": "Secrétaire Nationale chargée des Femmes du Parti"},
    {"order": 9,  "full_name": "DJAH Guy",                      "title": "Secrétaire National chargé de l'Entreprenariat et de l'Insertion Professionnelle"},
    {"order": 10, "full_name": "KOUADIO Narcisse",              "title": "Secrétaire National chargé des Alliances avec les Partis Politiques"},
    {"order": 11, "full_name": "KOUASSI Kouakou Kouman",        "title": "Secrétaire National chargé de l'Environnement et du Cadre de Vie"},
    {"order": 12, "full_name": "BALLO Oumar",                   "title": "Conseiller Stratégique et Politique"},
]

created = 0
for m in bureau_members:
    obj, is_new = BureauMember.objects.update_or_create(
        full_name=m["full_name"],
        defaults={"title": m["title"], "order": m["order"], "is_active": True},
    )
    if is_new:
        created += 1
    print(f"  {'✓ Créé' if is_new else '↻ Mis à jour'} : {obj}")

print(f"\nBureau National : {created} créé(s), {len(bureau_members) - created} mis à jour.")
```

---

## 2. Seed — Membres fictifs de test (production)

Ce script crée 3 utilisateurs de test avec différents statuts :
- **Aminata** : membre validée avec carte et matricule
- **Koffi** : demande d'adhésion en attente (pas encore membre, pas de carte)
- **Fatou** : sympathisante inscrite, n'a pas encore fait de demande d'adhésion

```python
"""seed_test_members.py — Membres fictifs de test pour production"""
from datetime import date
from django.utils import timezone
from apps.accounts.models import User
from apps.members.models import MemberProfile
from apps.members.utils import generate_hmac_matricule

PASSWORD = "FppTest2026!"

test_users = [
    {
        "email": "aminata.kone@test-fpp.ci",
        "first_name": "Aminata",
        "last_name": "KONÉ",
        "sex": "F",
        "phone": "+22507010203",
        "date_of_birth": date(1990, 3, 15),
        "member_profile": {
            "id_document_type": "cni",
            "id_document_number": "CI-2024-TEST-001",
            "city": "Abidjan",
            "commune": "Yopougon",
            "region": "Abidjan",
            "neighborhood": "Quartier Millionnaire",
            "profession": "Enseignante",
            "motivation": "Je souhaite contribuer au développement de la Côte d'Ivoire à travers l'engagement politique.",
            "membership_status": "validated",
        },
    },
    {
        "email": "koffi.traore@test-fpp.ci",
        "first_name": "Koffi",
        "last_name": "TRAORÉ",
        "sex": "M",
        "phone": "+22505040506",
        "date_of_birth": date(1985, 7, 22),
        "member_profile": {
            "id_document_type": "cni",
            "id_document_number": "CI-2024-TEST-002",
            "city": "Bouaké",
            "commune": "Bouaké",
            "region": "Gbêkê",
            "neighborhood": "Commerce",
            "profession": "Commerçant",
            "motivation": "Convaincu par le programme du FPP, je veux m'engager pour mon pays.",
            "membership_status": "pending",
        },
    },
    {
        "email": "fatou.diallo@test-fpp.ci",
        "first_name": "Fatou",
        "last_name": "DIALLO",
        "sex": "F",
        "phone": "+22501080910",
        "date_of_birth": date(1995, 11, 5),
        "member_profile": None,
    },
]

now = timezone.now()

for u_data in test_users:
    profile_data = u_data.pop("member_profile")

    user, user_created = User.objects.get_or_create(
        email=u_data["email"],
        defaults={
            **u_data,
            "email_verified": True,
            "is_active": True,
            "cgu_accepted_at": now,
            "privacy_accepted_at": now,
        },
    )
    if user_created:
        user.set_password(PASSWORD)
        user.save(update_fields=["password"])
        print(f"  ✓ User créé : {user.email}")
    else:
        print(f"  ↻ User existe : {user.email}")

    if profile_data:
        status = profile_data.pop("membership_status")
        profile, prof_created = MemberProfile.objects.get_or_create(
            user=user,
            defaults={
                **profile_data,
                "membership_status": status,
                "registration_source": "admin",
            },
        )

        if prof_created and status == "validated":
            profile.matricule = generate_hmac_matricule(user, profile.city)
            profile.membership_date = now
            profile.membership_status = "validated"
            profile.save(update_fields=["matricule", "membership_status", "membership_date"])
            print(f"    ✓ Membre validé, matricule : {profile.matricule}")
        elif prof_created:
            print(f"    ✓ Profil créé (statut : {status})")
        else:
            print(f"    ↻ Profil existe (statut : {profile.membership_status})")
    else:
        print(f"    — Pas de profil membre (sympathisante)")

print("\n" + "=" * 60)
print("Seed terminé.")
print("=" * 60)
```

---

## 3. Identifiants de connexion (test)

| Utilisateur | Email | Mot de passe | Statut |
|---|---|---|---|
| **Aminata KONÉ** | `aminata.kone@test-fpp.ci` | `FppTest2026!` | Membre **validée** (a un matricule, une carte) |
| **Koffi TRAORÉ** | `koffi.traore@test-fpp.ci` | `FppTest2026!` | Demande **en attente** (pas de carte, pas de matricule) |
| **Fatou DIALLO** | `fatou.diallo@test-fpp.ci` | `FppTest2026!` | **Sympathisante** inscrite (aucune demande d'adhésion) |

### Notes

- Les photos et scans de documents ne sont pas créés par le script (champs `photo` et `id_document_scan` de `MemberProfile` sont requis en BDD mais peuvent être ajoutés via l'admin Django).
- Si les champs `photo` et `id_document_scan` sont `NOT NULL` sans `blank=True`, il faudra soit :
  - Les rendre optionnels temporairement (`blank=True, null=True` + migration)
  - Soit fournir un fichier placeholder avant d'exécuter le script
- Le matricule d'Aminata est généré automatiquement via `generate_hmac_matricule()` (format `FPP-XXXX-XXXX-XXXX`).
- Pour les membres du bureau, les photos s'ajoutent dans : **Admin Django → Paramètres du site → Membres du bureau**.
