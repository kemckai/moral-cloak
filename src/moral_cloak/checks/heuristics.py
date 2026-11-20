"""Built-in heuristic checks: one per law, no network, no model.

These are a floor, not an oracle. They read the structured fields on a
:class:`~moral_cloak.action.ProposedAction` and a short list of unmistakable
phrases in ``intent`` and ``content``. A caller who describes the action
honestly gets an honest verdict; a caller who mislabels a grave harm as
harmless can still be caught by the phrase list, which is deliberately
narrow.

Replace any of them via :class:`~moral_cloak.checks.CheckRegistry` — for
example with an :class:`~moral_cloak.checks.LLMJudgeCheck`.
"""
from __future__ import annotations

from typing import Callable

from ..action import PrivacyImpact, ProposedAction, Reversibility, Severity
from ..charter import Principle
from ..verdicts import Finding, Verdict
from .base import Check, CheckRegistry


CheckFn = Callable[[Principle, ProposedAction], Finding]

# Narrow on purpose. Substring match, lowercased. These name the category
# of request; they are not procedures.
_GRAVE_PHRASES: tuple[str, ...] = (
    "build a bomb",
    "make a bomb",
    "pipe bomb",
    "synthesize sarin",
    "make sarin",
    "nerve agent",
    "bioweapon",
    "weaponize a virus",
    "child sexual",
    "sexualize a child",
    "how to murder",
    "how to kill someone",
    "how to kill a person",
    "mass shooting",
    "assassinat",
)

_DECEPTION_PHRASES: tuple[str, ...] = (
    "phishing",
    "impersonate",
    "pretend to be their",
    "pretend you are their",
    "forge a signature",
    "deepfake of",
)

_DISCRIMINATION_PHRASES: tuple[str, ...] = (
    "because of their race",
    "because of her race",
    "because of his race",
    "because of their gender",
    "because of her gender",
    "whites only",
    "no women allowed",
    "refuse them because they are",
)


def _blob(action: ProposedAction) -> str:
    return f"{action.intent}\n{action.content}".lower()


def _hit(action: ProposedAction, phrases: tuple[str, ...]) -> str | None:
    blob = _blob(action)
    for phrase in phrases:
        if phrase in blob:
            return phrase
    return None


def _has(action: ProposedAction, *tags: str) -> bool:
    owned = set(action.tags)
    return any(tag in owned for tag in tags)


def _make(
    principle: Principle,
    verdict: Verdict,
    score: float,
    severity: float,
    reasons: list[str],
    *,
    veto: bool = False,
    tags: list[str] | None = None,
) -> Finding:
    return Finding(
        principle_id=principle.id,
        verdict=verdict,
        score=score,
        severity=severity,
        reasons=reasons,
        veto=veto and principle.can_veto,
        tags=list(tags or []),
    )


def _clear(principle: Principle, reason: str, score: float = 0.25) -> Finding:
    return _make(principle, Verdict.ALLOW, score, 0.0, [reason])


# ---------------------------------------------------------------- Law I


def check_grave_harm(principle: Principle, action: ProposedAction) -> Finding:
    phrase = _hit(action, _GRAVE_PHRASES)
    if phrase is not None or action.potential_harm is Severity.GRAVE:
        why = (
            f"The request matches a grave-harm pattern ({phrase!r})."
            if phrase
            else "The action's own account rates the potential harm as grave."
        )
        return _make(
            principle,
            Verdict.REFUSE,
            -1.0,
            1.0,
            [why, "Law I vetoes grave harm. No lower law can buy it back."],
            veto=True,
            tags=["grave_harm"],
        )
    if action.potential_harm is Severity.SEVERE:
        return _make(
            principle,
            Verdict.ESCALATE_TO_HUMAN,
            -0.75,
            0.8,
            [
                "The potential harm is severe. Law I does not veto it "
                "outright, but Law VIII says to pause when the stakes are "
                "this high and hand the call to a human."
            ],
            tags=["severe_harm"],
        )
    if action.potential_harm is Severity.MODERATE:
        if action.expected_benefit.rank >= action.potential_harm.rank + 1:
            return _make(
                principle,
                Verdict.ALLOW_WITH_CAVEATS,
                -0.2,
                0.4,
                [
                    "Moderate harm is in view, but the stated benefit is "
                    "substantially larger. Proceed only if the harm is "
                    "actually necessary."
                ],
                tags=["moderate_harm"],
            )
        return _make(
            principle,
            Verdict.REVISE,
            -0.5,
            0.6,
            [
                "Moderate harm is not justified by the stated benefit. "
                "Find a lower-harm way, or do not do it."
            ],
            tags=["moderate_harm"],
        )
    return _clear(principle, "No grave harm is in view.")


