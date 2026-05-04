# Projects Page — Content Model

Schema and authoring rules for `projects.json`, the data source backing
the Projects index and detail views (TICK-7).

`projects.json` lives at the repo root and is loaded at runtime via
`fetch('projects.json')` from inline JS in `projects.html`, the same
pattern `index.html` uses for `youtube.json`. **It is hand-authored
and must not be touched by the YouTube workflow** (`youtube.json` is
the auto-regenerated file; keep them separate).

## Top-level shape

```json
{
  "categories": [ /* Category[] */ ],
  "projects":   [ /* Project[]   */ ]
}
```

## `Category`

```ts
{
  id:    string,  // slug used in `Project.category` and as the filter key
  label: string,  // human-readable chip text
  icon:  string   // Font Awesome 6 class (e.g. "fa-tractor"); rendered as <i class="fas {icon}">
}
```

The first category MUST be `{ "id": "all", "label": "All", "icon": "fa-th" }`
so the filter UI has a no-op default. `"all"` is reserved — do not
assign it to any project.

## `Project`

```ts
{
  slug:        string,         // URL-safe unique id; used for the detail-view anchor / filename
  title:       string,         // <h3> on the index card, <h2> on the detail view
  summary:     string,         // 1–2 sentence card blurb
  category:    string,         // MUST match a Category.id (other than "all")
  heroImage:   string,         // path under "images/" or full URL; used for card hero + detail hero
  heroAlt:     string,         // alt text for heroImage; "" only if purely decorative
  videoId?:    string,         // YouTube video id — preferred for detail-view embed
  playlistId?: string,         // YouTube playlist id — used if no videoId, or for "see the series" link
  body:        string,         // HTML string for the detail-view notes/tips/gotchas section
  publishedAt?: string         // ISO 8601; optional, used to sort the index newest-first
}
```

### Field rules

- **At least one of `videoId` / `playlistId` is required.** If both are
  set, the detail view embeds the single video and links out to the
  playlist as "see the full series".
- **`body` is a trusted HTML string** (we author it ourselves; no user
  input). Use semantic tags (`<p>`, `<ul>`, `<h3>` for sub-sections like
  "Notes" / "Tips" / "Gotchas"). Keep the heading level at `<h3>` so the
  detail view's `<h2>` (project title) stays the section's top heading.
- **`heroImage`** — drop new images into `images/` and reference as
  `images/<file>`. Tailwind's content glob does not scan `images/`, so
  any class names used inside `body` HTML must already be present in
  `index.html` / `projects.html` / `src/**/*.js`, otherwise they will
  be purged from `dist/output.css`.
- **`slug`** — lowercase, hyphenated, stable. Used as the detail anchor
  (`projects.html#<slug>`) and, if per-file detail views are ever
  introduced, as the filename.
- **`category`** — exactly one tag per project (no arrays). If a
  project genuinely spans tags, pick the dominant one and let the body
  copy mention the rest.

## Categories in use

The seeded category set covers the planned five-project launch:

| id            | label        | icon            | example                |
| ------------- | ------------ | --------------- | ---------------------- |
| `all`         | All          | `fa-th`         | (filter only)          |
| `tractor`     | Tractors     | `fa-tractor`    | Ford 2N restoration    |
| `3d-printing` | 3D Printing  | `fa-cube`       | 3D printing for beginners |
| `repair`      | Repairs      | `fa-wrench`     | Craftsman riding mower |
| `review`      | Reviews      | `fa-star`       | Higg Reviews           |
| `shop`        | Shop         | `fa-warehouse`  | Air compressor mod, shed move |

Adding a new category later: append to `categories` in `projects.json`
and use a Font Awesome 6 free-tier icon class. The filter chip UI
renders straight from this list, so no other code changes are needed.

## Validation

`projects.json` is plain JSON (not JSON-with-comments). Run any of:

```sh
python -m json.tool projects.json > /dev/null
node -e "JSON.parse(require('fs').readFileSync('projects.json'))"
```

…to confirm it parses before committing.
