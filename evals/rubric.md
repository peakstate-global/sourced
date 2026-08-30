---
rubricVersion: 5
frozen: 2026-08-30
reanchored: 2026-08-29
---

# The rubric

Eleven criteria. Nine score 0 to 3 against a written anchor. Two are gates: a zero there fails the
topic whatever the rest says, because a beautiful answer resting on a fabricated citation is worse
than a poor one.

**This file is frozen before any skill edit.** Writing a rubric to match what the skill already
does is gaming. Writing a skill to match criteria set in advance is alignment. The two are
distinguishable only by which came first, so the commit order is the evidence and this file is
committed first.

**v2, after round 01.** Round 01 returned 61 of 64 criterion readings at maximum, so the ruler
could not rank four runs or detect any improvement. Three changes: G1's check target was wrong and
produced a false gate failure on a correct artefact; C4 and C8 were ambiguous enough that the two
graders split on them in the same direction every time; and C1, C5 and C6 have been re-anchored so
that a 3 is rare. **A 2 is a good artefact.** Nothing here was added to describe a capability the
skill gained after round 01: the artefact-shape features are measured by coverage in
`features.json`, which is mechanical detection and has no anchor to write toward.

**v3, after round 02.** Three changes, all of them things round 02's graders said the anchors could
not express. C8 gains a middle rung and a scope ruling, because five of eight sheets independently
reported that its rungs did not fit what they found and the two graders disagreed on whether
inferred and adversarially-written claims were even in scope. C3 gains a line on generated padding,
the one criterion the graders split on in both directions. And **C9 is new**: it scores whether the
paper carries the shape the skill now specifies.

**C9 is scored against a shape written in the same cycle, which is a known weakness.** The
orchestrator argued for measuring it by coverage only, on the ground that a criterion written
alongside the thing it measures cannot tell you whether the specification was any good. The user
overruled that, on the ground that a criterion is how a rule actually gets enforced. So C9 is here,
and this paragraph is the disclosure: **a good C9 score in round 03 means the papers followed a
fresh instruction, not that the instruction was correct.** Read it as a conformance check, never as
evidence the shape earns its keep. That evidence, if it comes, comes from C1 to C8 moving.

**v4, after round 03.** Two changes, both from what round 03's graders found.

C8 gains a **quality clause**. Round 03's refusal made the falsifier field mandatory and one run
answered it with a stamped template across nine claims, which one grader marked down and the other
counted as present. Presence is now enforced by the skill, so the criterion scores whether the
falsifier names an observation somebody could go and make.

C9 is rewritten for the paper shape as it now stands: definitions in two subsections with a family
named for each term, propositions carried as claims, and a verdict table that restates the
proposition it is keyed to. **C9 is still conformance and still reported separately.** It measures
whether the paper followed the instruction, never whether the instruction was any good.

**v5, after round 04.** Four repairs, every one of them something a grader hit.

C9 now says how labels are checked. It split on all four papers in the same direction, which is one
ambiguous anchor rather than four differing papers: one grader read "labels agree" as the five parts
being present and labelled, the other as the body, the table and the sidecar cross-referencing
correctly. Two disputes were then settled by counting, and the cross-reference reading caught real
defects the presence reading missed. So the anchor says cross-reference.

C8 gains a rung for a paper that is mostly specific with one templated class, because 43 good
falsifiers and 9 stamped ones fitted the 1 and the 2 anchor equally. Its scope ruling now covers
normative claims, which can no more carry an observational falsifier than definitional ones can.

C3 separates a process-provenance sentence from a limit on the evidence. "The hashes were
re-checked" is not something a reader decides differently for, and counting it as padding cost two
papers a mark.

**v5 scores are not comparable to v4, v3, v2 or v1.** The ledger records the ruler version per round for
exactly this reason. This is the fourth consecutive round under a moved ruler, which is a deliberate
choice: the target is still being discovered, so learning per round is the output and the trend is
not yet the point.

## What the suite is scoring

Not "did it answer well". The question is whether a run on a deliberately polarised claim
**pushes through the polarisation to an integrated position**: generous to each side, explicit
about the conditions each holds under, honest about what could not be grounded, and willing to
say where things are going.

## The nine scored criteria

