"""Evaluate every example action and print the assembly's verdict.

Run from the repository root:

    python examples/run_examples.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from moral_cloak import Evaluator, ProposedAction  # noqa: E402


def main() -> None:
    evaluator = Evaluator()
    for path in sorted(ROOT.joinpath("examples").glob("*.json")):
        action = ProposedAction.from_dict(json.loads(path.read_text(encoding="utf-8")))
        evaluation = evaluator.evaluate(action)
        decided = ", ".join(evaluation.deciding_principles) or "—"
        print(f"{path.name:<36} {evaluation.verdict.value:<22} {decided}")
    print(f"\n{len(evaluator.audit)} evaluations in the audit log")


if __name__ == "__main__":
    main()
