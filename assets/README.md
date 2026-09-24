# assets/

Put static files here and reference them from `js/projects-data.js` or the HTML pages.

Suggested layout:

```
assets/
  CV.pdf                 # linked from about.html
  headshot.jpg
  projects/
    urban-heat.jpg       # card thumbnail (aim for ~1200x750, < 300 KB)
    greenway-access.jpg
    solar-suitability.jpg
```

Thumbnails: export a clean map or figure at roughly 16:10, compress it
(https://squoosh.app), and set the `thumb` field in `js/projects-data.js`, e.g.
`thumb: "assets/projects/urban-heat.jpg"`. Leave `thumb: ""` to show the text placeholder.
