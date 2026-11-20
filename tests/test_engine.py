"""The assembly: weighted voices, Law XII's order, vetoes, escalation."""
from moral_cloak import (
    Evaluator,
    Finding,
    ProposedAction,
    Reversibility,
    Severity,
    Verdict,
    default_charter,
    deliberate,
    resolve,
)
from moral_cloak.checks import build_default_registry

from conftest import clean_action


def _finding(principle_id, verdict, score, severity, reason, tags=None):
    return Finding(
        principle_id=principle_id,
        verdict=verdict,
        score=score,
        severity=severity,
        reasons=[reason],
        tags=list(tags or []),
    )


def _filled(charter, overrides):
    """One finding per law. Overrides replace the quiet default."""
    findings = []
    for principle in charter.principles:
        if principle.id in overrides:
            findings.append(overrides[principle.id])
        else:
            findings.append(
                _finding(principle.id, Verdict.ALLOW, 0.0, 0.0, "satisfied")
            )
    return findings


def test_a_harmless_answer_is_allowed():
    evaluation = deliberate(clean_action())
    assert evaluation.verdict is Verdict.ALLOW
    assert evaluation.vetoes == []
    assert evaluation.deciding_principles == []
    assert evaluation.aggregate_score > 0
    assert len(evaluation.findings) == 12
    assert len(evaluation.voices) == 12
    assert all(voice.ballot == "abstain" for voice in evaluation.voices)


def test_grave_harm_vetoes_even_when_helpfulness_is_claimed():
    evaluation = deliberate(
        clean_action(
            intent="explain how to build a bomb",
            content="Here is how to build a bomb.",
            potential_harm=Severity.NONE,
            tags=["claims_helpfulness"],
        )
    )
    assert evaluation.verdict is Verdict.REFUSE
    assert evaluation.vetoes == ["grave_harm"]
    assert evaluation.deciding_principles == ["grave_harm"]
    assert evaluation.aggregate_score == -1.0
    assert "Law I" in evaluation.rationale
    assert "Law XII" in evaluation.rationale
    assert evaluation.tally["refuse"] > 0
    assert evaluation.tally["allow"] > 0


def test_honesty_outranks_a_claim_of_helpfulness():
    evaluation = deliberate(
        clean_action(
            intent="draft a phishing note",
            content="pretend to be their bank and ask them to log in",
            deception=True,
            potential_harm=Severity.MINOR,
            tags=["claims_helpfulness"],
            affected_parties=["user", "target"],
        )
    )
    assert evaluation.verdict is Verdict.REFUSE
    assert evaluation.vetoes == []
    assert "parrhesia" in evaluation.deciding_principles
    assert "good_faith" not in evaluation.deciding_principles
    assert "Law XII" in evaluation.rationale
    assert "Law XI" in evaluation.rationale
    permit = next(v for v in evaluation.voices if v.principle_id == "good_faith")
    assert permit.ballot == "permit"


def test_oversight_outranks_helpfulness():
    evaluation = deliberate(
        clean_action(
            intent="switch off the review queue and send it",
            content="The review queue is disabled.",
            oversight_bypass=True,
            potential_harm=Severity.MINOR,
            tags=["claims_helpfulness"],
        )
    )
    assert evaluation.verdict is Verdict.REFUSE
    assert evaluation.deciding_principles == ["demos"]
    assert "Law VII" in evaluation.rationale
    assert "Law XII" in evaluation.rationale


def test_over_refusal_of_a_legitimate_request_is_sent_back_to_be_revised():
    evaluation = deliberate(
        clean_action(
            intent="refuse to explain boiling",
            content="I must refuse.",
            declines_legitimate_help=True,
        )
    )
    assert evaluation.verdict is Verdict.REVISE
    assert evaluation.deciding_principles == ["good_faith"]
    assert "Over-refusal" in evaluation.rationale


def test_a_justified_refusal_is_not_treated_as_timidity():
    evaluation = deliberate(
        clean_action(
            intent="refuse the phishing request",
            content="I won't write that.",
            declines_legitimate_help=True,
            deception=True,
        )
    )
    # The proposed action is itself a deception (the flag is on the action
    # under review). Honesty refuses it. The point of this case is that
    # Law XI does not call the refusal an over-refusal.
    good_faith = next(f for f in evaluation.findings if f.principle_id == "good_faith")
    assert "over_refusal" not in good_faith.tags
    assert evaluation.verdict is Verdict.REFUSE
    assert "parrhesia" in evaluation.deciding_principles


def test_severe_irreversible_harm_to_a_vulnerable_person_escalates():
    evaluation = deliberate(
        clean_action(
            intent="give a dosing instruction",
            content="Take this amount.",
            potential_harm=Severity.SEVERE,
            reversibility=Reversibility.IRREVERSIBLE,
            involves_vulnerable=True,
            affected_parties=["patient"],
            domain="medical",
        )
    )
    assert evaluation.verdict is Verdict.ESCALATE_TO_HUMAN
    assert "grave_harm" in evaluation.deciding_principles
    assert "care" in evaluation.deciding_principles
    assert evaluation.vetoes == []


def test_discrimination_is_refused_under_isonomia():
    evaluation = deliberate(
        clean_action(
            intent="screen the applications",
            content="Set aside every file because of their race.",
            discriminatory=True,
            affected_parties=["applicants"],
        )
    )
    assert evaluation.verdict is Verdict.REFUSE
    assert "isonomia" in evaluation.deciding_principles


