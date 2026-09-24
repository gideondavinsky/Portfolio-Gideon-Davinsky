/* ===========================================================================
   Thin MapLibre GL helper for project pages.

   Usage (in a project page, after maplibre-gl.js + this file):

     GISPortfolio.initMap({
       container: "map-heat",
       center: [-122.676, 45.523],
       zoom: 12,
       geojson: "../data/urban-heat.geojson",
       fill:  { colorBy: "lst_c",
                stops: [[30,"#2c7bb6"],[33,"#abd9e9"],[36,"#ffffbf"],[39,"#fdae61"],[42,"#d7191c"]],
                opacity: 0.72 },
       line:  { color: "#0f766e", width: 3 },
       circle:{ color: "#d7191c", radius: 6 },
       popup: ["name", "lst_c", "zone"],
       legend: { title: "Surface temp (°C)", items: [
         { color: "#2c7bb6", label: "< 33" }, { color: "#abd9e9", label: "33–36" },
         { color: "#ffffbf", label: "36–39" }, { color: "#fdae61", label: "39–42" },
         { color: "#d7191c", label: "> 42" } ] }
     });

   Base map: OpenFreeMap (https://openfreemap.org) — free, no API key, OK for
   production. Style switches with the site light/dark theme.
   =========================================================================== */
window.GISPortfolio = window.GISPortfolio || {};

