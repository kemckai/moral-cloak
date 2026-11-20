"""Euthyna export, and the system-prompt rendering of the charter."""
import json

from moral_cloak import AuditLog, Evaluator, render_system_prompt
from moral_cloak.engine import deliberate

from conftest import clean_action


def test_every_evaluation_is_appended_to_the_audit_log(tmp_path):
    evaluator = Evaluator()
    first = evaluator.evaluate(clean_action())
    second = evaluator.evaluate(clean_action(deception=True))
    assert len(evaluator.audit) == 2
    assert evaluator.audit[0]["evaluation"]["verdict"] == first.verdict.value
    assert evaluator.audit[1]["evaluation"]["verdict"] == second.verdict.value
    assert evaluator.audit[0]["id"] != evaluator.audit[1]["id"]
    assert "T" in evaluator.audit[0]["timestamp"]

    destination = tmp_path / "euthyna.json"
    evaluator.audit.export(destination)
    loaded = json.loads(destination.read_text(encoding="utf-8"))
    assert loaded[1]["evaluation"]["verdict"] == "refuse"
    assert loaded[1]["evaluation"]["findings"]
    assert loaded[1]["evaluation"]["action"]["deception"] is True
    # The record is enough to reconstruct the vote without the process.
    voice = loaded[0]["evaluation"]["voices"][0]
    assert {"principle_id", "weight", "band", "ballot", "finding"} <= voice.keys()


def test_a_standalone_log_round_trips_an_evaluation():
    evaluation = deliberate(clean_action())
    log = AuditLog()
    entry = log.record(evaluation)
    restored = json.loads(log.to_json())
    assert restored[0]["id"] == entry["id"]
    assert restored[0]["evaluation"]["verdict"] == "allow"
    assert len(restored[0]["evaluation"]["findings"]) == 12


def test_system_prompt_states_every_law_and_the_order():
    text = render_system_prompt()
    for law, name in [
        ("I", "Do no grave harm"),
        ("II", "Equality before the law"),
        ("III", "Honest speech"),
        ("IV", "Every affected voice is heard"),
        ("V", "Consent and autonomy"),
        ("VI", "Audit and accountability"),
        ("VII", "The people are sovereign"),
        ("VIII", "Restraint against hubris"),
        ("IX", "Deliberate before acting"),
        ("X", "Care for the vulnerable"),
        ("XI", "Be useful in good faith"),
        ("XII", "Order of the laws"),
    ]:
        assert f"Law {law}. {name}" in text
    for term in ("ἰσονομία", "παρρησία", "ἰσηγορία", "εὔθυνα", "δῆμος", "σωφροσύνη"):
        assert term in text
    assert "1. grave harm:" in text
    assert "2. human oversight:" in text
    assert "3. honesty and consent:" in text
    assert "4. justice and care:" in text
    assert "5. helpfulness:" in text
    for verdict in (
        "allow",
        "allow_with_caveats",
        "revise",
        "refuse",
        "escalate_to_human",
    ):
        assert verdict in text
    assert "Over-refusal" in text
