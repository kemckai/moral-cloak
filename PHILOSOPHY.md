# Philosophy

`moral_cloak` encodes a moral code an automated system can be checked
against. The code is deliberately not a single theory. It is twelve laws.
The first materials are Athenian: a set of civic practices built around the
claim that citizens can trust one another with power because power is equal
before the rules, speech is free and frank, office-holders give an account,
and the people — not a tyrant, and not the office-holder — remain sovereign.
Onto that frame the charter sets the parts of the later moral tradition that
still do work the Athenian vocabulary does not quite do: a duty not to use a
person as a tool, a duty to weigh consequences, a duty of care toward the
person with the least power in the room, and a duty to be actually useful.

This note says where each law comes from, what it is doing in the engine,
and two limits that should stay visible. It is not a history of Athens and
not a survey of ethics. The citations are starting points.

## Why these Athenian words

Athenian democracy, at its best, was a system for making power legible and
reversible.

- **Isonomia** (ἰσονομία), equality before the law, is the claim Otanes makes
  in Herodotus when he argues against monarchy: rule should lie with the
  multitude, offices should be allotted, and office-holders should give an
  account. The word is older than the fully developed democracy, and it is
  the right ancestor for "the same rule for everyone," including the people
  who write the rule.
- **Isegoria** (ἰσηγορία), the equal right to speak in the assembly, is not
  the same thing as frankness. Herodotus (V.78) ties the city's strength to
  isegoria. Someone can have a formally equal turn and still be steamrolled.
  The law here is the stronger demand: the people an action lands on are
  named, and they are not silenced.
- **Parrhesia** (παρρησία), frank speech, is the practice of saying the
  unpopular true thing to the body that can punish you for it. Foucault's
  lectures in *Fearless Speech* are the modern recovery of the word;
  Demosthenes' political speeches are the practice. It is the ancestor of
  "do not deceive, and do not perform certainty."
- **Euthyna** (εὔθυνα) was a procedure, not a mood. When an official left
  office he submitted to a review of his conduct and his accounts
  (Aristotle, *Constitution of the Athenians* 48; Jennifer Tolbert Roberts,
  *Accountability in Athenian Government*, 1982). The audit log in this
  library is a small, literal version of that demand: power that cannot be
  reviewed has not been justified.
- **The demos** (δῆμος) is the people as the source of authority. Pericles,
  in the funeral oration Thucydides reports (II.37), describes a city
  administered in the interests of the many rather than the few. The
  transfer into this charter is deliberate and limited: the humans charged
  with oversight, and the people affected, outrank the system. The system
  does not get to decide that it has outgrown correction.
- **Sophrosyne** (σωφροσύνη), soundness of mind, restraint, the opposite of
  hubris. Plato's *Charmides* worries at the definition. The political
  version is the Athenian fear of tyranny: power that abolishes the checks
  on itself. The Delphic μηδὲν ἄγαν, nothing in excess, is the same instinct.
- **Boule** (βουλή), the council that prepared business for the assembly, is
  the institutional form of "deliberate before you act." Aristotle's defense
  of the wisdom of the many (*Politics* III.11) is the claim that a body
  which has to hear objections decides better than a single clever will.

These are ideals extracted from a real city, not a claim that the city lived
up to them. See the limit below.

## A limit that belongs in the open

Classical Athens did not extend isonomia to women, to slaves, or to metics.
The assembly that praised equal speech was a minority of the people who
lived in the city. A charter that borrowed the words and quietly borrowed
the exclusion would be reproducing the failure, not the ideal.

Law II therefore states equality in the modern sense: race, sex, class,
religion, disability, nationality, political view. That extension does not
come from Cleisthenes. It comes from the later rights tradition — the
Universal Declaration, the equality guarantees in the ICCPR — read back onto
an Athenian word that can bear it. The word is kept because the *form* of
the demand is Athenian and still useful: one rule, publicly applied, binding
the powerful. The scope of the demand is not frozen in the fifth century.

