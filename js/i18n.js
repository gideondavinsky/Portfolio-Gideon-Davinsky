/* ===========================================================================
   Lightweight EN/ES i18n. No page reload, no build step.

   - window.I18N_COMMON holds strings shared by every page (nav, footer, tags,
     project-meta labels). Edit it here.
   - Each page defines window.PAGE_I18N = { en: {...}, es: {...} } BEFORE
     including this script, for its own headings/paragraphs.
   - Mark translatable elements with data-i18n="key" (sets innerHTML — safe
     here since values are our own authored strings, not user input) or
     data-i18n-aria="key" (sets aria-label).
   - Preference is stored in localStorage("lang") and falls back to the
     browser's language. `window.I18N.setLang()` / `.getLang()` / `.t(key)`
     are available to other scripts (site.js, map.js, per-page inline
     scripts) and a "langchange" event fires on every switch.
   =========================================================================== */

window.I18N_COMMON = {
  en: {
    nav_home: "Home",
    nav_projects: "Projects",
    nav_about: "About / CV",
    nav_contact: "Contact",
    theme_toggle_aria: "Toggle dark mode",
    lang_toggle_aria: "Switch language",
    menu_aria: "Menu",
    social_email: "Email",
    social_github: "GitHub",
    social_linkedin: "LinkedIn",
    footer_built: "Built as a static site.",
    tag_academic: "Academic",
    tag_professional: "Professional",
    back_all_projects: "All projects",
    meta_type: "Type",
    meta_year: "Year",
    meta_role: "Role",
    meta_tools: "Tools",
    meta_data: "Data",
    meta_area: "Study area",
    meta_deliverable: "Deliverable",
    meta_output: "Output",
    meta_org: "Client"
  },
  es: {
    nav_home: "Inicio",
    nav_projects: "Proyectos",
    nav_about: "Sobre mí / CV",
    nav_contact: "Contacto",
    theme_toggle_aria: "Cambiar modo oscuro",
    lang_toggle_aria: "Cambiar idioma",
    menu_aria: "Menú",
    social_email: "Correo",
    social_github: "GitHub",
    social_linkedin: "LinkedIn",
    footer_built: "Página web estática.",
    tag_academic: "Académico",
    tag_professional: "Profesional",
    back_all_projects: "Todos los proyectos",
    meta_type: "Tipo",
    meta_year: "Año",
    meta_role: "Rol",
    meta_tools: "Herramientas",
    meta_data: "Datos",
    meta_area: "Área de estudio",
    meta_deliverable: "Entregable",
    meta_output: "Resultado",
    meta_org: "Cliente"
  }
};

(function () {
  "use strict";
  var SUPPORTED = ["en", "es"];

  function detect() {
    try {
      var saved = localStorage.getItem("lang");
      if (SUPPORTED.indexOf(saved) !== -1) return saved;
    } catch (e) {}
    return (navigator.language || "").toLowerCase().indexOf("es") === 0 ? "es" : "en";
  }

  var lang = detect();
  document.documentElement.lang = lang;

  function dict() {
    var page = window.PAGE_I18N || {};
    return Object.assign({}, I18N_COMMON.en, page.en, lang === "es" ? Object.assign({}, I18N_COMMON.es, page.es) : {});
  }

  function apply() {
    var d = dict();
    document.querySelectorAll("[data-i18n]").forEach(function (el) {
      var key = el.getAttribute("data-i18n");
      if (d[key] != null) el.innerHTML = d[key];
    });
    document.querySelectorAll("[data-i18n-aria]").forEach(function (el) {
      var key = el.getAttribute("data-i18n-aria");
      if (d[key] != null) el.setAttribute("aria-label", d[key]);
    });
    if (d.doc_title) document.title = d.doc_title;
    var meta = document.querySelector('meta[name="description"]');
    if (meta && d.doc_description) meta.setAttribute("content", d.doc_description);

    var btn = document.querySelector(".lang-toggle");
    if (btn) btn.textContent = lang === "en" ? "ES" : "EN";

    document.dispatchEvent(new CustomEvent("langchange", { detail: { lang: lang } }));
  }

  function setLang(next) {
    if (SUPPORTED.indexOf(next) === -1 || next === lang) return;
    lang = next;
    document.documentElement.lang = lang;
    try { localStorage.setItem("lang", lang); } catch (e) {}
    apply();
  }

  window.I18N = {
    getLang: function () { return lang; },
    setLang: setLang,
    t: function (key) { return dict()[key]; },
    apply: apply
  };

  document.addEventListener("DOMContentLoaded", function () {
    var btn = document.querySelector(".lang-toggle");
    if (btn) btn.addEventListener("click", function () { setLang(lang === "en" ? "es" : "en"); });
    apply();
  });
})();
