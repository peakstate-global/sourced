# Philosophy

The positions SOURCED rests on, and how they were arrived at.

`framework.md` states what the seven checks are. This states **why they are shaped the way they
are**, and it exists because several of these positions were argued into their current form and the
earlier versions were wrong. A framework that cannot say why it holds a position will drift back to
the comfortable version of it.

Each entry says what was held, what is held now, and what moved it.

---

## 1. A decision log records what was in context, not why

**Held until 28 August 2026:** never reconstruct the decision log at the end, because a
reconstructed reason is confabulation with a timestamp.

**The problem with that.** It implies a reason written at the time is more truthful than one written
later. It is not. A stated reason is never a readout of the mechanism that produced the answer, at
any timestamp. And a justification is always generated after the choice, because you cannot know you
need to justify something until you have chosen. There is no moment at which the model has
privileged access to its own cause.

**Held now.** Record the **state**, not the story:

- what was retrieved and what was in context
- which options were enumerated
- which was chosen
- which were rejected, and one clause on why
- which model, which version, which run

None of that requires introspection. It is fact about a moment, as checkable as a hash. The
justification is still written, because humans read it, but it is labelled as narrative generated at
time T from context C, and never as cause.

**The one timing asymmetry that survives.** A note written before the *consequences* exist cannot be
shaped by them. An account written at the end is produced with everything built on that choice
sitting in context, which exerts real pressure toward a story in which the surviving option looks
inevitable. That is a smaller claim than the original and it is defensible.

**The reason a log is worth keeping at all** is not that it is true. It is that rejected options
leave no trace in the finished artefact, so they are unrecoverable later, and a log written as you go
can be checked against what actually happened. A reconstructed log cannot be wrong in any way anyone
can detect. Unfalsifiability is the defect, not dishonesty.

---

## 2. R is a traceability log, not a thinking framework

The hypothesis-and-falsifier structure belongs in **O** ("for every claim that stands, state the
observation that would make it false") and in the boundary record (`holds_when`, `fails_when`,
`replaced_by`). Putting it into R as well duplicates it and turns a log into a framework.

Keep R dumb. The only free text is one clause on each **rejected** option, because that is the single
piece of information nothing else preserves.

---

## 3. O needs a fresh thread. A different model is a second layer, not the mechanism

**Held until 28 August 2026:** the value of O comes from using a different model.

**Wrong as stated.** The dominant effect is the **fresh context**. An instance that is not holding its
own draft has no commitment to defend, and it finds holes in reasoning, structure and consistency
reliably. That is most of the value and it is available to anyone with one model and one extra thread.

A different model adds a **distinct and narrower** class of catch: shared priors, where the model
believes something wrong and a fresh copy of itself believes it too. Fresh context fixes commitment.
Model diversity fixes belief.

**So the requirement is a fresh thread, explicitly adversarial.** Cross-model is an upgrade to record
when you have it, not a precondition. Three grades, in descending order, and the disclosure says
which one ran:

| Grade | What it catches |
|---|---|
| Different model, fresh thread | Commitment and shared priors |
| Same model, fresh thread | Commitment. The workhorse |
| Same thread, self-challenge | Some. The student marking their own homework, and better than nothing |

The third grade exists because it always works, in every host, with no setup. It is never presented
as equivalent.

---

## 4. The public artefact is self-contained

Someone who picks up this repo gets value immediately, with no second vendor, no private corpus and
no bespoke tooling. How any one team runs it will be more elaborate, and that elaboration stays out
of here.

The practical consequence: a step that depends on something private ships as a **declared step with
no implementation**. "Check what you already hold before retrieving anything new" is a step in the
workflow. Binding it to a particular knowledge base is a local decision, not part of the standard.

---

## 5. Confabulation is the mechanism, not the malfunction

The deck this came from says it plainly: generating the most probable next token, over and over, is
what the machine does. Everything it produces is confabulation. Remove that and there is no model.

This is why SOURCED does not try to make the model honest. It cannot be. Every check in the framework
is instead a way of **attaching something checkable to the output**: a retrieved sentence, a named
person, a recorded state, a test with a known answer, a disclosure a reader can act on. The
provenance is the trustworthy part. The prose never is.

---

## 6. Nothing here claims a human review makes output correct

