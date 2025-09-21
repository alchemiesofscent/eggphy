#!/usr/bin/env python3
"""
Script to update witnesses in merged JSON with text data from CSV.
Use this after manually adding witness entries to witnesses_merged.json.
"""

import json
import csv
import sys
from pathlib import Path

def extract_author_from_source(source: str) -> str:
    """Extract author name from source field."""
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
        'Scarne': 'John Scarne',
        'Wecker': 'Johann Jacob Wecker',
        'Schwenter': 'Daniel Schwenter',
        'Witgeest': 'Simon Witgeest'
    }

    for key, author in known_authors.items():
        if key in source:
            return author

    return ''

def update_witnesses_with_text_data():
    """Update witnesses in merged JSON with text data from CSV."""

    # File paths
    csv_path = Path('data/raw_sources/witnesses_raw.csv')
    merged_path = Path('data/witnesses.json')

    if not csv_path.exists():
        print(f"Error: CSV file not found: {csv_path}")
        return False

    if not merged_path.exists():
        print(f"Error: Merged JSON file not found: {merged_path}")
        return False

    # Load CSV data
    print(f"Loading CSV data from {csv_path}")
    csv_data = {}
    with csv_path.open('r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            witness_id = row.get('WitnessID', '').strip()
            if witness_id:
                csv_data[witness_id] = {
                    'witness_id': witness_id,
                    'date': int(row.get('Date', 0)) if row.get('Date', '').strip().isdigit() else 0,
                    'source': row.get('Source', '').strip(),
                    'language': row.get('Language', '').strip(),
                    'full_text': row.get('Full_Text', '').strip(),
                    'url': row.get('URL', '').strip(),
                    'note': row.get('Note', '').strip(),
                    'translation': row.get('Translation', '').strip()
                }

    print(f"Loaded {len(csv_data)} witnesses from CSV")

    # Load merged JSON
    print(f"Loading merged JSON from {merged_path}")
    with merged_path.open('r', encoding='utf-8') as f:
        merged_data = json.load(f)

    print(f"Loaded {len(merged_data)} witnesses from merged JSON")

    # Update witnesses that need text data
    updated_count = 0
    missing_text_data = []

    for entry in merged_data:
        witness_id = entry.get('metadata', {}).get('witness_id')

        if not witness_id:
            continue

        # Check if text_data is missing or incomplete
        text_data = entry.get('text_data', {})
        needs_update = (
            not text_data or
            not text_data.get('full_text') or
            'text_length' not in text_data
        )

        if needs_update and witness_id in csv_data:
            csv_witness = csv_data[witness_id]

            # Update or create text_data section
            entry['text_data'] = {
                'full_text': csv_witness['full_text'],
                'translation': csv_witness['translation'],
                'source_citation': csv_witness['source'],
                'url': csv_witness['url'],
                'note': csv_witness['note'],
                'has_full_text': bool(csv_witness['full_text']),
                'has_translation': bool(csv_witness['translation']),
                'text_length': len(csv_witness['full_text']),
                'translation_length': len(csv_witness['translation'])
            }

            # Update metadata
            metadata = entry['metadata']

            # Update author if missing
            if not metadata.get('author') and csv_witness['source']:
                metadata['author'] = extract_author_from_source(csv_witness['source'])

            # Update URL availability
            metadata['url_available'] = bool(
                csv_witness['url'] and csv_witness['url'] != '[URL Missing]'
            )

            # Update data completeness
            if csv_witness['full_text']:
                if csv_witness['translation']:
                    metadata['data_completeness'] = 'complete_with_translation'
                else:
                    metadata['data_completeness'] = 'complete'
            else:
                metadata['data_completeness'] = 'fragmentary'

            updated_count += 1
            print(f"✅ Updated {witness_id}: text_length={len(csv_witness['full_text'])}, has_translation={bool(csv_witness['translation'])}")

        elif needs_update:
            missing_text_data.append(witness_id)

    # Save updated merged data
    with merged_path.open('w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)

    # Report results
    print(f"\n📊 Update Summary:")
    print(f"  ✅ Successfully updated: {updated_count} witnesses")
    print(f"  ❌ Missing in CSV: {len(missing_text_data)} witnesses")
    print(f"  📁 Total witnesses: {len(merged_data)}")

    if missing_text_data:
        print(f"\nWitnesses missing text data (not in CSV):")
        for witness_id in missing_text_data:
            print(f"  - {witness_id}")

    # Create web-optimized version
    try:
        from src.eggphy.data_merger import create_enhanced_web_data
        web_path = Path('data/witnesses_web.json')
        create_enhanced_web_data(merged_path, web_path)
        print(f"\n🌐 Updated web-optimized data: {web_path}")
    except Exception as e:
        print(f"\n⚠️  Could not update web data: {e}")

    return True

if __name__ == "__main__":
    success = update_witnesses_with_text_data()
    sys.exit(0 if success else 1)
