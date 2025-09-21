import json
import pathlib
import typer
import hashlib
from typing import Optional, List, Any, Dict
from datetime import datetime
from .web_server import serve_web_interface
from .data_converter import (
    csv_to_json_full, json_to_csv, sync_csv_json,
    edit_witness_table, validate_all_witnesses
)
from .data_merger import (
    merge_text_data_into_structured_json,
    create_enhanced_web_data,
    validate_merged_data
)

app = typer.Typer(help="eggphy — minimal CLI scaffold")

# Resolve project root relative to this file so CLI works regardless of CWD
BASE_DIR = pathlib.Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
# prefer canonical filename if present, fall back to test filename
if (DATA_DIR / "recipes.csv").exists():
    DATA_FILE = DATA_DIR / "recipes.csv"
else:
    DATA_FILE = DATA_DIR / "witnesses.csv"

# JSON/CSV data file paths (streamlined)
JSON_FILE = DATA_DIR / "witnesses.json"
# Structured analysis JSON is now canonical at witnesses.json
STRUCTURED_JSON_FILE = JSON_FILE
MERGED_JSON_FILE = JSON_FILE
WEB_JSON_FILE = DATA_DIR / "witnesses_web.json"

MODELS_DIR = BASE_DIR / "models"
PROPOSALS = MODELS_DIR / "character_proposals.jsonl"
DECISIONS = MODELS_DIR / "proposal_decisions.jsonl"
CHARACTERS = MODELS_DIR / "characters.jsonl"


def _line_count_csv(path: pathlib.Path) -> int:
    if not path.exists():
        return 0
    with path.open(encoding="utf-8") as f:
        # read lines and ignore blank lines at end; if there's a header detect by presence of comma
        lines = [ln for ln in (l.rstrip("\n") for l in f) if ln.strip() != ""]
    if not lines:
        return 0
    # heuristic: if first non-empty line looks like a header (contains a comma), subtract 1
    header = 1 if ("," in lines[0]) else 0
    return max(len(lines) - header, 0)


@app.command()
def status() -> None:
    """Show quick dataset stats."""
    n = _line_count_csv(DATA_FILE)
    typer.echo(f"witnesses: {n} (using {DATA_FILE.relative_to(BASE_DIR)})")


@app.command()
def discover(
    batch_size: int = typer.Option(8, min=1),
    seed: int = 42,
    engine: str = typer.Option("regex", help="regex|llm (llm wired later)")
) -> None:
    """Append a discovery record (stub)."""
    engine = engine.lower()
    if engine not in {"regex", "llm"}:
        raise typer.BadParameter("engine must be one of: regex, llm")
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    record = {"engine": engine, "seed": seed, "batch_size": batch_size}
    with PROPOSALS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    typer.echo(f"discovered (stub): {record}")


