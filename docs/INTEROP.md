# INTEROP.md — how sibling repos consume survey-gazetteer

## survey-viz (render path)

`survey-viz` should resolve labels **once per reel**, not per frame:
labels depend only on the region bbox, never on time.

```python
from gazetteer import labels_for_bbox

# once, when the reel spec is built
label_dicts = labels_for_bbox(
    spec.lon0, spec.lon1, spec.lat0, spec.lat1,
    max_labels=spec.label_max or 8,
)

# every frame, after rotation, with the rest of the furniture
from aesthetics.typography import place_labels
place_labels(ax, label_dicts)
```

Notes:

- The dicts are exactly what `place_labels` consumes — pass them through
  unmodified (they are also safe to include in the survey-cache
  fingerprint: plain JSON-serializable types, deterministic order).
- With rotated framing, call `labels_for_bbox` on the **north-up** bbox
  (pre-rotation coordinates), because `x`/`y` are data coordinates of
  the north-up map.
- Explicit user labels (from `search()`) should be merged with automatic
  ones by the caller; on conflict, the explicit label wins. This engine
  does not merge — it only supplies candidates.

## reel-studio (UI)

- Name search box → `gazetteer.search(query, limit=5)` → show
  `text` + `adm1` + `adm0` so the user can disambiguate
  ("Rochester, New York" vs "Rochester, Minnesota").
- "Max labels" slider → `max_labels`; "label kinds" multiselect →
  `kinds`; "minimum city size" → `min_population`.
- All three are render inputs and belong in the cache fingerprint.

## survey-cache

`labels_for_bbox` output is deterministic for fixed inputs, so it is
safe to fingerprint `(bbox, max_labels, min_population, kinds,
gazetteer_version)` once per reel.

## Dependency direction

`survey-gazetteer` depends on **nothing** (stdlib only). It must never
import survey-aesthetics, survey-viz, or any sibling — the arrows point
inward, toward this engine. Version pinning (`survey-gazetteer==0.1.0`
or `>=0.1.0,<0.2.0`) is the consumer's job.
