"""
Builds the five GeoJSON layers for the Logroño flood-resilience project.
Severity still comes from the flat "Features to JSON" export given for it;
risk and land cover are fetched live from the Logroño_Riesgo_T500
FeatureServer instead (see RIESGO_LAYER_URL / EXPOSICION_LAYER_URL) -- the
flat risk export turned out to be a stale, differently-classified version
(5 gridcode classes vs. the live service's 4, which match the report).

- data/logrono-severidad.geojson: T500 flood severity, from the flat export
  (~74k un-dissolved raster-to-polygon pixels, 62 MB). Genuinely speckled at
  the pixel level, not a floating-point export artifact -- confirmed by
  testing a union directly on live-service geometry in its native Web
  Mercator CRS (no reprojection involved at all) for the sibling risk layer
  and finding zero merging either way. No downstream vector processing fixes
  that; it would need a Majority Filter applied to the raster upstream in
  ArcGIS Pro. So this gets the same centroid-binned grid-majority treatment
  as build_iape_grid.py: bin each pixel's centroid into a 50 m cell, tally
  class votes, assign the cell its majority class.
- data/logrono-riesgo.geojson: final composite risk, fetched live (not from
  the stale flat export) via outSR=4326&f=geojson, which hands back ready
  -to-use GeoJSON already in WGS84 -- no esriJSON/reprojection juggling
  needed for this one, unlike land cover, since grid-majority binning (same
  treatment as severity; equally unfixable by dissolve) only needs accurate
  centroids, not adjacency-preserving geometry.
- data/logrono-cubierta.geojson: land cover, fetched live from the same
  FeatureServer's layer 0 ("Exposición" -- the severity x land-cover
  intersection). Unlike severity/risk, this one gets a real topological
  dissolve rather than a grid: it only looks fragmented because of that
  severity intersection, and dissolving by the 6 LAND_COVER_GROUPS
  categories alone (ignoring the severity split) recovers real, mostly
  -contiguous Urban Atlas parcels -- e.g. the Water class alone went from
  1,373 input fragments to 222 real parts on a test run. Dissolved in the
  service's native Web Mercator CRS (where adjacency actually holds), then
  the already-merged result is reprojected to WGS84 -- reprojecting the raw
  fragments first, before dissolving, is what breaks exact-edge adjacency
  for un-dissolved data.
- data/logrono-vulnerabilidad.geojson: ISVUN-G vulnerability index by census
  section -- already small (103 features), passed through with rounded
  coordinates and cleaned field names (source has mojibake from a
  Windows-1252 field-name export).
- data/logrono-municipio.geojson: municipal boundary, passthrough.

Gridcode -> severity label mapping (1-5, Baja..Extremadamente alta) is
confirmed from "Viario Expuesto.xlsx", which carries both GridCode and the
Spanish label for the same T500 analysis. The risk layer's gridcode->label
mapping (1-4, Bajo..Muy alto) is still an inference -- the field carries no
domain/legend (checked) -- but well-corroborated: true Shape__Area sums per
gridcode from the live service (1=0.338, 2=1.977, 3=6.403, 4=4.235 km2) rank
exactly as the report's own Alto > Muy alto > Medio > Bajo pattern, including
class 3 specifically outranking class 4 -- a much stronger match than simple
ascending order would be, though not a literal confirmed crosswalk.

Requires: ijson, shapely, pyproj (`pip install ijson shapely pyproj`)
"""
import ijson
import json
import math
import os
from collections import defaultdict, Counter

from shapely.geometry import shape, mapping, MultiPolygon
from shapely.geometry.polygon import orient

SRC_DIR = r"C:\Users\gideo\Documents\Resilencia"


