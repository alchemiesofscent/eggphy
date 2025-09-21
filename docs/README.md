# 🥚 Historical Egg Writing Recipes - Public Dataset

**A Digital Archive of "Invisible Ink" Egg Recipes (1000-2025 CE)**

[🌐 **Explore the Interactive Database**](https://alchemiesofscent.github.io/eggphy/) | [📊 **Download Dataset**](#download-data) | [🔬 **Research Repository**](https://github.com/alchemiesofscent/eggphy)

---

## About This Dataset

This dataset contains ~85 historical recipes claiming you can write on an eggshell with alum and vinegar such that, when boiled, the inscription appears on the egg white. Despite repeated modern failures (ordinary potassium alum does not work), this "zombie recipe" persisted for nearly two millennia across cultures and languages.

### 📚 Historical Significance

- **Time Span**: 1000 CE to 2025 CE (spanning Byzantine, Medieval, Renaissance, and Modern periods)
- **Languages**: Greek, Latin, German, French, Italian, English, and others
- **Sources**: Agricultural manuals, magic texts, household guides, entertainment books, and internet forums
- **Cultural Transmission**: Tracks how technical knowledge spreads and evolves across cultures

### 🔬 Research Applications

This dataset is valuable for researchers studying:
- **Historical Technology Transfer**: How technical recipes spread between cultures
- **Textual Transmission**: Patterns of copying, adaptation, and contamination
- **Science Communication**: Evolution of technical instructions over time
- **Digital Humanities**: Computational analysis of historical texts
- **Phylogenetics**: Applying biological evolution models to cultural transmission

---

## 🎯 Interactive Features

### [Recipe Explorer](https://alchemiesofscent.github.io/eggphy/)
- **Filter by Century**: Explore recipes from the 11th to 21st centuries
- **Language Families**: Compare Greek, Latin, and vernacular traditions
- **Ingredient Analysis**: Track changes in materials and methods
- **Process Variations**: See how instructions evolved over time
- **Search**: Find specific authors, sources, or content

### [Stemma Codicum Visualization](https://alchemiesofscent.github.io/eggphy/stemma/stemma.html)
- **Family Tree View**: Interactive phylogenetic trees showing recipe relationships
- **Timeline Mode**: Chronological visualization with zoom controls
- **Classification System**: 7 major family groups (A-G) based on diagnostic features
- **Collapsible Navigation**: Drill down from archetype to individual witnesses

---

## 📊 Download Data

All data is freely available under **CC BY 4.0** license:

| Format | Description | Size | Download |
|--------|-------------|------|----------|
| **JSON** | Complete structured dataset with metadata | ~2MB | [witnesses.json](data/witnesses.json) |
| **CSV** | Tabular format for spreadsheet analysis | ~500KB | [witnesses.csv](data/witnesses.csv) |
| **Raw Sources** | Original text collection | ~1MB | [See repository](https://github.com/seancoughlin/eggphy/tree/main/data/raw_sources) |

### 🔗 API Access

Access data programmatically:

```bash
# Fetch complete dataset
curl https://alchemiesofscent.github.io/eggphy/data/witnesses.json

# Or in JavaScript:
fetch('https://alchemiesofscent.github.io/eggphy/data/witnesses.json')
  .then(response => response.json())
  .then(data => console.log(data));
```

---

## 📖 Data Structure

Each recipe record includes:

```json
{
  "metadata": {
    "witness_id": "W01",
    "date": 1000,
    "author": "Constantinus VII",
    "language": "grc",
    "source_work": "Geoponikon",
    "genre": "Agriculture"
  },
  "ingredients": {
    "primary_components": [
      {"substance": "galls", "quantity": "ground"},
      {"substance": "alum", "quantity": "equal amount"}
    ],
    "diagnostic_variants": {
      "gall_presence": "present",
      "alum_type": "unspecified"
    }
  },
  "process_steps": {
    "preparation_sequence": [...],
    "critical_variants": {
      "boiling_timing": "after_writing",
      "soaking_duration": "unspecified"
    }
  },
  "full_text": "Original recipe text...",
  "process_summary": "Human-readable summary..."
}
```

---

## 🏛️ Research Context

### Why Study "Failed" Recipes?

1. **Transmission Mechanisms**: How do instructions spread without experimental verification?
2. **Cultural Authority**: What makes people trust and copy technical claims?
3. **Textual Evolution**: How do copying errors and adaptations accumulate?
4. **Cross-Cultural Exchange**: How do recipes adapt to local materials and practices?

### Methodology

This research combines:
- **Classical Stemmatology**: Traditional manuscript analysis techniques
- **Computational Phylogenetics**: Biological evolution models applied to texts
- **Digital Humanities**: Large-scale text analysis and visualization
- **Historical Chemistry**: Understanding period materials and processes

---

## 📄 Citation & License

### License
This dataset is released under [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

You are free to:
- **Share** — copy and redistribute the material
- **Adapt** — remix, transform, and build upon the material
- **Commercial Use** — use for any purpose, including commercially

**Attribution Required**: Please cite this work in any publications or derivative works.

### Suggested Citation

**Academic Papers:**
```
Coughlin, Sean. (2025). Historical Egg Writing Recipes Dataset: A Digital Archive
of Invisible Ink Traditions (1000-2025 CE). Digital Humanities Research.
https://alchemiesofscent.github.io/eggphy/
```

**Data Usage:**
```
Coughlin, S. (2025). Historical Egg Writing Recipes [Dataset].
Retrieved from https://alchemiesofscent.github.io/eggphy/data/witnesses.json
```

---

## 🤝 Contributing & Contact

### For Researchers
- Found additional historical sources? [Open an issue](https://github.com/alchemiesofscent/eggphy/issues)
- Spotted data errors? Submit corrections via GitHub
- Want to collaborate? See the [full research repository](https://github.com/alchemiesofscent/eggphy)

### For Developers
- API suggestions and improvements welcome
- Visualization ideas encouraged
- See the [technical documentation](https://github.com/alchemiesofscent/eggphy) for contributing guidelines

### Academic Inquiries
For research collaboration, methodology questions, or access to additional materials, please see the contact information in the [main repository](https://github.com/alchemiesofscent/eggphy).

---

## 🔍 Related Projects

- **Digital Stemmatology**: Computational approaches to manuscript analysis
- **Cultural Evolution**: Applying evolutionary models to human culture
- **Historical Recipe Collections**: Digital archives of historical technical knowledge
- **Science Communication History**: How scientific knowledge spreads over time

---

*This project demonstrates how digital humanities methods can illuminate patterns in historical knowledge transmission, showing that even "failed" technical traditions have rich stories to tell about human culture and communication.*