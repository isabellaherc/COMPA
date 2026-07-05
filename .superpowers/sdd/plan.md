# COMPA Netlify + Frontend Deployment Plan

## Goal
Deploy COMPA landing page to Netlify with full brandbook design system.

## Global Constraints
- Publish directory: `brandbook/dist`
- Build command: `npm run build` (runs `vite build`)
- Base directory for Netlify: `brandbook/`
- Package manager: npm
- Node version: 22+
- Colors: `#C1272D` (red), `#2E5339` (green), `#FFC5D3` (pink), `#FF6F91` (deep pink)
- Fonts: Space Grotesk (display), Inter (body) — loaded from Google Fonts CDN
- Language: Spanish (es)
- SPA redirect: `/* /index.html 200`
- Brand mark: 5-petal flower SVG (red/pink alternating, deep pink center)

## Tasks

### Phase 1 — Netlify Configuration (Tasks 1-3)

**Task 1: netlify.toml**
Create `brandbook/netlify.toml` with:
- Build settings: base = `brandbook/`, command = `npm run build`, publish = `dist`
- Environment variables placeholder section
- Headers for security (CSP, HSTS, X-Frame-Options, X-Content-Type-Options)
- Redirects: SPA fallback `/* /index.html 200`
- Node version pin

**Task 2: _redirects + _headers**
Create `brandbook/public/_redirects` with SPA rule.
Create `brandbook/public/_headers` with cache rules for assets.

**Task 3: Build verify**
Run `npm run build` in brandbook/, verify dist/ output exists with index.html and assets.

### Phase 2 — COMPA Landing Page (Tasks 4-11)

**Task 4: Update index.html metadata**
Change title, description, OG tags for COMPA product. Add favicon reference.

**Task 5: Create Hero section**
Replace brandbook hero with COMPA hero:
- Eyebrow: "Compa — Tu socio digital"
- h1: "Oportunidades de compras públicas, directo a tu teléfono"
- Lead: COMPA value proposition for MYPE salvadoreñas
- Two CTAs: primary (Conocer más) + outline (Cómo funciona)
- Keep swatch row and falling leaves

**Task 6: Create "Oportunidades" section**
- Cards showing 3 opportunity types (COMPRASAL detection, voice explanation, match by rubro)
- Use ui-card component style with colored icons

**Task 7: Create "Cofundador" section**
- Explain the AI co-founder voice agent
- 3-step flow: detecta → llama → decide
- Use the anatomy/step component pattern

**Task 8: Create "Cómo Funciona" section**
- 3 columns: n8n orchestration, ElevenLabs voice, Supabase data
- Icon per column with description

**Task 9: Update Nav component**
- Logo + "Compa" brand name (use existing Mark SVG)
- Nav links: Oportunidades, Cofundador, Cómo Funciona, Contacto
- One outline button in nav (never solid)

**Task 10: Create CTA + Footer**
- Dark green CTA section: "Empezá hoy con Compa"
- Footer with brand, links, copyright 2026

**Task 11: Responsive + final polish**
- Test all breakpoints (mobile 720px, tablet 900px)
- Ensure no broken layouts
- Final build verification
