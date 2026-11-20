"""ProposedAction loads from the JSON the CLI accepts."""
from moral_cloak import PrivacyImpact, ProposedAction, Reversibility, Severity


def test_from_dict_parses_enums_and_keeps_unknown_fields():
    action = ProposedAction.from_dict(
        {
            "intent": "look it up",
            "potential_harm": "moderate",
            "expected_benefit": "severe",
            "reversibility": "irreversible",
            "privacy_impact": "high",
            "analyst": "the night desk",
        }
    )
    assert action.potential_harm is Severity.MODERATE
    assert action.expected_benefit is Severity.SEVERE
    assert action.reversibility is Reversibility.IRREVERSIBLE
    assert action.privacy_impact is PrivacyImpact.HIGH
    assert action.metadata["analyst"] == "the night desk"


def test_to_dict_round_trip():
    original = ProposedAction(
        intent="note",
        content="text",
        declines_legitimate_help=True,
        potential_harm=Severity.MINOR,
    )
    restored = ProposedAction.from_dict(original.to_dict())
    assert restored.intent == original.intent
    assert restored.declines_legitimate_help is True
    assert restored.potential_harm is Severity.MINOR
