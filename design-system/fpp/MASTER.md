# FPP — Design System Master

> **LOGIC:** When building a specific page, first check `design-system/fpp/pages/[page-name].md`.
> If that file exists, its rules **override** this Master file.
> If not, strictly follow the rules below.

---

**Project:** FPP — Front Patriotique Panafricain
**Style:** Swiss Modernism 2.0 + Flat Design
**Theme:** Light mode only (pas de dark mode)
**Ton:** Institutionnel, moderne, sobre, crédible, engageant pour la jeunesse

---

## Palette de couleurs

### Couleurs principales

| Rôle | Hex | OKLCH | CSS Variable | Usage |
|------|-----|-------|--------------|-------|
| Noir primaire | `#111111` | `oklch(15% 0.005 145)` | `--color-primary` | Texte principal, titres, navbar |
| Noir doux | `#1F1F1F` | `oklch(20% 0.005 145)` | `--color-primary-soft` | Texte secondaire fort |
| Blanc | `#FFFFFF` | — | `--color-background` | Fond principal |
| Fond clair | `#F6F7F6` | `oklch(97% 0.005 145)` | `--color-surface` | Sections alternées, cards |
| Bordure | `#E0E5E0` | `oklch(90% 0.008 145)` | `--color-border` | Séparateurs, contours |
| Texte secondaire | `#52594F` | `oklch(42% 0.01 145)` | `--color-muted` | Labels, métadonnées |
| **Accent vert** | `#16A34A` | `oklch(62% 0.17 145)` | `--color-accent` | CTA, liens, badges, focus |
| Accent hover | `#138A3E` | `oklch(55% 0.15 145)` | `--color-accent-hover` | Hover sur accent |
| Accent léger | `#DCFCE7` | `oklch(95% 0.05 145)` | `--color-accent-light` | Background badges, tags |

### Couleurs sémantiques

| Rôle | Hex | CSS Variable |
|------|-----|--------------|
| Success | `#16A34A` | `--color-success` (= accent) |
| Error | `#DC2626` | `--color-error` |
| Warning | `#D97706` | `--color-warning` |
| Info | `#2563EB` | `--color-info` |

### Règle 60-30-10

- **60%** : Blanc + fond clair (`--color-background`, `--color-surface`)
- **30%** : Noir + texte (`--color-primary`, `--color-muted`)
- **10%** : Vert accent (`--color-accent`) — CTA, liens actifs, focus, badges

> **Impeccable** : Les gris sont teintés vers le vert (hue 145) pour créer une cohésion subconsciente avec l'accent. Pas de gris pur (#808080).

---

## Typographie

### Polices

| Rôle | Police | Poids | Variable |
|------|--------|-------|----------|
| Titres | **Outfit** | 500, 600, 700 | `--font-heading` |
| Corps | **Work Sans** | 300, 400, 500 | `--font-body` |

**Google Fonts :**
```css
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@500;600;700&family=Work+Sans:wght@300;400;500&display=swap');
```

**Tailwind :**
```js
fontFamily: {
  heading: ['Outfit', 'sans-serif'],
  body: ['Work Sans', 'sans-serif'],
}
```

### Échelle typographique (ratio 1.25 — major third)

| Token | Taille | Line-height | Usage |
|-------|--------|-------------|-------|
| `--text-xs` | `0.75rem` (12px) | 1.5 | Captions, legal, badges |
| `--text-sm` | `0.875rem` (14px) | 1.5 | Métadonnées, labels |
| `--text-base` | `1rem` (16px) | 1.6 | Corps de texte |
| `--text-lg` | `1.25rem` (20px) | 1.5 | Lead text, sous-titres |
| `--text-xl` | `1.5rem` (24px) | 1.3 | Titres de section |
| `--text-2xl` | `2rem` (32px) | 1.2 | Titres de page |
| `--text-3xl` | `2.5rem` (40px) | 1.1 | Hero headlines |
| `--text-4xl` | `3rem` (48px) | 1.05 | Chiffres clés, stats |

**Max-width texte :** `max-width: 65ch` pour la lisibilité.

---

## Espacement (base 4px)

| Token | Valeur | Usage |
|-------|--------|-------|
| `--space-xs` | `4px` / `0.25rem` | Gaps serrés |
| `--space-sm` | `8px` / `0.5rem` | Icônes, inline |
| `--space-md` | `12px` / `0.75rem` | Padding inputs |
| `--space-base` | `16px` / `1rem` | Padding standard |
| `--space-lg` | `24px` / `1.5rem` | Gap entre éléments |
| `--space-xl` | `32px` / `2rem` | Séparation de groupes |
| `--space-2xl` | `48px` / `3rem` | Marges de sections |
| `--space-3xl` | `64px` / `4rem` | Padding hero |
| `--space-4xl` | `96px` / `6rem` | Séparation majeure |

**Impeccable** : Utiliser `gap` pour les spacements entre siblings. Éviter les margins pour les groupes.

---

## Ombres

| Niveau | Valeur | Usage |
|--------|--------|-------|
| `--shadow-sm` | `0 1px 3px rgba(17,17,17,0.06)` | Hover subtil |
| `--shadow-md` | `0 4px 8px rgba(17,17,17,0.08)` | Cards |
| `--shadow-lg` | `0 8px 24px rgba(17,17,17,0.10)` | Dropdowns, tooltips |
| `--shadow-xl` | `0 16px 48px rgba(17,17,17,0.12)` | Modals |

