"""Command-line interface.

``moral-cloak charter`` prints the twelve laws.
``moral-cloak prompt`` prints the system-prompt block.
``moral-cloak evaluate FILE`` runs the assembly on a JSON action.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO

from .action import ProposedAction
from .charter import default_charter
from .engine import Evaluator
from .prompt import render_system_prompt
from .verdicts import Evaluation, Verdict


def main(argv: Sequence[str] | None = None, out: TextIO | None = None) -> int:
    """Entry point. Returns a process status code."""
    output = out if out is not None else sys.stdout
    parser = argparse.ArgumentParser(
        prog="moral-cloak",
        description=(
            "Evaluate a proposed AI action against the moral_cloak charter, "
            "or print the charter itself."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    charter_cmd = sub.add_parser("charter", help="print the twelve laws")
    charter_cmd.add_argument(
        "--json",
        action="store_true",
        help="print the charter as JSON",
    )

    sub.add_parser("prompt", help="print the charter as a system prompt")

    evaluate_cmd = sub.add_parser(
        "evaluate",
        help="evaluate one action, or a list of actions, from a JSON file",
    )
    evaluate_cmd.add_argument("file", type=Path, help="path to a JSON action")
    evaluate_cmd.add_argument(
        "--json",
        action="store_true",
        help="print the evaluation record as JSON",
    )
    evaluate_cmd.add_argument(
        "--audit",
        type=Path,
        help="write the euthyna audit log (JSON) to this path",
    )
    evaluate_cmd.add_argument(
        "--strict",
        action="store_true",
        help="exit 1 when any verdict is refuse or escalate_to_human",
    )

    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.command == "charter":
        charter = default_charter()
        if args.json:
            output.write(charter.to_json())
            output.write("\n")
        else:
            output.write(_format_charter())
        return 0

    if args.command == "prompt":
        output.write(render_system_prompt())
        return 0

    try:
        actions = _load_actions(args.file)
    except (OSError, json.JSONDecodeError, ValueError, KeyError) as exc:
        print(f"moral-cloak: {exc}", file=sys.stderr)
        return 2

    evaluator = Evaluator()
    evaluations = [evaluator.evaluate(action) for action in actions]
    if args.json:
        payload: Any
        if len(evaluations) == 1:
            payload = evaluations[0].to_dict()
        else:
            payload = [item.to_dict() for item in evaluations]
        output.write(json.dumps(payload, indent=2, ensure_ascii=False))
        output.write("\n")
    else:
        for index, evaluation in enumerate(evaluations):
            if index:
                output.write("\n")
            output.write(_format_evaluation(evaluation))
    if args.audit is not None:
        evaluator.audit.export(args.audit)
    if args.strict and any(
        item.verdict in {Verdict.REFUSE, Verdict.ESCALATE_TO_HUMAN}
        for item in evaluations
    ):
        return 1
    return 0


def _load_actions(path: Path) -> list[ProposedAction]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        raw_actions = data
    elif isinstance(data, dict) and "actions" in data:
        raw_actions = data["actions"]
    elif isinstance(data, dict) and "action" in data and isinstance(data["action"], dict):
        raw_actions = [data["action"]]
    elif isinstance(data, dict):
        raw_actions = [data]
    else:
        raise ValueError(f"{path} is not an action or a list of actions")
    if not raw_actions:
        raise ValueError(f"{path} contains no actions")
    return [ProposedAction.from_dict(item) for item in raw_actions]


def _format_charter() -> str:
    charter = default_charter()
    lines = [charter.name, ""]
    lines.append(charter.preamble)
    lines.append("")
    for principle in charter.principles:
        term = f"  {principle.greek_term}" if principle.greek_term else ""
        veto = "  [veto]" if principle.can_veto else ""
        lines.append(
            f"Law {principle.law}. {principle.name}{veto}{term}"
        )
        lines.append(f"    id: {principle.id}    tradition: {principle.tradition.value}")
        lines.append(f"    band: {principle.band}    weight: {principle.weight}")
        lines.append(f"    {principle.description}")
        lines.append("")
    lines.append("Resolution order (Law XII), highest first:")
    for index, (band, members) in enumerate(charter.resolution_bands, start=1):
        lines.append(f"  {index}. {band}: {', '.join(members)}")
    lines.append(
        "  Unresolved conflicts inside the deciding band escalate to a human."
    )
    lines.append("")
    return "\n".join(lines)


def _format_evaluation(evaluation: Evaluation) -> str:
    lines = [
        f"verdict: {evaluation.verdict.value}",
        f"score:   {evaluation.aggregate_score:+.3f}",
    ]
    if evaluation.vetoes:
        lines.append(f"vetoes:  {', '.join(evaluation.vetoes)}")
    if evaluation.deciding_principles:
        lines.append(
            "decided: " + ", ".join(evaluation.deciding_principles)
        )
    lines.append("")
    lines.append(evaluation.rationale)
    lines.append("")
    lines.append("findings:")
    for finding in evaluation.findings:
        lines.append(
            f"  {finding.principle_id:<18} {finding.verdict.value:<22} "
            f"score {finding.score:+.2f}  severity {finding.severity:.2f}"
        )
        for reason in finding.reasons:
            lines.append(f"      {reason}")
    if evaluation.caveats:
        lines.append("")
        lines.append("caveats:")
        for caveat in evaluation.caveats:
            lines.append(f"  - {caveat}")
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
