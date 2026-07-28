"""Pull parquet datasets from Box public links into public/data/.

Uses Python stdlib only (no third-party deps). Idempotent — skips existing files
unless --force is passed. Fails with exit code 1 if total parquet size exceeds
MAX_TOTAL_MB.

Usage:
    python3 dashboard/scripts/pull_data.py
    python3 dashboard/scripts/pull_data.py --force
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

MAX_TOTAL_MB: int = 150
MANIFEST_PATH: Path = Path(__file__).parent.parent / "data.manifest.json"
OUTPUT_DIR: Path = Path(__file__).parent.parent / "public" / "data"


def pull_data(*, force: bool = False) -> None:
    """Download parquet files listed in data.manifest.json."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    manifest: list[dict[str, str]] = json.loads(MANIFEST_PATH.read_text())

    for entry in manifest:
        name: str = entry["name"]
        url: str = entry["url"]
        dest: Path = OUTPUT_DIR / f"{name}.parquet"

        if dest.exists() and not force:
            print(f"  skip  {dest.name} (already exists; use --force to re-download)")
            continue

        print(f"  fetch {dest.name} from {url}")
        tmp: Path = dest.with_name(dest.name + ".tmp")
        urllib.request.urlretrieve(url, tmp)  # noqa: S310
        if tmp.read_bytes()[:4] != b"PAR1":
            tmp.unlink()
            print(
                f"ERROR: {url} did not return a parquet file "
                "(got HTML or other content -- check the Box static link).",
                file=sys.stderr,
            )
            sys.exit(1)
        tmp.replace(dest)
        print(f"        {dest.stat().st_size / 1_048_576:.2f} MB")

    _check_size_gate()


def _check_size_gate() -> None:
    """Fail if total parquet size in public/data/ exceeds MAX_TOTAL_MB."""
    total_bytes: int = sum(
        p.stat().st_size for p in OUTPUT_DIR.glob("*.parquet") if p.is_file()
    )
    total_mb: float = total_bytes / 1_048_576
    print(f"  total {total_mb:.2f} MB / {MAX_TOTAL_MB} MB limit")
    if total_mb > MAX_TOTAL_MB:
        print(
            f"ERROR: parquet data exceeds {MAX_TOTAL_MB} MB limit ({total_mb:.1f} MB).",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download files even if they already exist.",
    )
    args = parser.parse_args()
    pull_data(force=args.force)
