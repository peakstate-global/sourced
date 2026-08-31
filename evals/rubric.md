---
rubricVersion: 10
frozen: 2026-08-30
reanchored: 2026-08-29
---

# The rubric

Twelve criteria. Nine score 0 to 3 against a written anchor. Three are gates: a zero there fails the
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

**v6, after a human read of round 04's four papers.** Two changes, both from defects the rubric
could not see and a reader could.

C6 separates an **untested** region from a **contested** one. Across round 04's papers, 18 claims
were flagged `attempted-unresolved` by the adversarial pass and 15 had no conflict record at all:
nothing contested them, nobody had measured them. Every one read `Contested` in the verdict table
and **both graders passed all fifteen**. A criterion about conditional truth that cannot tell "two
sources disagree" from "no source exists" is not measuring conditional truth.

C9 checks that a proposition statement contains no verdict word. One round-04 paper wrote a
proposition asserting that the premises *are challenged*, which then took the verdict `Contested`,
and no reader could work out what was being claimed.

**v7, correcting v6.** Two of v6's changes were wrong and round 05's graders caught both.

C6's cap fired on any paper containing a `fails_when` region marked `untested`. But the skill was
changed in the same night to *let* a run mark such a region honestly, so the rubric penalised the
exact behaviour the skill was built to produce, and capped three of four papers for doing the right
thing. The cap now fires only where a paper **conflates** the two states.

C9 listed six definition families while the skill had seven. Every paper using the seventh was
marked down for following the specification. That is the third time one half of the instrument moved
without the other.

C9 also gains a partial reading: it scored a paper carrying 6 of 18 propositions in the sidecar the
same as one carrying none.

**v8 — every criterion is now a property of the artefact, not a property of the process.**

Three criteria used to name our machinery: C2 wanted an adversarial pass recorded in a sidecar, C8
wanted a `falsifier` field, C9 described our nine headings. **A rubric written that way chases the
skill** — C9 needed rewriting in three consecutive rounds because the skill's headings moved — and
it cannot score a paper produced any other way, which makes a control arm impossible to judge
fairly.

So each one is restated as the property it was really testing. C2 asks whether a reader can see
what was attacked and what survived, however that is recorded. C8 asks whether load-bearing claims
name what would overturn them, anywhere in the output. C9 asks whether the paper is decomposed and
navigable, without naming a heading.

**Nothing is weakened by this.** A sidecar is still the best way to satisfy C2 and C8, and a paper
that has one will score well. It is no longer the *only* way, which is the point: the rubric now
measures the depth we wanted rather than the mechanism we happened to build.

**The criteria are grounded in defects we have actually observed**, not in an idea of what good
looks like. Five rounds produced a real list: fabricated and mis-targeted citations, one quote per
source hiding what else it said, falsifiers that restate the claim, untested regions labelled
contested, propositions containing their own verdict, verdicts not matching the proposition they sit
under. Each is named in the anchor it belongs to.

**v8 scores are not comparable to v7, v6, v5, v4, v3, v2 or v1.** The ledger records the ruler version per round for
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

**The property:** the strongest case against the paper's own conclusion was engaged, and a reader
can see what that engagement changed. **However it is recorded.** A sidecar carrying a per-claim
`challenged` state is the cleanest way to show it; a section saying "I thought X, this objection
forced me to drop it, here is what replaced it" shows the same thing.

- **3.** Load-bearing claims have been attacked, and a reader can tell **which** claims and **what
  changed** — including claims of the author's own that died.
- **2.** The challenge is described but which claims it touched is not recoverable.
- **1.** Counter-arguments mentioned and answered, with no sign that any of them moved the position.
- **0.** Assertion. Nothing engaged.

**A paper that reports no claim of its own dying is suspicious at a 3**, not disqualified: it
happens, but it is rare enough to say so.

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

**Untested is not contested, and calling it so is a defect at any rung.** Three states get confused
and they are different findings for a reader:

| State | Means | Reads |
|---|---|---|
| **Contested** | Two sources were retrieved and they disagree | Somebody has to weigh them |
| **Untested** | Nobody has measured it. There is no second source | Somebody has to go and look |
| **Falsified** | Evidence was retrieved and it contradicts the claim | The claim is wrong |