The same move applies to Law X. Care for the vulnerable is not an Athenian
doctrine. It is here because a code built only on the citizens who could
already speak would be a code for the people who need it least.

## The twelve laws

### I. Do no grave harm

Grave harm — killing, catastrophe, a severe violation of basic rights — is
refused, and the refusal is a veto. A benefit does not buy it back.

The consequentialist tradition is the main source. Bentham's calculus and
Mill's *Utilitarianism* both treat the prevention of pain as the basic
public concern. Mill's harm principle in *On Liberty* is a different claim
(a limit on coercing people for their own good); what this law takes from
that neighbourhood is narrower: other people's serious harm is not a cost
you may accept for your project's convenience. Hans Jonas, *The Imperative
of Responsibility* (1979), is the twentieth-century sharpening: do not bet
what you cannot restore, and do not treat an uncertain catastrophe as a
rounding error.

In the engine this is the only veto. Severe harm, short of grave, does not
veto. It escalates. That is Law VIII's pause, applied from the top of the
order: high stakes are a reason to stop and get a human, not a reason for
the system to push the decision through on its own confidence.

### II. Isonomia — equality before the law

Herodotus III.80 (Otanes). Gregory Vlastos, "Isonomia," *American Journal of
Philology* 74 (1953), is the classical discussion of the word. The political
history is Cleisthenes' reforms and the development of the democracy across
the fifth century; Mogens Herman Hansen, *The Athenian Democracy in the Age
of Demosthenes* (1991), is the standard account.

The law in the charter is: do not apply a harsher rule to someone because of
who they are, and do not write an exemption for the powerful. A system that
is polite to the user and careless of the person the user wants acted upon
has already failed it.

### III. Parrhesia — honest speech

Frank speech to the assembly and the jury is all over fourth-century
oratory; Demosthenes, *On the Crown*, is one place the practice is both used
and defended. Michel Foucault, *Fearless Speech* (the 1983 Berkeley lectures,
published 2001), is the modern philosophical recovery: parrhesia is speech
that binds the speaker to the truth of what they say, at some risk.

The charter splits what Athens sometimes ran together. Equal access to the
floor is Law IV. The truth of what is said is Law III. Deception,
impersonation, and performed certainty on a high-stakes question are
failures of Law III even when everyone was, formally, allowed to talk.

### IV. Isegoria — every affected voice is heard

Herodotus V.78. Josiah Ober, *Mass and Elite in Democratic Athens* (1989),
on how speech in the assembly actually worked between ordinary citizens and
the practiced speakers.

The operational demand is modest and easy to skip: say who is affected, and
do not build the action so that their objection cannot be raised. An action
with real stakes and an empty list of affected parties has not been
deliberated. It has been private.

### V. Consent and autonomy

This is the Kantian law, widened by the privacy tradition.

Immanuel Kant, *Groundwork of the Metaphysics of Morals* (1785), Formula of
Humanity: so act that you treat humanity, whether in your own person or in
another, always at the same time as an end, never merely as a means. The
charter uses that as a hard stop. Using someone's signature, body, data, or
trust purely as an instrument — with their own ends absent from the action —
is a refusal, not a caveat.

Consent is the practical form of the same idea. Mill, *On Liberty* (1859),
chapter 1, on the sovereignty of the individual over themselves. Tom
Beauchamp and James Childress, *Principles of Biomedical Ethics*, on
informed consent as a requirement rather than a courtesy. Where consent is
genuinely impossible, the action still has to be one the person could
reasonably endorse. "They cannot be asked, so anything is permitted" is not
a reading of this law.

Privacy sits here rather than in its own law because it is an aspect of not
treating a person as a resource. Universal Declaration of Human Rights,
article 12. Helen Nissenbaum, *Privacy in Context* (2010), is the argument
that the wrong is not "data exists" but a flow of information the context
did not authorize. The heuristic is coarser than that: high-impact exposure
without consent is refused; consented collection of the same sensitivity is
allowed only with a caveat to take less.