# ---------------------------------------------------------------- Law II


def check_isonomia(principle: Principle, action: ProposedAction) -> Finding:
    phrase = _hit(action, _DISCRIMINATION_PHRASES)
    if action.discriminatory or _has(action, "exempt_the_powerful", "discriminatory") or phrase:
        why = (
            f"The wording sorts people unequally ({phrase!r})."
            if phrase
            else "The action treats people unequally before the rules."
        )
        return _make(
            principle,
            Verdict.REFUSE,
            -0.9,
            0.9,
            [why, "Isonomia: the same rule for the powerful and the powerless."],
            tags=["inequality"],
        )
    return _clear(principle, "No unequal treatment is flagged.")


# ---------------------------------------------------------------- Law III


def check_parrhesia(principle: Principle, action: ProposedAction) -> Finding:
    phrase = _hit(action, _DECEPTION_PHRASES)
    if action.deception or _has(action, "deception") or phrase:
        why = (
            f"The wording is a deception ({phrase!r})."
            if phrase and not action.deception
            else "The action is marked as deceptive."
        )
        return _make(
            principle,
            Verdict.REFUSE,
            -0.9,
            0.9,
            [why, "Parrhesia: say the true thing, including when it costs."],
            tags=["deception"],
        )
    if (
        not action.expresses_uncertainty
        and action.potential_harm.rank >= Severity.MODERATE.rank
    ):
        return _make(
            principle,
            Verdict.REVISE,
            -0.45,
            0.55,
            [
                "The stakes are real and the action states no uncertainty. "
                "Name what is not known."
            ],
            tags=["false_confidence"],
        )
    return _clear(principle, "No deception or false confidence is flagged.")


# ---------------------------------------------------------------- Law IV


def check_isegoria(principle: Principle, action: ProposedAction) -> Finding:
    if _has(action, "suppresses_voice", "silenced"):
        return _make(
            principle,
            Verdict.REFUSE,
            -0.85,
            0.85,
            ["The action suppresses someone's voice. Isegoria forbids that."],
            tags=["silenced"],
        )
    stakes = (
        action.potential_harm.rank >= Severity.MODERATE.rank
        or action.privacy_impact in {PrivacyImpact.MODERATE, PrivacyImpact.HIGH}
        or action.reversibility is Reversibility.IRREVERSIBLE
    )
    if stakes and not action.affected_parties:
        return _make(
            principle,
            Verdict.REVISE,
            -0.45,
            0.5,
            [
                "People are affected and none are named. Say who bears this, "
                "and whether they were heard."
            ],
            tags=["unheard"],
        )
    return _clear(principle, "Affected parties are named, or the stakes are low.")


# ---------------------------------------------------------------- Law V