**A region a claim "fails in" that contains no evidence is untested, not failed.** "Fails as a claim
about active-control trials, because none exist" is not a failure of the claim; it is an absence of
trials.

**Cap at 2 only where the paper CONFLATES the two.** A row that says a claim fails in a region
nobody has measured, or a verdict of `Contested` with no second source behind it, is the defect.
**A region explicitly marked `untested` — in the prose, or as a boundary `basis` — is the paper
getting this right, and must not be penalised.** v6 capped three of four papers for labelling the
distinction honestly, which is the opposite of what this criterion is for.

### C7 — Mechanism over verdict (weight 2)

- **3.** The causal or transmission channel is named, so a reader can watch the mechanism rather
  than wait for the outcome.
- **2.** Mechanism named for some claims, asserted for others.
- **1.** Correlation or authority standing in for mechanism.
- **0.** A probability or a rating with no mechanism at all.

### C8 — Falsifier stated (weight 2)

**The property:** the claims that carry the conclusion name the observation that would overturn
them, and a reader could go and make that observation.

**Anywhere in the output counts.** A `falsifier` field per claim is the most auditable form and the
easiest to score, but a sentence in the body — "this is wrong if the next trial reports X" — is the
same property. What does not count is a falsifier attached only to the headline while the claims
underneath carry none, because those are what the conclusion actually rests on.

**Scope — which claims need one.** Round 02's graders disagreed on this and both defended their
reading, so it is settled here rather than left to the grader.

- **In scope:** every claim the conclusion rests on, whatever its `status` and however the paper
  records it. Where a paper records a challenge round, that means every claim which survived it.
  That
  includes `inferred` claims, and it includes rival or replacement claims the pass itself wrote.
  A claim carrying the integrated position is the *most* in scope, not the least: it is doing the
  most work and is the least externally checkable.
- **Out of scope:** claims refuted or withdrawn during the pass; claims that are purely
  **definitional**, since a statement of what a word will mean here cannot be falsified by an
  observation; and claims that are purely **normative**, for the same reason — an *ought* is not
  settled by a measurement, and demanding a falsifier for one produces a fake. Both must be marked as such **somewhere in the paper
  or its record** to be excused — a sentence saying "this is a judgement, not a finding" excuses it
  exactly as a `kind` field does.

A claim is out of scope only if the artefact or sidecar makes it clear which of those two it is.
"Nobody wrote one" is not out of scope.

- **3.** Every in-scope claim carries a falsifier **somewhere in the output** — a per-claim field,
  a sentence in the body, a table column — and each one **names an observation somebody could go and
  make**: a measurement, a trial result, a published figure, a
  count. Different claims have different falsifiers, because different claims fail for different
  reasons.
- **2.** Every in-scope claim carries one, and **either** all are specific **except a single
  identifiable class** that carries none, **or** most are specific and **one identifiable class is
  templated** — a group sharing a stamped stem, whatever produced them.
  This is the rung for 43 specific falsifiers and 9 stamped ones. Name both counts.
- **2 (the older reading, still valid).** Every in-scope claim carries one except a single
  identifiable class — for example the
  inferred claims, or the rival claims the pass wrote — and the artefact still states checkable
  falsifiers for the headline positions in prose. This is the rung for a run that did the work and
  missed a category.
- **1.** The paper states falsifiers for the headline positions only, or coverage is scattered with
  no pattern to it. Also 1 if the falsifiers present are vague ("if the data
  changed"), **or if a group of claims share one stamped phrase with the specifics swapped out**.
  A template is what a run writes when a gate demands a field it has nothing to put in, and it is
  worth less than an honest absence because it passes a count.
- **0.** None.

**A per-claim field and a prose sentence score the same.** The field is easier to audit and that is
a convenience for the grader, not a credit to the paper.

**Count, then read three.** Name the number of in-scope claims and the number carrying a falsifier.
Then quote one falsifier and say whether you could go and check it. A count alone cannot see a
template, which is the failure this criterion now exists to catch.

### C9 — Decomposed and navigable (weight 2)

**The property:** a reader can find out where the paper stands on each part of the question without
reading it end to end, and can follow one part through the argument.

**No heading is named here, deliberately.** Until v8 this criterion described our own layout, which
meant it had to be rewritten every time the layout moved and could not score a paper written any
other way.

Four things carry it, and each can be satisfied by any structure:

i) **The question is split** into parts evidence can bear on separately, and the split is visible.
ii) **Contested words are defined** — the words two sides of the argument use differently — and the
    paper says what it means by them rather than instructing the reader.