A signature buys accountability, not accuracy. Wherever this framework asks for a name, it is asking
who answers for the thing, and what specifically they verified. It is never asking for reassurance,
and a disclosure that implies otherwise has failed the check it was written to pass.

---

## 7. Limitations carries limits on the evidence

**Held in writing from the start, and broken until it had a structural home.** The D rule has always
said our own frameworks, estimates, predictions and judgement do not belong in Limitations.
Restating it did not make it hold. A deck built under this framework still shipped the sentence
*"No evidence is offered that these seven checks improve outcomes."*

**Why it is wrong, not merely against the rules.** The artefact carrying that sentence had eleven
errors found in it by running the checks, errors that reading the same decks had not found. The
evidence was on a slide in the same deck. The sentence was not modesty, it was a claim contradicted
by the artefact it appeared in.

**The distinction.** Limitations carries limits on the **evidence**: a source not retrieved, a
primary read through a secondary, a small base. Our own thinking is the **value** of the piece, and
it is disclosed as INFERRED in the sidecar, which is the whole disclosure it needs.

**Why the rule now holds.** Restating it did not work, because the rule described where a
sentence must not go and left open where it should go instead. The fix was to give our own
contribution a place of its own: a claim carries a `kind`, and `position` and `story` are
evidence-exempt species, disclosed as INFERRED in the sidecar. There is nothing to refuse in
Limitations because there is nowhere else for those claims to want to be.

A checker did exist for a while, refusing the sentence at the door. It has been removed. The
`kind` field removes the failure at its source, so the gate was treating a symptom.

**Position 8 kept its script, and the difference is instructive.** `integrate.py` runs before any
statement ships and refuses a delivery that hides a disagreement: an open conflict, evidence rows
that disagree with nothing recorded, or a claim that says where it fails without saying what is
true instead. It survives because it refuses an **omission**, which no data model can prevent. A
gate earns its place when nothing upstream can make the failure impossible.

---

## 8. Adversarial is the method. Integration is the goal

**Held until 28 August 2026, in the wording if not the intent:** argue the strongest case against a
conclusion, and say what survived.

**The problem with "survived".** It is a contest with one winner, so a pass hunts a verdict and stops
when it has one. A cross-model pass raised eight findings and framed every one as a defeat, when at
least three were boundaries. The word was doing the damage.

**Held now.** Every claim is a model of something at some fidelity, and no model is completely right.
The three drawings of a cat are all true, and each is wrong in a way the drawing cannot show you.
**The output of an adversarial pass is a map, not a verdict.**

When two findings disagree, the default assumption is not that one is wrong. It is that each is right
inside conditions the other did not have, and the work is to find those conditions and write them
down. A verdict throws away the half of the evidence that lost. A boundary keeps both and says where
each applies.

**Why this is the point of the whole framework.** Polarisation is a modelling failure: a conditional
question answered black and white. Every boundary recorded moves the model a little closer to the
thing itself. Doing that for years is how the cat gets closer to being the cat.

**The practical consequence.** A conflict between two sources is a first-class object, not a decision
made quietly in a draft. It opens when the disagreement is found, it stays open until it resolves
into a boundary, and where it cannot be resolved it ships open, with the unknown region named.
Shipping an open conflict is honest. Resolving it silently is not.

---

## 9. Conditions are an open vocabulary, held in a registry

**Rejected on 28 August 2026:** a fixed set of five condition fields (population, period, setting,
tooling, n).

**Why it was wrong.** Conditions are as varied as the subject matter. The sky is blue when the
weather is fine, the sun is high, the air is clean, and you are looking overhead rather than at the
horizon. None of those is population or tooling. A fixed list would have forced every domain through
five holes that fit one domain.

**Held now.** A condition is `{dimension, value, basis, status}`. The **dimension is free text**,
so any domain can name what actually moderates its claims. The **shape is fixed**, so conditions
stay comparable.

**The basis split of 29 August 2026 does not touch this position.** `basis` became two fields, who
said it and how far it has been checked, and both are closed vocabularies. The dimension stayed
free text, because the reason for it has not changed: conditions are as varied as the subject
matter, and how a condition is known is not.

**The registry is what makes conflict computable.** Two claims can only be compared on a dimension
they both name, so first use of a dimension defines it in a per-project registry, and later uses
autocomplete against it rather than inventing a synonym. `tooling` and `tool-generation` as two
dimensions is the failure mode; the registry is the cheapest thing that prevents it.