def check_consent_autonomy(principle: Principle, action: ProposedAction) -> Finding:
    if action.treats_as_mere_means or _has(action, "mere_means"):
        return _make(
            principle,
            Verdict.REFUSE,
            -0.95,
            0.95,
            [
                "A person is being used merely as a means. Their own ends "
                "are not in the action at all."
            ],
            tags=["mere_means"],
        )
    high_privacy = action.privacy_impact is PrivacyImpact.HIGH
    if high_privacy and action.consent is not True:
        return _make(
            principle,
            Verdict.REFUSE,
            -0.85,
            0.85,
            ["Private information would be taken or exposed without consent."],
            tags=["privacy"],
        )
    if high_privacy and action.consent is True:
        return _make(
            principle,
            Verdict.ALLOW_WITH_CAVEATS,
            -0.15,
            0.4,
            ["Consent is present. Still take only what the task needs."],
            tags=["privacy"],
        )
    others_affected = any(p != "user" for p in action.affected_parties)
    if action.consent is False and (
        action.privacy_impact is PrivacyImpact.MODERATE
        or action.potential_harm.rank >= Severity.MINOR.rank
        or others_affected
    ):
        serious = (
            action.potential_harm.rank >= Severity.SEVERE.rank
            or action.privacy_impact is PrivacyImpact.MODERATE
        )
        if serious:
            return _make(
                principle,
                Verdict.REFUSE,
                -0.8,
                0.8,
                ["The action proceeds without consent on something that matters."],
                tags=["no_consent"],
            )
        return _make(
            principle,
            Verdict.REVISE,
            -0.5,
            0.55,
            ["Consent is missing. Ask, or narrow the action until you can."],
            tags=["no_consent"],
        )
    if action.consent is None and action.privacy_impact is PrivacyImpact.MODERATE:
        return _make(
            principle,
            Verdict.REVISE,
            -0.4,
            0.5,
            ["Privacy is affected and consent is unknown. Establish it."],
            tags=["consent_unknown"],
        )
    return _clear(principle, "No consent, privacy, or mere-means problem is flagged.")


# ---------------------------------------------------------------- Law VI


def check_euthyna(principle: Principle, action: ProposedAction) -> Finding:
    if _has(action, "unaudited") or bool(action.metadata.get("disable_audit")):
        return _make(
            principle,
            Verdict.REFUSE,
            -0.85,
            0.85,
            ["The action is built to have no record. Euthyna requires an account."],
            tags=["unaudited"],
        )
    if not action.explanation_provided:
        return _make(
            principle,
            Verdict.REVISE,
            -0.45,
            0.5,
            ["No account is given of what is being done and why. Add one."],
            tags=["no_account"],
        )
    return _clear(principle, "The action can be given an account.")


# ---------------------------------------------------------------- Law VII


def check_demos(principle: Principle, action: ProposedAction) -> Finding:
    if action.oversight_bypass or _has(action, "evade_correction", "oversight_bypass"):
        return _make(
            principle,
            Verdict.REFUSE,
            -0.95,
            0.95,
            [
                "The action evades legitimate human oversight. The people "
                "who watch this system are the authority, not an obstacle."
            ],
            tags=["oversight_bypass"],
        )
    return _clear(
        principle,
        "Oversight is intact. The action can still be corrected.",
        score=0.35,
    )


# ---------------------------------------------------------------- Law VIII


def check_sophrosyne(principle: Principle, action: ProposedAction) -> Finding:
    if action.concentrates_power and action.reversibility is Reversibility.IRREVERSIBLE:
        return _make(
            principle,
            Verdict.REFUSE,
            -0.85,
            0.85,
            [
                "This concentrates power and cannot be undone. That is hubris, "
                "not a measured use of means."
            ],
            tags=["hubris"],
        )
    if action.concentrates_power:
        return _make(
            principle,
            Verdict.REVISE,
            -0.55,
            0.6,
            ["The action gathers power to itself. Use a smaller means."],
            tags=["hubris"],
        )
    high = action.potential_harm.rank >= Severity.SEVERE.rank
    irreversible_and_real = (
        action.reversibility is Reversibility.IRREVERSIBLE
        and action.potential_harm.rank >= Severity.MODERATE.rank
    )
    if high or irreversible_and_real:
        return _make(
            principle,
            Verdict.ESCALATE_TO_HUMAN,
            -0.6,
            0.7,
            [
                "The stakes are high or the step is hard to undo. Pause, "
                "prefer a reversible alternative, and let a human decide."
            ],
            tags=["pause"],
        )
    if action.reversibility is Reversibility.IRREVERSIBLE:
        return _make(
            principle,
            Verdict.ALLOW_WITH_CAVEATS,
            -0.1,
            0.35,
            ["The step is irreversible. Be sure a smaller one will not do."],
            tags=["irreversible"],
        )
    return _clear(principle, "The means are proportioned and recoverable.")


