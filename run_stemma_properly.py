#!/usr/bin/env python3
"""
Run stemma analysis with explicit instructions to analyze the CSV data
"""

import json
import subprocess
import sys
from pathlib import Path

def run_claude_analysis(prompt_file, data_file, output_file):
    """Run Claude analysis with explicit CSV processing instructions."""

    # Read the prompt
    with open(prompt_file, 'r') as f:
        prompt_text = f.read()

    # Read the CSV data
    with open(data_file, 'r') as f:
        csv_data = f.read()

    # Create explicit instruction to analyze the data
    combined_input = f"""{prompt_text}

IMPORTANT: You must now analyze the CSV data below according to the stemmatic analysis framework above.
Process each row as a witness and return a JSON array with the complete structured analysis.

CSV DATA TO ANALYZE:
{csv_data}

Please analyze this CSV data and return the structured JSON output as specified in the prompt above."""

    # Run Claude with stdin
    cmd = [
        "claude",
        "-p",
        "--output-format", "text",  # Changed to text to get cleaner output
        "--permission-mode", "bypassPermissions"
    ]

    print(f"Analyzing: {data_file.name}")

    try:
        result = subprocess.run(
            cmd,
            input=combined_input,
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return False

        # Write the raw output (should be JSON)
        analysis_result = result.stdout.strip()

        # Try to validate it's JSON
        try:
            json.loads(analysis_result)
            print(f"✓ Valid JSON output")
        except json.JSONDecodeError:
            print(f"⚠ Output may not be valid JSON")

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
    prompt_file = base_dir / "prompts/stemma_agent.md"
    chunks_dir = base_dir / "data/chunks"
    output_dir = base_dir / "models/stemma"

    output_dir.mkdir(exist_ok=True)

    # Test with just one file first
    test_file = chunks_dir / "witnesses_part_aa.csv"
    if not test_file.exists():
        print(f"Test file not found: {test_file}")
        return 1

    output_file = output_dir / "witnesses_part_aa.json"

    print("Running test analysis on witnesses_part_aa.csv...")

    if run_claude_analysis(prompt_file, test_file, output_file):
        print("\n✓ Test successful! Check the output format.")
        print(f"Review: {output_file}")
        return 0
    else:
        print("\n✗ Test failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())