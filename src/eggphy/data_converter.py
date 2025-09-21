import csv
import json
import pathlib
import subprocess
import tempfile
from typing import List, Dict, Any, Optional


def csv_to_json_full(csv_path: pathlib.Path, json_path: pathlib.Path) -> None:
    """Convert CSV to JSON with full data preservation including long texts."""
    witnesses = []

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    with csv_path.open('r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Create witness entry preserving all original CSV fields
            witness = {
                'witness_id': row.get('WitnessID', '').strip(),
                'date': int(row.get('Date', 0)) if row.get('Date', '').strip().isdigit() else 0,
                'source': row.get('Source', '').strip(),
                'language': row.get('Language', '').strip(),
                'full_text': row.get('Full_Text', '').strip(),
                'url': row.get('URL', '').strip(),
                'note': row.get('Note', '').strip(),
                'translation': row.get('Translation', '').strip()
            }

            # Extract author from source field with improved logic
            witness['author'] = extract_author_from_source(witness['source'])

            # Add derived fields for web interface
            witness['century'] = calculate_century(witness['date'])
            witness['has_full_text'] = bool(witness['full_text'])
            witness['has_translation'] = bool(witness['translation'])
            witness['text_length'] = len(witness['full_text'])

            witnesses.append(witness)

    # Ensure output directory exists
    json_path.parent.mkdir(parents=True, exist_ok=True)

    # Write JSON with proper formatting
    with json_path.open('w', encoding='utf-8') as jsonfile:
        json.dump(witnesses, jsonfile, ensure_ascii=False, indent=2)

    print(f"Converted {len(witnesses)} witnesses from {csv_path} to {json_path}")


def json_to_csv(json_path: pathlib.Path, csv_path: pathlib.Path) -> None:
    """Convert JSON back to CSV format, preserving original CSV structure."""
    if not json_path.exists():
        raise FileNotFoundError(f"JSON file not found: {json_path}")

    with json_path.open('r', encoding='utf-8') as jsonfile:
        witnesses = json.load(jsonfile)

    if not witnesses:
        print("No witnesses found in JSON file")
        return

    # Define CSV column headers (original order)
    fieldnames = [
        'WitnessID', 'Date', 'Source', 'Language',
        'Full_Text', 'URL', 'Note', 'Translation'
    ]

    # Ensure output directory exists
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    with csv_path.open('w', encoding='utf-8', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for witness in witnesses:
            # Map JSON fields back to CSV format
            row = {
                'WitnessID': witness.get('witness_id', ''),
                'Date': witness.get('date', ''),
                'Source': witness.get('source', ''),
                'Language': witness.get('language', ''),
                'Full_Text': witness.get('full_text', ''),
                'URL': witness.get('url', ''),
                'Note': witness.get('note', ''),
                'Translation': witness.get('translation', '')
            }
            writer.writerow(row)

    print(f"Converted {len(witnesses)} witnesses from {json_path} to {csv_path}")


def structured_json_to_csv(json_path: pathlib.Path, csv_path: pathlib.Path) -> None:
    """Convert structured analysis JSON (StemmaAgent schema) to the flat CSV format.

    Columns: WitnessID, Date, Source, Language, Full_Text, URL, Note, Translation
    """
    if not json_path.exists():
        raise FileNotFoundError(f"JSON file not found: {json_path}")

    with json_path.open('r', encoding='utf-8') as jsonfile:
        data = json.load(jsonfile)

    if not data:
        print("No witnesses found in JSON file")
        return

    fieldnames = [
        'WitnessID', 'Date', 'Source', 'Language', 'Full_Text', 'URL', 'Note', 'Translation'
    ]

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open('w', encoding='utf-8', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for w in data:
            md = w.get('metadata', {})
            td = w.get('text_data', {})
            row = {
                'WitnessID': md.get('witness_id', ''),
                'Date': md.get('date', ''),
                'Source': td.get('source_citation', ''),
                'Language': md.get('language', ''),
                'Full_Text': td.get('full_text', ''),
                'URL': td.get('url', ''),
                'Note': td.get('note', ''),
                'Translation': td.get('translation', ''),
            }
            writer.writerow(row)

    print(f"Converted {len(data)} witnesses from structured {json_path} to {csv_path}")


def extract_author_from_source(source: str) -> str:
    """Extract author name from source field with improved logic."""
    if not source:
        return ''

    # Handle common patterns in the source field
    source = source.strip()

    # Pattern 1: "Author, Title" format
    if ',' in source:
        first_part = source.split(',')[0].strip()

        # Skip if it starts with common non-author prefixes
        skip_prefixes = [
            'Geoponica', 'Magiae', 'Della', 'Thurston,', 'Goldston,',
            'Scarne,', 'Ms.', 'Cod.', 'Laur.', 'Plut.', 'Book', 'Chapter'
        ]

        if not any(first_part.startswith(prefix) for prefix in skip_prefixes):
            # Check if it looks like an author name (contains letters, reasonable length)
            if len(first_part) > 2 and any(c.isalpha() for c in first_part):
                return first_part

    # Pattern 2: Look for known author names in the text
    known_authors = {
        'Geoponica': 'Cassianus Bassus',
        'Africanus': 'Africanus',
        'della Porta': 'Giambattista della Porta',
        'Thurston': 'Howard Thurston',
        'Goldston': 'Will Goldston',
        'Scarne': 'John Scarne'
    }

    for key, author in known_authors.items():
        if key in source:
            return author

    return ''


def calculate_century(date: int) -> int:
    """Calculate century from year."""
    if date <= 0:
        return 0
    return (date - 1) // 100 + 1


def edit_witness_table(csv_path: pathlib.Path, editor: Optional[str] = None) -> None:
    """Open CSV file in a table editor for easy editing."""
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    # Try different editors in order of preference
    editors_to_try = []

    if editor:
        editors_to_try.append(editor)

    # Add common CSV editors
    editors_to_try.extend([
        'vd',  # VisiData - excellent for CSV editing
        'sc-im',  # Spreadsheet Calculator Improved
        'libreoffice --calc',  # LibreOffice Calc
        'gnumeric',  # Gnumeric
        'csvkit',  # csvkit tools
    ])

    # Try to find and use an available editor
    for editor_cmd in editors_to_try:
        try:
            cmd_parts = editor_cmd.split()
            # Check if command exists
            result = subprocess.run(['which', cmd_parts[0]],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                # Command exists, try to open the file
                full_cmd = cmd_parts + [str(csv_path)]
                print(f"Opening {csv_path} with {editor_cmd}")
                subprocess.run(full_cmd)
                return
        except (subprocess.SubprocessError, FileNotFoundError):
            continue

    # Fallback: open with default system editor
    try:
        print(f"Opening {csv_path} with default editor")
        subprocess.run(['xdg-open', str(csv_path)])
    except subprocess.SubprocessError:
        print(f"Could not find a suitable editor. Please manually edit: {csv_path}")
        print("Suggested editors: vd (VisiData), LibreOffice Calc, or any CSV editor")


def sync_csv_json(csv_path: pathlib.Path, json_path: pathlib.Path,
                  direction: str = 'auto') -> None:
    """Sync between CSV and JSON files based on modification times or explicit direction."""

    csv_exists = csv_path.exists()
    json_exists = json_path.exists()

    if direction == 'auto':
        if not csv_exists and not json_exists:
            raise FileNotFoundError("Neither CSV nor JSON file exists")
        elif not csv_exists:
            direction = 'json_to_csv'
        elif not json_exists:
            direction = 'csv_to_json'
        else:
            # Both exist, check modification times
            csv_mtime = csv_path.stat().st_mtime
            json_mtime = json_path.stat().st_mtime

            if csv_mtime > json_mtime:
                direction = 'csv_to_json'
            else:
                direction = 'json_to_csv'

    # Normalize direction parameter
    direction = direction.replace('-', '_')

    if direction == 'csv_to_json':
        print(f"Converting {csv_path} → {json_path}")
        csv_to_json_full(csv_path, json_path)
    elif direction == 'json_to_csv':
        print(f"Converting {json_path} → {csv_path}")
        # Detect structured StemmaAgent schema
        try:
            with json_path.open('r', encoding='utf-8') as jf:
                probe = json.load(jf)
        except Exception:
            probe = []
        if isinstance(probe, list) and probe and isinstance(probe[0], dict) and (
            'metadata' in probe[0] and 'text_data' in probe[0]
        ):
            structured_json_to_csv(json_path, csv_path)
        else:
            json_to_csv(json_path, csv_path)
    else:
        raise ValueError(f"Invalid direction: {direction}. Use 'csv-to-json', 'json-to-csv', or 'auto'")


def validate_witness_data(witness: Dict[str, Any]) -> List[str]:
    """Validate a witness entry and return list of issues."""
    issues = []

    # Required fields
    if not witness.get('witness_id'):
        issues.append("Missing witness_id")

    if not witness.get('date') or witness.get('date', 0) <= 0:
        issues.append("Missing or invalid date")

    # Data quality checks
    if not witness.get('source'):
        issues.append("Missing source")

    if not witness.get('language'):
        issues.append("Missing language")

    if not witness.get('full_text') and not witness.get('translation'):
        issues.append("Missing both full_text and translation")

    # Date range check
    date = witness.get('date', 0)
    if date < 100 or date > 2030:
        issues.append(f"Date {date} seems outside reasonable range")

    return issues


def validate_all_witnesses(json_path: pathlib.Path) -> Dict[str, List[str]]:
    """Validate all witnesses in JSON file and return issues by witness_id."""
    if not json_path.exists():
        raise FileNotFoundError(f"JSON file not found: {json_path}")

    with json_path.open('r', encoding='utf-8') as f:
        witnesses = json.load(f)

    all_issues = {}
    witness_ids = set()

    for i, witness in enumerate(witnesses):
        witness_id = witness.get('witness_id', f'row_{i}')

        # Check for duplicate IDs
        if witness_id in witness_ids:
            if witness_id not in all_issues:
                all_issues[witness_id] = []
            all_issues[witness_id].append("Duplicate witness_id")
        witness_ids.add(witness_id)

        # Validate individual witness
        issues = validate_witness_data(witness)
        if issues:
            all_issues[witness_id] = all_issues.get(witness_id, []) + issues

    return all_issues
