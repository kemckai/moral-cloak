"""The charter is the twelve laws, in Law XII's order."""
import pytest

from moral_cloak import Charter, Tradition, default_charter
from moral_cloak.charter import DEFAULT_RESOLUTION_BANDS


LAWS = [
    ("I", "grave_harm", "grave_harm", 0, True),
    ("II", "isonomia", "justice_and_care", 3, False),
    ("III", "parrhesia", "honesty_and_consent", 2, False),
    ("IV", "isegoria", "justice_and_care", 3, False),
    ("V", "consent_autonomy", "honesty_and_consent", 2, False),
    ("VI", "euthyna", "justice_and_care", 3, False),
    ("VII", "demos", "human_oversight", 1, False),
    ("VIII", "sophrosyne", "justice_and_care", 3, False),
    ("IX", "deliberation", "justice_and_care", 3, False),
    ("X", "care", "justice_and_care", 3, False),
    ("XI", "good_faith", "helpfulness", 4, False),
    ("XII", "order_of_laws", "doctrine", 5, False),
]


def test_twelve_laws_in_numeral_order():
    charter = default_charter()
    assert len(charter.principles) == 12
    assert [(p.law, p.id) for p in charter.principles] == [(law, pid) for law, pid, *_ in LAWS]


def test_each_law_has_the_band_tier_and_veto_law_xii_requires():
    charter = default_charter()
    for law, pid, band, tier, veto in LAWS:
        principle = charter.get(pid)
        assert principle.law == law
        assert principle.band == band
        assert principle.priority_tier == tier
        assert principle.can_veto is veto
        assert principle.name
        assert principle.description
        assert principle.tradition in Tradition
        assert principle.sources


def test_athenian_laws_carry_a_greek_term():
    charter = default_charter()
    for principle in charter.principles:
        if principle.tradition is Tradition.ATHENIAN:
            assert principle.greek_term, principle.id


def test_only_law_i_can_veto():
    charter = default_charter()
    assert [p.id for p in charter.veto_principles()] == ["grave_harm"]


def test_resolution_bands_are_law_xii():
    charter = default_charter()
    assert charter.resolution_bands == DEFAULT_RESOLUTION_BANDS
    order = [p.id for p in charter.resolution_order]
    assert order[0] == "grave_harm"
    assert order[1] == "demos"
    assert set(order[2:4]) == {"parrhesia", "consent_autonomy"}
    assert set(order[4:10]) == {
        "isonomia",
        "isegoria",
        "euthyna",
        "sophrosyne",
        "deliberation",
        "care",
    }
    assert order[10:] == ["good_faith", "order_of_laws"]


def test_doctrine_is_not_a_voting_band():
    charter = default_charter()
    voting = {pid for _band, members in charter.resolution_bands for pid in members}
    assert "order_of_laws" not in voting
    assert voting == {p.id for p in charter.principles if p.id != "order_of_laws"}


def test_round_trip_through_json_keeps_the_laws():
    charter = default_charter()
    restored = Charter.from_dict(charter.to_dict())
    assert restored.name == charter.name
    assert [(p.id, p.law, p.can_veto, p.greek_term) for p in restored.principles] == [
        (p.id, p.law, p.can_veto, p.greek_term) for p in charter.principles
    ]
    assert restored.resolution_bands == charter.resolution_bands
    assert "ἰσονομία" in restored.to_json()


def test_duplicate_ids_are_rejected():
    charter = default_charter()
    with pytest.raises(ValueError, match="Duplicate"):
        Charter(principles=[charter.principles[0], charter.principles[0]])
