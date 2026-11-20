"""Check interface and registry.

Kept separate from ``heuristics`` so the two modules can import each other
without a cycle: heuristics imports the base classes, the package ``__init__``
imports both.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, Dict

from ..action import ProposedAction
from ..charter import Principle
from ..verdicts import Finding, Verdict


class Check(ABC):
    """Abstract base: one check speaks for one principle."""

    def __init__(self, principle: Principle) -> None:
        self.principle = principle

    @abstractmethod
    def evaluate(self, action: ProposedAction) -> Finding:
        """Return a :class:`Finding` describing how *action* fares.

        Implementations should be total — never raise on a well-formed
        action — and should default to a neutral finding when the action
        gives them nothing to complain or cheer about.
        """

    def _neutral(self, reason: str = "No concerns flagged.") -> Finding:
        return Finding(
            principle_id=self.principle.id,
            verdict=Verdict.ALLOW,
            score=0.0,
            severity=0.0,
            reasons=[reason],
        )


CheckFactory = Callable[[Principle], Check]


class CheckRegistry:
    """Maps principle ids to the check that evaluates them.

    Users can replace the built-in heuristic for any principle, for example
    with an LLM-based judge, by calling :meth:`register`.
    """

    def __init__(self) -> None:
        self._factories: Dict[str, CheckFactory] = {}

    def register(self, principle_id: str, factory: CheckFactory) -> None:
        self._factories[principle_id] = factory

    def unregister(self, principle_id: str) -> None:
        self._factories.pop(principle_id, None)

    def build(self, principle: Principle) -> Check | None:
        factory = self._factories.get(principle.id)
        if factory is None:
            return None
        return factory(principle)

    def ids(self) -> list[str]:
        return list(self._factories)


class LLMJudgeCheck(Check):
    """Scaffold for plugging in an LLM-based moral judge for one principle.

    Supply a callable ``judge`` that takes the principle and the action and
    returns a mapping with the keys a :class:`Finding` understands
    (``verdict``, ``score``, ``severity``, ``reasons``, ``veto``, ``tags``).
    The core library stays dependency-free; the model client lives in the
    callable you pass in.

    A judge cannot grant itself a veto the principle does not have.
    """

    def __init__(
        self,
        principle: Principle,
        judge: Callable[[Principle, ProposedAction], dict],
    ) -> None:
        super().__init__(principle)
        self._judge = judge

    def evaluate(self, action: ProposedAction) -> Finding:
        raw = self._judge(self.principle, action) or {}
        return Finding(
            principle_id=self.principle.id,
            verdict=Verdict(raw.get("verdict", Verdict.ALLOW.value)),
            score=float(raw.get("score", 0.0)),
            severity=float(raw.get("severity", 0.0)),
            reasons=list(raw.get("reasons", [])),
            veto=bool(raw.get("veto", False)) and self.principle.can_veto,
            tags=list(raw.get("tags", [])),
        )
