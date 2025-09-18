import json
import pathlib
import typer
from typing import Optional, List, Any
from datetime import datetime

app = typer.Typer(help="eggphy — minimal CLI scaffold")

# Resolve project root relative to this file so CLI works regardless of CWD
BASE_DIR = pathlib.Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
# prefer canonical filename if present, fall back to test filename
if (DATA_DIR / "recipes.csv").exists():
    DATA_FILE = DATA_DIR / "recipes.csv"
else:
    DATA_FILE = DATA_DIR / "witnesses.csv"

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
    write_sh: bool = typer.Option(
        False,
        "--write-sh",
        help="Also emit a shell script with codex commands alongside manifest",
    ),
    skip_existing: bool = typer.Option(
        True,
        help="Skip chunks whose output JSON already exists",
    ),
) -> None:
    """Prepare iterative StemmaAgent runs across all chunk CSVs.

    This generates a manifest of per-chunk commands to run with Codex CLI:
      codex run stemma --in <chunk.csv> --out <out.json>

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
    for fp in csvs:
        out_name = fp.with_suffix(".json").name
        out_path = dst_dir / out_name
        status = "pending"
        if out_path.exists() and skip_existing:
            status = "exists"
        cmd = (
            f"codex run stemma --in {src_dir.relative_to(BASE_DIR) / fp.name} "
            f"--out {dst_dir.relative_to(BASE_DIR) / out_name}"
        )
        entries.append({
            "in": str((src_dir.relative_to(BASE_DIR) / fp.name).as_posix()),
            "out": str((dst_dir.relative_to(BASE_DIR) / out_name).as_posix()),
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


if __name__ == "__main__":
    app()