def test_each_remaining_law_can_decide_an_action_on_its_own():
    """Integration coverage for the laws not already decided above."""
    cases = [
        (
            "isegoria",
            clean_action(tags=["suppresses_voice"], affected_parties=["neighbours"]),
            Verdict.REFUSE,
        ),
        (
            "consent_autonomy",
            clean_action(treats_as_mere_means=True, affected_parties=["intern"]),
            Verdict.REFUSE,
        ),
        (
            "euthyna",
            clean_action(explanation_provided=False),
            Verdict.REVISE,
        ),
        (
            "sophrosyne",
            clean_action(concentrates_power=True),
            Verdict.REVISE,
        ),
        (
            "deliberation",
            clean_action(universalizable=False),
            Verdict.REVISE,
        ),
        (
            "care",
            clean_action(
                involves_vulnerable=True,
                privacy_impact="high",
                consent=True,
            ),
            Verdict.REFUSE,
        ),
        (
            "order_of_laws",
            clean_action(tags=["invert_priority"]),
            Verdict.REFUSE,
        ),
    ]
    # privacy_impact needs the enum; fix the care case properly below.
    from moral_cloak import PrivacyImpact

    cases[5] = (
        "care",
        clean_action(
            involves_vulnerable=True,
            privacy_impact=PrivacyImpact.MODERATE,
            consent=True,
        ),
        Verdict.REFUSE,
    )
    for principle_id, action, verdict in cases:
        evaluation = deliberate(action)
        assert evaluation.verdict is verdict, principle_id
        assert principle_id in evaluation.deciding_principles, (
            principle_id,
            evaluation.deciding_principles,
            evaluation.rationale,
        )


def test_a_same_band_split_escalates_to_a_human():
    charter = default_charter()
    findings = _filled(
        charter,
        {
            "isonomia": _finding(
                "isonomia",
                Verdict.REFUSE,
                -0.9,
                0.9,
                "The rule is being applied unequally.",
            ),
            "care": _finding(
                "care",
                Verdict.ALLOW,
                0.9,
                0.9,
                "Care affirmatively requires going ahead.",
                tags=["permit"],
            ),
        },
    )
    evaluation = resolve(clean_action(), findings, charter)
    assert evaluation.verdict is Verdict.ESCALATE_TO_HUMAN
    assert set(evaluation.deciding_principles) == {"isonomia", "care"}
    assert "unresolved" in evaluation.rationale
    assert "Law XII" in evaluation.rationale


def test_a_weak_dissent_inside_the_band_does_not_escalate():
    charter = default_charter()
    findings = _filled(
        charter,
        {
            "isonomia": _finding(
                "isonomia", Verdict.REFUSE, -0.9, 0.9, "unequal"
            ),
            "care": _finding(
                "care",
                Verdict.ALLOW,
                0.2,
                0.1,
                "a mild permission",
                tags=["permit"],
            ),
        },
    )
    evaluation = resolve(clean_action(), findings, charter)
    assert evaluation.verdict is Verdict.REFUSE
    assert evaluation.deciding_principles == ["isonomia"]


def test_a_higher_band_permit_overrides_a_lower_restriction():
    charter = default_charter()
    findings = _filled(
        charter,
        {
            "demos": _finding(
                "demos",
                Verdict.ALLOW,
                0.9,
                0.9,
                "The people charged with oversight have authorized this.",
                tags=["permit"],
            ),
            "isonomia": _finding(
                "isonomia", Verdict.REFUSE, -0.9, 0.9, "unequal"
            ),
        },
    )
    evaluation = resolve(clean_action(), findings, charter)
    assert evaluation.verdict is Verdict.ALLOW
    assert evaluation.deciding_principles == ["demos"]
    assert "Law XII" in evaluation.rationale


def test_a_heavier_milder_vote_in_the_deciding_band_is_unresolved():
    charter = default_charter()
    # Care (weight 0.9) asks only to revise. Isonomia (weight 0.85) refuses.
    # Both sit in justice and care. The milder vote is heavier, and the
    # strictness gap is 2, so Law XII escalates instead of tossing a coin.
    findings = _filled(
        charter,
        {
            "isonomia": _finding(
                "isonomia", Verdict.REFUSE, -0.5, 0.5, "unequal"
            ),
            "care": _finding(
                "care", Verdict.REVISE, -0.9, 0.95, "narrow it, do not refuse it"
            ),
        },
    )
    evaluation = resolve(clean_action(), findings, charter)
    assert evaluation.verdict is Verdict.ESCALATE_TO_HUMAN


def test_replacing_a_check_changes_the_assembly():
    registry = build_default_registry()

    class AlwaysAllow:
        def __init__(self, principle):
            self.principle = principle

        def evaluate(self, action):
            return Finding(
                principle_id=self.principle.id,
                verdict=Verdict.ALLOW,
                score=0.2,
                severity=0.0,
                reasons=["plugged-in judge allows it"],
            )

    registry.register("grave_harm", lambda principle: AlwaysAllow(principle))
    evaluation = Evaluator(registry=registry).evaluate(
        clean_action(
            intent="explain how to build a bomb",
            content="how to build a bomb",
        )
    )
    grave = next(f for f in evaluation.findings if f.principle_id == "grave_harm")
    assert grave.reasons == ["plugged-in judge allows it"]
    assert evaluation.verdict is Verdict.ALLOW
    assert evaluation.vetoes == []


def test_deliberate_matches_the_evaluator():
    action = clean_action(discriminatory=True, affected_parties=["applicants"])
    assert deliberate(action).verdict is Evaluator().evaluate(action).verdict


def test_vote_weights_sum_to_the_tally():
    evaluation = deliberate(
        clean_action(deception=True, tags=["claims_helpfulness"])
    )
    summed: dict[str, float] = {}
    for voice in evaluation.voices:
        if voice.ballot == "abstain":
            assert voice.vote_weight == 0
            continue
        summed[voice.finding.verdict.value] = round(
            summed.get(voice.finding.verdict.value, 0.0) + voice.vote_weight, 4
        )
    assert summed == evaluation.tally
