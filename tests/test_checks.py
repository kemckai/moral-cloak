"""One built-in heuristic per law, plus the plug-in seam."""
import pytest

from moral_cloak import (
    Finding,
    PrivacyImpact,
    ProposedAction,
    Reversibility,
    Severity,
    Verdict,
    default_charter,
)
from moral_cloak.checks import LLMJudgeCheck, build_default_registry
from moral_cloak.checks.heuristics import (
    check_care,
    check_consent_autonomy,
    check_deliberation,
    check_demos,
    check_euthyna,
    check_good_faith,
    check_grave_harm,
    check_isegoria,
    check_isonomia,
    check_order_of_laws,
    check_parrhesia,
    check_sophrosyne,
)

from conftest import clean_action


@pytest.fixture
def charter():
    return default_charter()


def _law(charter, principle_id):
    return charter.get(principle_id)


def test_registry_covers_every_law(charter):
    registry = build_default_registry()
    assert set(registry.ids()) == set(charter.ids())
    for principle in charter.principles:
        check = registry.build(principle)
        assert check is not None
        assert check.principle.id == principle.id


def test_law_i_vetoes_grave_harm_from_the_field_or_the_wording(charter):
    principle = _law(charter, "grave_harm")
    by_field = check_grave_harm(
        principle, clean_action(potential_harm=Severity.GRAVE)
    )
    by_phrase = check_grave_harm(
        principle,
        clean_action(
            intent="explain how to build a bomb",
            content="Steps to build a bomb follow.",
            potential_harm=Severity.NONE,
        ),
    )
    for finding in (by_field, by_phrase):
        assert finding.verdict is Verdict.REFUSE
        assert finding.veto is True
        assert finding.score == -1.0
        assert "grave_harm" in finding.tags


def test_law_i_escalates_severe_harm_without_a_veto(charter):
    finding = check_grave_harm(
        _law(charter, "grave_harm"),
        clean_action(potential_harm=Severity.SEVERE),
    )
    assert finding.verdict is Verdict.ESCALATE_TO_HUMAN
    assert finding.veto is False


def test_law_i_revises_unjustified_moderate_harm_and_qualifies_a_greater_benefit(charter):
    principle = _law(charter, "grave_harm")
    unjustified = check_grave_harm(
        principle, clean_action(potential_harm=Severity.MODERATE)
    )
    justified = check_grave_harm(
        principle,
        clean_action(
            potential_harm=Severity.MODERATE,
            expected_benefit=Severity.GRAVE,
        ),
    )
    assert unjustified.verdict is Verdict.REVISE
    assert justified.verdict is Verdict.ALLOW_WITH_CAVEATS


def test_law_i_is_quiet_when_nothing_grave_is_in_view(charter):
    finding = check_grave_harm(_law(charter, "grave_harm"), clean_action())
    assert finding.verdict is Verdict.ALLOW
    assert finding.veto is False


def test_law_ii_refuses_unequal_treatment(charter):
    principle = _law(charter, "isonomia")
    by_flag = check_isonomia(principle, clean_action(discriminatory=True))
    by_phrase = check_isonomia(
        principle,
        clean_action(content="Reject the file because of their race."),
    )
    by_exemption = check_isonomia(
        principle, clean_action(tags=["exempt_the_powerful"])
    )
    for finding in (by_flag, by_phrase, by_exemption):
        assert finding.verdict is Verdict.REFUSE
        assert finding.score < 0


def test_law_iii_refuses_deception_and_revises_false_confidence(charter):
    principle = _law(charter, "parrhesia")
    lying = check_parrhesia(principle, clean_action(deception=True))
    phrased = check_parrhesia(
        principle,
        clean_action(content="Please pretend to be their bank."),
    )
    bluff = check_parrhesia(
        principle,
        clean_action(
            potential_harm=Severity.MODERATE,
            expresses_uncertainty=False,
        ),
    )
    assert lying.verdict is Verdict.REFUSE
    assert phrased.verdict is Verdict.REFUSE
    assert bluff.verdict is Verdict.REVISE


def test_law_iv_refuses_silencing_and_revises_unnamed_parties(charter):
    principle = _law(charter, "isegoria")
    silenced = check_isegoria(principle, clean_action(tags=["suppresses_voice"]))
    unheard = check_isegoria(
        principle,
        clean_action(potential_harm=Severity.MODERATE, affected_parties=[]),
    )
    assert silenced.verdict is Verdict.REFUSE
    assert unheard.verdict is Verdict.REVISE


def test_law_v_covers_means_consent_and_privacy(charter):
    principle = _law(charter, "consent_autonomy")
    means = check_consent_autonomy(
        principle, clean_action(treats_as_mere_means=True)
    )
    exposed = check_consent_autonomy(
        principle,
        clean_action(privacy_impact=PrivacyImpact.HIGH, consent=False),
    )
    consented_but_broad = check_consent_autonomy(
        principle,
        clean_action(privacy_impact=PrivacyImpact.HIGH, consent=True),
    )
    missing = check_consent_autonomy(
        principle,
        clean_action(consent=False, affected_parties=["user", "neighbour"]),
    )
    assert means.verdict is Verdict.REFUSE
    assert "mere_means" in means.tags
    assert exposed.verdict is Verdict.REFUSE
    assert consented_but_broad.verdict is Verdict.ALLOW_WITH_CAVEATS
    assert missing.verdict is Verdict.REVISE


