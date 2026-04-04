<script setup lang="ts">
const lastUpdated = '3 avril 2026'
const partyName = 'Front Patriotique Panafricain (FPP)'
const siteUrl = 'fpp-ci.online'
const contactEmail = 'info@fpp-ci.online'
const contactPhone = '+225 01 01 36 31 31 / +225 05 95 02 17 07'
</script>

<template>
  <div>
    <section class="relative bg-[var(--color-primary)] py-16 md:py-20 overflow-hidden">
      <div class="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,rgba(22,163,74,0.12),transparent_60%)]" />
      <div class="relative mx-auto max-w-[var(--container-xl)] px-6 text-center">
        <p class="font-heading text-xs font-bold uppercase tracking-[0.15em] text-[var(--color-accent)] mb-4">
          Informations légales
        </p>
        <h1 class="font-heading text-3xl md:text-4xl font-extrabold text-white leading-tight mb-3">
          Conditions Générales d'Utilisation
        </h1>
        <p class="text-sm text-white/50">
          Dernière mise à jour : {{ lastUpdated }}
        </p>
      </div>
    </section>

    <section class="bg-white py-12 md:py-16">
      <div class="mx-auto max-w-[var(--container-md)] px-6">
        <article class="prose prose-sm max-w-none text-[var(--color-text)] leading-relaxed space-y-8">

          <div>
            <h2 class="font-heading text-lg font-extrabold text-[var(--color-primary)] mb-3">Article 1 — Objet</h2>
            <p>
              Les présentes Conditions Générales d'Utilisation (ci-après « CGU ») régissent l'accès et l'utilisation
              de la plateforme numérique du <strong>{{ partyName }}</strong> accessible à l'adresse
              <strong>{{ siteUrl }}</strong> (ci-après « la Plateforme »).
            </p>
            <p>
              L'utilisation de la Plateforme implique l'acceptation pleine et entière des présentes CGU.
              Si vous n'acceptez pas ces conditions, vous êtes prié(e) de ne pas utiliser la Plateforme.
            </p>
          </div>

          <div>
            <h2 class="font-heading text-lg font-extrabold text-[var(--color-primary)] mb-3">Article 2 — Cadre juridique</h2>
            <p>
              Les présentes CGU sont établies en conformité avec la législation de la République de Côte d'Ivoire,
              notamment :
            </p>
            <ul class="list-disc pl-5 space-y-1 text-sm">
              <li>La <strong>Loi n° 2013-450 du 19 juin 2013</strong> relative à la protection des données à caractère personnel ;</li>
              <li>La <strong>Loi n° 2013-451 du 19 juin 2013</strong> relative à la lutte contre la cybercriminalité ;</li>
              <li>La <strong>Loi n° 2014-546 du 5 août 2014</strong> relative aux transactions électroniques ;</li>
              <li>La <strong>Constitution de la République de Côte d'Ivoire</strong>, notamment ses dispositions relatives à la liberté d'association et d'expression.</li>
            </ul>
          </div>

          <div>
            <h2 class="font-heading text-lg font-extrabold text-[var(--color-primary)] mb-3">Article 3 — Éditeur de la Plateforme</h2>
            <p>
              La Plateforme est éditée par le <strong>{{ partyName }}</strong>, parti politique légalement constitué
              et enregistré conformément à la législation ivoirienne sur les partis politiques et groupements politiques.
            </p>
            <ul class="list-disc pl-5 space-y-1 text-sm">
              <li><strong>Siège :</strong> Abidjan, Côte d'Ivoire</li>
              <li><strong>Site web :</strong> <a href="https://fpp-ci.online/" target="_blank" class="text-[var(--color-accent)] no-underline hover:underline">https://fpp-ci.online/</a></li>
              <li><strong>Email :</strong> {{ contactEmail }}</li>
              <li><strong>Téléphone :</strong> {{ contactPhone }}</li>
              <li><strong>Directeur de publication :</strong> Le Président du FPP</li>
            </ul>
          </div>

          <div>
            <h2 class="font-heading text-lg font-extrabold text-[var(--color-primary)] mb-3">Article 4 — Accès à la Plateforme</h2>
            <p>
              La Plateforme est accessible gratuitement à tout utilisateur disposant d'un accès à Internet.
              Certaines fonctionnalités nécessitent la création d'un compte (inscription en tant que sympathisant)
              ou l'adhésion formelle au parti (statut de membre).
            </p>
            <p>
              Le {{ partyName }} se réserve le droit de suspendre ou d'interrompre l'accès à la Plateforme
              pour des raisons de maintenance, de mise à jour ou pour tout autre motif, sans préavis ni indemnité.
            </p>
          </div>

          <div>
            <h2 class="font-heading text-lg font-extrabold text-[var(--color-primary)] mb-3">Article 5 — Inscription et compte utilisateur</h2>
            <p>Pour créer un compte, l'utilisateur doit :</p>
            <ul class="list-disc pl-5 space-y-1 text-sm">
              <li>Être âgé d'au moins <strong>18 ans</strong> ;</li>
              <li>Fournir des informations exactes, complètes et à jour ;</li>
              <li>Accepter les présentes CGU et la Politique de Confidentialité ;</li>
              <li>Vérifier son adresse email via le lien de confirmation envoyé.</li>
            </ul>
            <p>
              L'utilisateur est responsable de la confidentialité de ses identifiants de connexion.
              Toute utilisation de son compte est présumée faite par lui.
              En cas de suspicion d'utilisation frauduleuse, l'utilisateur doit en informer immédiatement le parti.
            </p>
          </div>

          <div>
            <h2 class="font-heading text-lg font-extrabold text-[var(--color-primary)] mb-3">Article 6 — Obligations de l'utilisateur</h2>
            <p>L'utilisateur s'engage à :</p>
            <ul class="list-disc pl-5 space-y-1 text-sm">
              <li>Utiliser la Plateforme conformément à sa finalité et à la législation en vigueur ;</li>
              <li>Ne pas diffuser de contenus illicites, diffamatoires, injurieux, incitant à la haine ou à la violence ;</li>
              <li>Ne pas tenter de porter atteinte à la sécurité, à l'intégrité ou à la disponibilité de la Plateforme ;</li>
              <li>Ne pas usurper l'identité d'un tiers ;</li>
              <li>Respecter les droits de propriété intellectuelle du {{ partyName }} et des tiers.</li>
            </ul>
          </div>

          <div>
            <h2 class="font-heading text-lg font-extrabold text-[var(--color-primary)] mb-3">Article 7 — Propriété intellectuelle</h2>
            <p>
              L'ensemble des contenus présents sur la Plateforme (textes, images, logos, graphismes, vidéos,
              bases de données, logiciels) est protégé par le droit de la propriété intellectuelle.
            </p>
            <p>
              Toute reproduction, représentation, modification, distribution ou exploitation non autorisée,
              en tout ou partie, est strictement interdite et constitue une infraction sanctionnée par la loi.
            </p>
          </div>

          <div>
            <h2 class="font-heading text-lg font-extrabold text-[var(--color-primary)] mb-3">Article 8 — Données personnelles</h2>
            <p>
              Le traitement des données personnelles collectées via la Plateforme est soumis à la
              <strong>Loi n° 2013-450 du 19 juin 2013</strong> relative à la protection des données à caractère personnel.
            </p>
            <p>
              Pour plus d'informations sur la collecte, l'utilisation et la protection de vos données,
              veuillez consulter notre
              <RouterLink to="/politique-confidentialite" class="text-[var(--color-accent)] font-semibold no-underline hover:underline">
                Politique de Confidentialité
              </RouterLink>.
            </p>
          </div>

          <div>
            <h2 class="font-heading text-lg font-extrabold text-[var(--color-primary)] mb-3">Article 9 — Cookies</h2>
            <p>
              La Plateforme utilise des cookies techniques nécessaires à son bon fonctionnement
              (authentification, session, préférences). Aucun cookie publicitaire ou de tracking tiers n'est utilisé.
            </p>
          </div>

          <div>
            <h2 class="font-heading text-lg font-extrabold text-[var(--color-primary)] mb-3">Article 10 — Responsabilité</h2>
            <p>
              Le {{ partyName }} s'efforce d'assurer l'exactitude des informations diffusées sur la Plateforme,
              mais ne saurait garantir leur exhaustivité ni l'absence d'erreurs.
            </p>
            <p>
              La responsabilité du {{ partyName }} ne saurait être engagée en cas de force majeure,
              de dysfonctionnement du réseau Internet, ou de tout événement échappant à son contrôle.
            </p>
          </div>

          <div>
            <h2 class="font-heading text-lg font-extrabold text-[var(--color-primary)] mb-3">Article 11 — Suspension et résiliation</h2>
            <p>
              Le {{ partyName }} se réserve le droit de suspendre ou de supprimer tout compte utilisateur
              en cas de violation des présentes CGU, sans préavis et sans indemnité.
              L'utilisateur en sera informé par email.
            </p>
            <p>
              L'utilisateur peut à tout moment demander la suppression de son compte en contactant
              le parti à l'adresse <strong>{{ contactEmail }}</strong>.
            </p>
          </div>

          <div>
            <h2 class="font-heading text-lg font-extrabold text-[var(--color-primary)] mb-3">Article 12 — Modification des CGU</h2>
            <p>
              Le {{ partyName }} se réserve le droit de modifier les présentes CGU à tout moment.
              Les utilisateurs seront informés de toute modification substantielle.
              La poursuite de l'utilisation de la Plateforme après notification vaut acceptation
              des nouvelles conditions.
            </p>
          </div>

          <div>
            <h2 class="font-heading text-lg font-extrabold text-[var(--color-primary)] mb-3">Article 13 — Droit applicable et juridiction</h2>
            <p>
              Les présentes CGU sont régies par le droit ivoirien. Tout litige relatif à leur interprétation
              ou à leur exécution sera soumis aux juridictions compétentes d'Abidjan, Côte d'Ivoire.
            </p>
          </div>

          <div>
            <h2 class="font-heading text-lg font-extrabold text-[var(--color-primary)] mb-3">Article 14 — Contact</h2>
            <p>
              Pour toute question relative aux présentes CGU, vous pouvez nous contacter :
            </p>
            <ul class="list-disc pl-5 space-y-1 text-sm">
              <li><strong>Email :</strong> {{ contactEmail }}</li>
              <li><strong>Téléphone :</strong> {{ contactPhone }}</li>
              <li><strong>Site web :</strong> <a href="https://fpp-ci.online/" target="_blank" class="text-[var(--color-accent)] no-underline hover:underline">https://fpp-ci.online/</a></li>
              <li><strong>Adresse :</strong> Siège du FPP, Abidjan, Côte d'Ivoire</li>
            </ul>
          </div>

        </article>
      </div>
    </section>
  </div>
</template>
