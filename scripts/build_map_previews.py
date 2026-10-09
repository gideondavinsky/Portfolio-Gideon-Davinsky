#!/usr/bin/env python3
"""Build compact SVG gallery images from the portfolio's real GeoJSON layers."""
from __future__ import annotations
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "maps"
W, H, PAD = 1200, 720, 56
PAPER = "#f2ebdd"


def polygons(geometry):
    if not geometry:
        return
    kind, coords = geometry.get("type"), geometry.get("coordinates", [])
    if kind == "Polygon":
        yield coords[0]
    elif kind == "MultiPolygon":
        for poly in coords:
            if poly:
                yield poly[0]


def project_features(dataset):
    features = dataset.get("features", [])
    points = [p for f in features for ring in polygons(f.get("geometry")) for p in ring]
    if not points:
        return []
    mean_lat = sum(p[1] for p in points) / len(points)
    cos_lat = math.cos(math.radians(mean_lat))
    projected = [((math.radians(p[0]) * cos_lat), math.log(math.tan(math.pi / 4 + math.radians(p[1]) / 2))) for p in points]
    minx, maxx = min(p[0] for p in projected), max(p[0] for p in projected)
    miny, maxy = min(p[1] for p in projected), max(p[1] for p in projected)
    spanx, spany = max(maxx - minx, 1e-9), max(maxy - miny, 1e-9)
    scale = min((W - 2 * PAD) / spanx, (H - 2 * PAD) / spany)
    ox, oy = (W - spanx * scale) / 2, (H - spany * scale) / 2

    def point_xy(p):
        x = math.radians(p[0]) * cos_lat
        y = math.log(math.tan(math.pi / 4 + math.radians(p[1]) / 2))
        return ox + (x - minx) * scale, H - (oy + (y - miny) * scale)

    rows = []
    for feature in features:
        geom = feature.get("geometry")
        if not geom:
            continue
        for ring in polygons(geom):
            if len(ring) < 4:
                continue
            coords = [point_xy(p) for p in ring]
            path = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in coords) + " Z"
            rows.append((path, feature.get("properties", {})))
    return rows


def svg_for(source, output, field, colors, palette_name):
    data = json.loads((ROOT / source).read_text(encoding="utf-8"))
    shapes = project_features(data)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="Data-derived map preview">',
        f'<rect width="{W}" height="{H}" fill="{PAPER}"/>',
        '<path d="M28 28h1144v664H28z" fill="none" stroke="#bcb29e" stroke-width="1"/>',
        '<g fill="none" stroke="#c9bfae" stroke-width="1" opacity=".72">',
        f'<path d="M56 {H//2}h{W-112}"/><path d="M{W//2} 56v{H-112}"/>',
        '</g>',
        '<g stroke="#f2ebdd" stroke-width="1.25" stroke-linejoin="round" stroke-linecap="round">'
    ]
    for path, props in shapes:
        value = props.get(field)
        if value is None:
            color = colors[0][1] if isinstance(colors, list) else colors.get(0, colors.get("default", "#a63d2f"))
        else:
            try:
                numeric = float(value)
                if isinstance(colors, dict):
                    color = colors.get(int(numeric), colors.get("default", "#a63d2f"))
                else:
                    color = colors[0][1]
                    for threshold, candidate in colors[1:]:
                        if numeric >= threshold:
                            color = candidate
            except (TypeError, ValueError):
                color = colors.get(str(value), colors.get("default", "#a63d2f")) if isinstance(colors, dict) else colors[0]
        parts.append(f'<path d="{path}" fill="{color}" fill-opacity=".94"/>')
    parts += ['</g>', f'<path d="M{W-PAD-32} {PAD}v44m-11-12h22" fill="none" stroke="#29342d" stroke-width="2"/>', '<circle cx="1138" cy="105" r="4" fill="#a63d2f"/>', '</svg>']
    OUT.mkdir(parents=True, exist_ok=True)
    (ROOT / output).write_text("\n".join(parts), encoding="utf-8")
    print(f"{output}: rendered {len(shapes)} polygon rings from {source} ({palette_name})")


svg_for(
    "data/logrono-riesgo.geojson", "assets/maps/logrono-risk.svg", "gridcode",
    {1: "#839579", 2: "#c0b47c", 3: "#d58b62", 4: "#a63d2f", "default": "#a63d2f"},
    "Logroño T500 risk classes",
)
svg_for(
    "data/e2sfca-atlanta.geojson", "assets/maps/atlanta-access.svg", "score_per1000",
    [(0, "#a63d2f"), (1, "#c27458"), (2, "#d4b277"), (3, "#a8a982"), (4, "#75886f"), (5, "#425f4b")],
    "Atlanta healthcare access score",
)
