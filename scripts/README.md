# Data build scripts

These reproduce every file in `data/` from the original ArcGIS exports. Nothing on
the live site depends on these at runtime — they're a record of how each GeoJSON was
trimmed/simplified/aggregated, so a refresh (new ACS year, more hospitals, a new
project) doesn't require reverse-engineering what was done from scratch.

**Requires:** Python 3 + `shapely` (`pip install shapely`) for the scripts that
simplify geometry, `ijson` (`pip install ijson`) for `build_resilencia_data.py`,
which streams sources too large (62 MB/22 MB) to load whole, and `pyproj`
(`pip install pyproj`) for `build_resilencia_data.py`'s land-cover dissolve
(reprojects Web Mercator → WGS84 after unioning). The rest use only the
standard library.

Each script takes the source export's path as `SRC` (edit the constant at the top —
these paths are local to whoever's machine has the original ArcGIS project) and
writes straight into `../data/`.

| Script | Source layer | Output | What it does |
|---|---|---|---|
| `build_e2sfca_data.py` | `MM_E2SFCA_Atlanta_Hospitals.geojson` | `e2sfca-atlanta.geojson` | Keeps the total + per-mode accessibility scores and a focused equity/travel-time field set (drops 150+ unused ACS columns); simplifies tract polygons (~20 m tolerance, 600 tracts: 2.97 MB → 0.65 MB). |
| `build_hospitals_data.py` | `Hospitales_CMS_FeaturesToJSO.geojson` | `hospitals-atlanta.geojson` | Trims to name/beds/type/address/county/note; title-cases names. |
| `build_resilencia_data.py` | `Severidad_Area_Sev_Logroño_r500.geojson`, `Logroño_Riesgo_T500.geojson`, the live `Logroño_Riesgo_T500` FeatureServer (layer 0, "Exposición", queried directly), `Indice_Sintetico_de_Vulnerabilidad_Urbana_Nacional_Global.geojson`, `Municipio_de_Logroño.geojson` | `logrono-severidad.geojson`, `logrono-riesgo.geojson`, `logrono-cubierta.geojson`, `logrono-vulnerabilidad.geojson`, `logrono-municipio.geojson` | Severity/risk sources are ~74k/~19.6k un-dissolved raster-to-polygon pixels (62 MB/22 MB) that are genuinely speckled at the pixel level (confirmed: a union on the live service's native Web Mercator geometry, no reprojection involved, still doesn't merge) -- aggregated to a 50 m majority-class grid instead (same centroid-binning approach as the IAPE grid). Land cover looks fragmented for a different reason (it's real Urban Atlas parcels cut up by intersection with that speckled severity raster), so it gets an actual topological dissolve by land-cover category instead, fetched live from the FeatureServer and dissolved in its native CRS before reprojecting. Vulnerability and the boundary are passed through near-unchanged (already small). |

Run from this directory once `SRC` is edited, e.g.:

```bash
python build_e2sfca_data.py
```
