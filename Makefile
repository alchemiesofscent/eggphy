.PHONY: help status serve data-merge web schema phase1 phase2 scripts

PY=python -m src.eggphy.cli

help:
	@echo "Targets:"
	@echo "  status    - show witness count"
	@echo "  serve     - start web UI"
	@echo "  data-merge- merge CSV→JSON (normalized) and update web JSON"
	@echo "  web       - alias for data-merge"
	@echo "  schema    - schema check for witnesses.json"
	@echo "  scripts   - generate phase1.sh and phase2.sh"
	@echo "  phase1    - run generated Phase I script"
	@echo "  phase2    - run generated Phase II script"

status:
	$(PY) status

serve:
	$(PY) serve

data-merge:
	$(PY) merge --create-web

web: data-merge

schema:
	$(PY) schema-check --sample 10

scripts:
	$(PY) scripts --out scripts

phase1: scripts
	bash scripts/phase1.sh

phase2: scripts
	bash scripts/phase2.sh