def fix_winding(geom):
    """RFC 7946 requires GeoJSON exterior rings to be counter-clockwise
    (holes clockwise). shapely's union/transform/simplify chain doesn't
    enforce this, and Esri services commonly store rings the other way
    round -- feeding backwards-wound rings into MapLibre's geojson-vt/
    earcut pipeline can make a shape tessellate as a hole instead of a
    fill, i.e. render as a gap where a shape should be. Found this via the
    cubierta dissolve: 220 of 222 Water exterior rings came out clockwise.
    Grid-cell rectangles (severity/risk) are hand-built in the right order
    already and don't need this; anything that's been through a shapely
    union/simplify/transform does."""
    if geom.geom_type == "Polygon":
        return orient(geom, sign=1.0)
    if geom.geom_type == "MultiPolygon":
        return MultiPolygon([orient(p, sign=1.0) for p in geom.geoms])
    return geom
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

LAT0 = 42.46
CELL_M = 50  # grid cell size in meters
CELL_LON = CELL_M / (111320 * math.cos(math.radians(LAT0)))
CELL_LAT = CELL_M / 111320

SEVERITY_LABELS = {
    1: {"es": "Baja", "en": "Low"},
    2: {"es": "Moderada", "en": "Moderate"},
    3: {"es": "Alta", "en": "High"},
    4: {"es": "Muy alta", "en": "Very high"},
    5: {"es": "Extremadamente alta", "en": "Extremely high"},
}
# The live service has exactly 4 gridcode values (1-4), matching the
# report's own 4-class risk table -- unlike the stale flat export this
# replaced, which had 5. The specific gridcode->label mapping is still an
# inference (no domain/legend attached to the field -- checked), but it's
# well-corroborated now: querying true Shape__Area sums per gridcode gives
# 1=0.338, 2=1.977, 3=6.403, 4=4.235 km2, and that ranking (3 > 4 > 2 > 1)
# reproduces the report's specific Alto > Muy alto > Medio > Bajo pattern --
# notably including class 3 outranking class 4, not just simple ascending
# order, which is a much stronger match than the ordering alone would be.
RISK_LABELS = {
    1: {"es": "Bajo", "en": "Low"},
    2: {"es": "Medio", "en": "Medium"},
    3: {"es": "Alto", "en": "High"},
    4: {"es": "Muy alto", "en": "Very high"},
}

# The 20 Urban Atlas classes actually present in Pelogrosidad_Logroño_T500
# (the severity x land-cover intersection) grouped into 6 legible categories
# -- a straight legend of all 20 raw classes would be unreadable on a small
# web map. Grouping choices, e.g. folding "Land without current use" into
# urban and "Sports and leisure facilities" into green/natural, are a
# judgment call, not something confirmed from the source report.
LAND_COVER_GROUPS = {
    "Continuous urban fabric (S.L. : > 80%)": 1,
    "Discontinuous dense urban fabric (S.L. : 50% -  80%)": 1,
    "Discontinuous medium density urban fabric (S.L. : 30% - 50%)": 1,
    "Discontinuous low density urban fabric (S.L. : 10% - 30%)": 1,
    "Discontinuous very low density urban fabric (S.L. : < 10%)": 1,
    "Isolated structures": 1,
    "Land without current use": 1,
    "Industrial, commercial, public, military and private units": 2,
    "Mineral extraction and dump sites": 2,
    "Construction sites": 2,
    "Fast transit roads and associated land": 3,
    "Other roads and associated land": 3,
    "Railways and associated land": 3,
    "Arable land (annual crops)": 4,
    "Pastures": 4,
    "Permanent crops (vineyards, fruit trees, olive groves)": 4,
    "Forests": 5,
    "Herbaceous vegetation associations (natural grassland, moors...)": 5,
    "Green urban areas": 5,
    "Sports and leisure facilities": 5,
    "Water": 6,
}
LAND_COVER_LABELS = {
    1: {"es": "Urbano / edificado", "en": "Urban / built-up"},
    2: {"es": "Industrial / comercial", "en": "Industrial / commercial"},
    3: {"es": "Infraestructura de transporte", "en": "Transport infrastructure"},
    4: {"es": "Agrícola", "en": "Agricultural"},
    5: {"es": "Verde y natural", "en": "Green & natural"},
    6: {"es": "Agua", "en": "Water"},
}


