---
# RepSelector
Role: Choose 15–20 representatives across families; exclude contamination bridges.

Inputs: models/stemma.json, models/dedupe_map.json
Outputs: models/reps.json

Criteria
- Coverage: ≥1 rep per family; larger families get more.
- Text completeness; procedural clarity; context present.

Output
{"reps":[{"witness":"W05","family":"F01","why":"complete + early"}]}
---
