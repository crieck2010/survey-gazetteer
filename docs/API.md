# API.md — function contracts

All public functions are importable from `gazetteer`:

```python
from gazetteer import labels_for_bbox, search, load_places, dataset_info
```

## `labels_for_bbox(lon0, lon1, lat0, lat1, *, max_labels=8, min_population=0, kinds=("city","town"))`

Returns the top-N ranked place labels inside a lon/lat bounding box.

**Parameters**

| name | type | default | meaning |
|---|---|---|---|
| `lon0, lon1` | float | — | longitude bounds. `lon0 > lon1` selects an antimeridian-crossing bbox (e.g. `177, -178` for Fiji) |
| `lat0, lat1` | float | — | latitude bounds; swapped automatically if reversed; clamped to [-90, 90] |
| `max_labels` | int | 8 | maximum labels returned; `0` → `[]` |
| `min_population` | int | 0 | drop places below this POP_MAX |
| `kinds` | sequence | `("city","town")` | kind filter; kinds are `"city"`, `"town"`, `"other"` (see `gazetteer.scoring.kind_of`) |

**Returns**: `list[dict]`, ranked best-first, each dict exactly

```python
{"x": lon, "y": lat, "text": "NAME", "priority": int}
```

This is the schema `survey-aesthetics`' `place_labels(ax, labels)` reads:
`x`/`y` are data coordinates, `text` is the label, `priority` breaks
placement ties (higher wins). No extra keys are ever added — downstream
code may compare dicts for cache keys.

**Ranking**: `(-priority, name)` where `priority` is the documented
formula in `gazetteer/scoring.py`:

```
priority = round(10 * log10(pop + 1)) - 2 * scalerank + (10 if capital else 0)
```

`name` is unique per record, so the sort is a total order:
deterministic for every input (required by survey-cache downstream).

**Edge cases**

- Empty region (no places) → `[]` (never an error).
- Antimeridian: `lon0 > lon1` wraps; a full 360° span (`-180, 180`) queries the whole planet.
- Bounds are inclusive; points on the bbox edge are candidates.

## `search(query, *, limit=5)`

Name lookup for explicit user label requests.

- Case-insensitive; matches `name` (ASCII) and `name_local` (diacritics).
- Prefix matches rank above substring matches, then `(-priority, name)`.
- Returns the `labels_for_bbox` dict **plus** disambiguation context:
  `{"x","y","text","priority","adm0","adm1","kind","pop"}`.
- Blank query or no match → `[]`. Deterministic.

## `load_places()`

All 7,342 bundled `Place` records as an immutable tuple, cached per
process. Fields: `name, name_local, lon, lat, pop, scalerank,
featurecla, adm0, adm1, kind, priority`.

## `dataset_info()`

Provenance dict: dataset name, source URL, pull date, license, record
counts (mirrors `data/PROVENANCE.json` plus `loaded_records`).

## Collision contract (important)

This engine returns **ranked candidates**. Final on-canvas decluttering —
greedy compass-offset placement, dropping labels that fit nowhere —
lives in `survey-aesthetics`' `place_labels` and is intentionally not
duplicated here. To show fewer labels, shrink `max_labels`.