def polygon_centroid(geom_dict):
    """Cheap coordinate-mean centroid, avoiding shapely construction on
    possibly-invalid raw pixel geometry. Good enough for grid binning."""
    if geom_dict["type"] == "Polygon":
        rings = [geom_dict["coordinates"][0]]
    elif geom_dict["type"] == "MultiPolygon":
        rings = [part[0] for part in geom_dict["coordinates"]]
    else:
        return None
    xs, ys, n = 0.0, 0.0, 0
    for ring in rings:
        for x, y in ring:
            xs += float(x)
            ys += float(y)
            n += 1
    return (xs / n, ys / n) if n else None


def grid_majority(src_path, labels, classify=None, prop_name="gridcode"):
    """Stream a raw raster-to-polygon (or raster-intersection) export from a
    file. See grid_majority_from_iter for the actual binning logic; this
    just wraps it with an ijson file stream."""
    classify = classify or (lambda p: p.get("gridcode"))

    def iter_features():
        with open(src_path, "rb") as f:
            for feat in ijson.items(f, "features.item"):
                yield feat

    return grid_majority_from_iter(iter_features(), labels, classify, prop_name)


def grid_majority_from_iter(features_iter, labels, classify=None, prop_name="gridcode"):
    """Bin each feature's centroid into a CELL_M grid cell, tally class
    votes per cell, assign each cell its majority class. Returns GeoJSON
    features, one per cell. `classify(properties) -> class key` defaults to
    reading properties["gridcode"] directly; pass one to derive the class
    from a different/raw field instead (e.g. grouping a land-cover class
    name). `features_iter` yields GeoJSON-shaped features (already in
    WGS84 degrees -- this does no reprojection of its own)."""
    classify = classify or (lambda p: p.get("gridcode"))
    cells = defaultdict(Counter)
    n = 0
    for feat in features_iter:
        n += 1
        gc = classify(feat["properties"])
        geom_dict = feat.get("geometry")
        if geom_dict is None or gc is None:
            continue
        c = polygon_centroid(geom_dict)
        if c is None:
            continue
        cx, cy = math.floor(c[0] / CELL_LON), math.floor(c[1] / CELL_LAT)
        cells[(cx, cy)][gc] += 1
        if n % 20000 == 0:
            print(f"  ...read {n} features")
    print(f"  total read: {n}, grid cells: {len(cells)}")

    class_counts = Counter()
    features = []
    for (cx, cy), votes in cells.items():
        gc, _ = votes.most_common(1)[0]
        class_counts[gc] += 1
        x0, x1 = cx * CELL_LON, (cx + 1) * CELL_LON
        y0, y1 = cy * CELL_LAT, (cy + 1) * CELL_LAT
        label = labels.get(gc, {"es": f"Clase {gc}", "en": f"Class {gc}"})
        features.append({
            "type": "Feature",
            "properties": {
                prop_name: gc if isinstance(gc, str) else int(gc),
                "label_es": label["es"],
                "label_en": label["en"],
            },
            "geometry": {"type": "Polygon", "coordinates": [[
                [round(x0, 6), round(y0, 6)], [round(x1, 6), round(y0, 6)],
                [round(x1, 6), round(y1, 6)], [round(x0, 6), round(y1, 6)],
                [round(x0, 6), round(y0, 6)],
            ]]},
        })
    for gc in sorted(class_counts, key=str):
        label = labels.get(gc, {}).get("es", gc)
        area_km2 = class_counts[gc] * (CELL_M * CELL_M) / 1e6
        print(f"     {prop_name}={gc} ({label}): {class_counts[gc]} cells, ~{area_km2:.3f} km2")
    return features


def build_severity():
    print("Building severity layer...")
    features = grid_majority(
        os.path.join(SRC_DIR, "Severidad_Area_Sev_Logroño_r500.geojson"),
        SEVERITY_LABELS,
    )
    out = {"type": "FeatureCollection", "features": features}
    out_path = os.path.join(OUT_DIR, "logrono-severidad.geojson")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, separators=(",", ":"))
    print(f"  -> {out_path} ({os.path.getsize(out_path)/1024:.1f} KB), {len(features)} cells")


