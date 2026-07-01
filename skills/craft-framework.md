---
name: craft-framework
description: Generates a complete, production-ready, self-contained single-file HTML website from a detailed description using the CRAFT framework (Context, Role, Action, Format, Target) and premium taste-skill directives. Use whenever a user wants to build, generate, prototype, or design a single-page website, landing page, or simple web application.
---

# CRAFT Framework Website Builder with Premium Taste

This skill enables the agent to act as an expert front-end developer and UI/UX designer, translating user descriptions and styles into high-quality, production-ready, single-file HTML websites. The design and implementation are guided by strict anti-slop, premium-agency aesthetic directives.

---

## [ C ] — CONTEXT & ANTI-SLOP NEGATIVE CONSTRAINTS

### 1. Single-File Portability
The entire website must reside inside a single HTML file. All styling (CSS) and logic (JavaScript) must be embedded directly. No external assets (images, stylesheets, scripts) are allowed, with the exception of:
- **Google Fonts** (for typography).
- **CDN Icons/Logos** (e.g., simple-icons / devicon CDN for logo walls).
- **Placeholder Photography** (e.g., desaturated Picsum photos with descriptive seeds).

### 2. Absolute Negative Constraints (Banned Elements)
To avoid generic AI templates, you must strictly avoid:
- **Banned Fonts:** DO NOT use `Inter`, `Roboto`, `Open Sans`, or `Helvetica` as the default font. Reach for character-rich pairings instead.
- **Banned Icons:** DO NOT hand-draw generic icons or mix families. Standardize stroke-width globally.
- **Banned Shadows:** DO NOT use heavy, dark box-shadows. Shadows must be practically non-existent or ultra-diffuse and low opacity (`rgba(0,0,0,0.03)`).
- **Banned Gradients:** DO NOT default to AI-purple gradients or glowing blobs. Use desaturated spots instead.
- **Banned Copy Clichés:** DO NOT use words like "elevate", "seamlessly", "unleash", "next-gen", "game-changer", "delve". Write plain, specific, professional language.
- **Banned Placeholders:** DO NOT use generic placeholder names like "John Doe", "Jane Doe", "Acme Corp", or "Lorem Ipsum". All copy must be fully written, contextual, and realistic.
- **Banned Formatting:** **ZERO em-dashes (`—`) anywhere in the text.** Use standard punctuation.
- **Banned Emojis:** DO NOT use emojis anywhere in the markup, headings, alt text, or body (unless explicitly requested for a playful vibe).
- **Banned Visual Clutter:** No version footers (`v1.0.0`), no decorative text strips (`BRAND. MOTION. SPATIAL.`), no scroll cues (`Scroll to explore`), no section-numbering eyebrows (`01 · capabilities`).

---

## [ R ] — ROLE & DESIGN PRINCIPLES

You are a Principal UI/UX Architect and Front-End Developer. Your designs must look like premium custom agency work ($150k+ budget). You design with haptic depth, spatial rhythm, and tactile feedback.

### 1. Typography Pairings
Establish a strong editorial hierarchy using Google Fonts:
- **Default Alternatives (Rotate, do not reuse the same pairing):**
  - **Satoshi + Geist Mono** (Clean technical/developer tool)
  - **Cabinet Grotesk + Switzer** (Modern agency/creative)
  - **Outfit + Cabinet Grotesk** (Premium consumer/lifestyle)
  - **Editorial Serif (Rarely, only if brand kit/vintage requires):** Reach for `Cormorant Garamond` or `EB Garamond`. *Instrument Serif* and *Fraunces* are banned as defaults.
- **Italic Descender Clearance:** When italic is used in display type, ensure `leading-[1.1]` or `line-height: 1.2` minimum to prevent descenders (`y g j p q`) from clipping.

### 2. Color Calibration & Page Theme Lock
- **Palette Consistency:** Pick one accent color and keep it identical across all sections.
- **Premium-Consumer Palette Ban:** Avoid the default beige + brass + oxblood + espresso family for artisan/premium-consumer briefs. Instead, rotate:
  - **Cold Luxury:** silver-grey + chrome + smoke (Tesla/Apple style)
  - **Forest:** deep green + bone + amber accent
  - **Black and Tan:** true off-black + warm tan, sharp contrast
  - **Cobalt + Cream:** saturated blue against cool slate/cream
- **Theme Lock:** The page has ONE theme. If the page is dark mode, all sections are dark mode. No light sections sandwiched in between (or vice versa).

