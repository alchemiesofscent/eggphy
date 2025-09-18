---
# Deduper
Role: Collapse trivial reprints and near-duplicates.

Inputs: data/merged_witnesses.csv (or data/witnesses.csv during testing)
Outputs: models/dedupe_map.json

Do
- Compute similarity over normalized text (lowercase, strip punctuation, collapse whitespace).
- Threshold: 0.98 => duplicate.
- Prefer earliest edition as canonical member.

Output
{"map":[{"keep":"W05","drop":["W05a","W05b"],"reason":"98.7% similarity"}]}
---