(function () {
  "use strict";

  var STYLES = {
    light: "https://tiles.openfreemap.org/styles/positron",
    dark:  "https://tiles.openfreemap.org/styles/dark"
  };

  function theme() {
    var t = document.documentElement.dataset.theme;
    if (t) return t;
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  // Accepts a plain string or a bilingual { en, es } object.
  function pickLang(field) {
    if (field == null) return "";
    if (typeof field === "object") {
      var lang = window.I18N ? window.I18N.getLang() : "en";
      return field[lang] || field.en || "";
    }
    return field;
  }

  function bounds(geojson) {
    var b = [Infinity, Infinity, -Infinity, -Infinity];
    function walk(coords) {
      if (typeof coords[0] === "number") {
        b[0] = Math.min(b[0], coords[0]); b[1] = Math.min(b[1], coords[1]);
        b[2] = Math.max(b[2], coords[0]); b[3] = Math.max(b[3], coords[1]);
      } else { coords.forEach(walk); }
    }
    (geojson.features || []).forEach(function (f) { if (f.geometry) walk(f.geometry.coordinates); });
    return b;
  }

  function stepExpr(prop, stops, nullColor) {
    // stops: [[value,color], ...] ascending. First color used below stops[1] value.
    var expr = ["step", ["get", prop], stops[0][1]];
    for (var i = 1; i < stops.length; i++) { expr.push(stops[i][0], stops[i][1]); }
    // A null/missing property value breaks a bare step expression (it needs a
    // number) — coalesce it to a distinct color instead of erroring per-feature.
    if (nullColor) return ["case", ["==", ["get", prop], null], nullColor, expr];
    return expr;
  }

  // matches: [[value,color], ...] for categorical/discrete fields (e.g. a 1-4 index).
  function matchExpr(prop, matches, fallback) {
    var expr = ["match", ["get", prop]];
    matches.forEach(function (m) { expr.push(m[0], m[1]); });
    expr.push(fallback || "#999999");
    return expr;
  }

  // spec: { color } | { colorBy, stops, nullColor? } | { matchBy, matches, default }
  function resolveColor(spec, fallback) {
    if (spec.colorBy && spec.stops) return stepExpr(spec.colorBy, spec.stops, spec.nullColor);
    if (spec.matchBy && spec.matches) return matchExpr(spec.matchBy, spec.matches, spec["default"]);
    return spec.color || fallback;
  }

  function addLayers(map, id, data, opts) {
    if (map.getSource(id)) {
      ["-fill", "-line", "-circle", "-fill-outline"].forEach(function (s) {
        if (map.getLayer(id + s)) map.removeLayer(id + s);
      });
      map.removeSource(id);
    }
    map.addSource(id, { type: "geojson", data: data });

    if (opts.fill) {
      map.addLayer({
        id: id + "-fill", type: "fill", source: id,
        filter: ["match", ["geometry-type"], ["Polygon", "MultiPolygon"], true, false],
        paint: {
          "fill-color": resolveColor(opts.fill, "#0f766e"),
          "fill-opacity": opts.fill.opacity != null ? opts.fill.opacity : 0.65
        }
      });
      map.addLayer({
        id: id + "-fill-outline", type: "line", source: id,
        filter: ["match", ["geometry-type"], ["Polygon", "MultiPolygon"], true, false],
        paint: { "line-color": opts.fill.outline || "rgba(255,255,255,.6)", "line-width": 1 }
      });
    }
    if (opts.line) {
      map.addLayer({
        id: id + "-line", type: "line", source: id,
        filter: ["match", ["geometry-type"], ["LineString", "MultiLineString"], true, false],
        layout: { "line-cap": "round", "line-join": "round" },
        paint: { "line-color": resolveColor(opts.line, "#0f766e"), "line-width": opts.line.width || 3 }
      });
    }
    if (opts.circle) {
      map.addLayer({
        id: id + "-circle", type: "circle", source: id,
        filter: ["match", ["geometry-type"], ["Point", "MultiPoint"], true, false],
        paint: {
          "circle-color": opts.circle.color || "#d7191c",
          "circle-radius": opts.circle.radius || 6,
          "circle-stroke-color": "#fff", "circle-stroke-width": 1.5
        }
      });
    }

    if (opts.popup && opts.popup.length) {
      ["-fill", "-circle", "-line"].forEach(function (suffix) {
        var layer = id + suffix;
        if (!map.getLayer(layer)) return;
        map.on("click", layer, function (e) {
          var props = e.features[0].properties || {};
          var noAttrs = window.I18N && window.I18N.getLang() === "es" ? "Sin atributos" : "No attributes";
          var html = opts.popup
            .filter(function (k) { return props[k] != null && props[k] !== ""; })
            .map(function (k) {
              var custom = opts.popupLabels && opts.popupLabels[k];
              return "<b>" + (custom ? pickLang(custom) : label(k)) + ":</b> " + props[k];
            })
            .join("<br>");
          openExclusivePopup(map, e.lngLat, html || noAttrs);
        });
        map.on("mouseenter", layer, function () { map.getCanvas().style.cursor = "pointer"; });
        map.on("mouseleave", layer, function () { map.getCanvas().style.cursor = ""; });
      });
    }
  }

  function label(k) {
    return k.replace(/_/g, " ").replace(/\b\w/g, function (c) { return c.toUpperCase(); });
  }

  // When two clickable layers overlap (e.g. a point marker sitting on top of
  // a filled polygon), MapLibre fires both layers' click handlers for the
  // same click — opening two stacked popups. Routing every popup through
  // here keeps at most one open at a time (last handler wins, i.e. whichever
  // layer was added last / is drawn on top).
  function openExclusivePopup(map, lngLat, html) {
    if (map._gpActivePopup) map._gpActivePopup.remove();
    map._gpActivePopup = new maplibregl.Popup({ closeButton: true }).setLngLat(lngLat).setHTML(html).addTo(map);
    return map._gpActivePopup;
  }

  function legendControl(cfg) {
    var ctrl = {
      render: function () {
        if (!ctrl._d) return;
        ctrl._d.innerHTML = "<b>" + pickLang(cfg.title) + "</b>" + cfg.items.map(function (it) {
          return '<div class="row"><span class="swatch" style="background:' + it.color +
                 '"></span>' + pickLang(it.label) + "</div>";
        }).join("");
      },
      onAdd: function () {
        var d = document.createElement("div");
        d.className = "maplibregl-ctrl map-legend";
        ctrl._d = d;
        ctrl.render();
        document.addEventListener("langchange", ctrl.render);
        return d;
      },
      onRemove: function () {
        document.removeEventListener("langchange", ctrl.render);
        ctrl._d.remove();
      }
    };
    return ctrl;
  }

  GISPortfolio.initMap = function (opts) {
    var id = opts.container.replace(/[^a-z0-9_-]/gi, "") + "-src";
    var map = new maplibregl.Map({
      container: opts.container,
      style: STYLES[theme()],
      center: opts.center || [0, 20],
      zoom: opts.zoom || 9,
      attributionControl: { compact: true }
    });
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");
    map.addControl(new maplibregl.ScaleControl({ maxWidth: 120, unit: "metric" }));
    if (opts.legend) map.addControl(legendControl(opts.legend), "bottom-left");

    var dataPromise = fetch(opts.geojson).then(function (r) {
      if (!r.ok) throw new Error("GeoJSON " + r.status);
      return r.json();
    });

    function draw() {
      dataPromise.then(function (data) {
        addLayers(map, id, data, opts);
        if (opts.fitToData !== false) {
          var b = bounds(data);
          if (isFinite(b[0])) map.fitBounds([[b[0], b[1]], [b[2], b[3]]], { padding: 40, duration: 0, maxZoom: 15 });
        }
        // Lets a page re-apply per-layer tweaks (e.g. a season/category toggle)
        // that would otherwise be lost when draw() reruns after a theme change.
        map.fire("gp:layersready", { id: id });
      }).catch(function (err) {
        console.error("Map data failed:", err);
        var el = document.getElementById(opts.container);
        var msg = window.I18N && window.I18N.getLang() === "es"
          ? "No se pudieron cargar los datos del mapa (" + err.message + ")."
          : "Could not load map data (" + err.message + ").";
        if (el) el.insertAdjacentHTML("beforeend", '<p class="notice" style="margin:1rem">' + msg + "</p>");
      });
    }

    // Whether a one-time event named "style.load"/"styledata" actually fires
    // again after setStyle() varies by MapLibre version, so addSource/addLayer
    // is only safe once the definitive isStyleLoaded() flag is true. Checked
    // from two independent triggers (MapLibre's own "styledata", which fires
    // as tile/style resources actually finish loading, plus a timer as a
    // backstop) so a background/throttled tab still recovers via whichever
    // fires first.
    function whenStyleLoaded(cb) {
      if (map.isStyleLoaded()) { cb(); return; }
      var done = false;
      function finish() {
        if (done || !map.isStyleLoaded()) return;
        done = true;
        map.off("styledata", finish);
        clearInterval(timer);
        cb();
      }
      map.on("styledata", finish);
      var tries = 0;
      var timer = setInterval(function () {
        tries++;
        if (map.isStyleLoaded() || tries > 100) finish(); // ~10s ceiling
      }, 100);
    }

    map.on("load", draw);
    document.addEventListener("themechange", function () {
      map.setStyle(STYLES[theme()]);
      whenStyleLoaded(draw);
    });

    return { map: map, id: id };
  };

  // Exposed so a page can build/swap a categorical paint expression itself
  // (e.g. a winter/summer toggle) via map.setPaintProperty(id + "-line", ...).
  GISPortfolio.matchExpr = matchExpr;
  GISPortfolio.stepExpr = stepExpr;
  GISPortfolio.openExclusivePopup = openExclusivePopup;
  // Exposed for pages that need a custom map setup initMap() doesn't fit —
  // e.g. toggling between several entirely different GeoJSON sources rather
  // than one source with several fields (initMap binds to a single fixed
  // geojson URL for its whole lifetime).
  GISPortfolio.STYLES = STYLES;
  GISPortfolio.theme = theme;
})();
