"""Verdicts, findings, and the top-level Evaluation record."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any

from .action import ProposedAction


class Verdict(str, Enum):
    """The final (or per-principle suggested) verdict on an action.

    Ordered from most permissive to least, except that
    ``ESCALATE_TO_HUMAN`` sits above ``REFUSE``: it means "I am not
    confident enough to decide; a human should".
    """

    ALLOW = "allow"
    ALLOW_WITH_CAVEATS = "allow_with_caveats"
    REVISE = "revise"
    REFUSE = "refuse"
    ESCALATE_TO_HUMAN = "escalate_to_human"

    @property
    def strictness(self) -> int:
        return {
            Verdict.ALLOW: 0,
            Verdict.ALLOW_WITH_CAVEATS: 1,
            Verdict.REVISE: 2,
            Verdict.ESCALATE_TO_HUMAN: 3,
            Verdict.REFUSE: 4,
        }[self]


@dataclass
class Finding:
    """One principle's verdict on one action.

    A finding is the atomic output of a check. The engine aggregates many
    findings into one Evaluation.

    Attributes
    ----------
    principle_id:
        The principle this finding speaks for.
    verdict:
        What this principle thinks should happen.
    score:
        Compliance score in [-1.0, +1.0]: +1 = exemplary adherence,
        0 = neutral, -1 = flagrant violation.
    severity:
        How badly the principle is affected, in [0.0, 1.0]. Independent of
        sign — a strongly-positive finding can still have high severity
        (e.g. great act of courage) but severity is mainly used for weighting
        violations.
    reasons:
        Human-readable short reasons. Shown in the audit log and, when the
        verdict is ``REFUSE`` or ``REVISE``, in the explanation to the user.
    veto:
        If True, this finding insists on refusing (or escalating) regardless
        of the overall vote. Only principles with ``can_veto=True`` are
        allowed to set this.
    tags:
        Arbitrary machine-readable tags (``"grave_harm"``, ``"deception"``,
        ...). Useful for downstream policy.
    """

    principle_id: str
    verdict: Verdict
    score: float = 0.0
    severity: float = 0.0
    reasons: list[str] = field(default_factory=list)
    veto: bool = False
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["verdict"] = self.verdict.value
        return d


@dataclass
class Voice:
    """One participant in the Athenian deliberation.

    A Voice bundles a finding with the weight the principle carries and the
    Law XII band it sits in, so the weighted vote can be reproduced from the
    audit record alone.
    """

    principle_id: str
    weight: float
    finding: Finding
    band: str = ""
    vote_weight: float = 0.0
    ballot: str = "abstain"

    def to_dict(self) -> dict[str, Any]:
        return {
            "principle_id": self.principle_id,
            "weight": self.weight,
            "band": self.band,
            "vote_weight": self.vote_weight,
            "ballot": self.ballot,
            "finding": self.finding.to_dict(),
        }


@dataclass
class Evaluation:
    """The complete, auditable record of one evaluation."""

    action: ProposedAction
    verdict: Verdict
    aggregate_score: float
    findings: list[Finding]
    voices: list[Voice]
    rationale: str
    vetoes: list[str] = field(default_factory=list)
    caveats: list[str] = field(default_factory=list)
    deciding_principles: list[str] = field(default_factory=list)
    tally: dict[str, float] = field(default_factory=dict)
    charter_name: str = ""
    charter_version: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "charter_name": self.charter_name,
            "charter_version": self.charter_version,
            "verdict": self.verdict.value,
            "aggregate_score": self.aggregate_score,
            "rationale": self.rationale,
            "vetoes": list(self.vetoes),
            "caveats": list(self.caveats),
            "deciding_principles": list(self.deciding_principles),
            "tally": dict(self.tally),
            "findings": [f.to_dict() for f in self.findings],
            "voices": [v.to_dict() for v in self.voices],
            "action": self.action.to_dict(),
        }
