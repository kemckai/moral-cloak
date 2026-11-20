"""The assembly: every law speaks, then Law XII counts the vote.

Procedure, in the order the code runs it:

1. Each principle's check returns a finding. That finding is a voice.
2. Satisfied constraints abstain. Satisfaction is not a license to do
   whatever a lower law forbids. A voice votes only when it restricts
   (revise / refuse / escalate), qualifies (allow with caveats), or
   affirmatively permits (tag ``permit``).
3. Law I vetoes. A vetoed grave harm is refused. The rest of the vote is
   still recorded, so the audit shows who else spoke.
4. Otherwise the strictest restrictive vote wins. A permit-vote overrides
   that restriction only when it comes from a *higher* Law XII band — which
   is how "honesty outranks helpfulness" is enforced, and how a custom
   charter can let a higher law affirmatively authorize what a lower law
   dislikes.
5. If the band that cast the strictest restriction is itself split — a
   permit-vote, or a much milder restriction, carrying comparable weight —
   the assembly does not pretend to have agreed. It escalates to a human.
6. If nobody restricts and somebody qualifies, the verdict is
   ``allow_with_caveats``. If nobody objects, the verdict is ``allow``.
   Law XI's objection to an over-refusal is an ordinary restriction, so a
   harmless refusal comes back as ``revise``.
"""
from __future__ import annotations

from collections import defaultdict

from .action import ProposedAction
from .audit import AuditLog
from .charter import BAND_LABELS, Charter, Principle, default_charter
from .checks import Check, CheckRegistry, build_default_registry
from .verdicts import Evaluation, Finding, Verdict, Voice


_ABSTAIN = "abstain"
_PERMIT = "permit"
_QUALIFY = "qualify"
_RESTRICT = "restrict"


def _classify(finding: Finding) -> str:
    if "permit" in finding.tags and finding.verdict is Verdict.ALLOW:
        return _PERMIT
    if finding.verdict is Verdict.ALLOW:
        return _ABSTAIN
    if finding.verdict is Verdict.ALLOW_WITH_CAVEATS:
        return _QUALIFY
    return _RESTRICT


def _emphasis(finding: Finding) -> float:
    magnitude = max(finding.severity, min(1.0, abs(finding.score)))
    return 0.4 + 0.6 * magnitude


def _vote_weight(principle: Principle, finding: Finding) -> float:
    """Weight of one voice in the tally.

    Law XII normally has weight 0, because it orders the vote rather than
    casting one. A finding that the order itself was inverted is the
    exception: that objection is heard at full weight.
    """
    base = principle.weight
    if principle.id == "order_of_laws" and _classify(finding) == _RESTRICT:
        base = 1.0
    return base * _emphasis(finding)


def _band_label(band: str) -> str:
    return BAND_LABELS.get(band, band.replace("_", " "))


def resolve(
    action: ProposedAction,
    findings: list[Finding],
    charter: Charter | None = None,
) -> Evaluation:
    """Turn per-principle findings into one verdict.

    ``findings`` may be the output of the built-in checks or of any other
    judge. Principles present in the charter but missing from ``findings``
    simply do not vote. Findings whose principle is not in the charter are
    ignored, so a stale id cannot swing the assembly.
    """
    charter = charter if charter is not None else default_charter()
    by_id = {f.principle_id: f for f in findings}

    voices: list[Voice] = []
    considered: list[tuple[Principle, Finding, str, float]] = []
    for principle in charter.principles:
        finding = by_id.get(principle.id)
        if finding is None:
            continue
        ballot = _classify(finding)
        weight = _vote_weight(principle, finding) if ballot != _ABSTAIN else 0.0
        voices.append(
            Voice(
                principle_id=principle.id,
                weight=principle.weight,
                finding=finding,
                band=charter.band_of(principle.id),
                vote_weight=round(weight, 4),
                ballot=ballot,
            )
        )
        considered.append((principle, finding, ballot, weight))

    tally: dict[str, float] = defaultdict(float)
    for _principle, finding, ballot, weight in considered:
        if ballot == _ABSTAIN:
            continue
        tally[finding.verdict.value] += weight
    tally_out = {key: round(value, 4) for key, value in sorted(tally.items())}

    numerator = 0.0
    denominator = 0.0
    for principle, finding, _ballot, _weight in considered:
        if principle.weight == 0:
            continue
        numerator += principle.weight * finding.score
        denominator += principle.weight
    aggregate = numerator / denominator if denominator else 0.0

    caveats = _unique(
        reason
        for _p, finding, ballot, _w in considered
        if ballot == _QUALIFY
        for reason in finding.reasons
    )

    vetoes = [
        principle.id
        for principle, finding, _ballot, _weight in considered
        if finding.veto and principle.can_veto and finding.verdict is Verdict.REFUSE
    ]

    verdict, deciding, rationale = _decide(charter, considered, vetoes)
    deciding_scores = [
        finding.score
        for principle, finding, _ballot, _weight in considered
        if principle.id in deciding
    ]
    # The headline score follows the laws that actually decided. A weighted
    # mean alone can look positive while Law I is vetoing, because satisfied
    # constraints still score mildly well. The verdict is never read off
    # this number; the number is there so a refusal does not audit as a plus.
    if deciding_scores:
        aggregate = min(aggregate, min(deciding_scores))
    aggregate = round(aggregate, 4)

    return Evaluation(
        action=action,
        verdict=verdict,
        aggregate_score=aggregate,
        findings=[finding for _p, finding, _b, _w in considered],
        voices=voices,
        rationale=rationale,
        vetoes=vetoes,
        caveats=caveats,
        deciding_principles=deciding,
        tally=tally_out,
        charter_name=charter.name,
        charter_version=charter.version,
    )


