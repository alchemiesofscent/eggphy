#!/usr/bin/env bash
set -euo pipefail

echo "=== EGGPHY AUTOMATED PIPELINE ==="
echo "This will run the full stemma analysis pipeline with automated review checkpoints"
echo

# Activate virtual environment
source .venv/bin/activate

echo "Phase I: Stemmatic Analysis"
echo "=========================="

# Step 1: Generate stemma batch manifest (already done, but ensuring it's current)
echo "1. Generating stemma batch manifest..."
eggphy stemma-batch --in data/chunks --out models/stemma --manifest models/stemma_manifest.json --write-sh
echo "✓ Manifest created: models/stemma_manifest.sh"
echo

# Step 2: Run stemma analysis on all chunks
echo "2. Running stemma analysis on all chunks..."
echo "   This analyzes ~85 recipes across 9 chunks..."
bash models/stemma_manifest.sh
echo "✓ Stemma analysis complete"
echo

# Review checkpoint 1
echo "REVIEW CHECKPOINT 1: Stemma Analysis Results"
echo "============================================="
echo "Results saved in models/stemma/"
echo "Press ENTER to review results and continue, or Ctrl+C to stop..."
read -r

# Step 3: Merge stemma outputs for easier review
echo "3. Merging stemma outputs..."
eggphy merge-stemma --in models/stemma --out models/stemma.json
echo "✓ Merged stemma analysis: models/stemma.json"
echo

# Step 4: Run deduplication
echo "4. Running deduplication analysis..."
claude @prompts/deduper.md data/merged_witnesses.csv -p --output-format json > models/dedupe_map.json
echo "✓ Deduplication complete: models/dedupe_map.json"
echo

# Step 5: Select representatives
echo "5. Selecting representative witnesses..."
claude @prompts/rep_selector.md models/stemma -p --output-format json > models/reps.json
echo "✓ Representatives selected: models/reps.json"
echo

# Review checkpoint 2
echo "REVIEW CHECKPOINT 2: Family Representatives"
echo "==========================================="
echo "Representatives saved in models/reps.json"
echo "Please review the selected families and representatives."
echo "Press ENTER to continue to Phase II, or Ctrl+C to stop..."
read -r

echo
echo "Phase II: Phylogenetic Analysis"
echo "==============================="

# Step 6: Character discovery
echo "6. Running character discovery..."
echo "   6a. Procedural character discovery..."
claude @prompts/proc_discover.md models/reps.json -p --output-format json > models/proc_proposals.jsonl
echo "   6b. Textual character discovery..."
claude @prompts/text_discover.md models/reps.json -p --output-format json > models/text_proposals.jsonl
echo "   6c. Contextual character discovery..."
claude @prompts/context_agent.md models/reps.json -p --output-format json > models/context_proposals.jsonl
echo "✓ Character discovery complete"
echo

# Step 7: Synthesize characters
echo "7. Synthesizing character proposals..."
claude @prompts/synthesizer.md models -p --output-format json > models/characters.jsonl
echo "✓ Character synthesis complete: models/characters.jsonl"
echo

# Review checkpoint 3
echo "REVIEW CHECKPOINT 3: Character Matrix"
echo "===================================="
echo "Proposed characters saved in models/characters.jsonl"
echo "Please review the character proposals before coding."
echo "Press ENTER to continue to matrix building, or Ctrl+C to stop..."
read -r

# Step 8: Code characters into matrices
echo "8. Coding characters into matrices..."
mkdir -p output/matrices
claude @prompts/coder.md models/characters.jsonl -p --output-format json > output/matrices/coding_result.json
echo "✓ Character coding complete: output/matrices/"
echo

# Step 9: Build trees
echo "9. Building phylogenetic trees..."
mkdir -p output/trees
claude @prompts/tree_builder.md output/matrices -p --output-format json > output/trees/tree_result.json
echo "✓ Tree building complete: output/trees/"
echo

# Step 10: Generate QC report
echo "10. Generating quality control report..."
mkdir -p reports
claude @prompts/qc_reporter.md output -p > reports/qc.html
echo "✓ QC report complete: reports/qc.html"
echo

echo "=== PIPELINE COMPLETE ==="
echo "Results:"
echo "- Traditional stemma: models/stemma.json"
echo "- Representatives: models/reps.json"
echo "- Character matrices: output/matrices/"
echo "- Phylogenetic trees: output/trees/"
echo "- QC report: reports/qc.html"
echo
echo "Open reports/qc.html in a browser to view the final analysis."