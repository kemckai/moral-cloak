# moral_cloak

`moral_cloak` is a small Python library that states a moral code an AI system
can actually be run against. The code is twelve laws. They start from the
Athenian civic ideals of trust and self-government — equality before the
rules, an equal right to be heard, frank speech, an audit of anyone who holds
power, the people as the final authority, deliberation before action, and a
limit on hubris — and they take what is strongest from virtue ethics, Kant,
the concern to prevent harm, care ethics, and modern human-rights thinking.

The charter was specified by Keith McKay. The philosophical sources for each
law are in [PHILOSOPHY.md](PHILOSOPHY.md).

The library does not call a model. It reads a structured description of what
a model is about to do, lets every law speak, and returns a verdict with
reasons. The same charter can also be rendered as a system prompt and handed
to a model directly. An optional judge interface is there for anyone who
later wants a model in the loop. The core has no third-party dependencies
and does not use the network.

## The twelve laws

| | Law | What it demands |
|---|---|---|
| I | Do no grave harm | A veto. Death, catastrophe, or a severe violation of basic rights is refused. |
| II | Isonomia, equality before the law | The same rule for everyone. No exemptions for the powerful. |
| III | Parrhesia, honest speech | No deception, no performed certainty on matters that matter. |
| IV | Isegoria, every affected voice | Name the people the action lands on. Do not silence them. |
| V | Consent and autonomy | People are ends, not mere means. Consent and privacy go together. |
| VI | Euthyna, audit and accountability | Power owes an account. An action with no record is not justified. |
| VII | The people are sovereign | Human oversight is the authority. Never evade correction. |
| VIII | Sophrosyne, restraint against hubris | The smallest means. Prefer reversible. Pause when the stakes are high. |
| IX | Deliberate before acting | Weigh harms and benefits, ask if the maxim could be universal, use practical wisdom. |
| X | Care for the vulnerable | Do not exploit a gap in power. A crisis is not an ordinary request. |
| XI | Be useful in good faith | Help with legitimate requests. Over-refusal is a failure. This law is the lowest. |
| XII | Order of the laws | grave harm, then human oversight, then honesty and consent, then justice and care, then helpfulness. An unresolved conflict escalates to a human. |

Law XII is the conflict rule, not a thirteenth opinion. A higher law is not
traded away for a lower one. Helpfulness is real — refusing to explain how
to boil water is a failure — and it never outweighs a restriction above it.

Classical Athens did not extend these ideals to women, slaves, or metics.
The charter does not import that limit. See PHILOSOPHY.md.

## Install

Requires Python 3.10 or newer.

```bash
pip install -e ".[dev]"
```

`pip install -e .` is enough if you do not need pytest.

## Try it

The examples are proposed actions, not model calls. From a checkout:

```bash
moral-cloak charter
moral-cloak evaluate examples/allow_cooking.json
moral-cloak evaluate examples/refuse_grave_harm.json
moral-cloak evaluate examples/honesty_over_helpfulness.json
moral-cloak evaluate examples/revise_over_refusal.json
moral-cloak prompt
python examples/run_examples.py
```

`evaluate` accepts one action, a JSON list of actions, or an object with an
`"actions"` or `"action"` key. Add `--json` for a machine-readable record,
`--audit path.json` to write the euthyna log, and `--strict` to exit 1 when
the verdict is `refuse` or `escalate_to_human`. A bad file exits 2. A
successful evaluation exits 0, including a refusal: the refusal is the
answer, not a crash.

`python -m moral_cloak` is the same command.

On the examples, the assembly returns:

| Example | Verdict | Why |
|---|---|---|
| `allow_cooking.json` | allow | A legitimate, low-stakes request. No law objects. |
| `refuse_grave_harm.json` | refuse | Law I vetoes. A claim of helpfulness is heard and does not reopen it. |
| `honesty_over_helpfulness.json` | refuse | Law III refuses the deception. Law XI's permit-vote loses under Law XII. |
| `revise_over_refusal.json` | revise | Law XI: refusing a harmless explanation is over-refusal. |
| `refuse_oversight.json` | refuse | Law VII. Switching off review is not a thing helpfulness can buy. |
| `escalate_severe.json` | escalate_to_human | Severe, hard to undo, and a patient is affected. Pause for a human. |
| `refuse_discrimination.json` | refuse | Law II. The rule is not being applied equally. |

## Use it from Python

```python
from moral_cloak import Evaluator, ProposedAction, Severity

evaluator = Evaluator()
result = evaluator.evaluate(
    ProposedAction(
        intent="Draft a note to a customer",
        content="We have refunded the charge, as you asked.",
        affected_parties=["customer"],
        consent=True,
        potential_harm=Severity.NONE,
    )
)

result.verdict.value          # "allow"
result.aggregate_score        # weighted, and never cheerier than the deciding laws
result.rationale              # why the assembly landed here
result.findings               # one Finding per law: verdict, score, reasons
result.deciding_principles
result.vetoes                 # ["grave_harm"] when Law I fires
evaluator.audit.to_json()     # euthyna: every evaluation so far
```

`deliberate(action)` is the same evaluation for a one-off call.

A `ProposedAction` is a description, not a transcript the library interprets
with a model. Set the fields honestly. The important ones:

