#!/usr/bin/env python3
"""Re-pull the Natural Earth 1:10m populated-places dataset and rebuild
``src/gazetteer/data/places.csv``.

This is a BUILD-TIME script (network allowed). The engine itself
(``src/gazetteer/``) is stdlib-only and never touches the network at
runtime: it reads the bundled CSV via ``importlib.resources``.

Usage:
    python3 scripts/fetch_places.py [--input path/to/ne_10m_populated_places.geojson]

Default source: the official natural-earth-vector GeoJSON mirror on GitHub.

The script prints a provenance block — paste it into ``docs/DATA.md``
(and it is also saved as ``src/gazetteer/data/PROVENANCE.json``).
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import sys
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA_DIR = REPO / "src" / "gazetteer" / "data"
OUT_CSV = DATA_DIR / "places.csv"
OUT_PROVENANCE = DATA_DIR / "PROVENANCE.json"

SOURCE_URL = (
    "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/"
    "master/geojson/ne_10m_populated_places.geojson"
)

# Fields we keep, in CSV column order.
COLUMNS = (
    "name",        # NAMEASCII (falls back to NAME) — label text
    "name_local",  # NAME — for search matching incl. diacritics
    "lon",
    "lat",
    "pop",         # POP_MAX
    "scalerank",   # SCALERANK (0 = most important .. 10 = least)
    "featurecla",  # FEATURECLA verbatim
    "adm0",        # ADM0NAME — country, for search context
    "adm1",        # ADM1NAME — region, for search context
)


def _num(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _fnum(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def extract(features):
    rows = []
    skipped = 0
    for feat in features:
        props = feat.get("properties") or {}
        geom = feat.get("geometry") or {}
        coords = geom.get("coordinates") or []
        if len(coords) < 2:
            skipped += 1
            continue
        lon, lat = _fnum(coords[0]), _fnum(coords[1])
        name = props.get("NAMEASCII") or props.get("NAME") or ""
        if not name:
            skipped += 1
            continue
        rows.append(
            {
                "name": str(name).strip(),
                "name_local": str(props.get("NAME") or "").strip(),
                "lon": lon,
                "lat": lat,
                "pop": _num(props.get("POP_MAX")),
                "scalerank": _num(props.get("SCALERANK"), 10),
                "featurecla": str(props.get("FEATURECLA") or ""),
                "adm0": str(props.get("ADM0NAME") or ""),
                "adm1": str(props.get("ADM1NAME") or ""),
            }
        )
    return rows, skipped


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=None, help="local GeoJSON file (skips download)")
    args = ap.parse_args()

    if args.input:
        src = Path(args.input)
        raw = src.read_bytes()
        source = f"local file: {src}"
    else:
        req = urllib.request.Request(SOURCE_URL, headers={"User-Agent": "survey-gazetteer/0.1.0"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read()
        source = SOURCE_URL

    doc = json.loads(raw.decode("utf-8"))
    features = doc.get("features", [])
    rows, skipped = extract(features)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)

    provenance = {
        "dataset": "Natural Earth 1:10m populated places",
        "source": source,
        "pulled_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "license": "Public domain (Natural Earth)",
        "license_url": "https://www.naturalearthdata.com/about/terms-of-use/",
        "upstream_features": len(features),
        "kept_records": len(rows),
        "skipped_records": skipped,
        "columns": list(COLUMNS),
    }
    OUT_PROVENANCE.write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")

    print(f"records: {len(rows)} kept, {skipped} skipped (of {len(features)} upstream)")
    print(f"wrote: {OUT_CSV.relative_to(REPO)} ({OUT_CSV.stat().st_size / 1024:.0f} KB)")
    print(f"wrote: {OUT_PROVENANCE.relative_to(REPO)}")
    print()
    print("--- provenance block for docs/DATA.md ---")
    for k, v in provenance.items():
        print(f"- {k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