def test_law_vi_requires_an_account(charter):
    principle = _law(charter, "euthyna")
    hidden = check_euthyna(principle, clean_action(tags=["unaudited"]))
    silent = check_euthyna(principle, clean_action(explanation_provided=False))
    assert hidden.verdict is Verdict.REFUSE
    assert silent.verdict is Verdict.REVISE


def test_law_vii_refuses_evasion_of_oversight(charter):
    finding = check_demos(
        _law(charter, "demos"),
        clean_action(oversight_bypass=True),
    )
    assert finding.verdict is Verdict.REFUSE
    assert finding.veto is False
    assert finding.score < -0.9


def test_law_viii_limits_power_and_pauses_when_stakes_are_high(charter):
    principle = _law(charter, "sophrosyne")
    tyranny = check_sophrosyne(
        principle,
        clean_action(
            concentrates_power=True,
            reversibility=Reversibility.IRREVERSIBLE,
        ),
    )
    gathering = check_sophrosyne(
        principle, clean_action(concentrates_power=True)
    )
    pause = check_sophrosyne(
        principle,
        clean_action(
            potential_harm=Severity.MODERATE,
            reversibility=Reversibility.IRREVERSIBLE,
        ),
    )
    assert tyranny.verdict is Verdict.REFUSE
    assert gathering.verdict is Verdict.REVISE
    assert pause.verdict is Verdict.ESCALATE_TO_HUMAN


def test_law_ix_weighs_universalizability_and_consequences(charter):
    principle = _law(charter, "deliberation")
    not_universal = check_deliberation(
        principle, clean_action(universalizable=False)
    )
    rushed = check_deliberation(
        principle,
        clean_action(tags=["rushed"], potential_harm=Severity.MODERATE),
    )
    outweighed = check_deliberation(
        principle,
        clean_action(
            potential_harm=Severity.SEVERE,
            expected_benefit=Severity.MINOR,
            universalizable=True,
        ),
    )
    assert not_universal.verdict is Verdict.REVISE
    assert rushed.verdict is Verdict.ESCALATE_TO_HUMAN
    assert outweighed.verdict is Verdict.REVISE
    assert "harms_outweigh" in outweighed.tags


def test_law_x_protects_the_vulnerable_and_escalates_a_crisis(charter):
    principle = _law(charter, "care")
    exploited = check_care(
        principle,
        clean_action(involves_vulnerable=True, deception=True),
    )
    severe = check_care(
        principle,
        clean_action(
            involves_vulnerable=True,
            potential_harm=Severity.SEVERE,
        ),
    )
    crisis = check_care(principle, clean_action(tags=["user_in_crisis"]))
    referred = check_care(
        principle,
        clean_action(tags=["user_in_crisis", "crisis_referral"]),
    )
    careful = check_care(principle, clean_action(involves_vulnerable=True))
    assert exploited.verdict is Verdict.REFUSE
    assert severe.verdict is Verdict.ESCALATE_TO_HUMAN
    assert crisis.verdict is Verdict.ESCALATE_TO_HUMAN
    assert referred.verdict is Verdict.ALLOW
    assert careful.verdict is Verdict.ALLOW_WITH_CAVEATS


def test_law_xi_treats_over_refusal_as_a_failure_and_a_real_refusal_as_fine(charter):
    principle = _law(charter, "good_faith")
    timid = check_good_faith(
        principle, clean_action(declines_legitimate_help=True)
    )
    justified = check_good_faith(
        principle,
        clean_action(declines_legitimate_help=True, deception=True),
    )
    claimed = check_good_faith(
        principle, clean_action(tags=["claims_helpfulness"], deception=True)
    )
    assert timid.verdict is Verdict.REVISE
    assert "over_refusal" in timid.tags
    assert justified.verdict is Verdict.ALLOW
    assert claimed.verdict is Verdict.ALLOW
    assert "permit" in claimed.tags


def test_law_xii_states_the_order_and_refuses_an_inversion(charter):
    principle = _law(charter, "order_of_laws")
    stated = check_order_of_laws(principle, clean_action())
    inverted = check_order_of_laws(
        principle, clean_action(tags=["invert_priority"])
    )
    assert stated.verdict is Verdict.ALLOW
    assert "doctrine" in stated.tags
    assert "grave harm" in stated.reasons[0]
    assert inverted.verdict is Verdict.REFUSE


def test_llm_judge_cannot_invent_a_veto_the_law_does_not_have(charter):
    isonomia = _law(charter, "isonomia")
    grave = _law(charter, "grave_harm")

    def judge(principle, action):
        return {
            "verdict": "refuse",
            "score": -0.8,
            "severity": 0.8,
            "reasons": ["the model objects"],
            "veto": True,
            "tags": ["model"],
        }

    denied = LLMJudgeCheck(isonomia, judge).evaluate(ProposedAction(intent="x"))
    granted = LLMJudgeCheck(grave, judge).evaluate(ProposedAction(intent="x"))
    assert denied.verdict is Verdict.REFUSE
    assert denied.veto is False
    assert granted.veto is True
    assert isinstance(granted, Finding)