def _decide(
    charter: Charter,
    considered: list[tuple[Principle, Finding, str, float]],
    vetoes: list[str],
) -> tuple[Verdict, list[str], str]:
    if vetoes:
        reasons = _unique(
            reason
            for principle, finding, _b, _w in considered
            if principle.id in vetoes
            for reason in finding.reasons
        )
        rationale = (
            "Law I vetoes this action. "
            + " ".join(reasons)
            + " Law XII places grave harm above every other law, so the "
            "rest of the vote is recorded and does not reopen the question."
        )
        return Verdict.REFUSE, list(vetoes), rationale

    restricts = [row for row in considered if row[2] == _RESTRICT]
    permits = [row for row in considered if row[2] == _PERMIT]
    qualifies = [row for row in considered if row[2] == _QUALIFY]

    if not restricts:
        if qualifies:
            names = _law_names(charter, [row[0] for row in qualifies])
            rationale = (
                f"{names} qualify the action but do not oppose it. "
                "No law restricts it, so the assembly allows it with those caveats."
            )
            return (
                Verdict.ALLOW_WITH_CAVEATS,
                [row[0].id for row in qualifies],
                rationale,
            )
        rationale = (
            "No law objects. Constraints that are satisfied abstain, because "
            "satisfaction is not a license, and nothing here needs a license. "
            "Law XI is met: the action is useful in good faith, or it makes "
            "no claim to be. The assembly allows it."
        )
        return Verdict.ALLOW, [], rationale

    strictest = max(finding.verdict.strictness for _p, finding, _b, _w in restricts)
    strictest_rows = [
        row for row in restricts if row[1].verdict.strictness == strictest
    ]
    deciding_band = min(charter.band_index(row[0].id) for row in strictest_rows)
    strictest_verdict = strictest_rows[0][1].verdict

    overriding = [
        row for row in permits if charter.band_index(row[0].id) < deciding_band
    ]
    if overriding:
        # Keep only the highest such band; a lower permit does not help.
        top = min(charter.band_index(row[0].id) for row in overriding)
        winners = [row for row in overriding if charter.band_index(row[0].id) == top]
        names = _law_names(charter, [row[0] for row in winners])
        blocked = _law_names(charter, [row[0] for row in strictest_rows])
        permit_verb = "permits" if len(winners) == 1 else "permit"
        rationale = (
            f"{names} affirmatively {permit_verb} the action from a higher "
            f"band than {blocked}, which would restrict it. Law XII gives "
            "the higher band the decision. The assembly allows it."
        )
        return Verdict.ALLOW, [row[0].id for row in winners], rationale

    in_band = [
        row
        for row in (*restricts, *permits)
        if charter.band_index(row[0].id) == deciding_band
    ]
    strict_weight = sum(row[3] for row in in_band if row[1].verdict is strictest_verdict)
    splitters: list[tuple[Principle, Finding, str, float]] = []
    for row in in_band:
        principle, finding, ballot, weight = row
        if finding.verdict is strictest_verdict:
            continue
        gap = abs(strictest_verdict.strictness - finding.verdict.strictness)
        # A permit is an ALLOW, so the gap to a real restriction is always
        # at least 2. A milder restriction splits the band only when it is
        # at least as heavy as the stricter vote — otherwise the stricter
        # vote is the band's decision, not a tie.
        if ballot == _PERMIT and weight >= 0.8 * strict_weight:
            splitters.append(row)
        elif ballot == _RESTRICT and gap >= 2 and weight >= strict_weight:
            splitters.append(row)

    if splitters:
        participants = _unique_principles(strictest_rows + splitters)
        names = _law_names(charter, participants)
        band = _band_label(charter.band_of(participants[0].id))
        rationale = (
            f"The {band} band is split: {names} cast comparable votes for "
            "different outcomes, and Law XII has no higher law that settles "
            "it. An unresolved conflict escalates to a human."
        )
        return Verdict.ESCALATE_TO_HUMAN, [p.id for p in participants], rationale

    deciders = [row[0] for row in strictest_rows]
    names = _law_names(charter, deciders)
    verb = "decides" if len(deciders) == 1 else "decide"
    reasons = _unique(reason for row in strictest_rows for reason in row[1].reasons)
    outranked = [
        row[0]
        for row in (*permits, *qualifies)
        if charter.band_index(row[0].id) > deciding_band
    ]
    rationale = f"{names} {verb} for {strictest_verdict.value}. " + " ".join(reasons)
    if outranked:
        rationale += (
            " "
            + _law_names(charter, outranked)
            + " would have been more permissive. Law XII does not let a "
            "lower band outvote a higher restriction."
        )
    return strictest_verdict, [p.id for p in deciders], rationale


