"""Lake Ontario labels, reference-reel style."""

from gazetteer import dataset_info, labels_for_bbox, search

info = dataset_info()
print(f"{info['loaded_records']} places "
      f"({info['dataset']}, pulled {info['pulled_utc'][:10]})")

print("\nLake Ontario bbox, max 8 labels:")
for lab in labels_for_bbox(-80.5, -76.0, 43.0, 44.6, max_labels=8):
    print(f"  {lab['text']:15s} priority={lab['priority']:3d} "
          f"({lab['x']:.2f}, {lab['y']:.2f})")

print("\nSearch 'Rochester':")
for hit in search("Rochester", limit=3):
    print(f"  {hit['text']}, {hit['adm1']}, {hit['adm0']} "
          f"(pop {hit['pop']:,}, priority {hit['priority']})")

print("\nAntimeridian bbox (Fiji):")
for lab in labels_for_bbox(177.0, -178.0, -19.0, -16.0, max_labels=3):
    print(f"  {lab['text']:15s} priority={lab['priority']}")
