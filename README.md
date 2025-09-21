# 🥚 Historical Egg Writing Recipes: Phylogenetic Analysis

**A Digital Humanities Study of "Invisible Ink" Recipe Transmission (1000-2025 CE)**

[![GitHub Pages](https://img.shields.io/badge/Live%20Site-alchemiesofscent.github.io%2Feggphy-blue)](https://alchemiesofscent.github.io/eggphy/)
[![Dataset](https://img.shields.io/badge/Dataset-JSON%2FCSV-green)](https://alchemiesofscent.github.io/eggphy/data/witnesses.json)
[![License](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey)](https://creativecommons.org/licenses/by/4.0/)

---

## 📖 Project Overview

This project reconstructs the transmission history of ~85 historical recipes claiming you can write on an eggshell with alum and vinegar such that, when boiled, the inscription appears on the egg white. Despite repeated modern failures (ordinary potassium alum does not work), this "zombie recipe" persisted for nearly two millennia across cultures and languages.

**Research Approach**: Combines classical stemmatic methods with computational phylogenetics to trace how non-functional technical knowledge spreads and evolves through cultural transmission.

**🌐 [Explore the Interactive Database →](https://alchemiesofscent.github.io/eggphy/)**

---

## 🔬 Research Questions

1. **Transmission Mechanisms**: How did a non-functional technical recipe transmit across time and cultures?
2. **Family Patterns**: What patterns of variation reveal distinct families of transmission?
3. **Feature Evolution**: Do procedural and textual features co-vary, or are they subject to different evolutionary pressures?
4. **Contextual Influence**: How do structural and contextual shifts (genre, audience, placement) affect transmission?

---

## 📊 Dataset Highlights

- **Temporal Span**: 1000 CE to 2025 CE (Byzantine to Internet era)
- **Languages**: Greek, Latin, German, French, Italian, English, and others
- **Sources**: Agricultural manuals, magic texts, household guides, entertainment books, internet forums
- **Witnesses**: ~85 recipe instances with detailed provenance and analysis
- **Geographic Spread**: European, North American, and digital transmission

### 🏛️ Historical Significance

This represents one of the longest-documented cases of persistent non-functional technical knowledge, offering unique insights into:
- Pre-modern technology transfer
- Authority and credibility in technical communication
- Cultural adaptation of technical instructions
- Digital-age transformation of historical claims

---

## 🧬 Methodology: Stemmatic + Phylogenetic Analysis

### Phase I: Stemmatic Reduction

**Goal**: Identify family relationships and collapse redundant copies using Lachmannian methods adapted for fluid textual traditions (following Raggetti's criteria).

**Key Features Analyzed**:
- **Structural placement**: Agricultural vs. magical vs. entertainment contexts
- **Critical variants**: Attribution (Africanus/Porta), liquid choice (vinegar/brine/lye), timing variations
- **Textual formulations**: Imperative vs. descriptive style, success claims, similes
- **Contamination patterns**: Cross-family borrowing and hybrid witnesses

**Current Progress**: ✅ Completed
- 7 major family groups identified (A-G)
- Diagnostic variant analysis complete
- Representative witnesses selected

### Phase II: Phylogenetic Modeling

**Goal**: Build parallel evolutionary trees for procedural, textual, and contextual features using computational phylogenetics.

**Approach**:
1. **Character Discovery**: Automated extraction of diagnostic features using LLM agents
2. **Matrix Construction**: Three parallel matrices (procedural, textual, contextual)
3. **Tree Building**: IQ-TREE and MrBayes analysis with appropriate evolutionary models
4. **Topology Comparison**: Traditional stemma vs. computational trees

**Current Status**: 🚧 In Progress
- Character discovery phase active
- Preliminary family classifications validated
- Matrix construction beginning

---

## 🛠️ Technical Architecture

### Automated Analysis Pipeline

```bash
# Phase I: Stemmatic Analysis (completed)
eggphy stemma-batch --in data/chunks --out models/stemma
claude-code @prompts/deduper.md --in data/witnesses.json --out models/dedupe_map.json
claude-code @prompts/rep_selector.md --in models/stemma --out models/reps.json

# Phase II: Phylogenetic Analysis (in progress)
claude-code @prompts/proc_discover.md --in models/reps.json --out models/proc_proposals.jsonl
claude-code @prompts/text_discover.md --in models/reps.json --out models/text_proposals.jsonl
claude-code @prompts/context_agent.md --in models/reps.json --out models/context_proposals.jsonl
claude-code @prompts/synthesizer.md --in models --out models/characters.jsonl
claude-code @prompts/coder.md --in models/characters.jsonl --out output/matrices
claude-code @prompts/tree_builder.md --in output/matrices --out output/trees
```

### Data Structure

- **Primary Dataset**: `data/witnesses.json` (structured JSON with full metadata)
- **Tabular Export**: `data/witnesses.csv` (researcher-friendly format)
- **Raw Sources**: `data/raw_sources/` (original transcriptions and metadata)
- **Analysis Models**: `models/stemma/` (family classifications and diagnostic features)

---

## 🌐 Interactive Visualizations

### [Recipe Explorer](https://alchemiesofscent.github.io/eggphy/)
- Advanced filtering by century, language, genre, ingredients
- Full-text search across historical sources
- Confidence scoring and uncertainty tracking
- Downloadable data in multiple formats

### [Stemma Codicum Viewer](https://alchemiesofscent.github.io/eggphy/stemma/stemma.html)
- Interactive family tree visualization
- Collapsible navigation from archetype to individual witnesses
- Timeline view with chronological zoom controls
- Color-coded family classifications

### [Family Tree Analysis](https://alchemiesofscent.github.io/eggphy/stemma/tree.html)
- Hierarchical witness relationships
- Diagnostic variant highlighting
- Cross-family contamination patterns
- Evidence-based relationship scoring

---

## 📚 Current Research Findings

### Family Classifications (Preliminary)

- **Family A (Classical)**: Gall + alum tradition, Byzantine/Medieval origins
- **Family B (Long-Soak)**: Multi-day soaking innovations, Northern European
- **Family C (Modern)**: Simplified alum-only versions, 18th-20th century
- **Family D (Salt-Water-Boil)**: Direct salt water processing variants
- **Family E (Meta-Witnesses)**: Commentary and discussion texts
- **Family F (Anomalous)**: Boil-then-write procedural variants
- **Family G (Cépak)**: Quantified measurements, modern systematization

### Key Insights

1. **Persistence Mechanism**: Recipe authority derives from attribution chains (Africanus → Porta → modern sources)
2. **Adaptation Patterns**: Procedural simplification over time, but core claims remain unchanged
3. **Cultural Translation**: Different contexts (agriculture → magic → entertainment) maintain functional claims
4. **Modern Transformation**: Internet era shows both preservation and skeptical commentary

---

## 📊 Data Access & API

### Public Dataset
- **Complete JSON**: [witnesses.json](https://alchemiesofscent.github.io/eggphy/data/witnesses.json)
- **CSV Export**: [witnesses.csv](https://alchemiesofscent.github.io/eggphy/data/witnesses.csv)
- **API Endpoint**: `https://alchemiesofscent.github.io/eggphy/data/witnesses.json`

### Usage Example
```javascript
// Fetch all recipe data
fetch('https://alchemiesofscent.github.io/eggphy/data/witnesses.json')
  .then(response => response.json())
  .then(recipes => {
    // Analysis code here
    console.log(`Found ${recipes.length} historical recipes`);
  });
```

---

## 🧪 Development & Local Usage

### Quick Start
```bash
# Clone repository
git clone https://github.com/alchemiesofscent/eggphy.git
cd eggphy

# Install dependencies
pip install -e .

# Start local web server
make serve
# or: python -m src.eggphy.cli serve

# View at http://localhost:8000
```

### Data Processing
```bash
# Check dataset status
make status

# Reprocess data pipeline
make data-merge

# Validate data schema
make schema

# Generate analysis scripts
make scripts
```

---

## 📄 Academic Citation

### Recommended Citation
```bibtex
@misc{coughlin2025eggphy,
  title={Historical Egg Writing Recipes: A Phylogenetic Analysis of Technical Knowledge Transmission},
  author={Coughlin, Sean},
  year={2025},
  publisher={Alchemies of Scent},
  url={https://alchemiesofscent.github.io/eggphy/},
  note={Digital humanities dataset and analysis}
}
```

### License
This work is licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/). You are free to use, modify, and distribute with attribution.

---

## 🤝 Contributing & Collaboration

### For Researchers
- **Historical Sources**: Found additional recipe instances? [Open an issue](https://github.com/alchemiesofscent/eggphy/issues)
- **Data Corrections**: Spotted errors? Submit pull requests with evidence
- **Methodology**: Questions about stemmatic or phylogenetic approaches? Join the discussion

### For Digital Humanists
- **Technical Improvements**: Code contributions welcome
- **Visualization Ideas**: Suggestions for new analytical views
- **Data Standards**: Help improve metadata schemas and export formats

### Academic Collaboration
For research partnerships, access to raw materials, or methodology discussions, see contact information in repository issues or the [live site](https://alchemiesofscent.github.io/eggphy/).

---

## 🔗 Related Work

- **Digital Stemmatology**: Computational approaches to manuscript tradition analysis
- **Cultural Evolution**: Mathematical models of knowledge transmission
- **Science Communication History**: How technical claims spread and persist
- **Recipe Studies**: Historical analysis of culinary and technical instructions

---

**🌟 This project demonstrates how digital humanities methods can reveal hidden patterns in historical knowledge transmission, showing that even "failed" technical traditions carry rich cultural and epistemological information.**

*Generated and maintained with Claude Code assistance*