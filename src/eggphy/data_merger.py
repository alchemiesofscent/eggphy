import csv
import json
import pathlib
from typing import Dict, List, Any, Optional


def load_csv_data(csv_path: pathlib.Path) -> Dict[str, Dict[str, Any]]:
    """Load CSV data and return a dictionary keyed by witness_id."""
    csv_data = {}

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

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

    return csv_data


def merge_text_data_into_structured_json(
    csv_path: pathlib.Path,
    structured_json_path: pathlib.Path,
    output_path: pathlib.Path
) -> None:
    """Merge CSV text data into structured JSON analysis data."""

    # Load CSV data
    print(f"Loading CSV data from {csv_path}")
    csv_data = load_csv_data(csv_path)
    print(f"Loaded {len(csv_data)} witnesses from CSV")

    # Load structured JSON
    print(f"Loading structured JSON from {structured_json_path}")
    if not structured_json_path.exists():
        raise FileNotFoundError(f"Structured JSON file not found: {structured_json_path}")

    with structured_json_path.open('r', encoding='utf-8') as f:
        structured_data = json.load(f)

    print(f"Loaded {len(structured_data)} witnesses from structured JSON")

    # Merge data
    merged_count = 0
    missing_in_csv = []
    missing_in_structured = []

    for witness_entry in structured_data:
        witness_id = witness_entry.get('metadata', {}).get('witness_id')

        if not witness_id:
            print(f"Warning: Found entry without witness_id in structured JSON")
            continue

        if witness_id in csv_data:
            csv_witness = csv_data[witness_id]

            # Add text data to the structured entry
            witness_entry['text_data'] = {
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

            # Update metadata with CSV information if more complete
            metadata = witness_entry['metadata']
            if not metadata.get('author') and csv_witness['source']:
                metadata['author'] = extract_author_from_source(csv_witness['source'])

            # Add URL availability flag
            metadata['url_available'] = bool(csv_witness['url'] and csv_witness['url'] != '[URL Missing]')

            # Update data completeness based on available text
            if csv_witness['full_text']:
                if csv_witness['translation']:
                    metadata['data_completeness'] = 'complete_with_translation'
                else:
                    metadata['data_completeness'] = 'complete'
            else:
                metadata['data_completeness'] = 'fragmentary'

            merged_count += 1
        else:
            missing_in_csv.append(witness_id)

    # Check for witnesses in CSV but not in structured JSON
    for csv_witness_id in csv_data:
        if not any(entry.get('metadata', {}).get('witness_id') == csv_witness_id
                  for entry in structured_data):
            missing_in_structured.append(csv_witness_id)

    # After merging text data, normalize structure per prompts/stemma_agent.md
    # - Ensure analysis_confidence is top-level (compute overall if missing)
    # - Hoist relationship_analysis, explanatory_material, attribution from
    #   linguistic_analysis into top-level (merging when needed)

    def _has_ac_fields(d: dict) -> bool:
        if not isinstance(d, dict):
            return False
        keys = (
            'overall_confidence', 'text_completeness', 'extraction_reliability',
            'relationship_indicators', 'linguistic_analysis', 'uncertainty_flags',
            'requires_manual_review'
        )
        return any(k in d for k in keys)

    def _compute_overall(d: dict) -> Optional[float]:
        try:
            oc = d.get('overall_confidence')
            if isinstance(oc, (int, float)):
                return float(oc)
            parts = [
                d.get('text_completeness'), d.get('extraction_reliability'),
                d.get('relationship_indicators'), d.get('linguistic_analysis')
            ]
            nums = [float(x) for x in parts if isinstance(x, (int, float))]
            if nums:
                return sum(nums) / len(nums)
        except Exception:
            pass
        return None

    def _merge_ac(top: dict, nested: dict) -> dict:
        out: Dict[str, Any] = {}
        # numeric fields (prefer top)
        for k in (
            'text_completeness', 'extraction_reliability',
            'relationship_indicators', 'linguistic_analysis', 'overall_confidence'
        ):
            if isinstance((top or {}).get(k), (int, float)):
                out[k] = float(top[k])
            elif isinstance((nested or {}).get(k), (int, float)):
                out[k] = float(nested[k])
        # uncertainty flags (union)
        flags = set()
        if isinstance((nested or {}).get('uncertainty_flags'), list):
            flags.update(map(str, nested.get('uncertainty_flags')))
        if isinstance((top or {}).get('uncertainty_flags'), list):
            flags.update(map(str, top.get('uncertainty_flags')))
        if flags:
            out['uncertainty_flags'] = sorted(flags)
        # requires_manual_review (OR)
        r_top = (top or {}).get('requires_manual_review')
        r_nested = (nested or {}).get('requires_manual_review')
        if isinstance(r_top, bool) or isinstance(r_nested, bool):
            out['requires_manual_review'] = bool(r_top) or bool(r_nested)
        # ensure overall
        if 'overall_confidence' not in out:
            oc = _compute_overall(out)
            if isinstance(oc, float):
                out['overall_confidence'] = oc
        return out

    def _merge_obj(prefer: Optional[dict], other: Optional[dict]) -> dict:
        """Shallow merge dictionaries, preferring keys from 'prefer';
        union arrays when both sides have lists with the same key."""
        out: Dict[str, Any] = dict(other or {})
        for k, v in (prefer or {}).items():
            if k in out and isinstance(out[k], list) and isinstance(v, list):
                # union while preserving JSON-serializable elements
                lhs = {json.dumps(x, ensure_ascii=False) for x in out[k]}
                rhs = {json.dumps(x, ensure_ascii=False) for x in v}
                out[k] = [json.loads(x) for x in sorted(lhs | rhs)]
            else:
                out[k] = v
        return out

    moved_counts = {'analysis_confidence': 0, 'relationship_analysis': 0, 'explanatory_material': 0, 'attribution': 0}

    for entry in structured_data:
        la = entry.get('linguistic_analysis')
        if not isinstance(la, dict):
            continue

        # Normalize analysis_confidence
        top_ac = entry.get('analysis_confidence') or {}
        nested_ac = la.get('analysis_confidence') or {}
        has_top = _has_ac_fields(top_ac)
        has_nested = _has_ac_fields(nested_ac)
        if has_top or has_nested:
            entry['analysis_confidence'] = _merge_ac(top_ac if isinstance(top_ac, dict) else {}, nested_ac if isinstance(nested_ac, dict) else {})
            if 'analysis_confidence' in la:
                del la['analysis_confidence']
            moved_counts['analysis_confidence'] += 1

        # Hoist/meld relationship_analysis
        if 'relationship_analysis' in la:
            entry['relationship_analysis'] = _merge_obj(entry.get('relationship_analysis'), la.pop('relationship_analysis'))
            moved_counts['relationship_analysis'] += 1

        # Hoist/meld explanatory_material
        if 'explanatory_material' in la:
            entry['explanatory_material'] = _merge_obj(entry.get('explanatory_material'), la.pop('explanatory_material'))
            moved_counts['explanatory_material'] += 1

        # Hoist/meld attribution
        if 'attribution' in la:
            entry['attribution'] = _merge_obj(entry.get('attribution'), la.pop('attribution'))
            moved_counts['attribution'] += 1

    # Save merged data
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open('w', encoding='utf-8') as f:
        json.dump(structured_data, f, ensure_ascii=False, indent=2)

    # Report results
    print(f"\nMerge completed:")
    print(f"  ✅ Successfully merged: {merged_count} witnesses")
    print(f"  ❌ Missing in CSV: {len(missing_in_csv)} witnesses")
    print(f"  ❌ Missing in structured JSON: {len(missing_in_structured)} witnesses")
    # Normalization summary
    print("  🔧 Normalization:")
    for k, v in moved_counts.items():
        print(f"    - {k}: {v}")

    if missing_in_csv:
        print(f"\nWitnesses in structured JSON but missing in CSV:")
        for witness_id in missing_in_csv[:10]:  # Show first 10
            print(f"  - {witness_id}")
        if len(missing_in_csv) > 10:
            print(f"  ... and {len(missing_in_csv) - 10} more")

    if missing_in_structured:
        print(f"\nWitnesses in CSV but missing in structured JSON:")
        for witness_id in missing_in_structured[:10]:  # Show first 10
            print(f"  - {witness_id}")
        if len(missing_in_structured) > 10:
            print(f"  ... and {len(missing_in_structured) - 10} more")

    print(f"\nMerged data saved to: {output_path}")


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


def create_enhanced_web_data(
    merged_json_path: pathlib.Path,
    web_output_path: pathlib.Path
) -> None:
    """Create a simplified JSON structure optimized for web interface."""

    if not merged_json_path.exists():
        raise FileNotFoundError(f"Merged JSON file not found: {merged_json_path}")

    with merged_json_path.open('r', encoding='utf-8') as f:
        merged_data = json.load(f)

    web_data = []

    def _normalize_ac(w: dict) -> Dict[str, Any]:
        ac = (w.get('analysis_confidence') or {})
        def _has_components(d: dict) -> bool:
            if not isinstance(d, dict):
                return False
            if isinstance(d.get('overall_confidence'), (int, float)):
                return True
            for k in ('text_completeness', 'extraction_reliability', 'relationship_indicators', 'linguistic_analysis'):
                if isinstance(d.get(k), (int, float)):
                    return True
            return False
        if not _has_components(ac):
            nested = (w.get('linguistic_analysis') or {}).get('analysis_confidence') or {}
            if _has_components(nested):
                ac = nested
        # compute overall if missing
        def _compute_overall(d: dict):
            try:
                oc = d.get('overall_confidence')
                if isinstance(oc, (int, float)):
                    return float(oc)
                parts = [d.get('text_completeness'), d.get('extraction_reliability'), d.get('relationship_indicators'), d.get('linguistic_analysis')]
                nums = [float(x) for x in parts if isinstance(x, (int, float))]
                if nums:
                    return sum(nums)/len(nums)
            except Exception:
                pass
            return None
        if isinstance(ac, dict):
            oc = _compute_overall(ac)
            if oc is not None and 'overall_confidence' not in ac:
                ac = dict(ac)
                ac['overall_confidence'] = oc
        else:
            ac = {}
        return ac

    for witness in merged_data:
        metadata = witness.get('metadata', {})
        text_data = witness.get('text_data', {})
        ingredients = witness.get('ingredients', {})
        attribution = witness.get('attribution', {})

        # Extract ingredient list for web display
        ingredient_list = []
        for component in ingredients.get('primary_components', []):
            if component.get('substance'):
                ingredient_list.append(component['substance'])

        # Create web-optimized entry
        web_entry = {
            'witness_id': metadata.get('witness_id', ''),
            'date': metadata.get('date', 0),
            'author': metadata.get('author', ''),
            'language': metadata.get('language', ''),
            'genre': metadata.get('genre', ''),
            'source_work': metadata.get('source_work', ''),
            'url': text_data.get('url', ''),
            'full_text': text_data.get('full_text', ''),
            'translation': text_data.get('translation', ''),
            'note': text_data.get('note', ''),
            'attribution': {
                'present': attribution.get('presence', False),
                'source_name': attribution.get('source_name', ''),
                'confidence': attribution.get('confidence', 0)
            },
            'ingredients': ingredient_list,
            'confidence': float((_normalize_ac(witness) or {}).get('overall_confidence') or 0),
            'has_full_text': text_data.get('has_full_text', False),
            'has_translation': text_data.get('has_translation', False),
            'text_length': text_data.get('text_length', 0),
            'century': calculate_century(metadata.get('date', 0)),
            'data_completeness': metadata.get('data_completeness', 'unknown'),
            'display_notes': witness.get('display_notes', '')
        }

        web_data.append(web_entry)

    # Save web-optimized data
    web_output_path.parent.mkdir(parents=True, exist_ok=True)
    with web_output_path.open('w', encoding='utf-8') as f:
        json.dump(web_data, f, ensure_ascii=False, indent=2)

    print(f"Created web-optimized data with {len(web_data)} witnesses: {web_output_path}")


def calculate_century(date: int) -> int:
    """Calculate century from year."""
    if date <= 0:
        return 0
    return (date - 1) // 100 + 1


def validate_merged_data(merged_json_path: pathlib.Path) -> Dict[str, Any]:
    """Validate the merged data and report statistics."""

    if not merged_json_path.exists():
        raise FileNotFoundError(f"Merged JSON file not found: {merged_json_path}")

    with merged_json_path.open('r', encoding='utf-8') as f:
        data = json.load(f)

    stats = {
        'total_witnesses': len(data),
        'with_full_text': 0,
        'with_translation': 0,
        'with_both': 0,
        'missing_both': 0,
        'by_language': {},
        'by_century': {},
        'by_completeness': {}
    }

    for witness in data:
        metadata = witness.get('metadata', {})
        text_data = witness.get('text_data', {})

        # Text availability
        has_full_text = text_data.get('has_full_text', False)
        has_translation = text_data.get('has_translation', False)

        if has_full_text:
            stats['with_full_text'] += 1
        if has_translation:
            stats['with_translation'] += 1
        if has_full_text and has_translation:
            stats['with_both'] += 1
        if not has_full_text and not has_translation:
            stats['missing_both'] += 1

        # Language distribution
        language = metadata.get('language', 'unknown')
        stats['by_language'][language] = stats['by_language'].get(language, 0) + 1

        # Century distribution
        date = metadata.get('date', 0)
        century = calculate_century(date)
        if century > 0:
            stats['by_century'][century] = stats['by_century'].get(century, 0) + 1

        # Completeness distribution
        completeness = metadata.get('data_completeness', 'unknown')
        stats['by_completeness'][completeness] = stats['by_completeness'].get(completeness, 0) + 1

    return stats
