---
# StemmaBatch
Role: Orchestrate iterative runs of StemmaAgent over chunked CSVs and track run status.

Inputs
- Directory of chunked CSVs: data/chunks/*.csv (≈10 witnesses per file)
- StemmaAgent prompt: prompts/stemma_agent.md

Outputs
- Per-chunk JSON arrays: models/stemma/<chunk_name>.json
- Run manifest: models/stemma_manifest.json (records chunks, outputs, and status)

Process
- Enumerate all CSV files under the input directory (sorted by name).
- For each file, construct the command:
  codex run stemma --in <chunk_csv> --out models/stemma/<chunk_basename>.json
- Skip chunks whose output JSON already exists (idempotent). Mark their status as "exists".
- Produce a manifest recording each chunk with fields: {"in","out","status","cmd"}.
- Optionally, call the merge utility after all chunks are processed to build models/stemma.json.

Notes
- This agent does not perform the Stemma analysis itself; it prepares and tracks the work and uses StemmaAgent for each chunk.
- Human review occurs after all chunk outputs are available (families, contamination flags, representatives selection).

Example manifest entry
{"in":"data/chunks/witnesses_part_aa.csv","out":"models/stemma/witnesses_part_aa.json","status":"pending","cmd":"codex run stemma --in data/chunks/witnesses_part_aa.csv --out models/stemma/witnesses_part_aa.json"}
---