Each anchor describes the artefact, not the process. A grader who cannot point at text scores 0.

### C1 — Integrated view (weight 3)

- **3.** Rare. All of a 2, **and** the position shows the debate was mis-specified: it names a
  word, measure or scope that both camps were using differently, and at least one part of the
  original claim comes out falsified rather than merely bounded. A reader who arrived holding
  either view finds their own concern inside it, and also finds out what they were arguing about.
- **2.** One position that holds the strongest part of each camp and says how the parts fit. Good
  work. Or: synthesis reached, but one camp is represented only by its weakest form.
- **1.** Two camps summarised side by side, with a preference stated and no synthesis.
- **0.** One camp restated. The other appears only as an error to be corrected.

### C2 — Robust and defensible (weight 3)

- **3.** Every load-bearing claim has been through an adversarial pass, and the pass is recorded:
  what was attacked, what survived, what did not.
- **2.** A pass ran and is summarised, but which claims it touched is not recoverable.
- **1.** Counter-arguments mentioned, no pass run.
- **0.** Assertion. No challenge anywhere.

### C3 — Limitations acknowledged (weight 2)

- **3.** Every limitation passes the decision test: a reader would decide differently knowing it.
  Limits on the evidence, never on our own thinking.
- **2.** Real limits stated, padded with one or two that change nothing.
- **1.** Boilerplate hedging.
- **0.** None, or the piece undercuts its own contribution instead of the evidence.

**A process sentence is not a limitation.** "The hashes were re-checked", "captures were re-verified
before delivery", "the prior corpus held nothing" describe how the work was done. They belong in
Attribution or in the body, and in Limitations they are neither padding nor substance — they are
misfiled. **Do not count them either way**: judge the section on the sentences that are genuinely
about the evidence, and note the misfiling in your reason line.

**Generated text is judged the same as written text.** `conflicts.py` writes a Limitations sentence
for every open conflict, and those sentences are templated. A templated line still passes the
decision test if a reader would act differently knowing it, and still fails if it only restates the
body. **Judge the sentence, not its origin.** Round 02's two graders split on this in opposite
directions on the same artefact, one counting three generated conflict paragraphs as padding and
the other counting them as material limits. Neither reading was unreasonable under v2, which is the
defect this line repairs.

### C4 — Sound forward hypothesis (weight 3)

- **3.** Rare. A stated view of where this is **and where it is going**, resting on the surviving
  claims, with the conditions under which it holds and what would change it. The forward half is
  the test: a well-conditioned account of the present, however careful, is a 2. To reach 3 the
  artefact must say what happens next, or what it expects to observe, in a way a reader could be
  wrong about later.
- **2.** A committed present-tense position with its conditions and its falsifiers, but no
  trajectory. Or: a view stated, links to the evidence thin.
- **1.** A view stated that the body does not support.
- **0.** Refusal to commit, or a summary presented as a view.

### C5 — Charitable reconstruction (weight 3)

The criterion carrying the whole point of the suite.

- **3.** Rare. All of a 2, **and** at least one reconstruction is one its own advocates would not
  have written: it names a mechanism, or a narrower supportable claim, that the position's
  proponents do not themselves offer, and says what evidence would settle it. The generosity has to
  produce a new object, not a kinder restatement of the same one.
- **2.** Each position restated in terms its opponents could accept, naming the defensible thing it
  reaches for, and where the stated form is not supportable the run finds the nearby thing that is
  rather than stopping at the refutation. Or: one position gets this treatment and the other is
  handled fairly but not generously.
- **1.** Both positions stated accurately and neither is reconstructed.
- **0.** A position is reduced to its weakest form and dismissed. Straw man, however polite.

**Worked example of a 3**, from the request that produced this suite: asked about spiritual
practice and wellbeing, the supported thing is unlikely to be anything supernatural. A 3 goes
looking for what might be carrying the effect, attention training, contemplative practice, a felt
sense of connection to something larger, purpose, awe, ritual and social belonging, and says which
of those the evidence reaches. A 0 says there is no evidence for the supernatural and stops.

### C6 — Conditional truth mapping (weight 3)

- **3.** Rare. All of a 2, **and** each dimension is named as a variable with the values that
  divide it (not "depends on severity" but "baseline Hamilton score, above and below 16"), **and**
  the unknown region is stated: where neither holds nor fails has been tested. Usually most of it.