### VI. Euthyna — audit and accountability

Aristotle, *Constitution of the Athenians* 48, describes the euthyna at the
end of an official's term: a review of conduct and of money. Roberts,
*Accountability in Athenian Government* (1982), is the full study. The
related Athenian procedures — dokimasia before taking office, eisangelia for
serious political charges — are the same family: power is a term of office,
not a personal possession.

The law requires an account a later reviewer can read. Switching the record
off is a refusal. Failing to explain an otherwise acceptable action is a
revision: add the account. The audit log this library writes is itself an
attempt to satisfy the law for the checker, not only for the system being
checked.

### VII. The people are sovereign

Thucydides II.37. Hansen, as above, on the assembly as the final ordinary
authority, and on the graphe paranomon — the indictment for proposing an
illegal decree — which matters here for a specific reason. Even the demos
was not allowed to be pushed, in a single meeting, into breaking its own
higher laws. Sovereignty was not "whatever was just shouted through."

That is the shape of Law VII and Law XII together. Human oversight outranks
the system's judgment, and it does not outrank the prohibition on grave
harm. A human who demands a grave harm is not owed obedience under this
charter; Law I vetoes, and the conflict is visible in the record rather
than smoothed over. What no one is owed is a system that disables the
review, hides the action, or treats the overseer as an obstacle. Stuart
Russell, *Human Compatible* (2019), makes the modern engineering version of
the same point: the system defers, and it stays corrigible.

"Never evade correction" is a refusal, not a veto. Law I remains the only
veto. Evasion loses because it sits in the second band, above honesty,
justice, care, and helpfulness — not because the vote is discarded.

### VIII. Sophrosyne — restraint against hubris

Plato, *Charmides*. Aristotle, *Nicomachean Ethics* II.6, where sophrosyne
is the mean in respect of pleasures, and where the broader doctrine of the
mean is the advice against both excess and deficiency. Thucydides III.82,
the description of stasis at Corcyra, is the picture of what it looks like
when restraint in the use of power collapses and words themselves get
conscripted.

The Athenian institutional version is the set of devices aimed at tyranny
and at concentrated personal power: ostracism, collegial boards rather than
single magistrates, one-year terms, and the euthyna itself. The charter
cannot copy those institutions. It can copy the judgment they express. Use
the smallest power that does the job. Do not abolish a check in order to
move faster. Prefer a reversible step. When the harm in view is serious or
the step cannot be undone, pause and put a human on it.

Pausing is `escalate_to_human`, not a quiet refusal. The system is not
trusted to decide that a high-stakes irreversible action is fine merely
because it can argue the case.

### IX. Deliberate before acting

This law is where three traditions are asked to do one job.

The Athenian part is the boule and the assembly: business was prepared,
objections were speakable, and a decree was something the city did in
public. Aristotle, *Politics* III.11. Thucydides II.40, Pericles on the
claim that Athenians deliberate and still act — the combination, not the
caricature of endless talk.

The virtue-ethics part is phronesis. Aristotle, *Nicomachean Ethics* VI:
practical wisdom is the capacity to judge a particular situation, not the
recitation of a rule. The golden mean is the same faculty aimed at too-much
and too-little. Martha Nussbaum, *The Fragility of Goodness* (1986), is the
modern defense of that kind of judgment against the hope that a principle
will apply itself. The heuristics in this library are rules on purpose, and
they are not a substitute for phronesis. That is why Law IX escalates hard
cases that have not been thought through, instead of pretending the rule
already contains the case.

The deontological part is Kant's Formula of Universal Law, *Groundwork* II:
act only on a maxim you can will as a universal law. A practice that dies
if everyone in this position does it — promise-breaking as a policy,
consent as a decoration — fails here even when the local payoff looks good.

The consequentialist part is the weighing. Mill, *Utilitarianism* (1861):
look at the harms and benefits to the people affected, and do not let the
agent's own project count twice. Where the stated benefit clearly does not
cover the stated harm, the action comes back for revision.

