import subprocess, sys, pathlib
def run(*args):
    return subprocess.run([sys.executable, "-m", "eggphy.cli", *args],
                          capture_output=True, text=True)
def test_status_runs_even_without_data():
    # ensure project root
    root = pathlib.Path(__file__).resolve().parents[1]
    data = root / "data" / "witnesses.csv"
    if not data.exists():
        data.parent.mkdir(parents=True, exist_ok=True)
        data.write_text("WitnessID,Date,Author\n", encoding="utf-8")
    p = run("status")
    assert p.returncode == 0
    assert "witnesses:" in p.stdout
