# GIS Portfolio

A static personal website to showcase academic and professional GIS work. No build
step, no framework — plain HTML, CSS, and vanilla JS, with interactive maps powered by
[MapLibre GL JS](https://maplibre.org/) and free [OpenFreeMap](https://openfreemap.org/)
base tiles.

## Structure

```
index.html            Landing page — hero, featured projects, "what I do"
projects.html         Full project list with Academic / Professional filter
about.html            Bio, education, experience, skills, CV link
projects/
  e2sfca-atlanta.html                  Detail page + interactive map
  pedestrian-accessibility-index.html  Detail page + interactive map
  optimal-walking-routes.html          Detail page + interactive map
css/main.css          All styling; light + dark themes via CSS variables
js/
  projects-data.js    >>> EDIT THIS to add/change projects (drives the cards)
  site.js             Theme toggle, mobile nav, card rendering, filtering
  map.js              GISPortfolio.initMap() — MapLibre helper for project pages
data/                 Real project GeoJSON (trimmed/aggregated from source layers)
scripts/              How each data/*.geojson was built from the original ArcGIS
                       exports — see scripts/README.md to regenerate one
assets/               Images, CV.pdf, thumbnails (see assets/README.md)
```

## Run locally

Browsers block `fetch()` of local files, so the maps need a local web server (not
`file://`). From this folder:

```bash
python -m http.server 8000
```

Then open <http://localhost:8000>. Any static server works (`npx serve`, VS Code Live
Server, etc.).

## Make it yours

1. **Projects:** edit `js/projects-data.js`. Each entry becomes a card. Set `featured: true`
   to show it on the home page. Point `page` at a detail file in `projects/` (or leave it
   `""` for a card with no link yet).
3. **New project page:** copy one of the files in `projects/`, swap the text, and update the
   `GISPortfolio.initMap({...})` call at the bottom to point at your GeoJSON.
4. **Maps:** drop a GeoJSON file in `data/`. `initMap` auto-styles polygons, lines, and
   points; pass `fill.colorBy` + `fill.stops` for a choropleth, `popup: [...]` for the
   attributes to show on click, and `legend` for the legend box. Reproject to EPSG:4326
   first (`ogr2ogr -t_srs EPSG:4326 out.geojson in.shp`).
5. **CV / images:** see `assets/README.md`.
6. **Colors:** edit the `--accent` variables at the top of `css/main.css`.

## Deploy (free options)

**GitHub Pages**
```bash
git init && git add . && git commit -m "Initial portfolio"
git branch -M main
git remote add origin https://github.com/yourhandle/portfolio.git
git push -u origin main
```
Then in the repo: Settings → Pages → Source: `main` / root. Live at
`https://yourhandle.github.io/portfolio/`.

**Netlify / Cloudflare Pages:** drag-and-drop this folder, or connect the repo. No build
command; publish directory is the repo root.

A custom domain (e.g. `yourname.dev`) can be pointed at any of these in their DNS settings.

## Notes

- OpenFreeMap is free for production use with no API key. If you prefer another base map
  (MapTiler, Stadia, Mapbox), change the `STYLES` URLs in `js/map.js` and add your key.
- Everything works offline except the base map tiles, Google Fonts, and the MapLibre CDN
  script. To fully self-host, download those into `assets/vendor/` and update the links.
