# Gideon Davinsky — GIS & Mobility Portfolio

A bilingual static portfolio for a GIS and urban data analyst based in Madrid. It pairs concise project summaries with interactive case studies in multimodal healthcare accessibility and flood-risk resilience. The site uses plain HTML, CSS and vanilla JavaScript, MapLibre GL JS for interactive maps, and OpenFreeMap vector basemaps.

## Structure

- `index.html` — editorial landing page, featured studies, methods and contact CTA
- `projects.html` — topic-filtered gallery of case studies
- `about.html` — background, experience, skills and bilingual CV downloads
- `contact.html` — email and professional contact links
- `projects/` — Atlanta healthcare-accessibility and Logroño flood-resilience case studies
- `css/main.css` — responsive Civic Cartography design system and light/dark themes
- `js/projects-data.js` — bilingual project-card content, topics and links
- `js/site.js` / `js/i18n.js` — site behavior, card rendering and language switching
- `js/map.js` — shared MapLibre layer, popup, legend and theme helpers
- `data/` — the original GeoJSON layers used by the interactive case-study maps
- `assets/CV_EN.pdf`, `assets/CV_ES.pdf` — original downloadable CVs
- `assets/maps/` — small SVG previews derived from actual project GeoJSON
- `scripts/build_map_previews.py` — reproducible generator for those map previews

## Run locally

Use an HTTP server so case-study pages can fetch their GeoJSON files:

```bash
python3 -m http.server 8000
```

Then open <http://localhost:8000>. The interactive base tiles, MapLibre script and Google Fonts are loaded from their respective public services.

## Update portfolio content

1. Update the bilingual objects and project metadata in `js/projects-data.js`.
2. For a new interactive case study, add its page under `projects/`, store its source GeoJSON in `data/`, and call `GISPortfolio.initMap()` as shown by the existing case studies.
3. Rebuild the gallery previews with `python3 scripts/build_map_previews.py` after updating the source GeoJSON.
4. Keep English and Spanish copy aligned in each page's `PAGE_I18N` object.

## Source and provenance

The redesign retains the owner's existing content, CVs, case studies and GeoJSON from the public portfolio:

- Live site: <https://gideondavinsky.github.io/Portfolio-Gideon-Davinsky/>
- GitHub repository: <https://github.com/gideondavinsky/Portfolio-Gideon-Davinsky>

The Logroño and Atlanta preview maps are drawn from `data/logrono-riesgo.geojson` and `data/e2sfca-atlanta.geojson`; their values are not simulated. The detail pages keep their interactive maps, original project methods and attribution.

## GitHub Pages

The repository is a static site and needs no build step. The current GitHub Pages source is the root directory on `main`. The existing source project documents other static hosting options in GitHub's Pages settings or a static hosting service.
