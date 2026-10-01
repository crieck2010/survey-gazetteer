# Changelog

All notable changes to this project are documented here. Semantic versioning.

## [0.1.0] - 2026-10-01

Initial release.

### Added
- Bundled dataset: Natural Earth 1:10m populated places, 7,342 records
  (`src/gazetteer/data/places.csv`, ~605 KB), public domain, with
  machine-readable provenance (`PROVENANCE.json`, `gazetteer.dataset_info()`).
- `labels_for_bbox(lon0, lon1, lat0, lat1, *, max_labels=8, min_population=0,
  kinds=("city","town"))` — ranked label candidates in exactly the schema
  survey-aesthetics' `place_labels` consumes (`x`/`y`/`text`/`priority`).
- `search(query, *, limit=5)` — case-insensitive name lookup with
  adm0/adm1 disambiguation context.
- Priority formula: `round(10·log10(pop+1)) − 2·scalerank + 10 if capital`
  (documented stable contract); kind mapping (city/town/other).
- 5°×5° grid spatial index; antimeridian-crossing bboxes supported;
  empty region → `[]`.
- `scripts/fetch_places.py` — reproducible dataset refresh from upstream.
- 34 pytest tests; stdlib-only runtime, no network.
