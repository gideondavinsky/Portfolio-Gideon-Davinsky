"""
Build data/hospitals-atlanta.geojson from the CMS provider export.

Keeps: name, bed count, type, address, city, county, and any CMS note.
"""
import json
import os

SRC = r"C:/Users/gideo/Documents/TFM/TFMFInal/Hospitales_CMS_FeaturesToJSO.geojson"
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "hospitals-atlanta.geojson")


def main():
    with open(SRC, encoding="utf-8") as f:
        data = json.load(f)

    out_features = []
    for feat in data["features"]:
        p = feat["properties"]
        out_features.append({
            "type": "Feature",
            "properties": {
                "name": (p.get("Hospital_Name") or "").title(),
                "beds": p.get("Number_of_Beds"),
                "type": p.get("Site_Subca"),
                "address": p.get("Address"),
                "city": (p.get("City") or "").title(),
                "county": (p.get("County") or "").title(),
                "note": p.get("Note"),
            },
            "geometry": feat["geometry"],
        })

    out = {"type": "FeatureCollection", "features": out_features}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))

    print(f"{len(out_features)} features, {os.path.getsize(OUT)} bytes -> {OUT}")


if __name__ == "__main__":
    main()
