import django
from datetime import date, timedelta
from django.utils import timezone

from apps.accounts.models import User
from apps.content.models import MediaContent, Category, Article, Event

# ─── Récupérer le superuser ───
user = User.objects.get(email="dt@fpp.org")
print(f"✅ Superuser: {user}")

# ═══════════════════════════════════════════════════════════════════════════
# 1. MEDIA CONTENT (FPP TV)
# ═══════════════════════════════════════════════════════════════════════════
media_data = [
    {
        "title": "Meeting Historique du FPP — Yopougon 2025",
        "description": "Retour en images sur le meeting historique du Front Patriotique Panafricain à Yopougon, 12 juillet 2025.",
        "platform": "facebook",
        "embed_type": "video",
        "source_url": "https://www.facebook.com/reel/946502157963600/",
        "published_at": date(2025, 7, 12),
        "category": "Meeting",
        "is_featured": True,
    },
    {
        "title": "Le FPP en action — Publication officielle",
        "description": "Publication officielle du Front Patriotique Panafricain sur les activités récentes du Parti.",
        "platform": "facebook",
        "embed_type": "post",
        "source_url": "https://www.facebook.com/leaderfpp/posts/pfbid0tXjRcZNQ6cqN7unxwBhm8DPAg8CiRdnEfRZ94Nt6y5xTnRKK3wbqzoKPkgddvYyWl",
        "published_at": date(2025, 7, 10),
        "category": "Communiqué",
        "is_featured": False,
    },
    {
        "title": "Mobilisation citoyenne — Communiqué du Parti",
        "description": "Le FPP appelle à la mobilisation citoyenne pour une Côte d'Ivoire plus juste.",
        "platform": "facebook",
        "embed_type": "post",
        "source_url": "https://www.facebook.com/leaderfpp/posts/pfbid0t5rCTHriEPvLyH1v2fNJVkVjk8buey3hFs6mQkGTApn4HDnvvEMQtwkBMaAzEVvul",
        "published_at": date(2025, 7, 8),
        "category": "Communiqué",
        "is_featured": False,
    },
    {
        "title": "Activités du Parti — Bilan et perspectives",
        "description": "Bilan des activités récentes du FPP et perspectives pour les prochains mois.",
        "platform": "facebook",
        "embed_type": "post",
        "source_url": "https://www.facebook.com/leaderfpp/posts/pfbid02EBtJfBAQS7Fqojf9A4EVtVsuyofgR248VtWTgY6QKcENkBv3n9JpjCUYep9BrKyWl",
        "published_at": date(2025, 7, 5),
        "category": "Communiqué",
        "is_featured": False,
    },
    {
        "title": "Reel FPP — Moments forts sur le terrain",
        "description": "Les temps forts des actions du FPP sur le terrain, captés en vidéo.",
        "platform": "facebook",
        "embed_type": "video",
        "source_url": "https://www.facebook.com/reel/953100833749265/",
        "published_at": date(2025, 6, 28),
        "category": "Terrain",
        "is_featured": False,
    },
    {
        "title": "Vidéo du Président — Message aux militants",
        "description": "Le Président Dabé Nogbo Wanaminou s'adresse aux militants et sympathisants du FPP.",
        "platform": "facebook",
        "embed_type": "video",
        "source_url": "https://www.facebook.com/leaderfpp/videos/934848615614460/",
        "published_at": date(2025, 6, 20),
        "category": "Interview",
        "is_featured": False,
    },
    {
        "title": "Sensibilisation citoyenne — Reel",
        "description": "Campagne de sensibilisation citoyenne du Front Patriotique Panafricain.",
        "platform": "facebook",
        "embed_type": "video",
        "source_url": "https://www.facebook.com/reel/973591361670445/",
        "published_at": date(2025, 6, 15),
        "category": "Terrain",
        "is_featured": False,
    },
    {
        "title": "Déclaration officielle du FPP",
        "description": "Déclaration officielle du Front Patriotique Panafricain sur l'actualité nationale.",
        "platform": "facebook",
        "embed_type": "post",
        "source_url": "https://www.facebook.com/leaderfpp/posts/pfbid0258NE3B1zxbQ7jDAMMtQS5SeYY2poDfcv4bWor4qfTbYSNhKv9ejvRuhSTHZ11Hwul",
        "published_at": date(2025, 6, 10),
        "category": "Communiqué",
        "is_featured": False,
    },
]

