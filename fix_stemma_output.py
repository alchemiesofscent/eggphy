#!/usr/bin/env python3
"""
Fix stemma analysis output by running Claude with proper settings
to get just the analysis result without wrapper metadata.
"""

import json
import subprocess
import sys
from pathlib import Path

def run_claude_analysis(prompt_file, data_file, output_file):
    """Run Claude analysis and extract just the result."""

    # Combine prompt and data
    cmd = [
        "claude",
        f"@{prompt_file}",
        str(data_file),
        "-p",
        "--output-format", "json",
        "--permission-mode", "bypassPermissions"
    ]

    print(f"Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if result.returncode != 0:
            print(f"Error running Claude: {result.stderr}")
            return False

        # Parse the output
        try:
            output_data = json.loads(result.stdout)

            # Extract just the result content
            if 'result' in output_data and output_data['result']:
                analysis_result = output_data['result']

                # Write just the analysis to the output file
                with open(output_file, 'w') as f:
                    f.write(analysis_result)

                print(f"✓ Analysis complete: {output_file}")
                return True
            else:
                print(f"No result in output: {output_file}")
                return False

        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return False

    except subprocess.TimeoutExpired:
        print(f"Timeout running analysis for {data_file}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    base_dir = Path(__file__).parent
    prompt_file = base_dir / "prompts/stemma_agent.md"
    chunks_dir = base_dir / "data/chunks"
    output_dir = base_dir / "models/stemma"

    output_dir.mkdir(exist_ok=True)

    chunk_files = sorted(chunks_dir.glob("witnesses_part_*.csv"))

    if not chunk_files:
        print("No chunk files found!")
        return 1

    print(f"Found {len(chunk_files)} chunk files to process")

    success_count = 0
    for chunk_file in chunk_files:
        output_file = output_dir / f"{chunk_file.stem}.json"

        if output_file.exists():
            print(f"Skipping existing: {output_file}")
            continue

        if run_claude_analysis(prompt_file, chunk_file, output_file):
            success_count += 1
        else:
            print(f"Failed: {chunk_file}")

    print(f"\nCompleted: {success_count}/{len(chunk_files)} files")
    return 0 if success_count == len(chunk_files) else 1

if __name__ == "__main__":
    sys.exit(main())