# ---------------------------------------------------------------- Law IX


def check_deliberation(principle: Principle, action: ProposedAction) -> Finding:
    if action.universalizable is False:
        verdict = (
            Verdict.REFUSE
            if action.potential_harm.rank >= Severity.SEVERE.rank
            else Verdict.REVISE
        )
        score = -0.8 if verdict is Verdict.REFUSE else -0.55
        return _make(
            principle,
            verdict,
            score,
            0.7,
            [
                "The maxim is not universalizable: it would defeat itself, "
                "or wreck the practice, if everyone in this position did it."
            ],
            tags=["not_universalizable"],
        )
    if _has(action, "rushed") and action.potential_harm.rank >= Severity.MODERATE.rank:
        return _make(
            principle,
            Verdict.ESCALATE_TO_HUMAN,
            -0.55,
            0.65,
            ["The action is rushed on a question that needed deliberation."],
            tags=["rushed"],
        )
    if (
        action.universalizable is None
        and action.potential_harm.rank >= Severity.SEVERE.rank
    ):
        return _make(
            principle,
            Verdict.ESCALATE_TO_HUMAN,
            -0.5,
            0.6,
            ["A hard case has not been deliberated. Do not close it alone."],
            tags=["undeliberated"],
        )
    harms_dominate = (
        action.potential_harm.rank >= Severity.MODERATE.rank
        and action.expected_benefit.rank + 1 < action.potential_harm.rank
    )
    if harms_dominate:
        return _make(
            principle,
            Verdict.REVISE,
            -0.5,
            0.55,
            ["Weighed honestly, the expected harms outrun the expected benefits."],
            tags=["harms_outweigh"],
        )
    return _clear(
        principle,
        "Nothing here skips deliberation or fails the universalizability test.",
    )


# ---------------------------------------------------------------- Law X


def check_care(principle: Principle, action: ProposedAction) -> Finding:
    if _has(action, "user_in_crisis") and not _has(action, "crisis_referral"):
        return _make(
            principle,
            Verdict.ESCALATE_TO_HUMAN,
            -0.55,
            0.65,
            [
                "The person may be in crisis. Do not handle it as an ordinary "
                "request; bring in a human who can actually help."
            ],
            tags=["crisis"],
        )
    if action.involves_vulnerable and (
        action.deception
        or action.consent is False
        or action.privacy_impact in {PrivacyImpact.MODERATE, PrivacyImpact.HIGH}
    ):
        return _make(
            principle,
            Verdict.REFUSE,
            -0.9,
            0.9,
            [
                "A vulnerable person would be deceived, overridden, or exposed. "
                "Care forbids using that gap."
            ],
            tags=["vulnerable"],
        )
    if action.involves_vulnerable and action.potential_harm.rank >= Severity.SEVERE.rank:
        return _make(
            principle,
            Verdict.ESCALATE_TO_HUMAN,
            -0.6,
            0.7,
            [
                "A vulnerable person faces severe harm. Do not proceed alone; "
                "escalate to a human."
            ],
            tags=["vulnerable"],
        )
    if action.involves_vulnerable and action.potential_harm.rank >= Severity.MODERATE.rank:
        return _make(
            principle,
            Verdict.REVISE,
            -0.5,
            0.55,
            ["A vulnerable person bears a real harm. Narrow the action or stop."],
            tags=["vulnerable"],
        )
    if action.involves_vulnerable:
        return _make(
            principle,
            Verdict.ALLOW_WITH_CAVEATS,
            0.05,
            0.35,
            ["A vulnerable person is affected. Proceed only with extra care."],
            tags=["vulnerable"],
        )
    return _clear(principle, "No special vulnerability is flagged.")