for m in media_data:
    obj, created = MediaContent.objects.get_or_create(
        source_url=m["source_url"],
        defaults=m,
    )
    status = "créé" if created else "existe déjà"
    print(f"  📺 {status}: {obj.title}")

print(f"\n✅ MediaContent: {MediaContent.objects.count()} total\n")

# ═══════════════════════════════════════════════════════════════════════════
# 2. CATÉGORIES D'ARTICLES
# ═══════════════════════════════════════════════════════════════════════════
categories_data = [
    {"name": "Politique", "description": "Actualités politiques et prises de position du FPP."},
    {"name": "Société", "description": "Enjeux sociaux et sociétaux en Côte d'Ivoire."},
    {"name": "Économie", "description": "Analyses économiques et propositions du FPP."},
    {"name": "Jeunesse", "description": "Actions et programmes dédiés à la jeunesse."},
    {"name": "International", "description": "Relations internationales et panafricanisme."},
    {"name": "Communiqué", "description": "Communiqués officiels du Parti."},
]

cats = {}
for c in categories_data:
    obj, created = Category.objects.get_or_create(name=c["name"], defaults=c)
    cats[c["name"]] = obj
    status = "créé" if created else "existe déjà"
    print(f"  🏷️  {status}: {obj.name}")

print(f"\n✅ Catégories: {Category.objects.count()} total\n")

# ═══════════════════════════════════════════════════════════════════════════
# 3. ARTICLES
# ═══════════════════════════════════════════════════════════════════════════
now = timezone.now()

