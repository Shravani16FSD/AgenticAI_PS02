# Chapter — AI Career Coach & Mentor

> A polished, human-centered, editorial-style career coaching web application built with React, TypeScript, and a custom Cream & Burgundy design system.

---

## 1. Product Vision

**Chapter** is designed to feel like a thoughtful personal mentor rather than an algorithmic dashboard:

- **Discover suitable career paths** grounded in day-to-day responsibilities, required skills, and genuine entry points.
- **Identify skills to develop** with honest time tracking and weekly pacing.
- **Build personalized learning roadmaps** sequenced into 5 distinct phases: Foundations, Core Skills, Applied Projects, Portfolio, and Interview Readiness.
- **Engage with an AI Career Coach** who provides direct answers, brief reasoning, practical next steps, and realistic weekly learning plans.
- **Track momentum without vanity metrics** — every milestone checkmark and practice hour reflects verified user activity.

**Brand Message:** *"Your career is a journey. You do not need to figure everything out today."*

---

## 2. Editorial Design System · Cream & Burgundy

The interface is inspired by thoughtfully designed magazines, premium educational products, and modern personal productivity tools. Stark white and neon gradients are replaced with warm cream surfaces and deep burgundy typography.

### Core Color Palette

| CSS Variable | Value | Purpose | Contrast vs Background |
|---|---|---|---|
| `--color-page` | `#F8F4ED` | Warm cream page background | Canvas |
| `--color-surface` | `#FFFDFA` | Primary content panels | Subtle lift |
| `--color-surface-muted` | `#F0E8DE` | Secondary panels and inputs | Secondary surface |
| `--color-burgundy` | `#702D3D` | Primary brand and primary buttons | **> 8.5:1** (WCAG AAA) |
| `--color-burgundy-hover` | `#57202F` | Hover and active interactive states | **> 10:1** |
| `--color-burgundy-soft` | `#EDE0E2` | Highlighted cards & badges | Soft accent |
| `--color-text` | `#292321` | Main body text | **> 13.8:1** (WCAG AAA) |
| `--color-text-secondary` | `#625853` | Secondary text | **> 5.6:1** (WCAG AA) |
| `--color-text-muted` | `#766A64` | Subdued supporting text | **> 4.6:1** (WCAG AA) |
| `--color-border` | `#DCD1C6` | Dividers and thin panel borders | Restrained outline |
| `--color-border-strong` | `#BDAEA2` | Focus-adjacent borders | High definition |
| `--color-focus` | `#702D3D` | Visible keyboard focus ring | High visibility |

### Typography

- **Playfair Display** (500, 600, 700): Reserved for headlines, page titles, and editorial section intros.
- **Manrope** (400, 500, 600, 700): Used for body text, navigation, forms, buttons, and dashboard metrics.

---

## 3. Application Structure & Pages

1. **Landing Page (`/`)**: Two-column editorial hero, real product preview, value pillars, 3-step workflow, and calm call to action.
2. **Onboarding Flow (`/onboarding`)**: Reassuring 5-step onboarding gathering study status, interests, near-term goals, baseline skills, and weekly hours.
3. **Career Dashboard (`/dashboard`)**: Action-first layout featuring "Your Next Step", current career direction, roadmap progress, weekly consistency, and coach preview.
4. **AI Career Coach (`/coach`)**: Real-time streaming conversation, context sidebar with active goal and roadmap tasks, 4 clickable suggested inquiry prompts, and safe markdown rendering.
5. **Career Exploration (`/explore`)**: Searchable directory of roles with domain filters, daily responsibilities, required skills, learning phases, bookmarking, and a side-by-side comparison modal.
6. **Learning Roadmap (`/roadmap`)**: Sequential 5-phase vertical timeline with task status toggles (`not_started`, `in_progress`, `completed`), verified resource links, and custom milestone creation.
7. **Skills & Progress (`/skills`)**: Transparent progress logging, session practice hour logger, and 7-day consistency calendar.
8. **Profile & Preferences (`/profile`)**: Manage your baseline goals, export your complete career plan as a formatted Markdown file, and reset to defaults.

---

## 4. AI Coach Architecture & Service Layer

The AI service layer (`src/services/aiService.ts`) is designed for production reliability:
- **Streaming Cadence**: Streams responses chunk by chunk with honest status indicators (*"Thinking through your question…"*, *"Putting your plan together…"*) and cancellation support.
- **Context-Aware Mentoring**: Synthesizes the user's active career, stated goal, current roadmap task, and weekly hours into grounded, realistic advice.
- **Backend API Integration**: Checks for an external endpoint via `VITE_AI_API_ENDPOINT` or `/api/chat`.
- **Zero-Friction Fallback**: When no backend API key is supplied, automatically falls back to the client-side mentor engine without breaking the application or faking credentials.

---

## 5. Local Development

### Prerequisites
- Node.js >= 18 (Tested on Node v24)
- npm >= 9

### Installation & Run
```bash
# 1. Install dependencies
npm install

# 2. Run local development server
npm run dev

# 3. Open in browser at http://localhost:5173
```

### Build & Lint
```bash
# Run production build and type checking
npm run build

# Run linter
npm run lint

# Preview production build locally
npm run preview
```

---

## 6. Deployment Guide

### Vercel
Deploy directly with zero configuration:
```bash
npx vercel
```
*The included `vercel.json` automatically handles SPA client-side route rewrites.*

### Netlify
```bash
npx netlify deploy --prod --dir=dist
```
*The included `public/_redirects` ensures all routes (`/dashboard`, `/coach`, `/roadmap`, etc.) resolve on page refresh.*

### Static Hosts (Cloudflare Pages, GitHub Pages)
Run `npm run build` and publish the generated `dist/` directory. Ensure single-page app fallback points to `index.html`.

---

## 7. Accessibility (WCAG 2.2 AA)

- Visible keyboard focus rings (`--color-focus: #702D3D`).
- Skip to main content link on every page.
- Semantic landmarks (`<header>`, `<nav>`, `<main>`, `<section>`, `<footer>`, `<dialog>`).
- Color contrast verified for all foreground/background pairings.
- Respects `prefers-reduced-motion` media queries.