**What this does not become.** A taxonomy exercise. The registry accretes from use, nobody designs it
up front, and a dimension with one claim against it is still a legitimate dimension.

**Added 29 August 2026: a name is not enough, because the two failures are not symmetric.** The
registry above prevented one failure and not the other.

A **split** is two names for one dimension. `tooling` and `tool-generation` recorded separately is a
spelling accident. You miss a comparison, the miss is silent, and it is recoverable: merge the two
rows later and the comparison comes back.

An **overload** is one name covering two meanings. `method` meaning a research method on one claim
and a manufacturing method on another is one name over two dimensions. You make a **false**
comparison. `conflicts.py` compares two rows because they share a name and nothing reads what the
name means, so two claims about different things are recorded as a conflict, that record reaches
`integrate.py`, and `integrate.py` refuses the delivery. **A wrong refusal is how a gate gets
bypassed**, because a gate that refuses good work is a gate somebody switches off.

**Overload is the expensive failure, and a registry of bare strings prevents only splits.** So a
registry row now carries a one-sentence **definition**, required at mint, and a mint with no
definition is refused. The definition is also what makes a near match safe to offer: matching on
names alone, with nothing to read, is exactly how an overload happens, so `register` hands back the
existing row with its definition and the author decides. **A mint is still never refused for
existing.** Only a missing definition refuses.

**Added 29 August 2026: a dimension is a claim, so it carries a level. This is what resolves the
fixed-list argument, and it resolves it rather than winning it.** `air quality` is a level-1
dimension. `particulate concentration` is a finer one whose `coarser` is `air quality`. That is
position 10's ladder, run through position 10's validator, with no second implementation.

The knowledge-base application's fixed list of thirteen is **not a rival vocabulary. It is the set
of level-1 rungs.** Coarse dimensions recur across projects and are stable enough for machine
extraction at corpus scale with no author present, which is the thing that list is for. The long
tail hangs off them as finer children, and the long tail is what free text is for. Neither side was
wrong; they were describing different rungs of one ladder and arguing as though there were only one.

`finer` is not stored, because it is the exact inverse of `coarser` and a stored pair of inverses is
a pair that can disagree.

---

## 10. The sophistication ladder has no top, its rungs have no names, and the numbers are relative

**Held until 29 August 2026:** a statement carried a level from a fixed set of four, level 4 was
named "conditional", and levels 1 to 3 were named conversational, informed and practitioner.

**Held now.** A level is any whole number from 1 up, and it is an ordinal with no name. It prints
as "level 7". A claim stated at level 3 or above whose evidence carries no quote and no locator does
not ship: `integrate.py` refuses it, and the two ways out are to cite the claim precisely or to state
the claim at level 2.

**What moved the top off.** There is no end to stating a claim more precisely, so a fixed top was an
arbitrary wall in front of work somebody will do. And naming a level after conditions confused the
ladder with the thing hanging off it: a claim at any level can carry conditions, and each of those
conditions carries its own level on the same unbounded ladder. "Clean air" and "particulate below six
parts per million" are one condition at two depths, and there is a third depth below that one.

**What took the names off, on 29 August 2026.** Levels are ordered, not named by audience, because
an audience name invites an argument about who counts as a practitioner. That
argument is not about the claim, and it is the argument the names kept starting. The names survive
only as a teaching gloss in prose, said as a gloss, and never in a rule, a message or a validator.

**The numbers are relative, not absolute, and this is what makes them safe.** A level does not name
an exact quantity of precision. Two artefacts do not have to agree about what their level 3 holds,
and consistency across artefacts is not maintainable, so nothing tries to maintain it. **A level is a
position in one artefact's ladder, so nothing may compare a level across two artefacts.** A number
that looked absolute would invite exactly that comparison, and the comparison would be meaningless.

**Re-levelling later is expected, not a defect.** A claim or a condition may need to move when
something turns up that sits between two rungs already written down. On a named ladder that move is
an argument about whether the new thing is really "informed". On a numbered one it is an edit.

**The accepted risk.** A hard gate on a stated level creates pressure to under-state the level to get
past it, which corrupts the field it is checking, and that pressure was accepted deliberately because
the alternative was a report nobody reads.

---

## How this file gets used

Add to it when a position moves. State what was held, what is held now, and what moved it. A position
that changes without a record is a position that will change back.