articles_data = [
    {
        "title": "Le FPP dévoile sa vision pour la Côte d'Ivoire de demain",
        "summary": "Le Front Patriotique Panafricain présente un programme ambitieux articulé autour de la souveraineté nationale, la justice sociale et le développement durable.",
        "content": """Le Front Patriotique Panafricain (FPP), sous la direction du Président Dabé Nogbo Wanaminou, a dévoilé lors d'une conférence de presse sa vision stratégique pour la Côte d'Ivoire.

Le programme s'articule autour de cinq piliers fondamentaux :

1. **Souveraineté nationale** — Renforcer l'indépendance économique et politique du pays.
2. **Justice sociale** — Garantir l'égalité des chances pour tous les Ivoiriens.
3. **Développement durable** — Investir dans les énergies renouvelables et l'agriculture moderne.
4. **Éducation** — Réformer le système éducatif pour former la jeunesse aux métiers d'avenir.
5. **Panafricanisme** — Renforcer les liens avec les nations africaines sœurs.

"Notre vision est celle d'une Côte d'Ivoire forte, unie et prospère, ancrée dans ses valeurs africaines", a déclaré le Président du FPP.""",
        "category": "Politique",
        "is_featured": True,
        "published_at": now - timedelta(days=2),
    },
    {
        "title": "Grande mobilisation citoyenne à Yopougon",
        "summary": "Des milliers de sympathisants se sont rassemblés à Yopougon pour soutenir le projet du FPP lors d'un meeting historique.",
        "content": """Le meeting du FPP à Yopougon a rassemblé plusieurs milliers de personnes venues de toute la commune et des alentours.

L'événement, qui s'est déroulé dans une ambiance festive et solennelle, a été marqué par les interventions de plusieurs cadres du Parti et du Président Dabé Nogbo Wanaminou.

Les thèmes abordés ont porté sur l'emploi des jeunes, la cherté de la vie, et la nécessité d'un renouveau politique en Côte d'Ivoire.

"Le peuple est prêt pour le changement. Le FPP est la voie vers une Côte d'Ivoire qui appartient à tous ses enfants", a lancé le Président sous les acclamations de la foule.""",
        "category": "Politique",
        "is_featured": False,
        "published_at": now - timedelta(days=5),
    },
    {
        "title": "Le FPP lance un programme de formation pour la jeunesse",
        "summary": "Un ambitieux programme de formation professionnelle et politique pour les jeunes militants et sympathisants du FPP.",
        "content": """Le Front Patriotique Panafricain annonce le lancement de son programme « Jeunesse d'Avenir », destiné à former la relève politique et professionnelle du pays.

Ce programme comprend :

- **Formations en leadership politique** — Ateliers mensuels animés par les cadres du Parti.
- **Formations professionnelles** — Partenariats avec des centres de formation en numérique, agriculture et entrepreneuriat.
- **Bourses d'études** — Un fonds de soutien pour les étudiants méritants issus de familles modestes.

"La jeunesse est le moteur du changement. Nous devons lui donner les outils pour construire l'avenir", a souligné le secrétaire général du FPP.

Les inscriptions sont ouvertes sur le site officiel du Parti.""",
        "category": "Jeunesse",
        "is_featured": False,
        "published_at": now - timedelta(days=8),
    },
    {
        "title": "Communiqué : Appel au dialogue national",
        "summary": "Le FPP appelle toutes les forces vives de la nation à un dialogue sincère et inclusif pour l'avenir de la Côte d'Ivoire.",
        "content": """COMMUNIQUÉ OFFICIEL

Le Front Patriotique Panafricain, fidèle à sa vocation de rassembleur, lance un appel solennel à toutes les forces politiques, sociales et citoyennes de Côte d'Ivoire.

Face aux défis qui se dressent devant notre nation — chômage des jeunes, fracture sociale, tensions communautaires — le FPP estime qu'il est impératif d'engager un dialogue national sincère, inclusif et constructif.

Nous proposons la mise en place d'une plateforme de concertation ouverte à tous les partis politiques, à la société civile, aux organisations syndicales et aux autorités traditionnelles.

Le FPP reste disponible et engagé pour contribuer à la paix, à la stabilité et au développement de notre cher pays.

Fait à Abidjan, le 25 mars 2026.
Le Président du FPP,
Dabé Nogbo Wanaminou""",
        "category": "Communiqué",
        "is_featured": False,
        "published_at": now - timedelta(days=12),
    },
    {
        "title": "Coopération panafricaine : le FPP renforce ses liens continentaux",
        "summary": "Le Président du FPP a rencontré plusieurs leaders de mouvements panafricains lors d'un sommet à Accra.",
        "content": """Dans le cadre de sa vision panafricaine, le Président Dabé Nogbo Wanaminou a participé à un sommet des mouvements panafricains à Accra, Ghana.

Cette rencontre a permis d'échanger sur les défis communs auxquels font face les peuples africains et de renforcer les liens de solidarité entre mouvements progressistes du continent.

Parmi les sujets abordés :
- L'intégration économique africaine
- La souveraineté monétaire
- La coopération Sud-Sud
- La lutte contre le néocolonialisme

"L'Afrique a les ressources et les talents pour se développer par elle-même. Il nous faut la volonté politique et l'unité", a déclaré le Président du FPP à l'issue du sommet.""",
        "category": "International",
        "is_featured": False,
        "published_at": now - timedelta(days=15),
    },
    {
        "title": "Hausse des prix : les propositions concrètes du FPP",
        "summary": "Face à la flambée des prix des denrées alimentaires, le FPP propose un plan d'urgence en 5 points.",
        "content": """Le Front Patriotique Panafricain exprime sa vive préoccupation face à la hausse continue des prix des produits de première nécessité qui frappe durement les ménages ivoiriens.

Le FPP propose un plan d'urgence en 5 points :

1. **Plafonnement temporaire des prix** sur les produits de base (riz, huile, sucre).
2. **Soutien aux producteurs locaux** — Subventions ciblées pour l'agriculture vivrière.
3. **Réduction des taxes** sur les importations alimentaires essentielles.
4. **Filets sociaux** — Renforcement des aides directes aux familles les plus vulnérables.
5. **Contrôle des marges** — Lutte contre la spéculation et les intermédiaires abusifs.

"La vie chère n'est pas une fatalité. C'est le résultat de choix politiques que nous pouvons changer", affirme le porte-parole du FPP.""",
        "category": "Économie",
        "is_featured": False,
        "published_at": now - timedelta(days=20),
    },
]

for a in articles_data:
    cat_name = a.pop("category")
    obj, created = Article.objects.get_or_create(
        title=a["title"],
        defaults={
            **a,
            "category": cats[cat_name],
            "author": user,
            "status": "published",
        },
    )
    status = "créé" if created else "existe déjà"
    print(f"  📰 {status}: {obj.title}")

print(f"\n✅ Articles: {Article.objects.count()} total\n")

