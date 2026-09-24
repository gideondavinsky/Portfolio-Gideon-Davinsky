/* ===========================================================================
   Site behaviour: theme toggle, mobile nav, footer year, project rendering.
   Vanilla JS, no build step. Loaded on every page (after projects-data.js
   and i18n.js on pages that show cards).
   =========================================================================== */
(function () {
  "use strict";

  /* ---- theme ---------------------------------------------------------- */
  var root = document.documentElement;
  try {
    var saved = localStorage.getItem("theme");
    if (saved === "dark" || saved === "light") root.dataset.theme = saved;
  } catch (e) { /* storage blocked — fall back to prefers-color-scheme */ }

  function currentTheme() {
    if (root.dataset.theme) return root.dataset.theme;
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  function toggleTheme() {
    var next = currentTheme() === "dark" ? "light" : "dark";
    root.dataset.theme = next;
    try { localStorage.setItem("theme", next); } catch (e) {}
    document.dispatchEvent(new CustomEvent("themechange", { detail: { theme: next } }));
  }

  function lang() { return window.I18N ? window.I18N.getLang() : "en"; }
  function t(key) { return (window.I18N && window.I18N.t(key)) || key; }

  /* ---- DOM ready ----------------------------------------------------- */
  var filterState = "all";

  document.addEventListener("DOMContentLoaded", function () {
    var y = document.getElementById("year");
    if (y) y.textContent = new Date().getFullYear();

    var tt = document.querySelector(".theme-toggle");
    if (tt) tt.addEventListener("click", toggleTheme);

    var nt = document.querySelector(".nav-toggle");
    var links = document.querySelector(".nav-links");
    if (nt && links) {
      nt.addEventListener("click", function () {
        var open = links.classList.toggle("open");
        nt.setAttribute("aria-expanded", String(open));
      });
    }

    var filters = document.querySelector(".filters");
    if (filters) {
      filters.addEventListener("click", function (e) {
        var b = e.target.closest(".filter-btn");
        if (!b) return;
        filterState = b.dataset.filter;
        filters.querySelectorAll(".filter-btn").forEach(function (x) {
          x.setAttribute("aria-pressed", String(x === b));
        });
        renderProjects();
      });
    }

    renderProjects();
  });

  // Re-render translated card text (and, on project pages, nothing —
  // handled by data-i18n) whenever the language switches.
  document.addEventListener("langchange", renderProjects);

  /* ---- project cards ------------------------------------------------- */
  function localized(field) {
    // Accepts either a plain string or a {en, es} object.
    if (field == null) return "";
    if (typeof field === "object") return field[lang()] || field.en || "";
    return field;
  }

  function cardMarkup(p) {
    var title = localized(p.title), blurb = localized(p.blurb);
    var tag = p.category === "academic" ? t("tag_academic") : t("tag_professional");
    var thumb = p.thumb
      ? '<img class="thumb" src="' + rel(p.thumb) + '" alt="' + esc(title) + '" loading="lazy">'
      : '<div class="thumb placeholder">' + esc(shortTitle(title)) + '</div>';
    var inner =
      thumb +
      '<div class="body">' +
        '<span class="tag">' + esc(tag) + '</span>' +
        '<h3>' + esc(title) + '</h3>' +
        '<p class="muted">' + esc(blurb) + '</p>' +
        '<div class="meta">' + esc((p.tools || []).slice(0, 3).join(" · ")) +
          (p.year ? '<br>' + p.year : '') + '</div>' +
      '</div>';
    if (p.page) {
      return '<article class="card"><a class="card-link" href="' + rel(p.page) + '">' + inner + '</a></article>';
    }
    return '<article class="card"><div class="card-link">' + inner + '</div></article>';
  }

  function renderProjects() {
    var all = window.PORTFOLIO_PROJECTS || [];

    var featured = document.getElementById("featured-projects");
    if (featured) {
      featured.innerHTML = all.filter(function (p) { return p.featured; }).map(cardMarkup).join("");
    }

    var grid = document.getElementById("project-grid");
    if (!grid) return;

    var list = filterState === "all" ? all : all.filter(function (p) { return p.category === filterState; });
    grid.innerHTML = list.map(cardMarkup).join("") ||
      '<p class="muted">' + esc(lang() === "es" ? "Todavía no hay proyectos en esta categoría." : "No projects in this category yet.") + '</p>';
  }

  /* ---- helpers ------------------------------------------------------- */
  // Detail pages live in /projects/, so their relative paths need "../".
  function rel(path) {
    var inSub = /\/projects\//.test(location.pathname);
    if (!inSub) return path;
    if (/^(https?:|\/|\.\.\/)/.test(path)) return path;
    return "../" + path;
  }
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c];
    });
  }
  function shortTitle(t) { return t.split("—")[0].split(":")[0].trim(); }
})();