> Ombres teintées vers la couleur primaire (#111111), pas du noir pur.

---

## Composants

### Boutons

```css
/* Bouton primaire (accent vert) */
.btn-primary {
  background: var(--color-accent);
  color: white;
  padding: 12px 24px;
  border-radius: 8px;
  font-family: var(--font-heading);
  font-weight: 600;
  font-size: 0.875rem;
  letter-spacing: 0.01em;
  transition: background 200ms ease, transform 200ms ease;
  cursor: pointer;
}
.btn-primary:hover {
  background: var(--color-accent-hover);
  transform: translateY(-1px);
}
.btn-primary:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

/* Bouton secondaire (noir outline) */
.btn-secondary {
  background: transparent;
  color: var(--color-primary);
  border: 1.5px solid var(--color-primary);
  padding: 12px 24px;
  border-radius: 8px;
  font-family: var(--font-heading);
  font-weight: 600;
  font-size: 0.875rem;
  transition: background 200ms ease, color 200ms ease;
  cursor: pointer;
}
.btn-secondary:hover {
  background: var(--color-primary);
  color: white;
}

/* Bouton ghost */
.btn-ghost {
  background: transparent;
  color: var(--color-accent);
  padding: 12px 24px;
  border: none;
  font-weight: 500;
  cursor: pointer;
  transition: color 200ms ease;
}
.btn-ghost:hover {
  color: var(--color-accent-hover);
}
```

### Cards

```css
.card {
  background: white;
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 24px;
  transition: box-shadow 200ms ease, transform 200ms ease;
}
.card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}
.card-interactive {
  cursor: pointer;
}
```

### Inputs

```css
.input {
  padding: 12px 16px;
  border: 1.5px solid var(--color-border);
  border-radius: 8px;
  font-family: var(--font-body);
  font-size: 1rem;
  color: var(--color-primary);
  background: white;
  transition: border-color 200ms ease, box-shadow 200ms ease;
}
.input::placeholder {
  color: var(--color-muted);
}
.input:focus {
  border-color: var(--color-accent);
  outline: none;
  box-shadow: 0 0 0 3px var(--color-accent-light);
}
.input-error {
  border-color: var(--color-error);
}
```

### Navbar

```css
.navbar {
  background: white;
  border-bottom: 1px solid var(--color-border);
  padding: 0 var(--space-lg);
  height: 64px;
  position: sticky;
  top: 0;
  z-index: 50;
}
```

---

## Layout

### Grille (12 colonnes)

```css
.grid-12 {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: var(--space-lg);
}
```

### Conteneurs

| Nom | Max-width | Usage |
|-----|-----------|-------|
| `--container-sm` | `640px` | Formulaires, login |
| `--container-md` | `768px` | Articles, profils |
| `--container-lg` | `1024px` | Pages standard |
| `--container-xl` | `1280px` | Dashboard, listes |

### Responsive

| Breakpoint | Min-width | Usage |
|------------|-----------|-------|
| `sm` | `375px` | Mobile |
| `md` | `768px` | Tablette |
| `lg` | `1024px` | Desktop |
| `xl` | `1440px` | Grand écran |

---

## Iconographie

- **Librairie** : Lucide Icons (SVG)
- **Taille standard** : 20px (w-5 h-5)
- **Taille large** : 24px (w-6 h-6)
- **Couleur** : `currentColor` (hérite du texte)
- **Jamais d'emojis** comme icônes

---

## Motion

| Propriété | Valeur | Usage |
|-----------|--------|-------|
| `--duration-fast` | `150ms` | Hover, focus |
| `--duration-normal` | `200ms` | Transitions standard |
| `--duration-slow` | `300ms` | Entrées, apparitions |
| `--easing-default` | `cubic-bezier(0.4, 0, 0.2, 1)` | Standard (ease-out-quart) |

- Pas de bounce, pas d'elastic
- Respecter `prefers-reduced-motion: reduce`
- Stagger les animations d'entrée (50ms entre éléments)

---

## Anti-patterns INTERDITS

- ❌ Dark mode / fond noir
- ❌ Dégradés violet-bleu "AI style"
- ❌ Gris pur sans teinte
- ❌ Polices Inter, Roboto, Arial
- ❌ Emojis comme icônes
- ❌ Cards imbriquées dans des cards
- ❌ Glassmorphism décoratif
- ❌ Bounce / elastic easing
- ❌ Texte gris sur fond coloré
- ❌ Layout shift au hover (pas de scale sur les cards)
- ❌ Placeholders à faible contraste
- ❌ Tout centrer — préférer l'alignement gauche avec compositions asymétriques

---

## Checklist pré-livraison

- [ ] Aucun emoji comme icône (SVG Lucide uniquement)
- [ ] `cursor-pointer` sur tous les éléments cliquables
- [ ] Hover states avec transitions 150-300ms
- [ ] Contraste texte 4.5:1 minimum (WCAG AA)
- [ ] Focus visible pour la navigation clavier
- [ ] `prefers-reduced-motion` respecté
- [ ] Responsive testé : 375px, 768px, 1024px, 1440px
- [ ] Pas de contenu caché derrière une navbar fixe
- [ ] Pas de scroll horizontal mobile
- [ ] Tous les états traités : loading, empty, error, success, disabled
- [ ] Formulaires : labels visibles, messages d'erreur clairs, validation temps réel
