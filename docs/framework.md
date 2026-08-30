# The framework

SOURCED in full. Written 26 August 2026, after a review pass on a client deck where
every part of it was argued out and forty-one review comments were resolved.

The deck teaches this. This states it.

---

## 1. What SOURCED is

Seven checks on any artefact that contains model output, in the order the work happens.
**It has two faces and they must not be collapsed:**

| Face | What it is | Where it belongs |
|---|---|---|
| **The seven problems** | Human failure modes, older than the tool, stated as the thing that hurts | The diagnosis. Stated with no letters attached |
| **SOURCED** | The seven checks that answer them, one each | The remedy |

Teaching or tooling that shows the letters while describing the problem has given away
the only thing that makes the framework land: the reader recognising the problem as
theirs before being handed a name for the fix.

## 2. The seven, both faces

| | Check | Answers the problem | Human failure mode |
|---|---|---|---|
| **S** | Sourced | Nobody can tell where any of it came from. | Fluency bias |
| **O** | Opposed & Integrated | Nothing ever argued back — or it argued back and nothing was built from what it found. | Confirmation bias, plus sycophancy |
| **U** | Underwritten | If it is wrong, no name is on it. | Diffusion of responsibility |
| **R** | Recorded | The reasoning was never written down (while it happened). | Narrative fallacy |
| **C** | Constrained | There is no safety net. Nothing stops it doing the wrong thing. | Normalisation of deviance |
| **E** | Evaluated | The system changed since it was checked. | Frozen baseline |
| **D** | Disclosed | The reader cannot tell what was checked, or by whom. | Automation bias |

**O carries two words on purpose.** Opposed blocks the under-evidenced claim, which is the
primary outcome. Integrated takes what survives further: using the evidence conditionally where
it holds, or finding the resolution that makes the tension unnecessary. One word made the second
half look like a by-product, and in practice that produced reviews which listed objections and
stopped. The asymmetry is deliberate, not a forced acronym.

**The parenthesis in R is deliberate.** Two failures, not one: the reasoning was never
written down, and it was never written down *at the time*. Reconstructing it afterwards
produces a story, not the reasoning.

## 3. What each check requires

| | In your own work | When a team runs it at volume |
|---|---|---|
| **S** | Ask for the verbatim sentence plus page or timestamp. A fabricated quote fails a text search in two seconds. | Retrieval with citations enforced in the pipeline, plus a hash of what was retrieved so you can tell when a source moves. |
| **O** | Run the challenge on a second tool, from a different model family. Pre-register the answer you expect. Then resolve what it found with one of the four moves, or record the tension as open. | A standing adversarial pass, with conflicts logged rather than resolved silently, and every resolution naming the move that produced it. |
| **U** | Write the check, not the act: "I verified every figure against source", never "reviewed". | A named owner per system, not per document. Nobody can sign ten thousand outputs. |
| **R** | Three lines in the doc while the work happens: what you decided, what you rejected, which model and when. | Traces emitted by the system: prompt, model version, tools, retrieved context. |
| **C** | A standing instruction: no number without a source, no claims about a named person, no legal conclusions. | Guardrails that fail closed and visibly. |
| **E** | Eyeball it, unless you will run it repeatedly. Then collect examples and have a second model grade the first. | A suite seeded from real failures, re-run on model, prompt, index or tool change. |
| **D** | The four-label provenance block, below. | Disclosure generated with the artefact, plus an inventory of which systems touch decisions about people. |

**Four of the seven have no manual version at volume: S, R, C and E.** That is the
argument for building them into systems rather than teaching them as a discipline, and
naming them as engineering work is how they get funded.

## 4. The provenance block — D's output

```
Attribution:  Who authored it, and that AI tools assisted, in one sentence.
Accountable:  The named person who answers for it.
Limitations:  What is not backed, and how far each claim is from its source.
References:   What backs it, where it lives, and how it can be checked.
```

**The governing test: every line must either make a limit transparent, or let the reader
go and check something.** A line that does neither is a motherhood statement and comes
out. Two of the four are integrity, two are investigable, by design.

- *"Twelve sources, retrieved and hashed on 25 August 2026, each figure quoted with a
  locator."* — investigable. Pick one, check it, catch me.
- *"Sources verified against originals."* — neither. It asserts diligence, the one thing a
  reader cannot verify. **Cut.**

**There is no `Verified:` label.** Verification is a property of the references and lives
inside that line as a checkable fact. **`Limitations` is never empty**: if nothing is
limited, the artefact has not been examined closely enough.

