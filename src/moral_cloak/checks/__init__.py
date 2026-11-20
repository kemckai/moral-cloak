"""Checks: pluggable per-principle evaluators.

A check implements :meth:`Check.evaluate` for one principle and returns a
:class:`~moral_cloak.verdicts.Finding`. The built-in checks in
:mod:`moral_cloak.checks.heuristics` are rule-based and have no network
dependencies. :class:`LLMJudgeCheck` is the seam for a model-based judge.
"""
from __future__ import annotations

from .base import Check, CheckFactory, CheckRegistry, LLMJudgeCheck
from .heuristics import build_default_registry, heuristic_ids

__all__ = [
    "Check",
    "CheckFactory",
    "CheckRegistry",
    "LLMJudgeCheck",
    "build_default_registry",
    "heuristic_ids",
]
