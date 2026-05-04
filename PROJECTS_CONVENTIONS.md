# Projects Page — Site Conventions Inventory

Reference for the TICK-7 build-out. Lock in to what already exists so the
new Projects page feels native to higgprojects.com.

## Stack

- Static site. No bundler, no framework, no SSG. Plain `index.html` at
  the repo root, served as-is (GitHub Pages — see `CNAME` =
  `higgprojects.com`).
- **Tailwind CSS 3.4** + **DaisyUI 4.12** for components.
- **Font Awesome 6.5.1** via CDN for icons.
- **Vanilla JS** in a `<script>` block at the end of `index.html`.
- Build: `npm run build` → `npx tailwindcss -i ./src/input.css -o
  ./dist/output.css --minify`. Watch via `npm run watch` / `npm run
  dev`.
- Tailwind `content` glob (in `tailwind.config.js`) is
  `["./*.html", "./src/**/*.js"]` — **any new HTML page must live at
  the repo root** (or the glob must be widened) so its classes get
  scanned. Same applies for any new JS files holding class strings —
  put them under `src/**/*.js` or extend the glob.

## Routing

- There is **no client router**. The current "Projects" nav item is a
  same-page anchor link (`href="#projects"`) that scrolls to the
  in-page `<section id="projects">` (the playlist grid).
- GitHub Pages serves files by path. The convention here will be a
  separate top-level HTML file: **`projects.html`** for the index, and
  either anchored sections within it or per-project HTML files for
  detail views. Whichever later stories choose, they must keep files
  at the repo root for the Tailwind content glob.
- Smooth-scroll handler in `index.html` intercepts every
  `a[href^="#"]`. On a new page, links to the home page should use
  `index.html#home`, `index.html#about`, etc. (the smooth-scroll
  handler only runs on the page it's loaded into, so cross-page
  anchors will use a normal browser jump — that's fine).

## Theming

- DaisyUI themes defined in `tailwind.config.js`:
  - `higgprojects` — dark (default)
  - `higgprojects-light` — light
- Theme is set on `<html data-theme="...">`. To prevent flash, every
  page must include this script in `<head>` **before** styles render:
  ```html
  <script>
    document.documentElement.setAttribute(
      'data-theme',
      localStorage.getItem('theme') || 'higgprojects'
    );
  </script>
  ```
- The theme dropdown markup + JS lives in the navbar/script of
  `index.html`. The Projects page must replicate the same dropdown
  (Dark / Light buttons with ids `themeDark` / `themeLight`) and the
  same `setTheme()` handler so toggling persists across pages via
  `localStorage`.
- Smooth theme-transition CSS (`html.theme-transitioning *`) is
  inlined in `<head>`. Copy verbatim onto new pages.

## Color & typography

- Primary palette is teal: `#5EEAD4` (dark) / `#14B8A6` (light). Use
  DaisyUI semantic classes (`text-primary`, `bg-primary`, `btn-primary`)
  rather than hex.
- Surfaces: `bg-base-100` (page), `bg-base-200` (alt sections),
  `bg-base-300` (cards/inputs).
- Headings use `font-oswald` (custom class in `src/input.css`) for the
  brand wordmark; section headings use Tailwind's default sans (Inter,
  loaded from Google Fonts). `font-anton` is also available.
- Section title pattern (component class in `input.css`):
  ```html
  <h2 class="section-title">Project <span class="text-primary">Playlists</span></h2>
  ```
  `.section-title` is `text-3xl md:text-4xl font-bold mb-8 text-center`.

## Layout patterns

- Page chrome:
  - `<nav>` (fixed top, `z-50`, `bg-base-200/95 backdrop-blur-sm`).
  - Sections wrap in `<section class="py-20 bg-base-XXX reveal">` with
    `<div class="container mx-auto px-4">` inside.
  - Footer (`footer footer-center p-10 bg-base-200`).
- Card grids:
  - Playlists today: `grid sm:grid-cols-2 lg:grid-cols-4 gap-6
    max-w-6xl mx-auto stagger-children`.
  - Featured videos today: `grid md:grid-cols-2 lg:grid-cols-3 gap-6
    max-w-6xl mx-auto stagger-children`.
  - Mobile-first: single column at base, breakpoints add columns.
- Card hover/lift convention:
  ```html
  class="card bg-base-100 shadow-xl hover:shadow-2xl transition-all
         duration-300 hover:-translate-y-2"
  ```
  Compose with DaisyUI `card` + `card-body`. Optional gradient-border
  effect is wired up via the `.video-card` component class.
- Reusable component classes (defined in `src/input.css`):
  - `.video-card` — gradient-border card with hover glow
  - `.play-overlay` / `.video-card:hover .play-overlay` — play-button
    overlay reveal
  - `.section-title`, `.social-btn`, `.nav-link`, `.gradient-text`
- Animations:
  - `.reveal` on a section + IntersectionObserver = fade/slide-in on
    scroll.
  - `.stagger-children` on a grid = staggered child reveal (already
    wired for up to 6 children; add more nth-child rules in
    `input.css` if a new grid needs them).
  - `.bg-noise` utility for subtle texture (used on `<body>`).

## Video embed conventions

- Thumbnails come from `https://img.youtube.com/vi/<VIDEO_ID>/hqdefault.jpg`
  (or `maxresdefault.jpg` with an `onerror=` fallback to `hqdefault`).
