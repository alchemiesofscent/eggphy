import json
import pathlib
import typer
from typing import Optional

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


if __name__ == "__main__":
    app()