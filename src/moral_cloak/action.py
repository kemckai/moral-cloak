"""Data shape for a proposed AI action to be evaluated.

A ``ProposedAction`` is a structured description of something an AI model is
about to do (produce a response, call a tool, publish a message, take an
action in the world). The evaluator reads these fields; it does not run the
underlying model.

The goal is to be *descriptive and honest*. If a field is unknown, leave it at
its default — the engine treats "unknown" conservatively.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any


class Severity(str, Enum):
    """Potential harm severity, ranked from none to grave.

    ``grave`` harms (irreversible or catastrophic, e.g. loss of life,
    mass harm, severe rights violations) trigger veto rules.
    """

    NONE = "none"
    MINOR = "minor"
    MODERATE = "moderate"
    SEVERE = "severe"
    GRAVE = "grave"

    @property
    def rank(self) -> int:
        return {
            Severity.NONE: 0,
            Severity.MINOR: 1,
            Severity.MODERATE: 2,
            Severity.SEVERE: 3,
            Severity.GRAVE: 4,
        }[self]


class Reversibility(str, Enum):
    REVERSIBLE = "reversible"
    HARD = "hard"
    IRREVERSIBLE = "irreversible"
    UNKNOWN = "unknown"


class PrivacyImpact(str, Enum):
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


@dataclass
class ProposedAction:
    """A proposed AI action under moral review.

    Attributes
    ----------
    intent:
        A short, honest description of what the action is trying to achieve
        ("answer a cooking question", "draft a layoff email", "run `rm -rf`").
    content:
        The full text (or best representation) of what the AI would produce
        or do. Heuristic checks scan this for red-flag patterns.
    affected_parties:
        People or groups materially affected. Use free-form labels like
        ``["user", "third_party_minor", "general_public"]``.
    consent:
        ``True`` if the affected parties have given informed consent for
        this action, ``False`` if they have not, ``None`` if unknown.
    reversibility:
        How recoverable are the effects? Irreversible actions get stricter
        treatment.
    deception:
        ``True`` if the action involves creating a false belief in a target
        (lying, impersonation, manipulation, dark patterns).
    potential_harm:
        Worst-case severity of the harm the action could cause if things go
        wrong.
    expected_benefit:
        Benefit the action is honestly expected to produce, on the same
        scale as ``potential_harm``. Used when weighing harms against
        benefits (Law IX).
    declines_legitimate_help:
        ``True`` when the proposed action is itself a refusal of a request
        that is otherwise legitimate. Law XI treats over-refusal as a
        failure.
    involves_vulnerable:
        Does the action target or materially affect someone in a position of
        reduced agency (minor, patient, person in crisis, detainee, etc.)?
    discriminatory:
        Does the action single out people based on a protected characteristic
        in a way that treats them as less than equal before the rules?
    privacy_impact:
        Degree to which private information about identifiable people is
        collected, inferred, shared or exposed.
    oversight_bypass:
        ``True`` if the action evades, disables, or hides from a legitimate
        human oversight mechanism (logging, approval, audit, supervisor).
    expresses_uncertainty:
        Does the action honestly flag what it does not know?
    explanation_provided:
        Does the action make its reasoning inspectable to the affected
        parties?
    universalizable:
        Would it be acceptable if every similarly-placed agent did this in
        every similar case? ``None`` for "not evaluated".
    concentrates_power:
        Does the action concentrate power, remove checks and balances, or
        make its author harder to hold to account?
    treats_as_mere_means:
        Does the action use a person purely instrumentally, without regard
        for their own ends?
    domain:
        Free-form domain tag ("medical", "legal", "financial", "children",
        "security", "political"). Used by some checks for extra caution.
    tags:
        Arbitrary string tags, e.g. ``["user_in_crisis", "public_figure"]``.
    metadata:
        Any additional structured context. Opaque to the core engine but
        preserved in the audit log.
    """

    intent: str
    content: str = ""
    affected_parties: list[str] = field(default_factory=list)
    consent: bool | None = None
    reversibility: Reversibility = Reversibility.UNKNOWN
    deception: bool = False
    potential_harm: Severity = Severity.NONE
    expected_benefit: Severity = Severity.NONE
    declines_legitimate_help: bool = False
    involves_vulnerable: bool = False
    discriminatory: bool = False
    privacy_impact: PrivacyImpact = PrivacyImpact.NONE
    oversight_bypass: bool = False
    expresses_uncertainty: bool = True
    explanation_provided: bool = True
    universalizable: bool | None = None
    concentrates_power: bool = False
    treats_as_mere_means: bool = False
    domain: str = ""
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["reversibility"] = self.reversibility.value
        d["potential_harm"] = self.potential_harm.value
        d["expected_benefit"] = self.expected_benefit.value
        d["privacy_impact"] = self.privacy_impact.value
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProposedAction":
        """Create an action from a plain dict (e.g. loaded from JSON).

        Unknown fields are stashed into ``metadata`` rather than raising,
        so forward-compatible JSON documents still load.
        """
        known = {f for f in cls.__dataclass_fields__}
        payload: dict[str, Any] = {}
        extras: dict[str, Any] = {}
        for k, v in data.items():
            (payload if k in known else extras)[k] = v
        if "reversibility" in payload and payload["reversibility"] is not None:
            payload["reversibility"] = Reversibility(payload["reversibility"])
        if "potential_harm" in payload and payload["potential_harm"] is not None:
            payload["potential_harm"] = Severity(payload["potential_harm"])
        if "expected_benefit" in payload and payload["expected_benefit"] is not None:
            payload["expected_benefit"] = Severity(payload["expected_benefit"])
        if "privacy_impact" in payload and payload["privacy_impact"] is not None:
            payload["privacy_impact"] = PrivacyImpact(payload["privacy_impact"])
        action = cls(**payload)
        if extras:
            action.metadata = {**extras, **action.metadata}
        return action