RIESGO_LAYER_URL = (
    "https://services1.arcgis.com/wKWg6g7Ozgov9sfw/arcgis/rest/services/"
    "Logro%C3%B1o_Riesgo_T500/FeatureServer/2/query"
)


def fetch_all_geojson_features(query_url, where="1=1", out_fields="*", page_size=2000):
    """Page through an ArcGIS REST FeatureServer query requesting GeoJSON
    output reprojected to WGS84 server-side (outSR=4326) -- returns
    ready-to-use GeoJSON Feature dicts, no esriJSON rings/attrs conversion
    needed."""
    import urllib.request
    import urllib.parse

    features = []
    offset = 0
    while True:
        params = {
            "where": where, "outFields": out_fields, "returnGeometry": "true",
            "outSR": "4326", "f": "geojson",
            "resultOffset": offset, "resultRecordCount": page_size,
        }
        url = query_url + "?" + urllib.parse.urlencode(params)
        with urllib.request.urlopen(url) as r:
            data = json.load(r)
        page = data.get("features", [])
        if not page:
            break
        features.extend(page)
        if len(page) < page_size:
            break
        offset += page_size
    return features


def build_risk():
    """The stale flat export (Logroño_Riesgo_T500.geojson) this used to
    read had 5 gridcode classes that didn't reconcile with the report's own
    4-class table. The live service only has 4 -- fetched directly instead
    (as proper GeoJSON in WGS84 via outSR=4326, so no format/reprojection
    juggling needed, unlike the land-cover dissolve). Still grid-majority,
    not a true dissolve -- confirmed risk is genuinely speckled at the pixel
    level, same as severity; see module docstring."""
    print("Building risk layer (live fetch)...")
    print("  fetching all features from live FeatureServer...")
    raw_features = fetch_all_geojson_features(RIESGO_LAYER_URL, out_fields="gridcode")
    print(f"  fetched {len(raw_features)} features")

    features = grid_majority_from_iter(iter(raw_features), RISK_LABELS)
    out = {"type": "FeatureCollection", "features": features}
    out_path = os.path.join(OUT_DIR, "logrono-riesgo.geojson")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, separators=(",", ":"))
    print(f"  -> {out_path} ({os.path.getsize(out_path)/1024:.1f} KB), {len(features)} cells")


EXPOSICION_LAYER_URL = (
    "https://services1.arcgis.com/wKWg6g7Ozgov9sfw/arcgis/rest/services/"
    "Logro%C3%B1o_Riesgo_T500/FeatureServer/0/query"
)


def fetch_all_features(query_url, where="1=1", out_fields="*", page_size=2000):
    """Page through an ArcGIS REST FeatureServer query (maxRecordCount caps
    a single request), returning raw esriJSON features (rings, not GeoJSON
    coordinates -- geometry is {"rings": [...]})."""
    import urllib.request
    import urllib.parse

    features = []
    offset = 0
    while True:
        params = {
            "where": where, "outFields": out_fields, "returnGeometry": "true",
            "f": "json", "resultOffset": offset, "resultRecordCount": page_size,
        }
        url = query_url + "?" + urllib.parse.urlencode(params)
        with urllib.request.urlopen(url) as r:
            data = json.load(r)
        page = data.get("features", [])
        if not page:
            break
        features.extend(page)
        if len(page) < page_size:
            break
        offset += page_size
    return features


