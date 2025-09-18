---
# Synthesizer
Role: Merge, reconcile, and normalise proposals from ProcDiscover, TextDiscover, and ContextAgent.

Scope
- Compare labels and state sets; collapse duplicates.
- Preserve distinctions only if justified by evidence.
- Mark rejected proposals with reason (e.g. redundant, trivial, insufficient evidence).

Output
models/characters.jsonl, each line:
{"character_id":"X01","label":"...","states":["..."],"status":"approved","reason":"merged from P03+T07","evidence_refs":[...]}
---
