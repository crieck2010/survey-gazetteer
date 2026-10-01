# survey-gazetteer

Offline place-label engine for Charlie's remote-sensing reel stack. Bundles
Natural Earth 1:10m populated places (7,342 records) and selects ranked
city/town labels for any region bounding box — in exactly the format
`survey-aesthetics`' `place_labels` consumes.

Stdlib only. No network at runtime. Deterministic: same bbox + params →
same labels, every time.

## Why

The mapped.earth reference reels carry minimal city labels — small type +
dot markers (KINGSTON, OSWEGO, ROCHESTER on the Lake Ontario reel).
`survey-aesthetics` v0.1.0 can *draw* those labels and `survey-viz`
v0.22.0 calls it, but there was no dataset or selection logic behind it.
This repo fills that gap.

## Install

```bash
pip install git+https://github.com/crieck2010/survey-gazetteer@v0.1.0
```

## Quick start

```python
from gazetteer import labels_for_bbox, search

# Lake Ontario, like the reference reel
labels = labels_for_bbox(-80.5, -76.0, 43.0, 44.6, max_labels=8)
# -> [{"x": -79.39, "y": 43.66, "text": "Toronto", "priority": 75}, ...]

# Straight into the aesthetics engine:
from aesthetics.typography import place_labels
place_labels(ax, labels)

# Name lookup (for explicit user label requests)
search("Rochester", limit=5)
# -> Rochester, United States of America, New York (pop 755,000) ...
```

## API

- `labels_for_bbox(lon0, lon1, lat0, lat1, *, max_labels=8, min_population=0, kinds=("city","town"))` — ranked candidates inside the bbox. `lon0 > lon1` selects an antimeridian-crossing bbox. Empty region → `[]`.
- `search(query, *, limit=5)` — case-insensitive name lookup with `adm0`/`adm1` disambiguation context.
- `load_places()` / `dataset_info()` — the bundled records and their provenance.

Priority formula (stable contract): `round(10·log10(pop+1)) − 2·scalerank + 10 if capital`.
See `docs/API.md` for the full contract, `docs/DATA.md` for the dataset.

## Contract notes

- **Output schema is fixed**: `{"x": lon, "y": lat, "text": "NAME", "priority": int}` — exactly what `place_labels` reads. Extra keys are never added to `labels_for_bbox` output.
- **Ranked candidates only**: final on-canvas decluttering stays in `survey-aesthetics`' `place_labels` (greedy compass-offset placement). This engine does not duplicate it.
- **Call once per reel**: labels depend on the region bbox, not on time. `survey-viz` should call `labels_for_bbox` once per reel and reuse the list for every frame.

## Interop

See `docs/INTEROP.md` for the survey-viz / reel-studio call patterns.

## Docs

- `docs/DATA.md` — dataset source, license, refresh procedure
- `docs/API.md` — full function contracts
- `docs/ARCHITECTURE.md` — module layout, index design, determinism notes
- `docs/INTEROP.md` — how sibling repos consume this engine

## Updating the dataset

```bash
python3 scripts/fetch_places.py   # re-pulls Natural Earth, rebuilds data/places.csv
```

## License

MIT — see `LICENSE`. The bundled Natural Earth data is public domain
(see `docs/DATA.md`).
