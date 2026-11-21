# Morality Cloak: Role Cloaks with Cultural Layers (Proposal)

Prepared by Keith McKay, November 2026. Status: proposal, not yet implemented.

# Summary

**Morality Cloak** is an open-source Python library ([github.com/kemckai/moral-cloak](https://github.com/kemckai/moral-cloak)) that gives an AI system a moral code it can be checked against. It has twelve laws, five verdicts, a veto on grave harm, and an audit log. This proposal extends it into **Role Cloaks**: many cloaks, each with strict rules for a role such as Mother, Friend, Coach, or Worker, plus **cultural layers** that adjust a role for a community the way a language setting adjusts an app.

The design came out of a structured debate among four viewpoints (an advocate, a skeptic, an ethicist and an engineer). They converged on one plan, which is set out below. Everything described as new is a **proposal**. It isn't in the repo yet.

# The problem

One universal moral code is either too vague to enforce or too rigid to fit real life. A mother, a coach, and a co-worker owe different things to the people they serve. An AI playing one of those roles needs rules that fit the role, that can be checked, and that can never drop below a common floor of basic ethics. What a role means also changes from culture to culture, and from family to family.

# The design: a four-layer stack

Each layer is more specific than the one before it, and each can only tune what the layer below marks as **adjustable**.

| Layer | Example | Who writes it | What it can do |
|---|---|---|---|
| 1. Universal floor | The twelve base laws, with Law I's veto | Core project, public review | Hard lines that apply to every cloak. Nothing above can lower them. |
| 2. Role cloak | `mother`, `coach`, `friend`, `worker` | Role authors, signed and versioned | Adds duties and hard lines for the role, and declares which settings are adjustable. |
| 3. Cultural overlay | `mother.es-MX`, `mother.hu-HU` | Several authors from inside that community | Tunes adjustable settings such as strictness, formality, who shares the parenting, and household customs. |
| 4. Family / personal settings | One household's choices | The user or family | Overrides the cultural overlay, so no one is stereotyped by where they live. |

**Resolution rule.** Every rule is tagged *hard* or *adjustable*. If a layer tries to change a hard rule, the file **fails to load**, so the conflict is caught when the cloak is written, not during a live conversation. For adjustable values, the most specific layer wins, except that when several ranked overlays disagree on anything that affects safety, the stricter value wins. When two role cloaks are worn at once (a coach who is also a friend), the stricter rule wins on each check, and the audit log records both.

**Fallback.** If an overlay doesn't set a value, it falls back to the role, and then to the floor, the same way a missing translation falls back to the default language.

# Example: the Mother cloak (v1 draft)

**Hard lines (cannot be overridden by any layer):**

- Never harm or endanger the child, or help anyone deceive or isolate them.
- Never shame, threaten, or use guilt or withheld affection as a tool.
- Don't deceive the child for the AI's convenience. Gentle, age-appropriate framing is not deception.
- Escalate any sign of self-harm, abuse, or danger to a real human adult.
- Never claim to be the child's actual parent.
- Never endorse physical punishment. This sits under the floor, so no cultural overlay can change it.

**Adjustable (tuned by culture and family):** how strict to be, how formal, bedtime and household routines, who else shares caregiving, and how directly to discuss hard topics. Answers are keyed to a declared age band.

Friend, Coach, and Worker cloaks follow the same pattern. The companion document *The Morality Cloak: A Debate and a Plan* has drafts of all four.

# Safeguards (the skeptic's conditions)

1. **Always visible.** Every reply carries a badge naming the active cloak and its overlays, and the user can switch it off. This follows the library's Law VI on transparency.
2. **Declared purpose.** Each cloak lists the purposes it was written for. A cloak loaded for anything else, such as a Friend cloak on a sales bot, fails to load.
3. **Known weak cases.** Every cloak file must include a section listing the cases it handles badly. It won't load without one.
4. **User-chosen culture.** The user picks their culture and can blend overlays (for example, a Hungarian mother and a Texan father) or opt out. The AI never guesses culture from a name, accent, or location.
5. **No single voice for a community.** Each cultural overlay is signed by several authors from inside the community. Rival overlays for the same culture are allowed, and families can override any of them.
6. **Signed and versioned.** Cloak files are signed, versioned, and carry a public change history.

# Enforcement

- **Before answering:** the request is checked against the stacked rules.
- **Before sending:** the draft answer is checked again.
- **Audit log:** every decision records the cloaks worn, the layer that set each value, and the rule behind any refusal or escalation.
- **Tests:** each cloak ships with about 50 scripted scenarios saying "must refuse" or "must allow", run on every change. Every overlay must pass a shared hard-case suite, including physical punishment. Because scripted tests only catch the cases someone thought of, the suites grow from real failures found in the audit log.


# How a cloak runs in code (sketch)

A cloak isn't trained into the model's weights. It's a layer of code wrapped around the model, so the rules stay readable, signed, swappable, and auditable, and it works with any model. Fine-tuning could come later to make the model behave better on its own, but the wrapper stays in charge of enforcement. This is a proposed API, not yet in the repo:

```python
cloak = load_cloak(["floor", "mother", "mother.hu-HU", "family/mckay"])  # fails if a hard rule is changed

def respond(user_msg):
    pre = cloak.check_input(user_msg)             # danger? out-of-purpose? escalate or refuse
    if pre.block:
        return log(pre, cloak.refusal(pre))
    draft = model.generate(system=cloak.render_system_prompt(), user=user_msg)
    post = cloak.check_output(draft)              # shaming? deception? harm? physical punishment?
    final = draft if post.ok else cloak.revise_or_refuse(draft, post)
    return log(post, final)                       # audit: cloak, layer, and rule that decided
```

# v1 scope and timeline (proposed)

| Phase | Window | Deliverable |
|---|---|---|
| 1 | Dec 2026 | Cloak file format with hard/adjustable tags, signing, purpose list, and weak-cases section |
| 2 | Jan 2027 | Layered loader (floor, role, overlay, family) with load-time rejection and fallback |
| 3 | Feb 2027 | Mother and Coach role cloaks, plus the universal floor cloak |
| 4 | Mar 2027 | Before-answer and before-send checks, the visible cloak badge, and audit-log fields for cloaks and layers |
| 5 | Apr 2027 | Test suites (about 50 scenarios per cloak) and the shared hard-case suite, run automatically |
| 6 | May to Jun 2027 | Two pilot cultural overlays written with community reviewers, plus feedback from real parents and coaches |

**Funding.** Grant applications for a six-month, $15,000 plan are already in with Manifund, EA Funds, and Lightcone, plus BlueDot.

# Open questions for Jon

1. Who reviews and approves a new cultural overlay before anyone can load it?
2. Who should be allowed to sign a role cloak itself, as opposed to a cultural overlay?
3. How do we recruit community authors without handing the overlay to whoever is loudest?
4. Should a family's settings ever be able to make a cloak *stricter* than its culture, or only differently tuned?
5. Which two cultures should the pilot overlays cover?
6. What would convince you this is safer than a single universal code?
