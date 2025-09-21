#!/usr/bin/env python3
"""
Run stemma analysis with proper stdin input
"""

import json
import subprocess
import sys
from pathlib import Path

def run_claude_with_stdin(prompt_file, data_file, output_file):
    """Send combined prompt + data via stdin to Claude."""

    # Read the prompt
    with open(prompt_file, 'r') as f:
        prompt_text = f.read()

    # Read the CSV data
    with open(data_file, 'r') as f:
        csv_data = f.read()

    # Combine them
    combined_input = f"{prompt_text}\n\n---\n\nHere is the CSV data to analyze:\n\n{csv_data}"

    # Run Claude with stdin
    cmd = [
        "claude",
        "-p",
        "--output-format", "json",
        "--permission-mode", "bypassPermissions"
    ]

    print(f"Processing: {data_file.name} -> {output_file.name}")

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

        # Parse the output and extract result
        try:
            output_data = json.loads(result.stdout)
            if 'result' in output_data and output_data['result']:
                analysis_result = output_data['result']

                # Write the analysis
                with open(output_file, 'w') as f:
                    f.write(analysis_result)

                print(f"✓ Complete: {output_file.name}")
                return True
            else:
                print(f"✗ No result in output")
                return False

        except json.JSONDecodeError as e:
            print(f"✗ JSON error: {e}")
            return False

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

    # Remove existing files
    for existing in output_dir.glob("witnesses_part_*.json"):
        existing.unlink()

    chunk_files = sorted(chunks_dir.glob("witnesses_part_*.csv"))
    print(f"Processing {len(chunk_files)} chunk files...")

    success_count = 0
    for chunk_file in chunk_files:
        output_file = output_dir / f"{chunk_file.stem}.json"

        if run_claude_with_stdin(prompt_file, chunk_file, output_file):
            success_count += 1

    print(f"\nStemma analysis complete: {success_count}/{len(chunk_files)} files")
    return 0 if success_count == len(chunk_files) else 1

if __name__ == "__main__":
    sys.exit(main())