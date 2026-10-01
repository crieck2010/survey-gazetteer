# ARCHITECTURE.md — module layout and design decisions

```
src/gazetteer/
    __init__.py     public API: labels_for_bbox, search, load_places,
                    dataset_info, kind_of, priority_of, DEFAULT_KINDS
    api.py          selection + search (the consumer contract)
    places.py       Place dataclass, CSV loading via importlib.resources
    index.py        5° x 5° grid spatial index (cached per process)
    scoring.py      priority formula + kind classification
    data/
        places.csv      7,342 records (see docs/DATA.md)
        PROVENANCE.json dataset provenance
scripts/
    fetch_places.py re-pull upstream Natural Earth, rebuild data/
tests/
    test_places.py  dataset integrity, no-network-at-runtime
    test_scoring.py priority formula + kind mapping
    test_api_bbox.py bbox selection, ranking, determinism, edge cases
    test_api_search.py name search
```

## Why a grid index, not a scan

7,342 points × a per-frame cost would be fine once per reel, but the
index makes bbox queries O(candidates) and documents the intent: this
engine is meant to stay fast if the dataset ever grows 10-100x
(e.g. a 1:50m + GeoNames hybrid). Build cost is one pass at import;
query cost is O(cells overlapped) dict lookups plus O(candidates)
point-in-bbox tests. For a regional reel bbox that is a few dozen
point tests.

## Why priority is computed at load, not stored

The formula is the documented contract (`scoring.py` + `docs/API.md`).
Computing it at load keeps one source of truth: a CSV refresh can never
silently ship stale scores, and the formula's unit tests guard the
contract directly.

## Determinism

- Sort key `(-priority, name)` is a total order (names unique) → every
  query is deterministic.
- No RNG, no dict-ordering dependence, no network.
- survey-cache can therefore fingerprint label inputs safely.

## Known limits (v0.1.0)

- 1:10m resolution: villages and neighborhoods are absent. A bbox over
  open ocean or deep wilderness returns few or no labels — by design,
  not an error.
- Labels are English/ASCII (`NAMEASCII`); `name_local` keeps diacritics
  for search only.
- No population for ~some small places (POP_MAX = 0): they rank by
  scalerank alone and are filtered by `min_population > 0`.
- Search is substring/prefix over 7,342 names — linear scan, ~1 ms.
  Fine at this scale; would need an index at 100x.
