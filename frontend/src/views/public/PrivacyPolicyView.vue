<script setup lang="ts">
import { RouterLink } from 'vue-router'

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
          Protection des données
        </p>
        <h1 class="font-heading text-3xl md:text-4xl font-extrabold text-white leading-tight mb-3">
          Politique de Confidentialité
        </h1>
        <p class="text-sm text-white/50">
          Dernière mise à jour : {{ lastUpdated }} — Conforme à la Loi n° 2013-450
        </p>
      </div>
    </section>

    <section class="bg-white py-12 md:py-16">
      <div class="mx-auto max-w-[var(--container-md)] px-6">
        <article class="prose prose-sm max-w-none text-[var(--color-text)] leading-relaxed space-y-8">

          <div>
            <h2 class="font-heading text-lg font-extrabold text-[var(--color-primary)] mb-3">Article 1 — Responsable du traitement</h2>
            <p>
              Le responsable du traitement des données à caractère personnel collectées via la plateforme
              <strong>{{ siteUrl }}</strong> est le <strong>{{ partyName }}</strong>, parti politique enregistré
              en République de Côte d'Ivoire.
            </p>
            <ul class="list-disc pl-5 space-y-1 text-sm">
              <li><strong>Siège :</strong> Abidjan, Côte d'Ivoire</li>
              <li><strong>Site web :</strong> <a href="https://fpp-ci.online/" target="_blank" class="text-[var(--color-accent)] no-underline hover:underline">https://fpp-ci.online/</a></li>
              <li><strong>Email :</strong> {{ contactEmail }}</li>
              <li><strong>Téléphone :</strong> {{ contactPhone }}</li>
            </ul>
          </div>

          <div>
            <h2 class="font-heading text-lg font-extrabold text-[var(--color-primary)] mb-3">Article 2 — Cadre juridique</h2>
            <p>
              La présente Politique de Confidentialité est établie conformément à la
              <strong>Loi n° 2013-450 du 19 juin 2013</strong> relative à la protection des données à caractère
              personnel en Côte d'Ivoire, et aux dispositions de l'<strong>Autorité de Régulation des
              Télécommunications/TIC de Côte d'Ivoire (ARTCI)</strong>.
            </p>
            <p>
              Conformément à l'article 33 de ladite loi, nous enregistrons et conservons la preuve
              de votre consentement (horodatage, adresse IP) lors de votre inscription.
            </p>
          </div>

          <div>
            <h2 class="font-heading text-lg font-extrabold text-[var(--color-primary)] mb-3">Article 3 — Données collectées</h2>
            <p>
              Dans le cadre de l'inscription et de l'utilisation de la Plateforme, nous collectons
              les catégories de données suivantes :
            </p>
            <h3 class="font-heading text-sm font-bold text-[var(--color-primary)] mt-4 mb-2">3.1 — Données d'identification</h3>
            <ul class="list-disc pl-5 space-y-1 text-sm">
              <li>Nom et prénom</li>
              <li>Sexe</li>
              <li>Date de naissance</li>
              <li>Adresse email</li>
              <li>Numéro de téléphone</li>
              <li>Photo d'identité (pour les membres adhérents)</li>
            </ul>
            <h3 class="font-heading text-sm font-bold text-[var(--color-primary)] mt-4 mb-2">3.2 — Données d'adhésion</h3>
            <ul class="list-disc pl-5 space-y-1 text-sm">
              <li>Type et numéro de pièce d'identité</li>
              <li>Ville, commune, quartier de résidence</li>
              <li>Région et sous-section d'affectation</li>
              <li>Matricule de membre</li>
            </ul>
            <h3 class="font-heading text-sm font-bold text-[var(--color-primary)] mt-4 mb-2">3.3 — Données techniques</h3>
            <ul class="list-disc pl-5 space-y-1 text-sm">
              <li>Adresse IP</li>
              <li>Navigateur et système d'exploitation (User-Agent)</li>
              <li>Horodatage des connexions et des consentements</li>
            </ul>
            <p class="text-sm mt-2">
              Ces données techniques sont utilisées par les équipes techniques du {{ partyName }}
              dans le but d'améliorer la Plateforme et l'expérience utilisateur (diagnostic de problèmes,
              optimisation des performances, analyse d'usage anonymisée).
            </p>
          </div>

          <div>
            <h2 class="font-heading text-lg font-extrabold text-[var(--color-primary)] mb-3">Article 4 — Finalités du traitement</h2>
            <p>Vos données sont collectées et traitées pour les finalités suivantes :</p>
            <ul class="list-disc pl-5 space-y-1 text-sm">
              <li>Gestion de votre compte et de votre inscription en tant que sympathisant ou membre ;</li>
              <li>Traitement et suivi de votre demande d'adhésion au parti ;</li>
              <li>Communication d'informations relatives aux activités du parti (événements, actualités, publications) ;</li>
              <li>Gestion interne du fichier des membres (articles 17 et 18 de la Loi 2013-450) ;</li>
              <li>Amélioration de la Plateforme et de l'expérience utilisateur (données techniques) ;</li>
              <li>Respect des obligations légales et réglementaires ;</li>
              <li>Preuve du consentement conformément à l'article 33 de la Loi 2013-450.</li>
            </ul>
          </div>

          <div>
            <h2 class="font-heading text-lg font-extrabold text-[var(--color-primary)] mb-3">Article 5 — Base légale du traitement</h2>
            <p>Les traitements de données reposent sur :</p>
            <ul class="list-disc pl-5 space-y-1 text-sm">
              <li><strong>Votre consentement explicite</strong> recueilli lors de l'inscription (article 10 de la Loi 2013-450) ;</li>
              <li><strong>L'exécution d'un engagement</strong> lié à votre adhésion au parti ;</li>
              <li><strong>L'intérêt légitime</strong> du {{ partyName }} pour la gestion de ses membres et activités.</li>
            </ul>
          </div>

          <div>
            <h2 class="font-heading text-lg font-extrabold text-[var(--color-primary)] mb-3">Article 6 — Destinataires des données</h2>
            <p>Vos données personnelles sont accessibles uniquement aux :</p>
            <ul class="list-disc pl-5 space-y-1 text-sm">
              <li>Responsables habilités du {{ partyName }} (bureau exécutif, secrétariat général) ;</li>
              <li>Administrateurs de la Plateforme, dans le strict cadre de leurs fonctions ;</li>
              <li>Sous-traitants techniques (hébergement, maintenance), tenus par des obligations de confidentialité.</li>
            </ul>
            <p>
              Aucune donnée n'est vendue, cédée ou partagée avec des tiers à des fins commerciales ou publicitaires.
            </p>
          </div>

          <div>
            <h2 class="font-heading text-lg font-extrabold text-[var(--color-primary)] mb-3">Article 7 — Durée de conservation</h2>
            <ul class="list-disc pl-5 space-y-1 text-sm">
              <li><strong>Données de compte :</strong> conservées pendant toute la durée d'activité du compte, puis 3 ans après sa suppression ;</li>
              <li><strong>Données d'adhésion :</strong> conservées pendant la durée de l'adhésion et 5 ans après la fin de celle-ci ;</li>
              <li><strong>Journaux de consentement :</strong> conservés pendant 10 ans conformément aux obligations de preuve (article 33 de la Loi 2013-450) ;</li>
              <li><strong>Données techniques :</strong> conservées pendant 12 mois.</li>
            </ul>
          </div>

          <div>
            <h2 class="font-heading text-lg font-extrabold text-[var(--color-primary)] mb-3">Article 8 — Vos droits</h2>
            <p>
              Conformément à la <strong>Loi n° 2013-450 du 19 juin 2013</strong>, vous bénéficiez des droits suivants :
            </p>

            <h3 class="font-heading text-sm font-bold text-[var(--color-primary)] mt-4 mb-2">8.1 — Droit d'information (art. 28)</h3>
            <p class="text-sm">
              Vous avez le droit d'être informé(e) de l'existence du traitement de vos données et de ses finalités.
            </p>

            <h3 class="font-heading text-sm font-bold text-[var(--color-primary)] mt-4 mb-2">8.2 — Droit d'accès (art. 29)</h3>
            <p class="text-sm">
              Vous pouvez à tout moment obtenir la confirmation que vos données sont traitées et en obtenir une copie.
            </p>

            <h3 class="font-heading text-sm font-bold text-[var(--color-primary)] mt-4 mb-2">8.3 — Droit de rectification (art. 31)</h3>
            <p class="text-sm">
              Vous pouvez demander la rectification de données inexactes, incomplètes ou périmées.
            </p>

            <h3 class="font-heading text-sm font-bold text-[var(--color-primary)] mt-4 mb-2">8.4 — Droit d'opposition (art. 30)</h3>
            <p class="text-sm">
              Vous pouvez vous opposer, pour des motifs légitimes, au traitement de vos données.
            </p>

            <h3 class="font-heading text-sm font-bold text-[var(--color-primary)] mt-4 mb-2">8.5 — Droit de suppression et droit à l'oubli (art. 31-33)</h3>
            <p class="text-sm">
              Vous pouvez demander la suppression de vos données lorsqu'elles ne sont plus nécessaires
              au regard des finalités pour lesquelles elles ont été collectées, ou lorsque vous retirez votre consentement.
            </p>

            <h3 class="font-heading text-sm font-bold text-[var(--color-primary)] mt-4 mb-2">8.6 — Droit à la portabilité (art. 38)</h3>
            <p class="text-sm">
              Vous pouvez obtenir vos données dans un format structuré et couramment utilisé.
            </p>

            <h3 class="font-heading text-sm font-bold text-[var(--color-primary)] mt-4 mb-2">8.7 — Droit de retirer votre consentement (art. 33)</h3>
            <p class="text-sm">
              Vous pouvez retirer votre consentement à tout moment. Le retrait du consentement ne compromet
              pas la licéité du traitement fondé sur le consentement effectué avant ce retrait.
            </p>

            <div class="mt-4 p-4 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg">
              <p class="text-sm">
                <strong>Pour exercer vos droits :</strong> adressez votre demande accompagnée d'une copie de pièce d'identité
                à <strong>{{ contactEmail }}</strong> ou par courrier au siège du FPP à Abidjan,
                ou par téléphone au <strong>{{ contactPhone }}</strong>.
                Nous y répondrons dans un délai de <strong>30 jours</strong>.
              </p>
            </div>
          </div>

          <div>
            <h2 class="font-heading text-lg font-extrabold text-[var(--color-primary)] mb-3">Article 9 — Sécurité des données</h2>
            <p>
              Conformément aux obligations de sécurité prévues par la Loi 2013-450, le {{ partyName }}
              met en œuvre les mesures techniques et organisationnelles appropriées pour protéger vos données :
            </p>
            <ul class="list-disc pl-5 space-y-1 text-sm">
              <li>Chiffrement des communications (HTTPS/TLS) ;</li>
              <li>Hachage sécurisé des mots de passe ;</li>
              <li>Restriction d'accès aux données selon les rôles ;</li>
              <li>Sauvegardes régulières et chiffrées ;</li>
              <li>Journalisation des accès et des modifications (piste d'audit) ;</li>
              <li>Protection contre les accès non autorisés et les intrusions.</li>
            </ul>
          </div>

          <div>
            <h2 class="font-heading text-lg font-extrabold text-[var(--color-primary)] mb-3">Article 10 — Transfert de données</h2>
            <p>
              Vos données sont hébergées sur des serveurs sécurisés. En cas de transfert vers un pays tiers,
              nous nous assurons que ce pays offre un niveau de protection adéquat conformément
              aux dispositions de la Loi 2013-450 et aux recommandations de l'ARTCI.
            </p>
          </div>

          <div>
            <h2 class="font-heading text-lg font-extrabold text-[var(--color-primary)] mb-3">Article 11 — Consentement et preuve</h2>
            <p>
              Lors de votre inscription, votre consentement aux présentes CGU et à la Politique de Confidentialité
              est recueilli de manière explicite par l'activation d'une case à cocher.
            </p>
            <p>
              Conformément à l'article 33 de la Loi 2013-450, nous conservons la preuve de ce consentement
              comprenant :
            </p>
            <ul class="list-disc pl-5 space-y-1 text-sm">
              <li>L'horodatage (date et heure) de l'acceptation ;</li>
              <li>L'adresse IP de l'utilisateur au moment du consentement ;</li>
              <li>La version des CGU et de la Politique de Confidentialité acceptées ;</li>
              <li>Les informations techniques du navigateur.</li>
            </ul>
          </div>

          <div>
            <h2 class="font-heading text-lg font-extrabold text-[var(--color-primary)] mb-3">Article 12 — Autorité de contrôle</h2>
            <p>
              Si vous estimez que le traitement de vos données porte atteinte à vos droits,
              vous pouvez introduire une réclamation auprès de l'<strong>Autorité de Régulation des
              Télécommunications/TIC de Côte d'Ivoire (ARTCI)</strong> :
            </p>
            <ul class="list-disc pl-5 space-y-1 text-sm">
              <li><strong>Adresse géographique :</strong> Abidjan — Marcory Anoumanbo</li>
              <li><strong>Adresse postale :</strong> 18 BP 2203 Abidjan 18, Côte d'Ivoire</li>
              <li><strong>Téléphone :</strong> +225 27 20 34 43 73 / +225 27 20 34 43 74</li>
              <li><strong>Fax :</strong> +225 27 20 34 43 75</li>
              <li><strong>Email :</strong> courrier@artci.ci</li>
              <li><strong>Site web :</strong> <a href="https://www.artci.ci" target="_blank" class="text-[var(--color-accent)] no-underline hover:underline">www.artci.ci</a></li>
            </ul>
          </div>

          <div>
            <h2 class="font-heading text-lg font-extrabold text-[var(--color-primary)] mb-3">Article 13 — Modification de la Politique</h2>
            <p>
              Le {{ partyName }} se réserve le droit de modifier la présente Politique de Confidentialité.
              Toute modification substantielle sera notifiée aux utilisateurs. En cas de modification
              des finalités du traitement, un nouveau consentement sera sollicité.
            </p>
          </div>

          <div>
            <h2 class="font-heading text-lg font-extrabold text-[var(--color-primary)] mb-3">Article 14 — Contact</h2>
            <p>
              Pour toute question relative à la protection de vos données personnelles :
            </p>
            <ul class="list-disc pl-5 space-y-1 text-sm">
              <li><strong>Email :</strong> {{ contactEmail }}</li>
              <li><strong>Téléphone :</strong> {{ contactPhone }}</li>
              <li><strong>Site web :</strong> <a href="https://fpp-ci.online/" target="_blank" class="text-[var(--color-accent)] no-underline hover:underline">https://fpp-ci.online/</a></li>
              <li><strong>Siège :</strong> FPP, Abidjan, Côte d'Ivoire</li>
            </ul>
          </div>

          <div class="mt-8 pt-6 border-t border-[var(--color-border)]">
            <p class="text-xs text-[var(--color-muted)] text-center">
              Voir également nos
              <RouterLink to="/cgu" class="text-[var(--color-accent)] font-semibold no-underline hover:underline">
                Conditions Générales d'Utilisation
              </RouterLink>
            </p>
          </div>

        </article>
      </div>
    </section>
  </div>
</template>
