import json
import pathlib
import typer

app = typer.Typer(help="eggphy — minimal CLI scaffold")

DATA_FILE = pathlib.Path("data/witnesses.csv")
MODELS_DIR = pathlib.Path("models")
PROPOSALS = MODELS_DIR / "character_proposals.jsonl"
DECISIONS = MODELS_DIR / "proposal_decisions.jsonl"
CHARACTERS = MODELS_DIR / "characters.jsonl"


def _line_count_csv(path: pathlib.Path) -> int:
    if not path.exists():
        return 0
    with path.open(encoding="utf-8") as f:
        # subtract header if present; never go below 0
        lines = sum(1 for _ in f)
    return max(lines - 1, 0)


@app.command()
def status() -> None:
    """Show quick dataset stats."""
    n = _line_count_csv(DATA_FILE)
    typer.echo(f"witnesses: {n}")


@app.command()
def discover(
    batch_size: int = typer.Option(8, min=1),
    seed: int = 42,
    engine: str = typer.Option("regex", help="regex|llm (llm wired later)")
) -> None:
    """Append a discovery record (stub)."""
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