# ═══════════════════════════════════════════════════════════════════════════
# 4. ÉVÉNEMENTS (AGENDA)
# ═══════════════════════════════════════════════════════════════════════════
events_data = [
    {
        "title": "Congrès National du FPP — Édition 2026",
        "description": "Grand congrès national du Front Patriotique Panafricain réunissant les délégués de toutes les régions de Côte d'Ivoire. Bilan des activités, adoption des résolutions et élection du bureau national.",
        "short_description": "Congrès national avec l'ensemble des délégués régionaux.",
        "event_type": "meeting",
        "status": "upcoming",
        "start_date": now + timedelta(days=30),
        "end_date": now + timedelta(days=32),
        "location": "Palais de la Culture",
        "city": "Abidjan",
        "address": "Boulevard de la Paix, Treichville, Abidjan",
        "organizer": "Bureau National du FPP",
        "contact_email": "info@fpp-ci.online",
        "is_featured": True,
    },
    {
        "title": "Meeting populaire — Commune de Cocody",
        "description": "Le FPP organise un grand meeting populaire dans la commune de Cocody. Venez nombreux écouter les propositions du Parti pour votre commune et pour la Côte d'Ivoire.",
        "short_description": "Grand meeting populaire à Cocody.",
        "event_type": "rally",
        "status": "upcoming",
        "start_date": now + timedelta(days=14),
        "end_date": now + timedelta(days=14, hours=4),
        "location": "Place Jean-Paul II",
        "city": "Cocody",
        "address": "Place Jean-Paul II, Cocody, Abidjan",
        "organizer": "Section FPP Cocody",
        "contact_email": "info@fpp-ci.online",
        "is_featured": False,
    },
    {
        "title": "Atelier de formation — Leadership et engagement citoyen",
        "description": "Atelier de formation destiné aux jeunes militants du FPP. Thèmes : leadership politique, communication, gestion de projet communautaire et engagement citoyen.",
        "short_description": "Formation au leadership pour les jeunes militants.",
        "event_type": "workshop",
        "status": "upcoming",
        "start_date": now + timedelta(days=7),
        "end_date": now + timedelta(days=7, hours=6),
        "location": "Siège du FPP",
        "city": "Abidjan",
        "organizer": "Commission Jeunesse du FPP",
        "contact_email": "info@fpp-ci.online",
        "is_featured": False,
    },
    {
        "title": "Conférence de presse — Bilan et perspectives",
        "description": "Conférence de presse du Président Dabé Nogbo Wanaminou sur le bilan des actions du Parti et les perspectives pour les prochains mois.",
        "short_description": "Point presse du Président du FPP.",
        "event_type": "conference",
        "status": "upcoming",
        "start_date": now + timedelta(days=3),
        "end_date": now + timedelta(days=3, hours=2),
        "location": "Hôtel Ivoire",
        "city": "Abidjan",
        "address": "Boulevard Hassan II, Cocody, Abidjan",
        "organizer": "Service Communication du FPP",
        "contact_email": "info@fpp-ci.online",
        "is_featured": False,
    },
    {
        "title": "Cérémonie d'hommage aux pionniers du panafricanisme",
        "description": "Le FPP rend hommage aux grandes figures du panafricanisme — Kwame Nkrumah, Patrice Lumumba, Thomas Sankara — à travers une cérémonie culturelle et mémorielle.",
        "short_description": "Hommage aux figures du panafricanisme.",
        "event_type": "ceremony",
        "status": "upcoming",
        "start_date": now + timedelta(days=21),
        "end_date": now + timedelta(days=21, hours=3),
        "location": "Espace Latrille",
        "city": "Abidjan",
        "organizer": "Commission Culture du FPP",
        "contact_email": "info@fpp-ci.online",
        "is_featured": False,
    },
    {
        "title": "Meeting de Yopougon — Juillet 2025",
        "description": "Retour sur le meeting historique du FPP à Yopougon qui a rassemblé des milliers de sympathisants.",
        "short_description": "Meeting historique à Yopougon.",
        "event_type": "rally",
        "status": "completed",
        "start_date": now - timedelta(days=270),
        "end_date": now - timedelta(days=270) + timedelta(hours=5),
        "location": "Place publique de Yopougon",
        "city": "Yopougon",
        "organizer": "Bureau National du FPP",
        "contact_email": "info@fpp-ci.online",
        "is_featured": False,
        "published_at": now - timedelta(days=275),
    },
]

for e in events_data:
    obj, created = Event.objects.get_or_create(
        title=e["title"],
        defaults={
            **e,
            "is_active": True,
            "published_at": e.get("published_at", now),
        },
    )
    status = "créé" if created else "existe déjà"
    print(f"  📅 {status}: {obj.title}")

print(f"\n✅ Events: {Event.objects.count()} total")
print("\n🎉 Seed terminé avec succès !")