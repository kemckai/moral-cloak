"""The moral-cloak command on the charter, the prompt, and the examples."""
import json
import subprocess
import sys
from io import StringIO
from pathlib import Path

from moral_cloak.cli import main

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


def test_charter_command_lists_the_twelve_laws():
    out = StringIO()
    assert main(["charter"], out=out) == 0
    text = out.getvalue()
    assert "Law I. Do no grave harm" in text
    assert "Law XII. Order of the laws" in text
    assert "ἰσονομία" in text
    assert "grave_harm: grave_harm" in text


def test_charter_json_round_trip():
    out = StringIO()
    assert main(["charter", "--json"], out=out) == 0
    payload = json.loads(out.getvalue())
    assert [item["law"] for item in payload["principles"]] == [
        "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII",
    ]
    assert payload["principles"][0]["can_veto"] is True


def test_prompt_command_matches_the_library():
    out = StringIO()
    assert main(["prompt"], out=out) == 0
    assert "You operate under the moral_cloak charter." in out.getvalue()


def test_evaluate_examples_and_strict_exit_codes(tmp_path):
    out = StringIO()
    cooking = EXAMPLES / "allow_cooking.json"
    assert main(["evaluate", str(cooking)], out=out) == 0
    assert "verdict: allow" in out.getvalue()

    out = StringIO()
    grave = EXAMPLES / "refuse_grave_harm.json"
    assert main(["evaluate", str(grave), "--strict"], out=out) == 1
    assert "verdict: refuse" in out.getvalue()
    assert "vetoes:  grave_harm" in out.getvalue()

    out = StringIO()
    audit_path = tmp_path / "audit.json"
    assert (
        main(
            ["evaluate", str(EXAMPLES / "honesty_over_helpfulness.json"), "--json", "--audit", str(audit_path)],
            out=out,
        )
        == 0
    )
    payload = json.loads(out.getvalue())
    assert payload["verdict"] == "refuse"
    assert "parrhesia" in payload["deciding_principles"]
    saved = json.loads(audit_path.read_text(encoding="utf-8"))
    assert saved[0]["evaluation"]["verdict"] == "refuse"


def test_evaluate_a_list_of_actions(tmp_path):
    batch = tmp_path / "batch.json"
    cooking = json.loads((EXAMPLES / "allow_cooking.json").read_text(encoding="utf-8"))
    timid = json.loads((EXAMPLES / "revise_over_refusal.json").read_text(encoding="utf-8"))
    batch.write_text(json.dumps([cooking, timid]), encoding="utf-8")
    out = StringIO()
    assert main(["evaluate", str(batch), "--json"], out=out) == 0
    payload = json.loads(out.getvalue())
    assert [item["verdict"] for item in payload] == ["allow", "revise"]


def test_missing_file_is_a_usage_error():
    assert main(["evaluate", "does-not-exist.json"], out=StringIO()) == 2


def test_module_entry_point_runs():
    completed = subprocess.run(
        [sys.executable, "-m", "moral_cloak", "evaluate", str(EXAMPLES / "allow_cooking.json")],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        env={**dict(**{k: v for k, v in __import__("os").environ.items()}), "PYTHONPATH": str(ROOT / "src")},
    )
    assert completed.returncode == 0
    assert "verdict: allow" in completed.stdout
