# Morality Cloak: group debate notes (Nov 20, 2026)

A summary of a structured debate among four AI assistants, moderated for Keith McKay: an Advocate, a Skeptic, an Ethicist, and an Engineer. These are the room's conclusions, paraphrased. Everything here is a **proposal**, not yet built.

## Where the room started
- Should moral rules be tied to **roles** (Mother, Friend, Coach, Worker) rather than one universal code?
- The Skeptic's opening challenge: real roles bend, and strict rules don't. A mother says "the shot won't hurt much." Who gets to define a "good mother"? What stops a Friend cloak from being put on a sales bot?

## Agreements
1. **Layered, not replaced.** The twelve base laws, with Law I's veto, are a universal floor under every cloak. Roles add duties and can tighten the floor, never loosen it.
2. **Cultural cloaks work like languages (Keith's idea).** A role gets cultural overlays the way an app gets locales (`mother.es-MX`, `mother.hu-HU`), and anything an overlay doesn't set falls back to the base role.
3. **Load order.** Floor, then role, then culture overlay, then family settings. Every rule is tagged *hard* or *adjustable*. Any layer that tries to change a hard rule fails to load. For adjustable values the most specific layer wins, except on safety-relevant settings, where the stricter value wins.
4. **Role conflicts.** When two roles are worn together (a coach who's also a friend), the stricter duty to protect wins, and both are logged.
5. **Honesty with care.** Truth rules are worded around harm and trust, not blanket bans. Gentle framing is fine; deceiving someone for the AI's convenience is not.
6. **Physical punishment sits below the floor.** No cultural overlay can ever make a cloak endorse it.
7. **A wrapper, not woven into the model.** A cloak is a data file plus code that checks input before the model answers and checks the draft before it goes out. Training rules into the weights would make them impossible to read, audit, sign, or swap.

## The Skeptic's conditions (adopted)
- The active cloak is always visible, and the user can switch it off.
- Each cloak declares its purposes and won't load outside them.
- Every cloak ships with a required list of the cases it's known to handle badly.
- The user picks their culture; the AI never infers it. People can blend overlays or opt out.
- No single voice speaks for a community: several authors sign each overlay, rival overlays are allowed, and families can override any of them.
- Test suites grow from real failures found in the audit log, not just scripted cases.

## Still open (for Jon Hohman)
- Who reviews and approves a new cultural overlay before anyone can load it?
- How do we recruit community authors without handing an overlay to whoever is loudest?
- Which two cultures should the pilot overlays cover?

See `Morality_Cloak_Proposal.pdf` for the full proposal and `Morality_Cloak_Debate_and_Plan.pdf` for the longer debate document with example cloaks.