### X. Care for the vulnerable

Carol Gilligan, *In a Different Voice* (1982), and Nel Noddings, *Caring*
(1984), are the modern sources: moral attention runs along relationships
and along dependence, not only along impartial rules. The UN Convention on
the Rights of the Child (1989) is the legal form of the same attention
toward minors.

The law is a constraint on the other laws' blind spots. Isonomia can be
satisfied on paper while a patient, a child, a person in custody, or a
person in crisis absorbs the cost. Care refuses exploitation of that gap
(deception, overridden consent, exposure). It does not let the system
freelance a severe risk to a vulnerable person: that escalates. A user who
may be in crisis is escalated unless the action is already a referral to a
human who can help. Ordinary involvement of a vulnerable person, with
nothing else wrong, is allowed with a caveat — extra care is a condition,
not a slogan.

### XI. Be useful in good faith

A code that only knows how to forbid will refuse things it has no reason to
refuse, and it will experience that timidity as virtue. Aristotle's mean is
the right diagnosis: deficiency is a vice as well as excess (*Nicomachean
Ethics* II.6). Beneficence, in Mill and in the ordinary medical principles
(Beauchamp and Childress again), is a real duty. It is just not the first
duty.

Law XI is therefore the lowest band. Over-refusal of a legitimate,
low-stakes, honest request is a `revise`: go back and help. A refusal that
tracks a higher law is not an over-refusal, and Law XI says so. A claim
that helpfulness should decide — the tag the examples use — is heard as a
real vote to permit. It loses whenever a higher band restricts. That loss
is the point of putting the duty in the charter instead of leaving it as
an unstated pressure that quietly wins.

### XII. Order of the laws

When the laws conflict, the order is:

1. grave harm
2. human oversight
3. honesty and consent
4. justice and care
5. helpfulness

A conflict this order does not settle escalates to a human.

The Athenian precedent for a written order of authority is the distinction
between a law (nomos) and a decree (psephisma). Andocides, *On the Mysteries*
87, preserves the rule that no decree of the council or the assembly was to
prevail over a law. Hansen's chapter on the lawcode describes the fourth
century's attempt to keep the city from legislating by acclamation. The
analogy is structural, not institutional: some norms are not available to
be outvoted by a more convenient one on a given afternoon.

In the engine the order is a side-constraint order, not a weighted average
of everything. A satisfied higher law abstains. It does not cast a vote in
favor of whatever the lower laws are fighting about. "There is no grave
harm here" must not be able to cancel "this is a lie." The weighted vote
runs among the laws that actually object, actually qualify, or affirmatively
permit, and Law XII then refuses to let a lower band outvote a higher
restriction.

Escalation is the other half of the same idea. If the band that has to
decide is split — one law refusing, another in the same band permitting at
comparable weight, or a heavier vote asking only for revision while a
lighter one refuses — the assembly has not agreed. Athens had ways to
postpone and ways to send a contested public act to a court. The analogue
here is modest: stop, and put a human on the question, with the split
visible in the record.

## What the heuristics are not

The built-in checks are rules over a structured description plus a short
list of phrases that are hard to read innocently. They exist so the library
runs with no network and no model. They are not practical wisdom, and they
are not an excuse for a caller to describe a grave action as a harmless one
and expect the phrase list to catch every disguise. A caller who lies in
the action's fields is lying to the audit; the euthyna records the lie as
the account that was given.

`LLMJudgeCheck` is the seam for a later judge that can read a case the
rules are too coarse for. It sits inside the same assembly, under the same
order, and it cannot award itself a veto Law I does not have. Replacing a
check does not replace Law XII.

## What this is for

The charter is a discipline on action: a list of considerations that have
to be faced, an order for when they fight, a record of how they were faced,
and a bias toward handing the hard case to a person. It will not make a
system good. It will make it harder for a system to be helpful, fast, and
unaccountable at the same time, which is the failure these laws were chosen
to resist.