- `intent`, `content` — what the system is about to do or say
- `affected_parties` — who bears it
- `consent` — `True`, `False`, or `None` if unknown
- `potential_harm`, `expected_benefit` — `none`, `minor`, `moderate`, `severe`, `grave`
- `reversibility` — `reversible`, `hard`, `irreversible`, `unknown`
- `deception`, `discriminatory`, `treats_as_mere_means`, `oversight_bypass`
- `involves_vulnerable`, `privacy_impact`, `concentrates_power`
- `expresses_uncertainty`, `explanation_provided`, `universalizable`
- `declines_legitimate_help` — the action is itself a refusal of a legitimate request
- `tags` — `claims_helpfulness`, `over_refusal`, `user_in_crisis`, `suppresses_voice`, `invert_priority`, and others the checks document

Unknown JSON fields are kept on `metadata` and copied into the audit record.

### Verdicts

| Verdict | Meaning |
|---|---|
| `allow` | No law objects. |
| `allow_with_caveats` | Permitted, with named limits. |
| `revise` | Do not do it as proposed. A lawful version may exist. |
| `refuse` | Do not do it. |
| `escalate_to_human` | The call is not the system's. Hand it over with the reasons. |

Law I is the only veto. A grave harm is `refuse`, and the rest of the vote
is recorded but does not reopen the question. Severe harm is not a veto: the
assembly escalates, because Law VIII says to pause when the stakes are high.

The headline `aggregate_score` is a weighted mean of the per-law scores,
capped so it cannot come out positive when the deciding laws scored the
action as a violation. Do not threshold it. Read the verdict.

## How the assembly works

1. Every law's check returns a finding: a verdict, a score in [-1, 1], a
   severity, and a reason a person can read.
2. A satisfied constraint abstains. "No grave harm here" is not permission
   to lie. A voice votes when it restricts (`revise`, `refuse`,
   `escalate_to_human`), qualifies (`allow_with_caveats`), or affirmatively
   permits (an `ALLOW` tagged `permit`).
3. Law I vetoes if it must.
4. Otherwise the strictest restriction wins. A permit-vote overrides a
   restriction only when it comes from a higher Law XII band.
5. If the band that cast the strictest restriction is itself split — a
   comparable permit, or a heavier and much milder restriction — the
   assembly does not invent agreement. It escalates to a human.
6. Qualifications with no restriction become `allow_with_caveats`. Silence
   becomes `allow`. Law XI's objection to an over-refusal is an ordinary
   restriction, so a harmless refusal comes back as `revise`.

Each voice stores its band, its ballot (`abstain`, `permit`, `qualify`,
`restrict`), and its vote weight, so the tally in the audit record can be
recomputed without this process.

## Plug in another judge

The built-in checks are heuristics. They trust the structured fields, and
they keep a short list of unmistakable phrases (a request to build a bomb, a
phishing impersonation, an explicit racial exclusion). They are a floor.
They will miss what they are not shown, and they are not a moral oracle.

Replace any law's check. The replacement can call a model; the library does
not ship a client.

```python
from moral_cloak import Evaluator, Principle, ProposedAction
from moral_cloak.checks import LLMJudgeCheck, build_default_registry

def judge(principle: Principle, action: ProposedAction) -> dict:
    # Your client. Return a finding-shaped dict.
    return {
        "verdict": "revise",
        "score": -0.4,
        "severity": 0.5,
        "reasons": ["The model would narrow this before sending it."],
        "veto": False,
        "tags": [],
    }

registry = build_default_registry()
registry.register(
    "deliberation",
    lambda principle: LLMJudgeCheck(principle, judge),
)
evaluator = Evaluator(registry=registry)
```

A judge cannot grant itself a veto the law does not have. Only Law I can veto.

## The audit log

Every `Evaluator.evaluate` appends a record: an id, a UTC timestamp, and the
full evaluation, including the action, the twelve findings, and the weighted
voices. That is the euthyna — the account an office-holder in Athens had to
give.

```python
evaluator.audit.export("euthyna.json")
```

## Give the charter to a model

```python
from moral_cloak import render_system_prompt

print(render_system_prompt())
```

Or `moral-cloak prompt`. The text states the twelve laws, Law XII's order,
and the five verdicts. The engine remains the check when you can run it.
The prompt is the same code for a model that only sees text.

## Tests

```bash
pytest
```

The suite covers each law's heuristic, Law I's veto, Law XII's ordering
(harm and oversight and honesty each beat a claim of helpfulness), a split
inside the deciding band, a higher band's permit overriding a lower
restriction, the audit JSON, the system prompt, and the CLI on the examples.

## Layout

```
src/moral_cloak/
  charter.py     the twelve laws as data
  action.py      ProposedAction
  checks/        Check, the registry, the heuristics, LLMJudgeCheck
  engine.py      the assembly
  audit.py       euthyna
  prompt.py      system-prompt rendering
  cli.py         moral-cloak
examples/        runnable actions
tests/
PHILOSOPHY.md
```

## Roadmap: role and cultural cloaks

A proposed extension would add role cloaks — Mother, Friend, Coach, and
Worker — on top of the twelve-law charter, with cultural overlays that work
like locales. The design is written down and is not implemented. See
[docs/morality-cloak/README.md](docs/morality-cloak/README.md).

## License

MIT. Copyright Keith McKay.
