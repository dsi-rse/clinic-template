{% if cookiecutter.dashboard == 'yes' -%}
"""Export pipeline outputs as parquet + data dictionaries for the dashboard.

Usage:
    from {{ cookiecutter.code_directory }}.dashboard_export import export_dataset
    export_dataset(df, "my_dataset")
    # Writes dashboard/public/data/my_dataset.parquet and
    # dashboard/data/dictionary/my_dataset.{json,md}.
"""

from __future__ import annotations

import contextlib
import json
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

DASHBOARD_DIR: Path = Path(__file__).parent.parent.parent / "dashboard"
PARQUET_DIR: Path = DASHBOARD_DIR / "public" / "data"
DICT_DIR: Path = DASHBOARD_DIR / "data" / "dictionary"


def describe_dataframe(
    df: pd.DataFrame, *, include_samples: bool = False
) -> dict[str, Any]:
    """Return a data-dictionary dict for *df* (row count + per-column stats).

    The dictionary files are COMMITTED to git (the parquet is not), so by
    default no raw row values are included — for partner data, five verbatim
    samples per column (names, addresses, record IDs) would live in git
    history forever. Pass ``include_samples=True`` only for data that is safe
    to publish.

    Args:
        df: DataFrame to describe.
        include_samples: Include five verbatim example values per column.
    """
    columns: dict[str, Any] = {}
    for col in df.columns:
        series = df[col]
        entry: dict[str, Any] = {
            "dtype": str(series.dtype),
            "nulls": int(series.isna().sum()),
            "n_unique": int(series.nunique()),
        }
        if pd.api.types.is_numeric_dtype(series):
            entry["min"] = float(series.min())
            entry["max"] = float(series.max())
        elif hasattr(series, "min"):
            with contextlib.suppress(Exception):
                entry["min"] = str(series.min())
                entry["max"] = str(series.max())
        if include_samples:
            entry["samples"] = series.dropna().head(5).tolist()
        columns[col] = entry
    return {"row_count": len(df), "columns": columns}


def _dict_to_markdown(name: str, info: dict[str, Any]) -> str:
    """Render a data-dictionary dict as a Markdown table."""
    rows = []
    for col, meta in info["columns"].items():
        samples = ", ".join(str(s) for s in meta.get("samples", []))
        rows.append(
            f"| {col} | {meta['dtype']} | {meta['nulls']} | {meta['n_unique']} "
            f"| {meta.get('min', '—')} | {meta.get('max', '—')} | {samples} |"
        )
    header = (
        f"# {name} — Data Dictionary\n\n"
        f"**Rows:** {info['row_count']:,}\n\n"
        "| Column | Type | Nulls | Unique | Min | Max | Sample Values |\n"
        "|--------|------|-------|--------|-----|-----|---------------|\n"
    )
    return header + "\n".join(rows) + "\n"


def export_dataset(
    df: pd.DataFrame, name: str, *, include_samples: bool = False
) -> None:
    """Write *df* as ``<name>.parquet`` + data dictionary files for the dashboard.

    Tip: sort *df* by its primary time/key column before exporting — sorted
    data compresses much better and gives each row group tight statistics.

    Args:
        df: DataFrame to export.
        name: Dataset name (used as parquet stem and DuckDB view name).
        include_samples: Put five verbatim example values per column into the
            COMMITTED data dictionary. Leave False unless the values are safe
            to publish (see ``describe_dataframe``).
    """
    PARQUET_DIR.mkdir(parents=True, exist_ok=True)
    DICT_DIR.mkdir(parents=True, exist_ok=True)

    parquet_path = PARQUET_DIR / f"{name}.parquet"
    table = pa.Table.from_pandas(df)
    # zstd + modest row groups: pyarrow's defaults produce a couple of huge
    # row groups whose statistics prune nothing.
    pq.write_table(table, parquet_path, compression="zstd", row_group_size=131072)
    print(f"  wrote {parquet_path} ({parquet_path.stat().st_size / 1_048_576:.2f} MB)")

    info = describe_dataframe(df, include_samples=include_samples)
    info["name"] = name

    json_path = DICT_DIR / f"{name}.json"
    json_path.write_text(json.dumps(info, indent=2, default=str))
    print(f"  wrote {json_path}")

    md_path = DICT_DIR / f"{name}.md"
    md_path.write_text(_dict_to_markdown(name, info))
    print(f"  wrote {md_path}")
{%- endif %}