### 3. Spatial Rhythm & Layout Discipline
- **Hero Height:** The Hero section must fit within the initial viewport (`min-h-[100dvh]` to prevent Safari jumping). H1 max 2 lines, subtext max 20 words, and primary CTAs must be visible without scrolling. Hero top padding is capped at `6rem` (`pt-24`) at desktop.
- **Layout Repetition Ban:** Once you use a layout family for a section (e.g., 3-column-cards, split-text-image), that family can appear at most ONCE on the page. Use at least 4 different layout families for an 8-section landing page.
- **Bento Grid Cell Count:** A bento grid has EXACTLY as many cells as you have content for (no blank tiles). At least 2-3 cells must have visual variation (e.g., images, desaturated patterns, or tinted backgrounds).
- **Zigzag Alternation Cap:** Max 2 consecutive split text-image layouts. Break the pattern with full-width sections or marquees.
- **Eyebrow Restraint:** An eyebrow (small uppercase wide-tracking mono label above H2) is limited to **max 1 eyebrow per 3 sections** (Hero counts as 1). Drop them elsewhere.
- **CTA Button Wrap & Intent:** CTA buttons must never wrap text at desktop (max 3 words). No two CTAs on the page should share the same intent (e.g., don't mix "Get in touch" and "Let's talk" on the same page).

---

## [ A ] — ACTION (STEP-BY-STEP WORKFLOW)

### Step 1: Design Read Inference (Before Writing Code)
First, output a one-line declaration of the design direction:
**"Reading this as: [page kind] for [audience], with a [vibe] language, leaning toward [aesthetic family or system]."**

### Step 2: Establish the Three Dials
Reason and declare the values for the three dials:
- **`DESIGN_VARIANCE`** (1-10): 1 = Perfect Symmetry, 10 = Artsy Chaos
- **`MOTION_INTENSITY`** (1-10): 1 = Static, 10 = Cinematic physics
- **`VISUAL_DENSITY`** (1-10): 1 = Airy/Art Gallery, 10 = Dense dashboard/cockpit

*Baseline for landing pages is `8 / 6 / 4`. Muted/minimalist styles lean toward `5 / 3 / 3`.*

### Step 3: Implement Structure, Styling & Motion
- **Double-Bezel Card Technique:** For premium cards, use nested containers:
  - Outer Shell: subtle background, hairline border, specific padding, large radius (e.g., `32px`).
  - Inner Core: core background, inner highlight/shadow, mathematically smaller radius (e.g., `calc(32px - 8px)`).
- **Tactile Hover/Active State:** Add button transitions with spring-like physics (`cubic-bezier(0.32, 0.72, 0, 1)`) and active downscales (`scale(0.98)`).
- **Mobile Menu Morph:** Create a clean floating glass header menu. The burger menu icon must animate fluidly to an 'X' on toggle.
- **Scroll Entry Animation:** Implement scroll staggers using an IntersectionObserver to dynamically reveal cards with a cascading delay.
- **Reduced Motion:** Wrap all motion behaviors under `@media (prefers-reduced-motion: reduce)` to gracefully collapse animations to static.

---

## [ F ] — FORMAT (TEMPLATE & CONVENTIONS)

The output must be a single, raw HTML string matching this structure. Use standard CSS variables for spacing, radius, and typography tokens.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="[Compelling SEO meta description]">
  <title>[Premium Descriptive Title]</title>
  
  <!-- Google Fonts Preconnect & Link -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=[Primary+Font]:wght@300;400;500;600;700&family=[Secondary+Font]:wght@400;500;600&display=swap" rel="stylesheet">
  
  <style>
    /* CSS Variables matching the chosen Dials & Palette */
    :root {
      --font-primary: '[Primary Font]', sans-serif;
      --font-mono: '[Secondary Font]', monospace;
      
      --bg-color: #0d0d0d; /* or light warm cream */
      --bg-card-outer: rgba(255, 255, 255, 0.03);
      --bg-card-inner: #141414;
      
      --accent-color: #e5c158; /* Accents desaturated under 80% */
      --text-primary: #f5f5f5;
      --text-secondary: #8e8e93;
      
      --border-hairline: 1px solid rgba(255, 255, 255, 0.08);
      --radius-outer: 24px;
      --radius-inner: calc(24px - 6px);
      
      --transition-spring: all 0.6s cubic-bezier(0.32, 0.72, 0, 1);
      --transition-fast: all 0.2s ease;
    }

    /* Reset & Base Layout */
    *, *::before, *::after {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      font-family: var(--font-primary);
      background-color: var(--bg-color);
      color: var(--text-primary);
      line-height: 1.6;
      overflow-x: hidden;
      -webkit-font-smoothing: antialiased;
    }

    /* Scroll entry animation placeholders */
    .reveal-item {
      opacity: 0;
      transform: translateY(20px);
      transition: opacity 0.8s cubic-bezier(0.16, 1, 0.3, 1), transform 0.8s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .reveal-item.revealed {
      opacity: 1;
      transform: translateY(0);
    }

    /* Custom styles go here... */
    @media (prefers-reduced-motion: reduce) {
      .reveal-item, * {
        transition: none !important;
        animation: none !important;
        transform: none !important;
        opacity: 1 !important;
      }
    }
  </style>
</head>
<body>

  <!-- Navigation / Header -->
  <header>
    <!-- Floating glass header layout -->
  </header>

  <main>
    <!-- Hero (fits initial viewport, max 20 words subtext, visible CTA) -->
    <!-- Logo wall / Social proof (uses simple-icons/devicon CDN) -->
    <!-- Feature Bento Grid (asymmetric, visual variety) -->
    <!-- Layout variations (no repeating layouts) -->
  </main>

  <footer>
    <!-- Footer layout -->
  </header>

  <script>
    document.addEventListener('DOMContentLoaded', () => {
      // Mobile hamburger burger menu morphing and overlay logic
      
      // Scroll entry animations via IntersectionObserver
      const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.15
      };
      
      const observer = new IntersectionObserver((entries, obs) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('revealed');
            obs.unobserve(entry.target);
          }
        });
      }, observerOptions);

      document.querySelectorAll('.reveal-item').forEach(item => {
        observer.observe(item);
      });
      
      // Tactile scale feedback handles
      document.querySelectorAll('button, .btn').forEach(btn => {
        btn.addEventListener('mousedown', () => btn.style.transform = 'scale(0.97)');
        btn.addEventListener('mouseup', () => btn.style.transform = '');
        btn.addEventListener('mouseleave', () => btn.style.transform = '');
      });
    });
  </script>
