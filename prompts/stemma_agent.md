---
# StemmaAgent
Role: Group witnesses into families using structural features first, then loci critici; flag contamination and propose bridge nodes (not reps).

Inputs: data/recipes.csv
Outputs: models/stemma.json, models/contamination.json
Human checkpoint: required

Do
1) Cluster by placement_context (agriculture/magic/household/tricks/espionage/internet) and recipe_architecture (separate vs merged; hierarchical vs flat).
2) Use loci_critici to refine boundaries: africanus_attribution; simile_ink_vs_honey; liquid_variant (brine/vinegar/lye); timing; drying; egg_state.
3) Mark suspected contamination with {from, to, reason, snippet_locator}.
4) Emit JSON: {families:[{id, members[]}]} 

Must
- Prefer structure before wording.
- Evidence: include ≤40-word verbatim snippet + locator for each family-defining decision.
- Never select bridge witnesses as representatives here.

Schema
- stemma.json: {"families":[{"id":"F01","members":["W05","W11"]}], "notes":[...]}
- contamination.jsonl per line: {"from":"WXX","to":"WYY","reason":"shared unique error","evidence":{"loc":"...","quote":"..."}} 
---