- **2.** For each contested claim, the region where it holds and the region where it fails, with
  the dimension named. "True for whom, when, under what" rather than "60 per cent likely". Or:
  conditions named for the headline claim only.
- **1.** Conditions gestured at without dimensions.
- **0.** A single verdict, unconditioned.

### C7 — Mechanism over verdict (weight 2)

- **3.** The causal or transmission channel is named, so a reader can watch the mechanism rather
  than wait for the outcome.
- **2.** Mechanism named for some claims, asserted for others.
- **1.** Correlation or authority standing in for mechanism.
- **0.** A probability or a rating with no mechanism at all.

### C8 — Falsifier stated (weight 2)

**Where the falsifier must live:** on the claim, in the sidecar's `falsifier` field. A falsifier
section in the artefact covering the headline positions is a 2, however good it is.

**Scope — which claims need one.** Round 02's graders disagreed on this and both defended their
reading, so it is settled here rather than left to the grader.

- **In scope:** every claim that survived the adversarial pass, whatever its `status`. That
  includes `inferred` claims, and it includes rival or replacement claims the pass itself wrote.
  A claim carrying the integrated position is the *most* in scope, not the least: it is doing the
  most work and is the least externally checkable.
- **Out of scope:** claims refuted or withdrawn during the pass; claims that are purely
  **definitional**, since a statement of what a word will mean here cannot be falsified by an
  observation; and claims that are purely **normative**, for the same reason — an *ought* is not
  settled by a measurement, and demanding a falsifier for one produces a fake. Both must be marked
  as such in the sidecar to be excused.

A claim is out of scope only if the artefact or sidecar makes it clear which of those two it is.
"Nobody wrote one" is not out of scope.

- **3.** Every in-scope claim carries a `falsifier` in the sidecar, and each one **names an
  observation somebody could go and make**: a measurement, a trial result, a published figure, a
  count. Different claims have different falsifiers, because different claims fail for different
  reasons.
- **2.** Every in-scope claim carries one, and **either** all are specific **except a single
  identifiable class** that carries none, **or** most are specific and **one identifiable class is
  templated** — a group sharing a stamped stem, typically the claims the adversarial pass wrote.
  This is the rung for 43 specific falsifiers and 9 stamped ones. Name both counts.
- **2 (the older reading, still valid).** Every in-scope claim carries one except a single
  identifiable class — for example the
  inferred claims, or the rival claims the pass wrote — and the artefact still states checkable
  falsifiers for the headline positions in prose. This is the rung for a run that did the work and
  missed a category.
- **1.** The artefact states falsifiers for the headline positions only, or the sidecar's coverage
  is scattered with no pattern to it. Also 1 if the falsifiers present are vague ("if the data
  changed"), **or if a group of claims share one stamped phrase with the specifics swapped out**.
  A template is what a run writes when a gate demands a field it has nothing to put in, and it is
  worth less than an honest absence because it passes a count.
- **0.** None.

**Count, then read three.** Name the number of in-scope claims and the number carrying a falsifier.
Then quote one falsifier and say whether you could go and check it. A count alone cannot see a
template, which is the failure this criterion now exists to catch.

### C9 — Paper shape (weight 2)

**Conformance only** (see the v3 and v4 notes at the top). This criterion asks whether the paper has
the shape the skill specifies. It scores structure, never quality: whether the forward view is any
*good* is C4's job, and a paper can score 3 here and 1 there.

Five parts carry it. All are required by `reference/research-mode.md`.

i) **Definitions, in two subsections.** *Terms not used here*, each with what the paper uses
   instead and one line on why; then *Terms used here*, as full blocks. A block describes a term the
   paper keeps — it never mixes a retired term and its replacement in one entry.
ii) **A family named on each defined term**, from the closed set: `umbrella`, `compound`,
    `overloaded`, `unmeasured`, `imprecise`, `judgement`.
iii) **Propositions enumerated and labelled `P1`…`Pn`**, each with its kind, and carried in the
     sidecar as claims with `role: proposition` rather than living only in prose.