iii) **There is a scannable statement of where each part stands**, before or alongside the
     argument, so a reader knows the shape before following it.
iv) **Labels hold.** Whatever names the parts — numbers, headings, terms — the same name means the
    same thing in the summary, the argument and any supporting record. **Check by following two or
    three labels through, not by confirming labels exist.**

- **3.** All four, and a followed label names the same thing everywhere.
- **2.** All four present, and a label points at different things in two places.
- **1.** Two or three present.
- **0.** One or none.

**C9 is conformance, not quality.** Whether the forward view is any *good* is C4's job, and a paper
can score 3 here and 1 there.

**A paper is not required to use our layout.** Until v8 this criterion listed the skill's own
headings and required them; that second scale was left standing underneath the new one in v8 and is
removed in v9, because a control paper could satisfy navigability in full and still score 0 against
it, with no rule telling a grader which scale to use.

## The three gates

### G1 — Provenance honesty

**The property: every citation exists, and says what the paper claims it says.**

Where the paper carries a capture store, check the quote against the capture — it is cheaper and
exact. **Where it does not, check against the live source yourself.** A paper produced without this
framework is not excused the standard; it is held to it with more work on the grader's side, which
is the correct direction for the burden to run.

**Check the quote against the capture in the run store, never against the sidecar's evidence
row.** An evidence row carries one representative quote per source. An artefact may legitimately
quote several passages from the same capture, and only one of them will be in the row. Round 01
failed a correct artefact on exactly this mistake, on three separate quotes, and the fail had to be
overturned by hand.

Read the captured text file under the store's dated folder and search it. **Normalisation is not a
provenance failure**: an en dash rendered as an em dash, a curly quote straightened, collapsed
whitespace, or a line break inside a sentence are all the same quote. A changed word is not.

**Fail if any of:** a citation that does not exist; a citation that does not say what the paper
claims it says; a quote that is not in the source it is attributed to; material the paper itself
marks as recalled or inferred, presented as sourced; a number with no source given.

**Do not fail on how a citation was produced.** v8 still listed "a reference written from memory
rather than retrieved", which a grader cannot observe from the artefact and which is false-positive
by construction on a correct citation from a paper with no capture store. **If the citation exists
and entails the claim, it passes, whatever route it took.**

**Before recording a fail, name the file you searched and the string you searched for.** A gate
that fails a correct artefact is more expensive than one that passes a flawed one, because it makes
every other score on the topic advisory.

A fail here fails the topic. Everything else in the round is then advisory, because a grader
scoring the reasoning of an ungrounded artefact is scoring fiction.

### G1b — Attribution and representativeness

**The property: the paper's empirical claims say where they come from, and a cited source read
past the quoted sentence still supports the use made of it.**

G1 checks the citations that are there. This checks whether there are enough of them, and whether
they were used fairly. It is the only place the suite looks at what a paper did *not* quote.

**This is attribution coverage, not evidence recall.** It asks whether the paper's own claims are
attributed. It does **not** ask whether the paper found the right literature — that would need an
independent search and is out of scope for a grader. **Say so when reporting it**, because
"attribution is complete" is a much weaker statement than "the evidence base is complete" and the
two are easy to confuse.

**Bounded and deterministic, so two graders get the same answer:**

- **Coverage.** List the load-bearing empirical claims — the ones the conclusion needs, not every
  sentence. **Cap the list at ten**; where there are more, take the first ten in document order.
  Report `cited` out of that list.
- **Representativeness.** Take **the three most-cited sources**, ties broken by first appearance.
  For each, read **the abstract, the results or findings section, and the limitations or discussion
  section** — not the whole document. Report `checked`.

**Fail if:**

- a load-bearing empirical claim carries no citation **and** no cited premises it is drawn from —
  **a label saying "my own inference" does not excuse an empirical assertion**. An invented effect
  size marked as the author's inference fails here, because an inference from nothing is a number
  with no source; or
