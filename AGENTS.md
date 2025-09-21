# AGENTS.md — Eggphy (Claude Code)

Project aim
Reconstruct the transmission of the invisible-ink egg recipe via a two-phase workflow: stemmatic reduction followed by phylogenetic analysis. Agents are orchestrated by Claude Code; humans review at checkpoints.

Operating principles
1) Evidence-based coding with verbatim snippets and locators. 2) Contamination marked, not erased; bridge witnesses are not representatives. 3) Uncertainty coded as ?. 4) Representatives carry weights for their collapsed family members. 5) Small commits, reproducible runs.

Data layout
- Input witnesses: data/witnesses.csv + witness_meta.csv (merged as data/merged_witnesses.csv)
- Chunked inputs for batch runs: data/chunks/*.csv (≈10 witnesses per file)
- Models and intermediate state: models/
- Outputs: output/matrices, output/trees, reports/
- Prompts: prompts/*.md

Session defaults (Claude Code)
- model: claude-3.5-sonnet
- approvals: file write, create, and read require confirmation; listing and dry runs allowed

Agents

StemmaBatch
Purpose: Orchestrate iterative runs of StemmaAgent over chunked CSVs and track run status.
Inputs: data/chunks/*.csv, prompts/stemma_agent.md
Outputs: models/stemma/<chunk>.json, models/stemma_manifest.json
Prompt: prompts/stemma_batch.md
Human review: optional (review occurs post-merge)

StemmaAgent
Purpose: Extract per-witness diagnostic analysis (structural, ingredients, process, linguistic, relationship signals) for stemmatic reduction; flag contamination signals.
Inputs: data/chunks/*.csv (run over each chunk); alternatively data/merged_witnesses.csv for small tests
Outputs: models/stemma/*.json (JSON array per chunk); optionally merged models/stemma.json
Prompt: prompts/stemma_agent.md
Human review: required

Deduper
Purpose: Collapse near-duplicates and trivial reprints (threshold ~0.98 similarity).
Inputs: data/merged_witnesses.csv (or data/witnesses.csv during testing)
Outputs: models/dedupe_map.json
Prompt: prompts/deduper.md
Human review: optional

RepSelector
Purpose: Pick 15–20 representatives per family; exclude contamination bridges as reps. Families inferred from StemmaAgent analyses (e.g., structural_variants, ingredients.diagnostic_variants, relationship_analysis).
Inputs: models/stemma/*.json (or merged models/stemma.json), models/dedupe_map.json
Outputs: models/reps.json
Prompt: prompts/rep_selector.md
Human review: required

ProcDiscover
Purpose: Propose procedural characters and state spaces from representatives.
Inputs: models/reps.json
Outputs: models/proc_proposals.jsonl
Prompt: prompts/proc_discover.md
Human review: required

TextDiscover
Purpose: Propose textual and paratextual characters and states.
Inputs: models/reps.json
Outputs: models/text_proposals.jsonl
Prompt: prompts/text_discover.md
Human review: required

ContextAgent
Purpose: Extract strict observable context (placement, headings, adjacency).
Inputs: models/reps.json
Outputs: models/context_proposals.jsonl
Prompt: prompts/context_agent.md
Human review: optional

Synthesizer
Purpose: Merge proposals, normalise states, remove redundancies, harmonise labels.
Inputs: models/*_proposals.jsonl
Outputs: models/characters.jsonl
Prompt: prompts/synthesizer.md
Human review: required

Coder
Purpose: Apply approved characters to witnesses; attach evidence snippets and locators.
Inputs: models/characters.jsonl, models/reps.json, data/merged_witnesses.csv
Outputs: output/matrices/P.csv, T.csv, C.csv
Prompt: prompts/coder.md
Human review: required

MatrixBuilder
Purpose: Validate matrices, handle missing data thresholds, export final CSV and NEXUS.
Inputs: output/matrices/*.csv
Outputs: output/matrices/*.nex
Prompt: prompts/matrix_builder.md
Human review: optional

TreeBuilder
Purpose: Build trees with IQ-TREE (MK+ASC) and MrBayes; export NEXUS and logs.
Inputs: output/matrices/*.nex (optional: models/stemma*.json for exporting traditional stemma if available)
Outputs: output/trees/tree_P.nex, tree_T.nex, tree_C.nex, stemma_traditional.nex
Prompt: prompts/tree_builder.md
Human review: optional

QCReporter
Purpose: Summarise uncertainty, contamination, and topology distances; RF metrics and cophylogeny notes.
Inputs: output/trees, output/matrices, models/stemma/*.json (derive contamination summary from relationship_analysis)
Outputs: reports/qc.html
Prompt: prompts/qc_reporter.md
Human review: optional

Command invocations
- For up-to-date exec-style commands, see README “Command Map”.

Pipelines

Phase I — stemmatic reduction
0) Optional plan: eggphy stemma-batch --in data/chunks --out models/stemma --manifest models/stemma_manifest.json --write-sh
1) For each CSV in data/chunks: claude-code @prompts/stemma_agent.md --in data/chunks/<file>.csv --out models/stemma/<file>.json
2) claude-code @prompts/deduper.md --in data/merged_witnesses.csv --out models/dedupe_map.json
3) claude-code @prompts/rep_selector.md --in models/stemma --out models/reps.json
Checkpoint: review inferred families, contamination flags, and representatives

Phase II — phylogenetic analysis
4) claude-code @prompts/proc_discover.md --in models/reps.json --out models/proc_proposals.jsonl
5) claude-code @prompts/text_discover.md --in models/reps.json --out models/text_proposals.jsonl
6) claude-code @prompts/context_agent.md --in models/reps.json --out models/context_proposals.jsonl
7) claude-code @prompts/synthesizer.md --in models --out models/characters.jsonl
8) claude-code @prompts/coder.md --in models/characters.jsonl --out output/matrices
9) claude-code @prompts/matrix_builder.md --in output/matrices --out output/matrices
10) claude-code @prompts/tree_builder.md --in output/matrices --out output/trees
11) claude-code @prompts/qc_reporter.md --in output --out reports/qc.html
Checkpoint: approve character set, coding, matrices, and tree builds

Approvals policy
- Allowed without prompt: list files, dry-run analyses, reading prompts and data.
- Requires approval: creating or modifying files in prompts/, models/, output/, reports/.
- Disallowed: network access and executing non-declared binaries.

File conventions
- Proposals: JSON Lines with schema {character_id, label, states[], rationale, evidence_refs[]}
- Evidence: verbatim up to 40 words with locator; multi-language supported; store minimal necessary snippet
- Unknown: use ?; do not impute across languages or epochs
- Thresholds: drop witnesses with more than 40% unknown loci critici and missing context

Review checklist
- Families are coherent on structural features before loci critici
- Representatives exclude contamination bridges
- Characters are independent, observable, and non-redundant
- Matrices pass validation; ascertainment correction set where needed
- Trees reproducible with fixed seeds; logs archived

Notes for first-time run
- For a quick smoke test, use the two-row test CSV and run through steps 1–3 and 4, 7, 8, 10, 11
- Expand to full dataset only after prompts are finalised
