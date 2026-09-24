"""
Build data/e2sfca-atlanta.geojson from the ArcGIS E2SFCA output.

Keeps: the total multimodal score, the three per-mode scores, and a focused
equity/travel-time field set. Drops 150+ ACS columns not used on the site.
Simplifies tract polygons (independently per feature — fine for a choropleth
fill, not meant as authoritative admin boundaries) to cut file size.

Requires: shapely (`pip install shapely`)
"""
import json
import os
import re

from shapely.geometry import mapping, shape

SRC = r"C:/Users/gideo/Documents/TFM/TFMFInal/MM_E2SFCA_Atlanta_Hospitals.geojson"
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "e2sfca-atlanta.geojson")

SIMPLIFY_TOLERANCE = 0.0002  # ~20 m at this latitude


def r1(v):
    return round(v, 1) if isinstance(v, (int, float)) else v


def r2(v):
    return round(v, 2) if isinstance(v, (int, float)) else v


def r6(v):
    return round(v, 6)


def county_from_name(name):
    m = re.search(r",\s*([A-Za-z]+) County", name or "")
    return m.group(1) if m else None


def round_coords(geom_type, coords):
    if geom_type == "Polygon":
        return [[[r6(x), r6(y)] for x, y in ring] for ring in coords]
    return [[[[r6(x), r6(y)] for x, y in ring] for ring in poly] for poly in coords]


def main():
    with open(SRC, encoding="utf-8") as f:
        data = json.load(f)

    out_features = []
    for feat in data["features"]:
        p = feat["properties"]

        props = {
            "geoid": p.get("GEOID"),
            "name": p.get("Name"),
            "county": county_from_name(p.get("Name")),
            "score_per1000": r1(p.get("MM_A_i_Total_Norm_per_1000")),
            "score_drive_per1000": r1(p.get("SUM_MM_Drive_Contributed_R_Norm_per_1000")),
            "score_transit_per1000": r1(p.get("SUM_MM_Transit_Contributed_R_Norm_per_1000")),
            "score_walk_per1000": r1(p.get("SUM_MM_Walk_Contributed_R_Norm_per_1000")),
            "pop": p.get("TotPop_e24"),
            "med_hh_income": p.get("mMedHHInc_"),
            "pct_no_vehicle": r2(p.get("p_no_VA")),
            "pct_black": r2(p.get("pNHBlack_e")),
            "pct_hispanic": r2(p.get("pHisp_e24")),
            "pct_65plus": r2(p.get("pAge65P_e2")),
            # Normalized mode share — verified by reconstructing
            # MM_A_i_Total_Norm from its components: it reproduces exactly
            # with Pct_*_Norm, not the raw Pct_Drive/Transit/Walk.
            "pct_drive": r2((p.get("Pct_Drive_Norm") or 0) * 100),
            "pct_transit": r2((p.get("Pct_Transit_Norm") or 0) * 100),
            "pct_walk": r2((p.get("Pct_Walk_Norm") or 0) * 100),
            "min_drive_time": r2(p.get("M_DT")),
            "min_walk_time": r2(p.get("M_WT")),
            "min_transit_time": r2(p.get("M_PT")),
        }

        geom = shape(feat["geometry"]).simplify(SIMPLIFY_TOLERANCE, preserve_topology=True)
        m = mapping(geom)

        out_features.append({
            "type": "Feature",
            "properties": props,
            "geometry": {"type": m["type"], "coordinates": round_coords(m["type"], m["coordinates"])},
        })

    out = {"type": "FeatureCollection", "features": out_features}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))

    print(f"{len(out_features)} features, {os.path.getsize(OUT) / 1e6:.2f} MB -> {OUT}")


if __name__ == "__main__":
    main()
