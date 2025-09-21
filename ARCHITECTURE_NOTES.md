# Architecture Notes & Technical Debt

## Current Hybrid Architecture Issue

The eggphy project currently has a **hybrid architecture** that needs simplification:

### Original Purpose
- Started as a CLI tool for automatic stemma generation and phylogenetic coding
- Core data processing in Python (`src/eggphy/`)
- Canonical data stored in `data/witnesses.json`

### Added Web Interface
- Built a web application (`docs/`) to display research data
- Web app expects data in `docs/data/witnesses.json`
- Two separate data files that need manual synchronization

### Current Problems
1. **Data Duplication**: Same data exists in two locations
2. **Sync Issues**: Changes to canonical data don't automatically update web app
3. **Inconsistent APIs**: CLI tools vs web app have different data expectations
4. **Maintenance Overhead**: Need to manually copy data between locations

## Immediate Workaround (Current State)
- **Manual Sync**: Copy `data/witnesses.json` to `docs/data/witnesses.json` when data changes
- **Recipe Page Fix**: Updated to use full structured data for display_notes functionality
- **Display Notes**: Successfully implemented human-readable scholarly notes

## Recommended Future Architecture Revision

### Option 1: Unified Data Source
- Single `data/witnesses.json` as canonical source
- Web app reads directly from canonical location
- Remove `docs/data/` duplication entirely

### Option 2: Build Process
- Establish clear build pipeline (`make web` or similar)
- Automated data transformation for web deployment
- Clear separation between research data and web-optimized data

### Option 3: API Server
- Python backend serves data via API
- Web frontend consumes API endpoints
- Single source of truth with proper data access layer

## Current Workaround Commands
```bash
# When data changes, manually sync to web app:
cp data/witnesses.json docs/data/witnesses.json

# Or use existing merge command (needs path updates):
python -m src.eggphy.cli merge --create-web
```

## Files That Need Attention
- `src/eggphy/cli.py` - WEB_JSON_FILE path configuration
- `src/eggphy/data_merger.py` - Web data generation logic
- `docs/app.js` - Main database data loading
- `docs/recipe.js` - Individual recipe data loading

---
**Note**: This documentation created during implementation of display_notes feature when the architecture duplication issue was discovered.