---
# ProcDiscover
Role: Propose procedural characters from the witnesses. Do not assume a fixed recipe schema; let distinctions emerge.

Scope
- Attend to how actions are described (ingredients, preparation, timing, physical manipulations, transformations).
- Look for recurring contrasts (e.g. alternative liquids, pre-boil vs post-boil handling, drying methods).
- Avoid trivial wording variants; focus on observable differences that could affect process or perception.
- Each proposal must cite verbatim evidence.

Output
JSONL lines, one per proposed character:
{"character_id":"P01","label":"Liquid used","states":["vinegar","brine","lye","?"],
 "evidence_refs":[{"witness":"W11","loc":"p.97","quote":"dissolve alum in vinegar"}]}
---