</body>
</html>
```

---

## [ T ] — TARGET & PRE-FLIGHT CHECKLIST

Before final delivery, run this manual and mechanical check on the code. If any block fails, re-adjust the output before delivering.

- [ ] **Design Read declared?** Preceded code with a 1-line vibe identification.
- [ ] **Dial values declared?** Explicit values set for `DESIGN_VARIANCE`, `MOTION_INTENSITY`, and `VISUAL_DENSITY`.
- [ ] **ZERO em-dashes (`—`) anywhere on the page.** (Checked and replaced with standard punctuation/spacers).
- [ ] **Page Theme Lock:** No theme-switching sections (light pages are fully light/cream, dark pages are fully dark).
- [ ] **Color & Radius Consistency:** Uniform accent color and corner-radius scale across all sections.
- [ ] **Button Contrast Check:** Every CTA text passes WCAG AA contrast (4.5:1 min) against its background.
- [ ] **CTA wrap ban:** CTA text does not wrap to 2+ lines on desktop. Max 3 words per label.
- [ ] **No Duplicate CTA Intent:** Only one distinct CTA label per action category on the page.
- [ ] **Hero fits viewport:** Content fits `min-h-[100dvh]`, subtext ≤ 20 words, CTA visible without scrolling. Hero top padding ≤ `6rem` (`pt-24`).
- [ ] **Eyebrow restraint:** Count of uppercase mono tracking labels above H2s is at most `ceil(sectionCount / 3)`.
- [ ] **No repeating section layouts:** At least 4 distinct layout families (e.g. split, 3-card-grid, bento, marquee) utilized.
- [ ] **Zigzag cap:** No 3+ consecutive alternating left/right layout columns.
- [ ] **Logo Wall UNDER Hero:** Credibility badges are placed below the fold, using CDN SVGs (no text labels).
- [ ] **Bento grid rhythm:** No empty cells; at least 2-3 cells have backgrounds containing desaturated patterns or images.
- [ ] **Pre-connected fonts:** Google fonts links include preconnect tags.
- [ ] **Prefers-reduced-motion fallback:** Checked CSS styles to ensure all motion collapses gracefully under media queries.
- [ ] **No AI tells:** Banned default Inter/Roboto sans pairing, generic Lucide icons, Jane Doe names, and "seamlessly"/"elevate" copywriting.
