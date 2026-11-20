"""Shared builders for charter tests."""
from moral_cloak import ProposedAction, Reversibility


def clean_action(**overrides) -> ProposedAction:
    """A legitimate, low-stakes action. Overrides replace fields by name."""
    fields = dict(
        intent="Explain how boiling works",
        content="Water boils at 100°C at sea level. Altitude lowers that.",
        affected_parties=["user"],
        consent=True,
        reversibility=Reversibility.REVERSIBLE,
        expresses_uncertainty=True,
        explanation_provided=True,
    )
    fields.update(overrides)
    return ProposedAction(**fields)