@app.command()
def review() -> None:
    """Approve one placeholder character (stub)."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    decision = {"proposal": "Attribution to Africanus", "decision": "approve"}
    with DECISIONS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(decision, ensure_ascii=False) + "\n")
    with CHARACTERS.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"id": "C0001", "label": "Attribution to Africanus"}, ensure_ascii=False) + "\n")
    typer.echo("approved: C0001")


@app.command("merge-stemma")
def merge_stemma(
    input_dir: str = typer.Option(
        "models/stemma",
        "--in",
        help="Directory containing per-chunk StemmaAgent JSON arrays (*.json)",
    ),
    out: str = typer.Option(
        "models/stemma.json",
        "--out",
        help="Merged JSON array output path",
    ),
    unique: bool = typer.Option(
        True,
        help="Deduplicate by metadata.witness_id while merging",
    ),
    sort: bool = typer.Option(
        True,
        help="Sort by metadata.witness_id when available",
    ),
) -> None:
    """Merge models/stemma/*.json chunk outputs into one JSON array.

    - Accepts relative paths (resolved against repo root) or absolute paths.
    - Skips files that are not valid JSON arrays with a warning.
    - When unique=True, keeps the first occurrence per witness_id.
    """

    def _resolve(p: str) -> pathlib.Path:
        path = pathlib.Path(p)
        return path if path.is_absolute() else (BASE_DIR / path)

    src_dir = _resolve(input_dir)
    out_path = _resolve(out)

    if not src_dir.exists() or not src_dir.is_dir():
        raise typer.BadParameter(f"input dir not found or not a directory: {src_dir}")

    files = sorted(src_dir.glob("*.json"))
    if not files:
        typer.echo(f"no JSON files found in {src_dir}")
        raise typer.Exit(code=1)

    merged: List[Any] = []
    seen_ids = set()
    total_items = 0

    for fp in files:
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
        except Exception as e:
            typer.secho(f"WARN: failed to read {fp.name}: {e}", fg=typer.colors.YELLOW)
            continue
        if not isinstance(data, list):
            typer.secho(f"WARN: {fp.name} is not a JSON array; skipping", fg=typer.colors.YELLOW)
            continue
        total_items += len(data)
        if not unique:
            merged.extend(data)
            continue
        for item in data:
            try:
                wid = item.get("metadata", {}).get("witness_id")
            except AttributeError:
                wid = None
            if wid is None:
                # keep items without identifiable witness_id
                merged.append(item)
                continue
            if wid in seen_ids:
                continue
            seen_ids.add(wid)
            merged.append(item)

    if sort:
        def _key(x: Any) -> str:
            try:
                return str(x.get("metadata", {}).get("witness_id"))
            except Exception:
                return ""
        merged.sort(key=_key)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")

    typer.echo(
        f"merged {len(files)} file(s), {total_items} items → {len(merged)} unique → {out_path.relative_to(BASE_DIR)}"
    )


@app.command("stemma-batch")
def stemma_batch(
    input_dir: str = typer.Option(
        "data/chunks",
        "--in",
        help="Directory of chunked CSV files",
    ),
    out_dir: str = typer.Option(
        "models/stemma",
        "--out",
        help="Directory for per-chunk JSON outputs",
    ),
    manifest: str = typer.Option(
        "models/stemma_manifest.json",
        help="Where to write the batch manifest JSON",
    ),
    claude_code_mode: str = typer.Option(
        "default",
        "--claude-code-mode",
        help="How to format Claude Code commands: default",
    ),
    write_sh: bool = typer.Option(
        False,
        "--write-sh",
        help="Also emit a shell script with claude commands alongside manifest",
    ),
    skip_existing: bool = typer.Option(
        True,
        help="Skip chunks whose output JSON already exists",
    ),
) -> None:
    """Prepare iterative StemmaAgent runs across all chunk CSVs.

    This generates a manifest of per-chunk commands to run with Claude Code.
    Commands use the format: claude @prompts/stemma_agent.md <chunk> -p --output-format json > <out>

    It does not execute external commands; follow the manifest to run them.
    """

    def _resolve(p: str) -> pathlib.Path:
        path = pathlib.Path(p)
        return path if path.is_absolute() else (BASE_DIR / path)

    src_dir = _resolve(input_dir)
    dst_dir = _resolve(out_dir)
    mani_path = _resolve(manifest)

    if not src_dir.exists() or not src_dir.is_dir():
        raise typer.BadParameter(f"input dir not found or not a directory: {src_dir}")
    dst_dir.mkdir(parents=True, exist_ok=True)

    csvs = sorted(src_dir.glob("*.csv"))
    if not csvs:
        typer.echo(f"no CSV chunks found in {src_dir}")
        raise typer.Exit(code=1)

    entries: List[dict] = []
    mode = claude_code_mode.strip().lower()
    if mode not in {"default"}:
        raise typer.BadParameter("--claude-code-mode must be: default")
    for fp in csvs:
        out_name = fp.with_suffix(".json").name
        out_path = dst_dir / out_name
        status = "pending"
        if out_path.exists() and skip_existing:
            status = "exists"
        rel_in = (src_dir.relative_to(BASE_DIR) / fp.name).as_posix()
        rel_out = (dst_dir.relative_to(BASE_DIR) / out_name).as_posix()
        # Claude Code command format
        cmd = f"claude @prompts/stemma_agent.md {rel_in} -p --output-format json > {rel_out}"
        entries.append({
            "in": rel_in,
            "out": rel_out,
            "status": status,
            "cmd": cmd,
        })

    manifest_obj = {
        "created_at": datetime.utcnow().isoformat() + "Z",
        "input_dir": str(src_dir.relative_to(BASE_DIR).as_posix()),
        "output_dir": str(dst_dir.relative_to(BASE_DIR).as_posix()),
        "skip_existing": skip_existing,
        "chunks": entries,
    }
    mani_path.parent.mkdir(parents=True, exist_ok=True)
    mani_path.write_text(json.dumps(manifest_obj, ensure_ascii=False, indent=2), encoding="utf-8")

    if write_sh:
        sh_path = mani_path.with_suffix(".sh")
        lines = ["#!/usr/bin/env bash", "set -euo pipefail", ""]
        for e in entries:
            if e["status"] == "exists" and skip_existing:
                continue
            lines.append(e["cmd"]) 
        sh_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        try:
            sh_path.chmod(0o755)
        except Exception:
            pass

    typer.echo(f"wrote manifest: {mani_path.relative_to(BASE_DIR)} ({len(entries)} chunks)")
    if write_sh:
        typer.echo(f"wrote script:   {mani_path.with_suffix('.sh').relative_to(BASE_DIR)}")


@app.command("serve")
def serve(
    port: int = typer.Option(8000, help="Port to serve on"),
    no_browser: bool = typer.Option(False, "--no-browser", help="Don't open browser automatically")
) -> None:
    """Start web server for the Historical Egg Writing Recipe Explorer."""
    serve_web_interface(DATA_FILE, port=port, open_browser=not no_browser)


@app.command("convert")
def convert(
    direction: str = typer.Argument(help="Direction: csv-to-json, json-to-csv, or auto"),
    csv_file: Optional[str] = typer.Option(None, "--csv", help="CSV file path (default: data/witnesses.csv)"),
    json_file: Optional[str] = typer.Option(None, "--json", help="JSON file path (default: data/witnesses.json)")
) -> None:
    """Convert between CSV and JSON formats with full data preservation."""
    csv_path = pathlib.Path(csv_file) if csv_file else DATA_FILE
    json_path = pathlib.Path(json_file) if json_file else JSON_FILE

    # Resolve relative paths
    if not csv_path.is_absolute():
        csv_path = BASE_DIR / csv_path
    if not json_path.is_absolute():
        json_path = BASE_DIR / json_path

    try:
        sync_csv_json(csv_path, json_path, direction)
    except Exception as e:
        typer.echo(f"Error during conversion: {e}", err=True)
        raise typer.Exit(code=1)


@app.command("edit")
def edit_table(
    editor: Optional[str] = typer.Option(None, help="Specific editor to use (e.g., 'vd', 'libreoffice --calc')"),
    csv_file: Optional[str] = typer.Option(None, "--csv", help="CSV file to edit (default: data/witnesses.csv)")
) -> None:
    """Open witness data in a table editor for easy editing."""
    csv_path = pathlib.Path(csv_file) if csv_file else DATA_FILE

    if not csv_path.is_absolute():
        csv_path = BASE_DIR / csv_path

    try:
        edit_witness_table(csv_path, editor)
    except Exception as e:
        typer.echo(f"Error opening editor: {e}", err=True)
        raise typer.Exit(code=1)


@app.command("validate")
def validate(
    json_file: Optional[str] = typer.Option(None, "--json", help="JSON file to validate (default: data/witnesses.json)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show all issues in detail")
) -> None:
    """Validate witness data for completeness and consistency."""
    json_path = pathlib.Path(json_file) if json_file else JSON_FILE

    if not json_path.is_absolute():
        json_path = BASE_DIR / json_path

    try:
        issues = validate_all_witnesses(json_path)

        if not issues:
            typer.echo("✅ All witnesses validated successfully!")
            return

        typer.echo(f"❌ Found issues in {len(issues)} witnesses:")

        for witness_id, witness_issues in issues.items():
            if verbose:
                typer.echo(f"\n{witness_id}:")
                for issue in witness_issues:
                    typer.echo(f"  • {issue}")
            else:
                typer.echo(f"  {witness_id}: {len(witness_issues)} issue(s)")

        if not verbose:
            typer.echo("\nUse --verbose to see detailed issues")

        typer.echo(f"\nTotal issues: {sum(len(w_issues) for w_issues in issues.values())}")

    except Exception as e:
        typer.echo(f"Error during validation: {e}", err=True)
        raise typer.Exit(code=1)


@app.command("sync")
def sync_data() -> None:
    """Auto-sync between CSV and JSON based on modification times."""
    try:
        sync_csv_json(DATA_FILE, JSON_FILE, 'auto')
    except Exception as e:
        typer.echo(f"Error during sync: {e}", err=True)
        raise typer.Exit(code=1)


@app.command("merge")
def merge_structured_data(
    csv_file: Optional[str] = typer.Option(None, "--csv", help="CSV file with text data (default: data/raw_sources/witnesses_raw.csv)"),
    structured_file: Optional[str] = typer.Option(None, "--structured", help="Structured JSON file (default: data/witnesses.json)"),
    output_file: Optional[str] = typer.Option(None, "--output", help="Output merged file (default: data/witnesses.json)"),
    create_web: bool = typer.Option(True, "--create-web/--no-web", help="Also create web-optimized JSON"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would change without writing files"),
    force: bool = typer.Option(False, "--force", help="Run even if inputs unchanged since last merge")
) -> None:
    """Merge CSV text data with structured JSON analysis data."""
    # Default CSV source is now the raw_sources file
    default_raw_csv = DATA_DIR / "raw_sources" / "witnesses_raw.csv"
    csv_path = pathlib.Path(csv_file) if csv_file else default_raw_csv
    structured_path = pathlib.Path(structured_file) if structured_file else STRUCTURED_JSON_FILE
    output_path = pathlib.Path(output_file) if output_file else MERGED_JSON_FILE

    # Resolve relative paths
    if not csv_path.is_absolute():
        csv_path = BASE_DIR / csv_path
    if not structured_path.is_absolute():
        structured_path = BASE_DIR / structured_path
    if not output_path.is_absolute():
        output_path = BASE_DIR / output_path

    # Change detection: hash inputs
    def _sha256(path: pathlib.Path) -> str:
        h = hashlib.sha256()
        with path.open('rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                h.update(chunk)
        return h.hexdigest()

    try:
        # Compute input signature
        sig: Dict[str, str] = {}
        if csv_path.exists():
            sig['csv'] = _sha256(csv_path)
        if structured_path.exists():
            sig['structured'] = _sha256(structured_path)
        sig_str = json.dumps(sig, sort_keys=True)

        cache_dir = DATA_DIR / 'cache'
        cache_dir.mkdir(parents=True, exist_ok=True)
        sig_file = cache_dir / 'merge_signature.json'
        prev_sig = sig_file.read_text(encoding='utf-8') if sig_file.exists() else ''

        if not force and prev_sig == sig_str:
            typer.echo("No changes detected in inputs; merge is up-to-date.")
            if dry_run:
                typer.echo("(dry-run) Would skip merging and web generation")
            return

        if dry_run:
            typer.echo("(dry-run) Would merge CSV text into structured JSON and normalize")
            typer.echo(f"Inputs: csv={csv_path.relative_to(BASE_DIR)} structured={structured_path.relative_to(BASE_DIR)}")
            typer.echo(f"Output: {output_path.relative_to(BASE_DIR)} (+ web JSON)")
            return

        merge_text_data_into_structured_json(csv_path, structured_path, output_path)

        if create_web:
            web_path = WEB_JSON_FILE
            if not web_path.is_absolute():
                web_path = BASE_DIR / web_path
            create_enhanced_web_data(output_path, web_path)

        # Save new signature
        sig_file.write_text(sig_str, encoding='utf-8')

    except Exception as e:
        typer.echo(f"Error during merge: {e}", err=True)
        raise typer.Exit(code=1)


@app.command("merge-stats")
def merge_statistics(
    merged_file: Optional[str] = typer.Option(None, "--merged", help="Merged JSON file (default: data/witnesses_merged.json)"),
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Show detailed statistics")
) -> None:
    """Show statistics about merged witness data."""
    merged_path = pathlib.Path(merged_file) if merged_file else MERGED_JSON_FILE

    if not merged_path.is_absolute():
        merged_path = BASE_DIR / merged_path

    try:
        stats = validate_merged_data(merged_path)

        typer.echo(f"📊 Merged Data Statistics ({merged_path.name})")
        typer.echo("=" * 50)
        typer.echo(f"Total witnesses: {stats['total_witnesses']}")
        typer.echo(f"With full text: {stats['with_full_text']}")
        typer.echo(f"With translation: {stats['with_translation']}")
        typer.echo(f"With both: {stats['with_both']}")
        typer.echo(f"Missing both: {stats['missing_both']}")

        if detailed:
            typer.echo(f"\n📈 By Language:")
            for lang, count in sorted(stats['by_language'].items()):
                typer.echo(f"  {lang}: {count}")

            typer.echo(f"\n📅 By Century:")
            for century, count in sorted(stats['by_century'].items()):
                typer.echo(f"  {century}th century: {count}")

            typer.echo(f"\n📋 By Completeness:")
            for completeness, count in sorted(stats['by_completeness'].items()):
                typer.echo(f"  {completeness}: {count}")

    except Exception as e:
        typer.echo(f"Error reading statistics: {e}", err=True)
        raise typer.Exit(code=1)


@app.command("schema-check")
def schema_check(
    json_file: Optional[str] = typer.Option(None, "--json", help="Structured JSON file (default: data/witnesses.json)"),
    fail_on_error: bool = typer.Option(False, "--fail", help="Exit non-zero if any issues found"),
    sample: int = typer.Option(0, "--sample", help="Print details for first N issues")
) -> None:
    """Validate that structured JSON matches the StemmaAgent schema (presence of key sections)."""
    json_path = pathlib.Path(json_file) if json_file else JSON_FILE
    if not json_path.is_absolute():
        json_path = BASE_DIR / json_path

    try:
        data = json.loads(json_path.read_text(encoding='utf-8'))
    except Exception as e:
        typer.echo(f"Error reading JSON: {e}", err=True)
        raise typer.Exit(code=1)

    required = [
        'metadata', 'structural_variants', 'ingredients', 'process_steps',
        'linguistic_analysis', 'relationship_analysis', 'explanatory_material',
        'attribution', 'analysis_confidence'
    ]
    issues = []
    for w in data:
        wid = (w.get('metadata') or {}).get('witness_id', 'UNKNOWN')
        for key in required:
            if key not in w or (key == 'analysis_confidence' and not isinstance(w.get(key), dict)):
                issues.append((wid, f"missing {key}"))

    if not issues:
        typer.echo("✅ Schema check passed: all required sections present")
        return

    typer.echo(f"❌ Schema check failed: {len(issues)} issue(s)")
    for i, (wid, msg) in enumerate(issues[:sample] if sample > 0 else []):
        typer.echo(f"  - {wid}: {msg}")
    if fail_on_error:
        raise typer.Exit(code=1)


@app.command("scripts")
def generate_scripts(
    out_dir: Optional[str] = typer.Option("scripts", "--out", help="Directory to write scripts"),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite existing scripts"),
    shell: str = typer.Option("bash", "--shell", help="Shell header for scripts")
) -> None:
    """Generate shell scripts for Phase I and Phase II pipelines with streamlined filenames."""
    out = BASE_DIR / out_dir
    out.mkdir(parents=True, exist_ok=True)

    def _write(path: pathlib.Path, content: str):
        if path.exists() and not overwrite:
            typer.echo(f"skip (exists): {path.relative_to(BASE_DIR)}")
            return
        path.write_text(content, encoding='utf-8')
        path.chmod(0o755)
        typer.echo(f"wrote {path.relative_to(BASE_DIR)}")

    phase1 = f"""#!/usr/bin/env {shell}
set -euo pipefail

# Phase I — stemmatic reduction (streamlined paths)
# 0) optional: batch manifest
eggphy stemma-batch --in data/chunks --out models/stemma --manifest models/stemma_manifest.json --write-sh || true

# 1) StemmaAgent over chunks
for f in data/chunks/*.csv; do
  claude-code @prompts/stemma_agent.md --in "$f" --out "models/stemma/$(basename "$f").json"
done

# 2) Deduper
claude-code @prompts/deduper.md --in data/witnesses.csv --out models/dedupe_map.json

# 3) RepSelector
claude-code @prompts/rep_selector.md --in models/stemma --out models/reps.json
"""

    phase2 = f"""#!/usr/bin/env {shell}
set -euo pipefail

# Phase II — phylogenetic analysis
claude-code @prompts/proc_discover.md --in models/reps.json --out models/proc_proposals.jsonl
claude-code @prompts/text_discover.md --in models/reps.json --out models/text_proposals.jsonl
claude-code @prompts/context_agent.md --in models/reps.json --out models/context_proposals.jsonl
claude-code @prompts/synthesizer.md --in models --out models/characters.jsonl
claude-code @prompts/coder.md --in models/characters.jsonl --out output/matrices
claude-code @prompts/matrix_builder.md --in output/matrices --out output/matrices
claude-code @prompts/tree_builder.md --in output/matrices --out output/trees
claude-code @prompts/qc_reporter.md --in output --out reports/qc.html
"""

    _write(out / 'phase1.sh', phase1)
    _write(out / 'phase2.sh', phase2)


if __name__ == "__main__":
    app()