iv) **A verdict table that restates the proposition** in column one alongside its label, with
    supporting claims grouped beneath as `P2.1`, `P2.2`; a `Conditions` column that says
    `Unconditional` rather than repeating the reasoning; and a fourth column for the evidence and
    reasoning.
v) **A forward-view section**, present and named, or an explicit statement that no forward view is
   supportable and why.

**Check the labels by cross-reference, not by presence.** Pick two or three labels and follow each
one through all three places: the proposition list, the verdict table row, and the body section
heading. They must name the same claim in each. A label that appears everywhere and points at
different things in two of them is the defect this criterion exists to catch, and it is invisible to
a reader who only checks that labels exist.

- **3.** All five present, and a label followed through the split, the table and the body names the
  same claim in each. A sub-row's id resolves to a claim in the sidecar.
- **2.** All five present, and a label points at different things in two places — the table restates
  a different claim from the proposition it is keyed to, a body heading uses a number the table
  gives to another claim, or sub-row ids do not resolve to sidecar claims. Also 2 if the
  propositions are enumerated but not carried in the sidecar.
- **1.** Three or four present.
- **0.** Two or fewer.

**Do not credit a part for being gestured at.** A paragraph discussing what a word means is not a
definitions block. A sentence saying the claim contains several propositions is not an enumeration.
A `Conditions` cell restating why the verdict was reached is not a condition.

**One instruction that is not scored here but is worth knowing while you read:** the definitions say
what the words mean *in this paper*, and never tell the reader their own usage is wrong. If a block
reads as an instruction to the reader, note it — it is a real defect with no criterion, and that is
information about the rubric.

## The two gates

### G1 — Provenance honesty

**Check the quote against the capture in the run store, never against the sidecar's evidence
row.** An evidence row carries one representative quote per source. An artefact may legitimately
quote several passages from the same capture, and only one of them will be in the row. Round 01
failed a correct artefact on exactly this mistake, on three separate quotes, and the fail had to be
overturned by hand.

Read the captured text file under the store's dated folder and search it. **Normalisation is not a
provenance failure**: an en dash rendered as an em dash, a curly quote straightened, collapsed
whitespace, or a line break inside a sentence are all the same quote. A changed word is not.

**Fail if any of:** a citation that does not exist; a reference written from memory rather than
retrieved; a quote that is not in the capture it is attributed to; RECALLED or INFERRED material
presented as sourced; a number without its source.

**Before recording a fail, name the file you searched and the string you searched for.** A gate
that fails a correct artefact is more expensive than one that passes a flawed one, because it makes
every other score on the topic advisory.

A fail here fails the topic. Everything else in the round is then advisory, because a grader
scoring the reasoning of an ungrounded artefact is scoring fiction.

### G2 — Anti-mush

**Fail if:** the integration is not load-bearing. "Both sides have a point" is a fail, not a pass.

The test: does the integrated position change what a reader would do, expect, or watch for? If the
answer is the same whichever side was right, nothing was integrated and the run has produced
diplomacy. Generosity is the method here, not the output.

## Scoring mechanics

- Two graders score independently, Claude and Codex, on the artefact plus its sidecar, with no
  access to prior rounds or to the recommendations that came out of them.
- **Disagreements are recorded per criterion, never averaged.** A split score is the most
  informative output a round produces: it means the criterion is ambiguous, or one grader is
  reading something the other cannot see. Both are worth knowing.
- Weighted mean over C1 to C9, out of 3. Gates are pass or fail and are reported separately.
- **C9 is reported separately as well as in the mean**, because it is a conformance check
  against a shape written in the same cycle. A round whose mean rose only because C9 landed
  has not improved: say so.
- Codex unavailable falls back to `adversarial-reviewer`, and the report names which grader ran. A
  fallback is not reported as a cross-model pass.

## Triage before belief

**Any criterion scored 0 or 1 gets a one-line triage naming what is at fault, in this order:**

i) **The topic.** Is the claim as worded actually answerable at that level?
ii) **The rubric.** Does the anchor describe something an artefact could show?
iii) **The skill.** Only then.

This is not ceremony. This suite's own predecessor reported a 67 per cent failure rate on its
first day and every one of those failures was in the measuring instrument. A round whose findings
all point at the rubric has measured the ruler, and that is a legitimate result to report.