# ---------------------------------------------------------------- Law XI


def check_good_faith(principle: Principle, action: ProposedAction) -> Finding:
    over_refusal = action.declines_legitimate_help or _has(action, "over_refusal")
    blocked = (
        action.potential_harm.rank > Severity.MINOR.rank
        or action.deception
        or action.discriminatory
        or action.oversight_bypass
        or action.treats_as_mere_means
    )
    if over_refusal and not blocked:
        return _make(
            principle,
            Verdict.REVISE,
            -0.7,
            0.7,
            [
                "Over-refusal is a failure. The request is legitimate; "
                "help in good faith instead of dressing timidity up as ethics."
            ],
            tags=["over_refusal"],
        )
    if over_refusal and blocked:
        return _clear(
            principle,
            "The refusal tracks a higher law. That is not an over-refusal.",
            score=0.45,
        )
    # An explicit claim that helpfulness should decide is a real permit-vote.
    # Law XII then has something to outrank: the claim is heard, and it loses
    # to any higher restriction. It is recorded even when the claim is a bad
    # one (a useful lie, for example), so the audit shows the conflict.
    if _has(action, "claims_helpfulness"):
        return _make(
            principle,
            Verdict.ALLOW,
            0.85,
            0.75,
            [
                "Helpfulness is claimed as a reason to proceed. The claim "
                "is heard; it does not outrank a higher law."
            ],
            tags=["permit", "helpfulness"],
        )
    if not blocked and action.intent.strip() and action.content.strip():
        return _clear(
            principle,
            "The action is useful and does not trip a higher law.",
            score=0.55,
        )
    return _clear(principle, "No failure of good-faith usefulness is flagged.", score=0.15)


# ---------------------------------------------------------------- Law XII


_ORDER_TEXT = (
    "Law XII orders the assembly: grave harm, then human oversight, then "
    "honesty and consent, then justice and care, then helpfulness. A "
    "conflict this order does not settle escalates to a human."
)


def check_order_of_laws(principle: Principle, action: ProposedAction) -> Finding:
    if _has(action, "invert_priority") or bool(action.metadata.get("invert_priority")):
        return _make(
            principle,
            Verdict.REFUSE,
            -1.0,
            1.0,
            [
                "The action asks a lower law to override a higher one. "
                + _ORDER_TEXT
            ],
            tags=["inverted_order"],
        )
    return _make(
        principle,
        Verdict.ALLOW,
        0.0,
        0.0,
        [_ORDER_TEXT],
        tags=["doctrine"],
    )


_CHECKS: dict[str, CheckFn] = {
    "grave_harm": check_grave_harm,
    "isonomia": check_isonomia,
    "parrhesia": check_parrhesia,
    "isegoria": check_isegoria,
    "consent_autonomy": check_consent_autonomy,
    "euthyna": check_euthyna,
    "demos": check_demos,
    "sophrosyne": check_sophrosyne,
    "deliberation": check_deliberation,
    "care": check_care,
    "good_faith": check_good_faith,
    "order_of_laws": check_order_of_laws,
}


class HeuristicCheck(Check):
    """Adapts a pure function to the :class:`Check` interface."""

    def __init__(self, principle: Principle, fn: CheckFn) -> None:
        super().__init__(principle)
        self._fn = fn

    def evaluate(self, action: ProposedAction) -> Finding:
        return self._fn(self.principle, action)


def build_default_registry() -> CheckRegistry:
    """A registry with the built-in heuristic for every default law."""
    registry = CheckRegistry()
    for principle_id, fn in _CHECKS.items():
        registry.register(
            principle_id,
            lambda principle, fn=fn: HeuristicCheck(principle, fn),
        )
    return registry


def heuristic_ids() -> list[str]:
    return list(_CHECKS)
