# /// script
# requires-python = ">=3.11"
# dependencies = ["geopandas>=1.0", "pyarrow>=15"]
# ///
"""Build the community_areas sample GeoParquet from the Chicago Data Portal.

Joins community area boundaries with the 2008-2012 socioeconomic indicators
census dataset, simplifies geometry, and writes:

  public/data/community_areas.parquet   (GeoParquet: WKB `geometry` column +
                                         a `geometry_geojson` string column
                                         for direct use in MapLibre)
  data/dictionary/community_areas.{json,md}

Sources (public domain, City of Chicago):
  https://data.cityofchicago.org/d/igwz-8jzy  (boundaries)
  https://data.cityofchicago.org/d/kn9c-c2s2  (socioeconomic indicators)

Usage:
    uv run dashboard/scripts/make_sample_geodata.py
"""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path

import geopandas as gpd
import pandas as pd
import shapely

BOUNDARIES_URL = (
    "https://data.cityofchicago.org/api/geospatial/igwz-8jzy"
    "?method=export&format=GeoJSON"
)
SOCIO_URL = "https://data.cityofchicago.org/resource/kn9c-c2s2.json?$limit=100"

DASHBOARD_DIR = Path(__file__).parent.parent
PARQUET_PATH = DASHBOARD_DIR / "public" / "data" / "community_areas.parquet"
DICT_DIR = DASHBOARD_DIR / "data" / "dictionary"

RENAME = {
    "percent_of_housing_crowded": "pct_housing_crowded",
    "percent_households_below_poverty": "pct_below_poverty",
    "percent_aged_16_unemployed": "pct_unemployed",
    "percent_aged_25_without_high_school_diploma": "pct_no_hs_diploma",
    "percent_aged_under_18_or_over_64": "pct_dependent_age",
    "per_capita_income_": "per_capita_income",
    "hardship_index": "hardship_index",
}


def build() -> gpd.GeoDataFrame:
    """Download Chicago community-area boundaries and join socioeconomic indicators."""
    with urllib.request.urlopen(BOUNDARIES_URL) as resp:  # noqa: S310
        boundaries = gpd.read_file(resp)
    with urllib.request.urlopen(SOCIO_URL) as resp:  # noqa: S310
        socio = pd.DataFrame(json.load(resp))

    # Drop the citywide summary row (it has no community area number).
    socio = socio.dropna(subset=["ca"])
    socio = socio.rename(columns=RENAME)
    socio["area_num"] = socio["ca"].astype(int)
    for col in RENAME.values():
        socio[col] = socio[col].astype(float)

    boundaries["area_num"] = boundaries["area_numbe"].astype(int)
    boundaries["name"] = boundaries["community"].str.title()

    gdf = boundaries[["area_num", "name", "geometry"]].merge(
        socio[["area_num", *RENAME.values()]], on="area_num", validate="1:1"
    )
    gdf = gdf.sort_values("area_num").reset_index(drop=True)

    # Simplify + round coordinates so the file stays small (~0.5 MB).
    gdf["geometry"] = shapely.set_precision(gdf.geometry.simplify(0.0001), 1e-5)
    # MapLibre-ready GeoJSON strings; DuckDB-wasm can't decode WKB without
    # the spatial extension, so ship both representations.
    gdf["geometry_geojson"] = gdf.geometry.apply(shapely.to_geojson)
    return gdf


def write_dictionary(gdf: gpd.GeoDataFrame) -> None:
    """Write the JSON and Markdown data dictionaries for *gdf*."""
    columns: dict[str, dict] = {}
    for col in gdf.columns:
        series = gdf[col]
        if col == "geometry":
            columns[col] = {
                "dtype": "geometry (WKB, EPSG:4326 MultiPolygon)",
                "nulls": 0,
                "n_unique": len(gdf),
            }
            continue
        if col == "geometry_geojson":
            columns[col] = {
                "dtype": "str (GeoJSON geometry, for MapLibre)",
                "nulls": 0,
                "n_unique": len(gdf),
            }
            continue
        entry: dict = {
            "dtype": str(series.dtype),
            "nulls": int(series.isna().sum()),
            "n_unique": int(series.nunique()),
        }
        if pd.api.types.is_numeric_dtype(series):
            entry["min"] = float(series.min())
            entry["max"] = float(series.max())
        else:
            entry["min"] = str(series.min())
            entry["max"] = str(series.max())
        entry["samples"] = series.dropna().head(5).tolist()
        columns[col] = entry

    info = {
        "name": "community_areas",
        "description": (
            "Chicago's 77 community areas with 2008-2012 census socioeconomic "
            "indicators. Percent columns are 0-100; hardship_index is a 1-98 "
            "composite (higher = more hardship). Sources: Chicago Data Portal "
            "igwz-8jzy (boundaries) + kn9c-c2s2 (indicators)."
        ),
        "row_count": len(gdf),
        "columns": columns,
    }
    DICT_DIR.mkdir(parents=True, exist_ok=True)
    (DICT_DIR / "community_areas.json").write_text(
        json.dumps(info, indent=2, default=str)
    )

    rows = []
    for col, meta in columns.items():
        samples = ", ".join(str(s) for s in meta.get("samples", []))
        rows.append(
            f"| {col} | {meta['dtype']} | {meta['nulls']} | {meta['n_unique']} "
            f"| {meta.get('min', '—')} | {meta.get('max', '—')} | {samples} |"
        )
    md = (
        "# community_areas — Data Dictionary\n\n"
        f"{info['description']}\n\n"
        f"**Rows:** {len(gdf)}\n\n"
        "| Column | Type | Nulls | Unique | Min | Max | Sample Values |\n"
        "|--------|------|-------|--------|-----|-----|---------------|\n"
        + "\n".join(rows)
        + "\n"
    )
    (DICT_DIR / "community_areas.md").write_text(md)


if __name__ == "__main__":
    gdf = build()
    PARQUET_PATH.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_parquet(PARQUET_PATH, compression="zstd")
    print(f"wrote {PARQUET_PATH} ({PARQUET_PATH.stat().st_size / 1_048_576:.2f} MB)")
    write_dictionary(gdf)
    print(f"wrote {DICT_DIR}/community_areas.json + .md")