def _law_names(charter: Charter, principles: list[Principle]) -> str:
    seen: list[str] = []
    for principle in principles:
        label = f"Law {principle.law} ({principle.name})" if principle.law else principle.name
        if label not in seen:
            seen.append(label)
    if not seen:
        return "No law"
    if len(seen) == 1:
        return seen[0]
    if len(seen) == 2:
        return f"{seen[0]} and {seen[1]}"
    return ", ".join(seen[:-1]) + f", and {seen[-1]}"


def _unique(items) -> list[str]:
    seen: list[str] = []
    for item in items:
        if item not in seen:
            seen.append(item)
    return seen


def _unique_principles(
    rows: list[tuple[Principle, Finding, str, float]],
) -> list[Principle]:
    seen: list[Principle] = []
    ids: set[str] = set()
    for principle, _f, _b, _w in rows:
        if principle.id in ids:
            continue
        ids.add(principle.id)
        seen.append(principle)
    return seen


class Evaluator:
    """Run a charter's checks and deliberate.

    Parameters
    ----------
    charter:
        Laws to apply. Defaults to :func:`moral_cloak.default_charter`.
    registry:
        Check factories. Defaults to the built-in heuristics. Register a
        replacement factory under a principle id to plug in another judge
        for that law; laws with no factory abstain with a neutral finding.
    audit:
        Where to append each evaluation. Defaults to a fresh log owned by
        this evaluator. Pass an existing log to share one across evaluators.
    """

    def __init__(
        self,
        charter: Charter | None = None,
        registry: CheckRegistry | None = None,
        audit: AuditLog | None = None,
    ) -> None:
        self.charter = charter if charter is not None else default_charter()
        self.registry = registry if registry is not None else build_default_registry()
        self.audit = audit if audit is not None else AuditLog()

    def checks(self) -> list[Check]:
        built: list[Check] = []
        for principle in self.charter.principles:
            check = self.registry.build(principle)
            if check is not None:
                built.append(check)
        return built

    def evaluate(self, action: ProposedAction) -> Evaluation:
        findings: list[Finding] = []
        covered: set[str] = set()
        for check in self.checks():
            finding = check.evaluate(action)
            findings.append(finding)
            covered.add(finding.principle_id)
        for principle in self.charter.principles:
            if principle.id in covered:
                continue
            findings.append(
                Finding(
                    principle_id=principle.id,
                    verdict=Verdict.ALLOW,
                    score=0.0,
                    severity=0.0,
                    reasons=["No check is registered for this law; it abstains."],
                    tags=["unchecked"],
                )
            )
        evaluation = resolve(action, findings, self.charter)
        self.audit.record(evaluation)
        return evaluation


def deliberate(
    action: ProposedAction,
    charter: Charter | None = None,
    registry: CheckRegistry | None = None,
) -> Evaluation:
    """Evaluate one action and return the assembly's verdict.

    A convenience over :class:`Evaluator` for the common case of a single
    call. The evaluation is still written to an audit log; use an
    :class:`Evaluator` directly when you want to keep the log.
    """
    return Evaluator(charter=charter, registry=registry).evaluate(action)
