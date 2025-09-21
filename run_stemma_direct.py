#!/usr/bin/env python3
"""
Run stemma analysis with direct, explicit instructions
"""

import json
import subprocess
import sys
from pathlib import Path

def run_claude_analysis(data_file, output_file):
    """Run Claude analysis with very direct instructions."""

    # Read the CSV data
    with open(data_file, 'r') as f:
        csv_data = f.read()

    # Create very direct instruction
    direct_prompt = f"""You are a textual critic analyzing historical recipe manuscripts. Analyze the CSV data below and extract structured JSON data for each witness (row).

For each witness (row), create a JSON object with this structure:
{{
  "metadata": {{
    "witness_id": "string from first column",
    "date": number from second column,
    "author": "string from third column",
    "language": "string from language column",
    "genre": "string from genre column"
  }},
  "ingredients": {{
    "galls_present": true/false,
    "alum_present": true/false,
    "vinegar_present": true/false,
    "wax_present": true/false
  }},
  "process_analysis": {{
    "method_count": number,
    "boiling_mentioned": true/false,
    "drying_mentioned": true/false
  }},
  "attribution": {{
    "africanus_mentioned": true/false,
    "other_attribution": "string or null"
  }}
}}

Return a JSON array containing one object for each row in the CSV.

CSV DATA:
{csv_data}

Analyze each row and return the JSON array:"""

    # Run Claude
    cmd = [
        "claude",
        "-p",
        "--output-format", "text",
        "--permission-mode", "bypassPermissions"
    ]

    print(f"Analyzing: {data_file.name}")

    try:
        result = subprocess.run(
            cmd,
            input=direct_prompt,
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return False

        analysis_result = result.stdout.strip()

        # Try to validate it's JSON
        try:
            parsed = json.loads(analysis_result)
            if isinstance(parsed, list):
                print(f"✓ Valid JSON array with {len(parsed)} witnesses")
            else:
                print(f"✓ Valid JSON but not an array")
        except json.JSONDecodeError:
            print(f"⚠ Output is not valid JSON")

        with open(output_file, 'w') as f:
            f.write(analysis_result)

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

    print("Testing direct analysis approach...")

    if run_claude_analysis(test_file, output_file):
        print("\n✓ Test complete! Check the output format.")
        return 0
    else:
        print("\n✗ Test failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())