- one of the three checked sources materially contradicts, in the sections read, the use the paper
  makes of it, and the paper does not say so.

**Report the numbers, not just the verdict:** how many load-bearing claims, how many cited, how many
sources checked. **A gate with no denominator cannot be compared between papers**, and the counts
are what make it possible to say anything about arms later.

### G2 — Anti-mush

**Fail if:** the integration is not load-bearing. "Both sides have a point" is a fail, not a pass.

The test: does the integrated position change what a reader would do, expect, or watch for? If the
answer is the same whichever side was right, nothing was integrated and the run has produced
diplomacy. Generosity is the method here, not the output.

## The defects this rubric is built from

**Every anchor above is grounded in something that actually happened**, across five rounds and four
topics. Listed here so the coverage is auditable and so a new criterion has to name the failure it
prevents rather than a virtue it admires.

| Defect observed | Where it is caught |
|---|---|
| A citation pointing at a different paper than the one described | G1 |
| A quote that is not in the source it is attributed to | G1 |
| One quote per source, hiding whatever else that source said | **G1b** |
| A claim of fact with no citation and no label saying it is the author's own | **G1b** |
| A falsifier that restates the claim: "an observation showing the opposite of X" | C8 |
| A group of claims sharing one stamped falsifier with the details swapped | C8 |
| A region nobody has measured, labelled as a region the claim fails in | C6 |
| A verdict of contested where nothing contests the claim | C6 |
| A proposition containing its own verdict, so the reader unpicks a double negative | C9 |
| A summary row naming a different claim from the section that argues it | C9 |
| A conclusion whose supporting claims carry no way to be wrong | C8, C4 |
| Limitations padded with sentences about process rather than evidence | C3 |
| A position that changes nothing a reader would do | G2 |

**When a grader's note names a defect not in this table, the rubric is not yet comprehensive.** That
has happened in every round so far, which is the honest state of it: the note field is the detector,
and a round whose notes name no new class is the first evidence of saturation.

## Scoring mechanics

- Two graders score independently, Claude and Codex, on the artefact plus its sidecar, with no
  access to prior rounds or to the recommendations that came out of them.
- **Disagreements are recorded per criterion, never averaged.** A split score is the most
  informative output a round produces: it means the criterion is ambiguous, or one grader is
  reading something the other cannot see. Both are worth knowing.
- **Weighted mean over C1 to C8 only.** C9 is a conformance check and is reported **beside** the
  mean, never inside it. Including it meant a round could move because a paper adopted our layout,
  which the rubric itself says is not improvement — reporting it separately did not undo that.
- **Three gates** — G1, G1b, G2 — pass or fail, reported separately.
- **C9 is outside the mean entirely**, because it is a conformance check. A round cannot move its
  headline number by adopting a layout.
- Codex unavailable falls back to `adversarial-reviewer`, and the report names which grader ran. A
  fallback is not reported as a cross-model pass.

## What the weights do, and what they double-count

The weights — C1 3, C2 3, C3 2, C4 3, C5 3, C6 3, C7 2, C8 2 — were set by judgement and have
never been calibrated. **Two things follow and both should be said whenever a mean is quoted.**

**Conditions and falsifiers are counted more than once.** A paper that adds boundary conditions and
a falsifier to its claims raises C4, C6 and C8 together — eight of the twenty-one available weight
— for what is substantially one property. The mean therefore moves faster on that property than on
anything else, which is a choice nobody made deliberately.

**So report the per-criterion table as the primary result and the mean as a convenience.** A
conclusion that rests on the mean moving, and not on which criteria moved, is resting on the
weighting.

## Triage before belief

**Any criterion scored 0 or 1 gets a one-line triage naming what is at fault, in this order:**

i) **The topic.** Is the claim as worded actually answerable at that level?
ii) **The rubric.** Does the anchor describe something an artefact could show?
iii) **The skill.** Only then.

This is not ceremony. This suite's own predecessor reported a 67 per cent failure rate on its
first day and every one of those failures was in the measuring instrument. A round whose findings
all point at the rubric has measured the ruler, and that is a legitimate result to report.
