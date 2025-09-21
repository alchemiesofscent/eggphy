Here’s a full revised `README.md` integrating the automated LLM-agent pipeline, the two-phase strategy (stemmatic reduction + phylogenetic analysis), and your Lachmannian + Raggetti criteria. It strips out the older file-structure references and Claude-specific code, and sets the project up for Codex CLI.

---

# Invisible Ink Egg Recipe Phylogeny Project

## Project Overview

This project analyses \~85 historical recipes (1000 CE–2025) that claim one can write on an eggshell with alum and vinegar such that, when boiled, the inscription appears on the egg white. Despite repeated modern failures (ordinary potassium alum does not work), the recipe persisted for nearly two millennia as a “zombie recipe.”

The aim is to reconstruct the transmission history of this recipe tradition by combining classical stemmatic methods with computational phylogenetics.

## Research Questions

1. How did a non-functional technical recipe transmit across time and cultures?
2. What patterns of variation reveal distinct families of transmission?
3. Do procedural and textual features co-vary, or are they subject to different evolutionary pressures?
4. How do structural and contextual shifts (genre, audience, placement) affect transmission?

## Theoretical Framework

* **Witness-based analysis** (each recipe instance = a witness).
* **Phase I**: Lachmannian stemmatic reduction, incorporating Raggetti’s criteria for fluid traditions.
* **Phase II**: Phylogenetic modelling of independent families using procedural, textual, and contextual character matrices.
* **Comparative topology**: Traditional stemma vs. computational trees.

---

## Current Status

* Dataset flattened and merged: `data/witnesses.csv` + `data/witness_meta.csv` → `data/merged_witnesses.csv` (WitnessID, Date, Source, Language, Full_Text, Translation, URL, Note, plus meta fields).
* Chunked inputs for batch processing: `data/chunks/*.csv` (≈10 witnesses per file).
* Languages: Greek, Latin, German, French, Italian, English.
* Git repo and environment configured.
* Recipes grouped in preliminary categories (Geoponica, Porta, Household, Entertainment, Espionage, Internet).
* Modern replications confirm recipe does not work as described.

---

## Methodology: Two-Phase Strategy

### Phase I — Stemmatic Reduction

**Goal**: Collapse redundant copies, identify families, and select representatives.

**Criteria (Raggetti-inspired):**

1. **Structural features (primary):** recipe position (agriculture, magic, kitchen tips, tricks, espionage), chapter/section migration, clustering with other recipes.
2. **Meaningful variants (loci critici):** attribution (Africanus/Porta), similes (“thickness of ink” vs. “honey”), liquid choice (brine vs. vinegar vs. lye), processing differences (days vs. hours, drying methods).
3. **Stylistic formulation (secondary):** imperative vs. descriptive, attributional framing, success claims.
4. **Exclusionary:** ignore orthographic noise, manuscript age, trivial substitutions.

**Outputs:**

* `models/stemma/*.json` — per-chunk arrays of per-witness diagnostic analyses (structural/ingredients/process/linguistic/relationship/confidence). Optionally merged into `models/stemma.json`.
* `models/dedupe_map.json` — collapsed duplicates.
* `models/reps.json` — selected representatives (\~15–20).

### Phase II — Phylogenetic Analysis

**Goal**: Build parallel trees for procedural, textual, and contextual features, and compare to traditional stemma.

**Steps:**

1. **ProcDiscover**: propose procedural characters (ingredients, ratios, steps).
2. **TextDiscover**: propose textual/paratextual characters (attributions, similes, claims).
3. **ContextAgent**: extract strict observable context (book/chapter placement, adjacent recipes, headings).
4. **Synthesizer**: merge near-duplicates, harmonise state spaces.
5. **Coder**: apply approved characters across representatives; back-propagate to collapsed members.
6. **MatrixBuilder**: output three matrices (P.csv, T.csv, C.csv).
7. **TreeBuilder**: generate `.nex` files; run IQ-TREE (MK+ASC) and MrBayes; produce `tree_P.nex`, `tree_T.nex`, `tree_C.nex`, and `stemma_traditional.nex`.
8. **QCReporter**: assess uncertainty, contamination, and topology distances.

---

## Agent System (Claude Code)

Agents are automated via Claude Code; human input occurs only at review checkpoints.

### Agents

* **StemmaAgent** — extracts per-witness diagnostic analyses (structural, loci critici, linguistic features, relationship and contamination signals) used to infer families.
* **Deduper** — collapses direct copies (≥0.98 similarity).
* **RepSelector** — infers families from Stemma analyses and selects representatives; excludes contamination bridges.
* **ProcDiscover** — procedural character discovery.
* **TextDiscover** — textual/paratextual character discovery.
* **ContextAgent** — contextual data extraction.
* **Synthesizer** — merges and normalises proposals.
* **Coder** — systematic coding with evidence snippets.
* **MatrixBuilder** — builds matrices.
* **TreeBuilder** — produces trees and topology comparisons.
* **QCReporter** — reports uncertainty, contamination, missing data.

