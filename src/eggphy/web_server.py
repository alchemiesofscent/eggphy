import csv
import json
import pathlib
import http.server
import socketserver
import webbrowser
from typing import List, Dict, Any
from urllib.parse import urlparse, parse_qs
import mimetypes


def csv_to_json(csv_path: pathlib.Path) -> List[Dict[str, Any]]:
    """Convert CSV data to JSON format for the web interface."""
    recipes = []

    if not csv_path.exists():
        return recipes

    with csv_path.open('r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Extract author from Source field if possible
            source = row.get('Source', '')
            author = ''
            if ',' in source:
                parts = source.split(',')
                # Try to extract author from various patterns
                if 'Geoponica' in parts[0]:
                    author = 'Cassianus Bassus'
                elif len(parts) > 1:
                    potential_author = parts[0].strip()
                    if not potential_author.startswith('http') and len(potential_author) > 3:
                        author = potential_author

            recipe = {
                'witness_id': row.get('WitnessID', ''),
                'date': int(row.get('Date', 0)) if row.get('Date', '').isdigit() else 0,
                'source': source,
                'language': row.get('Language', ''),
                'full_text': row.get('Full_Text', ''),
                'url': row.get('URL', ''),
                'note': row.get('Note', ''),
                'translation': row.get('Translation', ''),
                'author': author
            }

            # Only include recipes with meaningful data
            if recipe['witness_id'] and recipe['date']:
                recipes.append(recipe)

    return recipes


class EggPhyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP request handler for the eggphy web interface."""

    def __init__(self, *args, csv_path=None, **kwargs):
        self.csv_path = csv_path
        super().__init__(*args, **kwargs)

    def _base_dir(self) -> pathlib.Path:
        return pathlib.Path(__file__).resolve().parents[2]

    def _web_dir(self) -> pathlib.Path:
        return self._base_dir() / 'web'

    def _serve_file(self, path: pathlib.Path) -> bool:
        try:
            if not path.exists() or not path.is_file():
                return False
            ctype, _ = mimetypes.guess_type(str(path))
            self.send_response(200)
            self.send_header('Content-type', ctype or 'application/octet-stream')
            self.end_headers()
            with path.open('rb') as f:
                self.wfile.write(f.read())
            return True
        except Exception:
            return False

    def convert_merged_to_web_format(self, merged_data):
        """Convert full merged JSON to web-friendly format with clean cards but rich details.

        Notes:
        - Some witnesses have analysis_confidence mistakenly nested under
          linguistic_analysis.analysis_confidence. We normalize that here so UI
          consumers always see full_data.analysis_confidence and top-level
          card-level confidence populated.
        """
        web_data = []

        def _normalize_ac(w: dict) -> Dict[str, Any]:
            """Return a normalized analysis_confidence dict for a witness.

            Prefers top-level analysis_confidence; if missing/empty, falls back
            to linguistic_analysis.analysis_confidence. Computes and backfills
            overall_confidence when possible.
            """
            ac = (w.get('analysis_confidence') or {})
            # If no usable fields, fall back to nested location used by some entries
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

            # Compute robust overall confidence if missing
            def _compute_overall(d: dict):
                try:
                    oc = d.get('overall_confidence', None)
                    if isinstance(oc, (int, float)):
                        return float(oc)
                    comps = [
                        d.get('text_completeness'),
                        d.get('extraction_reliability'),
                        d.get('relationship_indicators'),
                        d.get('linguistic_analysis'),
                    ]
                    comps_num = [float(c) for c in comps if isinstance(c, (int, float))]
                    if comps_num:
                        return sum(comps_num) / len(comps_num)
                except Exception:
                    pass
                return None

            if isinstance(ac, dict):
                overall = _compute_overall(ac)
                if overall is not None and 'overall_confidence' not in ac:
                    ac = dict(ac)
                    ac['overall_confidence'] = overall
            else:
                ac = {}

            return ac

        for witness in merged_data:
            metadata = witness.get('metadata', {})
            text_data = witness.get('text_data', {})
            ingredients = witness.get('ingredients', {})
            attribution = witness.get('attribution', {})
            structural_variants = witness.get('structural_variants', {})

            # Normalize analysis_confidence regardless of where it's stored
            analysis_confidence = _normalize_ac(witness)

            # Extract simple ingredient list for cards
            ingredient_list = []
            for component in ingredients.get('primary_components', []):
                if component.get('substance'):
                    ingredient_list.append(component['substance'])

            # Determine gall presence for filtering
            gall_presence = ingredients.get('diagnostic_variants', {}).get('gall_presence', 'unspecified')
            if gall_presence == 'unspecified':
                # Check if galls are in ingredient list
                gall_presence = 'present' if 'galls' in ingredient_list else 'absent'

            # Calculate century
            date = metadata.get('date', 0)
            century = (date - 1) // 100 + 1 if date > 0 else 0

            # Create web entry with clean card data + full details
            web_entry = {
                # Clean card data
                'witness_id': metadata.get('witness_id', ''),
                'date': date,
                'author': metadata.get('author', ''),
                'language': self.normalize_language(metadata.get('language', '')),
                'genre': metadata.get('genre', ''),
                'source_work': metadata.get('source_work', ''),
                'ingredients': ingredient_list,
                'gall_presence': gall_presence,
                'confidence': float(analysis_confidence.get('overall_confidence') or 0) if analysis_confidence else 0.0,
                'process_summary': self.extract_process_summary(witness),
                'attribution': attribution.get('source_name', ''),

                # Rich detail data (for modal)
                'full_data': {
                    'metadata': metadata,
                    'text_data': text_data,
                    'structural_variants': structural_variants,
                    'ingredients_detailed': ingredients,
                    'process_steps': witness.get('process_steps', {}),
                    'linguistic_analysis': witness.get('linguistic_analysis', {}),
                    'attribution_detailed': attribution,
                    'explanatory_material': witness.get('explanatory_material', {}),
                    'relationship_analysis': witness.get('relationship_analysis', {}),
                    'analysis_confidence': analysis_confidence
                },

                # Convenience flags
                'has_full_text': text_data.get('has_full_text', False),
                'has_translation': text_data.get('has_translation', False),
                'text_length': text_data.get('text_length', 0),
                'century': century,
                'data_completeness': metadata.get('data_completeness', 'unknown')
            }

            web_data.append(web_entry)

        return web_data

    def normalize_language(self, lang_code):
        """Convert language codes to display names."""
        lang_map = {
            'grk': 'Greek',
            'grc': 'Greek',
            'lat': 'Latin',
            'eng': 'English',
            'deu': 'German',
            'fra': 'French',
            'ita': 'Italian'
        }
        return lang_map.get(lang_code, lang_code.title() if lang_code else 'Unknown')

    def extract_process_summary(self, witness):
        """Extract a brief process summary from detailed steps."""
        process_steps = witness.get('process_steps', {}).get('preparation_sequence', [])

        if process_steps:
            # Combine first few steps into a summary
            summary_parts = []
            for step in process_steps[:3]:  # First 3 steps
                details = step.get('details', '')
                if details:
                    summary_parts.append(details)

            if summary_parts:
                summary = '. '.join(summary_parts)
                return summary[:200] + '...' if len(summary) > 200 else summary

        # Fallback to looking for explanatory material
        explanatory = witness.get('explanatory_material', {})
        theoretical = explanatory.get('theoretical_explanation', {})
        if theoretical.get('content_summary'):
            return theoretical['content_summary'][:200] + '...'

        return 'Process details available in analysis'

    def do_GET(self):
        parsed_path = urlparse(self.path)

        if parsed_path.path == '/api/witnesses':
            self.serve_json_data()
        elif parsed_path.path == '/' or parsed_path.path == '/index.html':
            self.serve_main_page()
        else:
            # Try serving from web/ directory for static assets (css/js/images)
            web_dir = self._web_dir()
            raw = parsed_path.path.lstrip('/')
            candidates = []
            if raw.startswith('web/'):
                candidates.append(web_dir / raw.split('/', 1)[1])
            elif raw.startswith('static/'):
                candidates.append(web_dir / raw)
            else:
                # root-level asset like /app.css or /favicon.ico
                candidates.append(web_dir / raw)

            for cand in candidates:
                try:
                    cand_resolved = cand.resolve()
                    if web_dir in cand_resolved.parents or cand_resolved == web_dir:
                        if self._serve_file(cand_resolved):
                            return
                except Exception:
                    pass

            # Fallback to default behavior
            super().do_GET()

    def serve_json_data(self):
        """Serve the witness data as JSON."""
        try:
            # Priority: Use merged JSON with full data, then web JSON, then convert from CSV
            # Prefer streamlined filename
            merged_path = self.csv_path.parent / "witnesses.json"
            web_path = self.csv_path.parent / "witnesses_web.json"
            simple_path = self.csv_path.parent / "witnesses.json"

            if merged_path.exists():
                # Use full merged JSON with all structured data
                with merged_path.open('r', encoding='utf-8') as f:
                    merged_data = json.load(f)

                # Convert to web-friendly format while preserving all data
                web_data = self.convert_merged_to_web_format(merged_data)
                json_data = json.dumps(web_data, ensure_ascii=False, indent=2)

            elif web_path.exists():
                # Use existing web-optimized JSON
                with web_path.open('r', encoding='utf-8') as f:
                    json_data = f.read()
            elif simple_path.exists():
                # Use simple JSON (already streamlined)
                with simple_path.open('r', encoding='utf-8') as f:
                    json_data = f.read()
            else:
                # Convert from CSV as fallback
                recipes = csv_to_json(self.csv_path)
                json_data = json.dumps(recipes, ensure_ascii=False, indent=2)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json_data.encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f'Error serving data: {str(e)}'.encode('utf-8'))

    def serve_main_page(self):
        """Serve the main HTML interface."""
        try:
            # Serve the streamlined web index
            html_path = self._web_dir() / 'index.html'

            if html_path.exists():
                with html_path.open('r', encoding='utf-8') as f:
                    content = f.read()

                # Update the loadRecipes function to use real API
                content = content.replace(
                    'async function loadRecipes() {',
                    '''async function loadRecipes() {
            try {
                const response = await fetch('/api/witnesses');
                if (response.ok) {
                    recipes = await response.json();
                    return;
                }
            } catch (e) {
                console.error('Failed to load recipes:', e);
            }

            // Fallback function'''
                )

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))
            else:
                self.send_response(404)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Web interface not found')
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f'Error serving page: {str(e)}'.encode('utf-8'))


def serve_web_interface(csv_path: pathlib.Path, port: int = 8000, open_browser: bool = True):
    """Start a web server to serve the eggphy interface."""

    def handler_factory(*args, **kwargs):
        return EggPhyHTTPRequestHandler(*args, csv_path=csv_path, **kwargs)

    try:
        with socketserver.TCPServer(("", port), handler_factory) as httpd:
            print(f"Serving eggphy web interface at http://localhost:{port}")
            print(f"Using data from: {csv_path}")
            print("Press Ctrl+C to stop the server")

            if open_browser:
                try:
                    webbrowser.open(f"http://localhost:{port}")
                except Exception:
                    pass  # Browser opening is optional

            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"Error: Port {port} is already in use. Try a different port with --port")
        else:
            print(f"Error starting server: {e}")
