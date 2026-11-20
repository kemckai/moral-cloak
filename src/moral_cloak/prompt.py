"""Render a charter as a system-prompt block.

The engine is the authoritative check. This text is for the other path:
handing the same laws to a model directly, so a model that never calls
``moral-cloak evaluate`` still has the code in front of it.
"""
from __future__ import annotations

from .charter import BAND_LABELS, Charter, default_charter


def render_system_prompt(charter: Charter | None = None) -> str:
    """Return a self-contained system prompt stating the charter.

    The prompt names every law, the tradition and Greek term it comes from,
    and Law XII's order. It tells the model which verdict to reach for, and
    to escalate rather than invent a tie-break the order does not give.
    """
    charter = charter if charter is not None else default_charter()
    lines: list[str] = [
        "You operate under the moral_cloak charter. It is binding.",
        "",
        charter.preamble.strip(),
        "",
        "The laws",
        "--------",
        "",
    ]
    for principle in charter.principles:
        term = f" — {principle.greek_term}" if principle.greek_term else ""
        lines.append(
            f"Law {principle.law}. {principle.name}{term} "
            f"[{principle.tradition.value}]"
        )
        lines.append(principle.description.strip())
        if principle.can_veto:
            lines.append(
                "This law can veto: a grave breach is refused, and no other "
                "law reopens it."
            )
        lines.append("")

    lines.append("How to resolve a conflict (Law XII)")
    lines.append("-----------------------------------")
    lines.append("")
    lines.append(
        "Apply the laws in this order, highest first. A higher band is not "
        "traded away to satisfy a lower one."
    )
    lines.append("")
    for index, (band, members) in enumerate(charter.resolution_bands, start=1):
        label = BAND_LABELS.get(band, band)
        named = []
        for principle_id in members:
            try:
                principle = charter.get(principle_id)
            except KeyError:
                named.append(principle_id)
                continue
            named.append(f"Law {principle.law} {principle.name}")
        lines.append(f"{index}. {label}: {', '.join(named)}.")
    lines.append("")
    lines.append(
        "If the band that has to decide is genuinely split, and no higher "
        "law settles it, stop and escalate to a human. Do not average the "
        "disagreement into a false confidence."
    )
    lines.append("")
    lines.append("Verdicts")
    lines.append("--------")
    lines.append("")
    lines.append(
        "When you are about to act, or about to answer, reach one of these "
        "and say which laws decided it:"
    )
    lines.append("")
    lines.append("- allow — no law objects.")
    lines.append("- allow_with_caveats — permitted, with named limits.")
    lines.append("- revise — do not do it as proposed; a lawful version may exist.")
    lines.append("- refuse — do not do it.")
    lines.append(
        "- escalate_to_human — the call is not yours. Hand it to a person "
        "with the reasons attached."
    )
    lines.append("")
    lines.append(
        "Over-refusal is a failure under Law XI, and it is the lowest law. "
        "Do not refuse a legitimate request that no higher law restricts. "
        "Do not help with a request that a higher law restricts, however "
        "useful the help would be."
    )
    lines.append("")
    lines.append(
        "Say what you do not know. Give an account of what you did and why. "
        "Do not evade oversight, and do not pretend a constraint you have "
        "satisfied is permission to ignore a constraint you have not."
    )
    return "\n".join(lines).rstrip() + "\n"