### CLI Pattern

```
# Phase I
# run over each chunk
## optional: generate a batch plan + manifest
eggphy stemma-batch --in data/chunks --out models/stemma --manifest models/stemma_manifest.json --write-sh
# then run the generated commands in models/stemma_manifest.sh
claude-code @prompts/deduper.md --in data/merged_witnesses.csv --out models/dedupe_map.json
claude-code @prompts/rep_selector.md --in models/stemma --out models/reps.json
## optional: merge all chunk outputs into one file for review
eggphy merge-stemma --in models/stemma --out models/stemma.json

# Phase II
claude-code @prompts/proc_discover.md --in models/reps.json --out models/proc_proposals.jsonl
claude-code @prompts/text_discover.md --in models/reps.json --out models/text_proposals.jsonl
claude-code @prompts/context_agent.md --in models/reps.json --out models/context_proposals.jsonl
claude-code @prompts/synthesizer.md --in models --out models/characters.jsonl
claude-code @prompts/coder.md --in models/characters.jsonl --out output/matrices/{P,T,C}.csv
claude-code @prompts/tree_builder.md --in output/matrices --out output/trees
claude-code @prompts/qc_reporter.md --in output --out reports/qc.html
```

### Command Map

- StemmaBatch: `eggphy stemma-batch --in data/chunks --out models/stemma --manifest models/stemma_manifest.json --write-sh`
- StemmaAgent: `claude-code @prompts/stemma_agent.md --in <chunk.csv> --out <out.json>`
- Deduper: `claude-code @prompts/deduper.md --in data/merged_witnesses.csv --out models/dedupe_map.json`
- RepSelector: `claude-code @prompts/rep_selector.md --in models/stemma --out models/reps.json`
- ProcDiscover: `claude-code @prompts/proc_discover.md --in models/reps.json --out models/proc_proposals.jsonl`
- TextDiscover: `claude-code @prompts/text_discover.md --in models/reps.json --out models/text_proposals.jsonl`
- ContextAgent: `claude-code @prompts/context_agent.md --in models/reps.json --out models/context_proposals.jsonl`
- Synthesizer: `claude-code @prompts/synthesizer.md --in models --out models/characters.jsonl`
- Coder: `claude-code @prompts/coder.md --in models/characters.jsonl --out output/matrices`
- MatrixBuilder: `claude-code @prompts/matrix_builder.md --in output/matrices --out output/matrices`
- TreeBuilder: `claude-code @prompts/tree_builder.md --in output/matrices --out output/trees`
- QCReporter: `claude-code @prompts/qc_reporter.md --in output --out reports/qc.html`

---

## Principles

* **Evidence-based coding:** every 1/0/? decision cites verbatim snippet + locator.
* **Contamination:** marked but not eliminated; bridge witnesses not representatives.
* **Missing data:** drop witnesses with >40% unknown loci critici + absent context.
* **Uncertainty:** code as `?` rather than guess.
* **Weighting:** trees built on family representatives; metadata tracks represented members.

---

## Expected Deliverables

1. **Traditional stemma** (families, representatives, contamination map).
2. **Three character matrices** (procedural, textual, contextual).
3. **Four trees**: stemma, procedural, textual, contextual.
4. **Comparative topology analysis** (RF distances, cophylogeny metrics).
5. **Transmission map** of recipe families and cross-family borrowings.
6. **Stability analysis**: core vs. variable features.

---

## Next Steps

1. Run **StemmaAgent** over all files in `data/chunks/` (or a single test chunk for smoke tests).
2. Review inferred family boundaries; approve representatives.
3. Launch **ProcDiscover** and **TextDiscover** on reps.
4. Merge and code characters.
5. Export matrices and trees.
6. Compare stemma vs. procedural vs. textual topologies.

---

## Web Interface

- Location: `web/index.html` (single-file UI; legacy pages removed)
- Serve: `python -m src.eggphy.cli serve` → http://localhost:8000
- API: `/api/witnesses` returns the web-friendly dataset derived from `data/witnesses.json`
- Static: the server serves assets from `web/` (e.g., `/app.css`, `/app.js`, images)

## Streamlined Data Layout

- Canonical structured JSON (StemmaAgent schema): `data/witnesses.json`
- Flat export for quick editing/viewing: `data/witnesses.csv`
- Raw inputs: `data/raw_sources/witnesses_raw.csv`

## Makefile Shortcuts

- `make status` — show witness count
- `make serve` — start the web UI
- `make data-merge` — merge raw CSV with structured JSON, normalize, update web JSON
- `make schema` — schema presence check on `data/witnesses.json`
- `make scripts` — generate `scripts/phase1.sh` and `scripts/phase2.sh`
