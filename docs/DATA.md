# DATA.md — the bundled place dataset

## What is bundled

`src/gazetteer/data/places.csv` — 7,342 populated places extracted from
Natural Earth's 1:10m populated-places layer, one row per place:

| column | meaning |
|---|---|
| `name` | NAMEASCII — ASCII label text drawn on the map |
| `name_local` | NAME — local spelling with diacritics, for search matching |
| `lon`, `lat` | WGS84 coordinates |
| `pop` | POP_MAX (best available population estimate) |
| `scalerank` | 0 (most important) .. 10 (least) — Natural Earth's own importance rank |
| `featurecla` | FEATURECLA verbatim (e.g. "Admin-0 capital", "Populated place") |
| `adm0` | country (for search disambiguation) |
| `adm1` | region / state (for search disambiguation) |

Size: ~605 KB. Loaded once per process via `importlib.resources`; no
network access at runtime (asserted by `tests/test_places.py`).

## Provenance (this release)

- dataset: Natural Earth 1:10m populated places
- source: https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_populated_places.geojson
- pulled_utc: 2026-10-01T00:31:16Z
- license: Public domain (Natural Earth) — https://www.naturalearthdata.com/about/terms-of-use/
- upstream_features: 7342
- kept_records: 7342
- skipped_records: 0
- note: sha256 of the downloaded GeoJSON verified byte-identical to the upstream file.

Machine-readable copy: `src/gazetteer/data/PROVENANCE.json`; exposed at
runtime via `gazetteer.dataset_info()`.

## Refresh procedure

```bash
python3 scripts/fetch_places.py [--input local.geojson]
```

The script re-downloads the upstream GeoJSON, re-extracts the columns
above, rewrites `places.csv` + `PROVENANCE.json`, and prints a provenance
block to paste into this file. The priority formula lives in
`src/gazetteer/scoring.py` (computed at load, not stored), so a data
refresh never silently changes ranking semantics — but the formula is a
documented stable contract, so a refresh that changes outputs should
still ship as a minor version bump with a CHANGELOG note.

## Design notes

- **Why 1:10m and not 1:50m**: the 10m layer has ~7k places vs ~1.2k at
  50m — dense enough for regional reels (Lake Ontario shows 8 sensible
  labels from this layer; 50m would show ~2).
- **Why CSV, not the 19 MB GeoJSON**: only 9 fields of ~130 are needed;
  CSV is stdlib-readable with zero dependencies and loads in milliseconds.
- **Why ASCII labels**: the reference reels set labels in ASCII caps
  (KINGSTON, OSWEGO); `name` is ASCII-safe for DejaVu/matplotlib text.
  `name_local` preserves diacritics for search.
