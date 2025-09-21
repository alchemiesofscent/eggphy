#!/usr/bin/env python3
"""
Final working version of stemma analysis
"""

import json
import subprocess
import sys
import re
from pathlib import Path

def clean_json_output(text):
    """Extract JSON from markdown code blocks or other wrapper text."""
    # Look for JSON in code blocks
    json_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', text, re.DOTALL)
    if json_match:
        return json_match.group(1)

    # Look for bare JSON array
    json_match = re.search(r'(\[.*?\])', text, re.DOTALL)
    if json_match:
        return json_match.group(1)

    return text.strip()

def run_claude_analysis(data_file, output_file):
    """Run Claude analysis with clean JSON extraction."""

    # Read CSV data (first 10 rows only for testing)
    with open(data_file, 'r') as f:
        lines = f.readlines()
        header = lines[0]
        data_rows = lines[1:11]  # First 10 rows
        csv_data = header + ''.join(data_rows)

    # Simplified prompt for structured analysis
    prompt = f"""Analyze this CSV of historical recipe manuscripts. For each data row, extract key information into JSON format.

CSV DATA:
{csv_data}

For each witness (data row), return JSON with this structure:
{{
  "witness_id": "string from WitnessID column",
  "date": number from Date column,
  "author": "string from Author column",
  "language": "string from Language column",
  "genre": "string from Book_Genre column",
  "attribution_africanus": true/false (if "Africanus" or "Ἀφρικανοῦ" appears in text),
  "ingredients": {{
    "galls_mentioned": true/false,
    "alum_mentioned": true/false,
    "vinegar_mentioned": true/false,
    "wax_mentioned": true/false
  }},
  "process": {{
    "boiling_mentioned": true/false,
    "drying_mentioned": true/false,
    "two_methods": true/false (if text has [W1a] and [W1b] or similar)
  }}
}}

Return a JSON array containing one object per data row. Output only the JSON array, no explanatory text."""

    cmd = ["claude", "-p", "--output-format", "text", "--permission-mode", "bypassPermissions"]

    print(f"Analyzing: {data_file.name}")

    try:
        result = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=300)

        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return False

        # Clean the output
        raw_output = result.stdout.strip()
        json_text = clean_json_output(raw_output)

        # Validate JSON
        try:
            parsed = json.loads(json_text)
            if isinstance(parsed, list):
                print(f"✓ Valid JSON array with {len(parsed)} witnesses")
            else:
                print(f"✓ Valid JSON but not an array")
        except json.JSONDecodeError as e:
            print(f"✗ JSON parsing failed: {e}")
            print(f"Raw output: {raw_output[:200]}...")
            return False

        # Write cleaned JSON
        with open(output_file, 'w') as f:
            json.dump(parsed, f, indent=2)

        print(f"✓ Complete: {output_file.name}")
        return True

    except subprocess.TimeoutExpired:
        print(f"✗ Timeout")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    base_dir = Path(__file__).parent
    chunks_dir = base_dir / "data/chunks"
    output_dir = base_dir / "models/stemma"

    output_dir.mkdir(exist_ok=True)

    # Test with one file
    test_file = chunks_dir / "witnesses_part_aa.csv"
    output_file = output_dir / "witnesses_part_aa.json"

    print("Running final stemma analysis test...")

    if run_claude_analysis(test_file, output_file):
        print(f"\n✓ Success! Check output: {output_file}")
        return 0
    else:
        print("\n✗ Failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())