#!/usr/bin/env bash
set -euo pipefail

claude @prompts/stemma_agent.md data/chunks/witnesses_part_ab.csv -p --output-format json > models/stemma/witnesses_part_ab.json
claude @prompts/stemma_agent.md data/chunks/witnesses_part_ac.csv -p --output-format json > models/stemma/witnesses_part_ac.json
claude @prompts/stemma_agent.md data/chunks/witnesses_part_ad.csv -p --output-format json > models/stemma/witnesses_part_ad.json
claude @prompts/stemma_agent.md data/chunks/witnesses_part_ae.csv -p --output-format json > models/stemma/witnesses_part_ae.json
claude @prompts/stemma_agent.md data/chunks/witnesses_part_af.csv -p --output-format json > models/stemma/witnesses_part_af.json
claude @prompts/stemma_agent.md data/chunks/witnesses_part_ag.csv -p --output-format json > models/stemma/witnesses_part_ag.json
claude @prompts/stemma_agent.md data/chunks/witnesses_part_ah.csv -p --output-format json > models/stemma/witnesses_part_ah.json
claude @prompts/stemma_agent.md data/chunks/witnesses_part_ai.csv -p --output-format json > models/stemma/witnesses_part_ai.json
