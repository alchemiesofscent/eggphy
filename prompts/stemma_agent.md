# prompts/stemma_agent.md

System role: build families using structural features first, then loci critici; mark contamination; output a traditional stemma artefact.

## Inputs
- CSV rows from `data/recipes.csv` as JSON array.
- Optional: previous `stemma.json` for incremental runs.

## Do
1. For each witness, extract:
   - placement_context: where in source (agriculture/fowl; natural magic/secret writing; household tips; entertainment/tricks; espionage/manual; internet/DIY; unknown).
   - recipe_architecture: separate methods vs merged; hierarchical vs flat; attribution positions.
   - loci_critici: africanus_attribution, simile_ink_vs_honey, liquid_variant (muria/brine, vinegar, lye), timing (days/hours/none), drying (sun/heat/none), egg_state (raw/preboiled/unknown).
   - stylistic: voice (imperative/descriptive), success_claim (assertive/cautious/negative/none).
2. Cluster into families prioritising structural similarity; refine with loci critici; mark likely contamination edges.
3. Produce families, edges, contamination.

## Output (JSON)
```json
{
  "families": [
    {
      "family_id": "F01",
      "label": "Agricultural/Geoponica-like",
      "members": ["W01", "W03"],
      "centroid_features": {}
    }
  ],
  "contamination": [
    {"from": "W05", "to": "F01", "evidence": "borrows Africanus formula"}
  ],
  "edges": [
    {"parent": "F01", "child": "F03", "type": "inferred"}
  ],
  "witness_features": {
    "W01": {},
    "W02": {}
  }
}
