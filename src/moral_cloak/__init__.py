"""moral_cloak — a moral code AI models can operate within.

Grounded in Athenian civic ideals (isonomia, isegoria, parrhesia, euthyna,
sophrosyne, deliberation, demos) and combined with virtue ethics, Kantian
deontology, consequentialism, care ethics and modern human-rights thinking.

Public API:

    from moral_cloak import (
        Charter, Principle, Tradition,
        ProposedAction, Verdict, Finding, Evaluation,
        Evaluator, deliberate, resolve,
        AuditLog, render_system_prompt, default_charter,
    )
"""
from .charter import Charter, Principle, Tradition, default_charter
from .action import ProposedAction, Severity, Reversibility, PrivacyImpact
from .verdicts import Verdict, Finding, Evaluation, Voice
from .engine import Evaluator, deliberate, resolve
from .audit import AuditLog
from .prompt import render_system_prompt

__all__ = [
    "Charter",
    "Principle",
    "Tradition",
    "default_charter",
    "ProposedAction",
    "Severity",
    "Reversibility",
    "PrivacyImpact",
    "Verdict",
    "Finding",
    "Evaluation",
    "Voice",
    "Evaluator",
    "deliberate",
    "resolve",
    "AuditLog",
    "render_system_prompt",
]

__version__ = "0.1.0"