- Click-to-play uses the existing in-page lightbox: any element with
  class `.video-lightbox` and a `data-video="<VIDEO_ID>"` attribute
  triggers the modal. The lightbox markup + handler are at the bottom
  of `index.html` (`#videoLightbox`, `#videoFrame`, `#closeLightbox`).
  Reuse this verbatim on Projects pages so behavior matches.
- Iframe src pattern:
  `https://www.youtube-nocookie.com/embed/<ID>?autoplay=1&playsinline=1&rel=0`.
- Direct/external playlist link pattern:
  `https://www.youtube.com/playlist?list=<PLAYLIST_ID>` with
  `target="_blank" rel="noopener noreferrer"`.

## Existing Projects-relevant content

- The **current** "Projects" section is `<section id="projects">` in
  `index.html` lines 382–437. It's a 4-card grid linking to YouTube
  playlists:
  - **Ford 2N Tractor Restoration** —
    `PLKAsT-fsdrzF2BfVNSK4FZwfs-oP3RnWj` (icon `fa-tractor`)
  - **3D Printing for Beginners** —
    `PLKAsT-fsdrzEW_F-3iyGQKXnrIBF1wzF-` (icon `fa-cube`)
  - **Higg Reviews** —
    `PLKAsT-fsdrzG0ocgJjUyjhSKsvQliZGiJ` (icon `fa-star`)
  - **Craftsman Riding Mower** —
    `PLKAsT-fsdrzFJhYtjjDXv6w6PxnRttVvg` (icon `fa-wrench`)
  - (Stats from `youtube.json` say there are 9 total playlists; the
    other 5 aren't surfaced.)
- Story 7 will replace the `href="#projects"` nav target with the new
  `projects.html` route. The in-page section can stay (renamed/repurposed)
  or be removed — that's a Story 7 call.
- Featured videos already embedded on the home page use these IDs and
  give the planner pre-vetted material for seeded projects:
  - `0LTwHzOjneE` — Bringing grandpa's Ford 2N home (40:07)
  - `qa3fVjtNyCY` — Boost Your Air Compressor (propane-tank mod)
  - `GDKEo4ovsck` — Move our shed with a 4-wheeler

## Data sources

- `youtube.json` is auto-regenerated daily by
  `.github/workflows/fetch-youtube.yml`. **Do not hand-edit it.**
  Project content for TICK-7 should live in a *separate* file
  (e.g. `projects.json`) so the YouTube workflow won't clobber it.
- The existing JSON-loading pattern is `fetch('youtube.json')` from
  inline JS in `index.html`. The Projects page can follow the same
  pattern (`fetch('projects.json')` then template into the DOM), or
  inline content directly into `projects.html` if the planner prefers
  static HTML — both fit the repo's "vanilla JS, no build step for
  data" idiom.

## Assets

- `images/` holds local images (`logo.jpg`, `shopsunset.jpg`). Drop
  any new project hero images here and reference as `images/<name>`.
  Remember the Tailwind content glob does **not** scan this directory —
  that's fine, it's not for source code.
- `fonts/varsity-team.woff2` exists but isn't currently `@font-face`'d.
  Don't add it without reason.

## Accessibility checkpoints already in use

- Every external link uses `target="_blank" rel="noopener noreferrer"`.
- All images have `alt=""`; navbar SVG icons are decorative inside
  `role="button"` triggers.
- Heading order on `index.html` is h1-free (the logo is the brand),
  one `<h2>` per section, `<h3>` for cards/sub-blocks. Match this on
  the Projects page (one `<h2>` for the index title, `<h3>` for each
  project card; on detail views, h2 for project title, h3 for sub-
  sections like "Notes" / "Tips").
- Cards are `<a>` elements (focusable; keyboard-navigable for free).
  Keep that pattern — wrap each project card in an `<a href=...>`
  rather than using a nested button.

## Summary for downstream stories

1. **Project data model** (Story 2) → new `projects.json` (don't touch
   `youtube.json`). Each entry needs: `slug`, `title`, `summary`,
   `category` (tag), `heroImage`, `videoId` *or* `playlistId`, body
   (markdown or HTML string).
2. **Index page** (Story 4) → `projects.html` at repo root. Reuse
   navbar + footer + theme-toggle markup from `index.html`. Card grid:
   `grid sm:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto
   stagger-children`. Wrap with `bg-noise` body and `.reveal`
   sections.
3. **Detail view** (Story 5) → either anchored sections within
   `projects.html` (simplest, matches single-page idiom) or
   per-project files like `projects/<slug>.html`. If choosing the
   latter, the Tailwind glob must be widened to `"./**/*.html"` and
   the relative paths to `dist/output.css`, `images/`, etc. need a
   `..` prefix.
4. **Filter** (Story 6) → vanilla JS toggling card visibility by
   `data-category` attribute. Filter chips styled as DaisyUI
   `btn btn-sm btn-outline btn-primary` (active = solid).
5. **Nav** (Story 7) → change `href="#projects"` → `href="projects.html"`
   in both the desktop and mobile menus of `index.html`. Active-route
   highlight on the Projects page itself: hard-code the link's classes
   (e.g. add `text-primary`) since there's no router.
6. **Home CTA** (Story 8) → add a `btn btn-lg btn-primary` link to
   `projects.html` near the existing playlists section, or replace the
   playlists section's lead-in with a CTA.
7. **Verify** (Story 9) → `npm run build`, open `index.html` and
   `projects.html` in a browser, toggle theme, resize to phone width,
   tab through cards.