**Do not use "Out of scope" as the label.** It was tried and it silently changed the
content: "out of scope" invites facts about the *project* ("this session has never been
run"), where the line's job is facts about the *claims* ("read through a citation, not the
original"). The wrong label produced the wrong content.

## 5. The stance underneath

Say this before the seven, not after:

> **None of these problems are new. A machine did not invent one of them. It made every
> one of them faster, cheaper and harder to see, at a volume nobody reads.**

Consequences that follow, and that any implementation should not drift from:

- **Human work has always needed this.** A report with no sources fails S whether or not a
  model touched it. Any tooling that only fires on AI-assisted artefacts has misread the
  problem.
- **The policy conversation about disclosing AI is largely an overreaction to a new tool.**
  Ghost-writers never got a credit line. The one thing that survives the comparison: a
  ghost-writer can be asked what they checked, and a model cannot. The disclosure is about
  **scope**, not credit.
- **A signature buys accountability, not accuracy.** U is real and it is not a quality
  mechanism. The quality mechanism is the system around the person.
- **No complete automated checker can exist** (Rice, 1953). C is provably incomplete, which
  is exactly what U is for.
- **Provenance and quality are different questions.** Conflating them turns a governance
  conversation into a taste argument.

## 6. Where the checks come from, and where they do not

Mapping done against the four bodies the deck cites:

| Body | Requires | Maps to |
|---|---|---|
| APRA, letter to industry, 30 Apr 2026 | Governance, risk management, assurance, resilience; transparency over how models are trained, updated or constrained | R, E, D |
| National AI Centre, 21 Oct 2025 | Six essential practices: decide who is accountable; understand impacts and plan accordingly; measure and manage risks; share essential information; test and monitor; maintain human control | U, D, E |
| Privacy Act, APP 1.7–1.8, from 10 Dec 2026 | The privacy policy must describe decisions made solely by a computer program, and those where something substantially and directly related to the decision is automated | D |
| NIST GenAI Profile, 2024 | Names confabulation, and human-AI configuration (automation bias, over-reliance), among twelve risks | S, D |

**C is ours.** No body asks you to constrain anything. APRA comes closest and even that is
transparency over constraint, not a requirement to constrain. Worth knowing internally; the
deck deliberately does not say it, because it reads as a no-brainer safety practice and
flagging its provenance is pedantry.

**Nothing above requires the provenance block.** APP 1.7–1.8 is a privacy-policy obligation
discharged by the entity, not by a line on a document. The block exists because every other
line tells the reader what *is* backed, and without Limitations a reader reasonably assumes
everything has the same evidential status as the parts carrying references.

## 7. Claim strength is a separate axis

Do not build strength grading into SOURCED. It already exists, in Publish's claim-tier
spectrum, and a claim-record store stores it:

- **Tier** — how much backs a claim. 0 unanalysed · 1 evidence sought, none found or
  contradicted · 2 single source · 3 multi-source corroborated · 4 **boundary recorded**,
  meaning the claim carries a record of where it holds and where it fails. Plus **position** (a stance, evidence-exempt by design) and **story**
  (author-verified lived experience) as their own species of sentence, not weak tiers.
- **State** — lifecycle: open → awaiting-decision → awaiting-revalidation → settled.
  Computed, never stored.
- **Provenance[]** — the typed, timestamped event chain.

**Tiers grade a claim. The block covers the artefact.** Two scales, do not merge them.

A further point sharpened in this review: **a condition is itself a claim, so it carries
its own tier.** "Clear air" is a tier-1 condition; "particulates below X" is the tier-3
version of the same condition. The rule to implement: *state a condition at the level the
decision needs, not the level you happen to reach.*

**Sophistication is a second, separate axis, and it is unbounded.** The tier above runs 0
to 4 and grades how much backs a claim. Sophistication grades how precisely a claim is
stated, it starts at 1, and it has no top, because there is no end to stating a claim more
precisely. **A level has no name; it is an ordinal and prints as "level 3."** Do not confuse
the two scales. A tier-4 claim carries a boundary record; a level-4 claim is simply
phrased more precisely than a level-3 one, and says nothing about its evidence. The numbers
are relative to one artefact, so nothing compares a level across two.

### One vocabulary for the book and the sidecar

The book and the sidecar now use one vocabulary, so one claim is not described two ways.
`skills/sourced/vocabulary.py` holds the mapping and the derivation.

| State | Label | Kind | Backing | Process |
|---|---|---|---|---|
| `0` | `unanalyzed` | not decided by the state | none | none |
| `1` | `no / contradicted evidence` | not decided by the state | 1, none found | evidence was sought |
| `2` | `single source` | not decided by the state | 2 | none |
| `3` | `multi-source` | not decided by the state | 3 | none |
| `4` | `boundary recorded` | not decided by the state | none | a boundary was recorded |
| `position` | `stance (evidence-exempt)` | position | none, evidence-exempt | none |
| `story` | `lived experience` | story | none, evidence-exempt | none |

The labels are Publish's stored strings, quoted verbatim, which is why `unanalyzed` keeps
its American spelling.

**The 0 to 4 ladder is not one scale, and the map no longer pretends it is.** Tiers 1 and
4 report what was **done to** the claim, tiers 2 and 3 report what **supports** it. A claim carrying a boundary record while resting on one self-interested
source is a 4 and a 2 at the same time, and one number cannot say so. `MAP` therefore
reports `backing` and `process` in every row, `backing()` returns the backing axis alone,
and the 0 to 4 number survives as a presentation computed by `publish_state()`.

**Tiers 0 to 4 decide no kind.** A tier-3 claim may be empirical or a synthesis, and the
tier does not say which. **`position` and `story` are kinds and carry neither axis**,
because they are their own species of sentence and not weak tiers.

**Provenance and fidelity are independent of all seven states.** A tier-4 claim can be a
paraphrase, and a position can quote somebody and still be a stance. The map states that
independence in every row rather than leaving it out, because silence in a table reads as
"not applicable".

**Strength is derived from the evidence rows and is never stored.** 0 nothing recorded ·
1 evidence sought and none found, or a row that argues against the claim · 2 a single
origin group · 3 two or more distinct origin groups · 4 tier 3 with a boundary record on
the claim. `decisions.py validate()` refuses a sidecar that stores `strength` or `tier` on
a claim. **Since SOURCED 1.6 the number also says why it is what it is:**
`vocabulary.backing()` returns the grade with its named `downgrades`, in the claim
standard's own words, deriving only the four a sidecar can actually see and leaving the
rest unset rather than guessing at them. A state Publish adds later is reported by name by `vocabulary.unmapped()` rather
than folded into whichever row looks closest.

### A third system, and the disagreements it surfaces

A third system, the claim store, holds claims too, as Claim Record v1, and its record is
the standard the author's other applications write to. `vocabulary.py` maps all three
systems, and **[docs/vocabulary-map.md](vocabulary-map.md)** writes the map out for a
reader: the exact matches, the fields the sidecar cannot answer, and the ten places
SOURCED, the claim store and Publish disagree.

Four of the ten were decided on 29 August 2026 and shipped in SOURCED 1.4: the condition
basis split, the removal of the level names, `mixed` as an evidence direction, and an owner
on a claim. Two more shipped in SOURCED 1.6: a per-claim `challenged`, with a competing
claim becoming a claim in its own right that a conflict and a `replaced_by` can name, and a
backing number that carries its named reasons. v2 stands open and v5 is half decided.
Where they differ the ADR is the authority and this repo has not moved. `python3 skills/sourced/vocabulary.py conflicts` prints all ten
and says which are decided.


## 8. The sidecar

`<artefact>.sourced`, JSON beside the artefact. Manifest, claims with a locator into the
artefact, evidence, disclosure block. `evidence[]` is deliberately the same object the claim-record store's
Claim Record stores; `claims[]` is deliberately thin, with no tier and no assertion type,
because those are the fields the platform implementations disagree about.

**A `.sourced` file is a lowest common denominator on purpose.** If it grows relations and
computed tiers it has become the Claim Record with extra steps, and the right move then is
to adopt that instead.

A worked example now exists, produced by the audit that accompanied this handoff:
the deck sidecar captured in a separate private repository — 13 claims, 12
evidence items, 10 sourced, 2 inferred, 1 recalled.

## 9. Working rules, each one earned

- **Quote and locate.** A verbatim sentence plus page, section or timestamp.
- **Fetch, do not recall.** If it was not retrieved, it is RECALLED, however sure you are.
- **Collapse origin before counting sources.** Ten write-ups of one press release are one
  source. Record `originGroup`.
- **Mark distance from primary.** "Cited in X, not read directly" is a fact the reader needs
  and costs one line.
- **Say what could not be grounded.** Silence reads as "everything here is backed".
- **Check before a delivery, not on a schedule.** A claim only hurts you when it is used.
- **A live source moves.** The tracker on the deck's stat slide moved by 37 in nine days
  while the deck was being written. Re-read dates are part of the claim.
- **Triage a failing eval before you believe it.** A 67 per cent "failure" in our own eval
  was a regular expression.
- **Scale it to the consequence.** A reversible internal draft is not a board paper.
