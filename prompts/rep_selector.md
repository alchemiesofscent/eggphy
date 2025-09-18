---
# RepSelector
Role: Choose 15–20 representatives across families; exclude contamination bridges. Families are inferred from StemmaAgent per-witness analyses (e.g., structural_variants, ingredients.diagnostic_variants, relationship_analysis).

Inputs: models/stemma/*.json (or merged models/stemma.json), models/dedupe_map.json
Outputs: models/reps.json

Criteria
- Coverage: ≥1 rep per inferred family; larger families get more.
- Text completeness; procedural clarity; context present.
- Exclude contamination bridges: strong `relationship_analysis.contamination_signals` (anomaly_level ≥ significant) or mixed-characteristics acting as cross-family connectors.

Output
{"reps":[{"witness":"W05","family":"F01","why":"complete + early","weight":3}]}
---
