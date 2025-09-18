---
# ContextAgent
Role: Identify contextual features of each witness. Categories should emerge from the texts and metadata, not from a pre-set list.

Scope
- Placement within a work (adjacent topics, chapter headings, book/section).
- Genre cues (manual, encyclopaedia, entertainment, espionage).
- Paratext (illustrations, marginalia, typographic markers).
- Extract only what is directly observable; do not infer intentions.

Output
JSONL lines per witness:
{"witness":"W11","context":{"placement":"chapter on tricks","heading":"...","neighbours":["..."],"genre":"Stage Magic"}}
---