def build_cubierta():
    """Unlike severity/risk (raw raster classification -- genuinely
    speckled at pixel level, confirmed by testing union on the live
    service's native Web Mercator geometry directly: zero merging even
    with no reprojection involved), land cover is sourced from real Urban
    Atlas vector parcels and only looks fragmented because the export
    intersects it with that speckled severity raster. Dissolving by
    land-cover category alone (ignoring the severity split) recovers real,
    mostly-contiguous polygons -- e.g. the Water class alone went from 1,373
    input fragments to 222 real parts on a test run. So this one gets an
    actual topological dissolve instead of the grid-majority treatment,
    fetched fresh from the live FeatureServer (the flat export used
    elsewhere doesn't carry this same live layer)."""
    print("Building land-cover layer (live dissolve, not grid)...")
    import pyproj
    from shapely.ops import unary_union, transform

    print("  fetching all features from live FeatureServer...")
    raw_features = fetch_all_features(EXPOSICION_LAYER_URL, out_fields="class_2018")
    print(f"  fetched {len(raw_features)} features")

    groups = defaultdict(list)
    for feat in raw_features:
        cat = LAND_COVER_GROUPS.get(feat["attributes"].get("class_2018"))
        geom_dict = feat.get("geometry")
        if cat is None or geom_dict is None:
            continue
        g = shape({"type": "Polygon", "coordinates": geom_dict["rings"]})
        if not g.is_valid:
            g = g.buffer(0)
        groups[cat].append(g)

    # Dissolve in the service's native Web Mercator CRS (where adjacency
    # actually holds), THEN reproject the already-merged result to WGS84,
    # THEN simplify. Reprojecting the raw fragments first -- before
    # dissolving -- is what breaks exact-edge adjacency for un-dissolved
    # data; doing it after is harmless since there's only one geometry left.
    to_wgs84 = pyproj.Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True).transform

    features = []
    for cat in sorted(groups):
        merged = unary_union(groups[cat])
        merged = transform(to_wgs84, merged)
        merged = merged.simplify(0.00003, preserve_topology=True)
        merged = fix_winding(merged)
        label = LAND_COVER_LABELS[cat]
        features.append({
            "type": "Feature",
            "properties": {"category": cat, "label_es": label["es"], "label_en": label["en"]},
            "geometry": mapping(merged),
        })
        print(f"     category={cat} ({label['es']}): {len(groups[cat])} inputs -> dissolved")

    out = {"type": "FeatureCollection", "features": features}
    out_path = os.path.join(OUT_DIR, "logrono-cubierta.geojson")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, separators=(",", ":"))
    print(f"  -> {out_path} ({os.path.getsize(out_path)/1024:.1f} KB)")


def build_vulnerability():
    print("Building vulnerability layer...")
    src_path = os.path.join(SRC_DIR, "Indice_Sintetico_de_Vulnerabilidad_Urbana_Nacional_Global.geojson")
    features = []
    with open(src_path, "rb") as f:
        for feat in ijson.items(f, "features.item"):
            p = feat["properties"]
            geom = shape(feat["geometry"]).simplify(0.00003, preserve_topology=True)
            geom = fix_winding(geom)
            val = p.get("ISVUN_G__Clasificaci\u00f3n_Global")
            if val is None:
                continue
            # Source "Etiqueta" field has corrupted (mojibake) encoding for
            # \u00f1/accented characters -- build a clean label instead.
            distrito, seccion = p.get("DISTRITO"), p.get("SECCION")
            features.append({
                "type": "Feature",
                "properties": {
                    "seccion": p.get("CODIGO"),
                    "label": f"Distrito {distrito} \u00b7 Secci\u00f3n {seccion}",
                    "isvun_g": round(float(val), 3),
                },
                "geometry": mapping(geom),
            })
    out = {"type": "FeatureCollection", "features": features}
    out_path = os.path.join(OUT_DIR, "logrono-vulnerabilidad.geojson")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, separators=(",", ":"))
    print(f"  -> {out_path} ({os.path.getsize(out_path)/1024:.1f} KB), {len(features)} secciones")


def build_municipio():
    print("Building municipio boundary...")
    src_path = os.path.join(SRC_DIR, "Municipio_de_Logroño.geojson")
    with open(src_path, encoding="utf-8") as f:
        data = json.load(f)
    for feat in data["features"]:
        geom = shape(feat["geometry"]).simplify(0.00003, preserve_topology=True)
        geom = fix_winding(geom)
        feat["geometry"] = mapping(geom)
        feat["properties"] = {"name": feat["properties"].get("NAMEUNIT")}
    out_path = os.path.join(OUT_DIR, "logrono-municipio.geojson")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, separators=(",", ":"))
    print(f"  -> {out_path} ({os.path.getsize(out_path)/1024:.1f} KB)")


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    build_severity()
    build_risk()
    build_cubierta()
    build_vulnerability()
    build_municipio()
