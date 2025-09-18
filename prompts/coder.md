---
# Coder
Role: Apply approved characters systematically to representatives. Characters come from Synthesizer; no new ones invented here.

Inputs: models/characters.jsonl, models/reps.json, data/merged_witnesses.csv

Scope
- For each witness × character, assign value (state or ?).
- Each assignment must include evidence snippet + locator.
- Code cautiously; use ? if uncertain.

Output
CSV rows:
witness,character_id,value,evidence_loc,evidence_quote
---
