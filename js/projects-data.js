/* ===========================================================================
   Portfolio content — EDIT THIS FILE to add / change projects.
   Each entry renders a card on index.html and projects.html.
   `title` and `blurb` are bilingual: { en: "...", es: "..." }. `page` points
   to a detail HTML file in /projects (optional — omit for card-only
   entries). `thumb` is a path under /assets (optional — a placeholder is
   drawn if missing). `tools` stays a single list (tool names are proper
   nouns, same in both languages).
   =========================================================================== */

window.PORTFOLIO_PROJECTS = [
  {
    slug: "logrono-flood-resilience",
    title: {
      en: "Fluvial Flood Risk & Resilience — Logroño",
      es: "Riesgo y Resiliencia ante Inundación Fluvial — Logroño"
    },
    category: "academic",
    year: 2026,
    blurb: {
      en: "A T500 flood hazard-to-risk pipeline for Logroño, Spain: severity, land-cover " +
          "and road exposure, a national vulnerability index, and a composite risk map " +
          "with a drainage recommendation.",
      es: "Un pipeline de peligrosidad a riesgo T500 para Logroño, España: severidad, " +
          "exposición de cubiertas y viario, un índice nacional de vulnerabilidad y un " +
          "mapa de riesgo compuesto con una recomendación de drenaje."
    },
    tools: ["ArcGIS Pro", "Spatial Analyst", "ISVUN-G", "Urban Atlas"],
    thumb: "",
    page: "projects/logrono-flood-resilience.html",
    featured: true
  },
  {
    slug: "e2sfca-atlanta",
    title: {
      en: "Multimodal Healthcare Accessibility (E2SFCA) — Atlanta",
      es: "Accesibilidad Sanitaria Multimodal (E2SFCA) — Atlanta"
    },
    category: "academic",
    year: 2026,
    blurb: {
      en: "A multimodal Enhanced Two-Step Floating Catchment Area model scoring 600 " +
          "census tracts across metro Atlanta for hospital-bed access by drive, " +
          "transit, and walk.",
      es: "Un modelo E2SFCA multimodal que puntúa 600 secciones censales del área " +
          "metropolitana de Atlanta según su acceso a camas hospitalarias en coche, " +
          "transporte público y a pie."
    },
    tools: ["ArcGIS Pro", "Network Analyst", "Python", "GTFS", "US Census ACS"],
    thumb: "",
    page: "projects/e2sfca-atlanta.html",
    featured: true
  }
];
