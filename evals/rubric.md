---
rubricVersion: 2
frozen: 2026-08-29
reanchored: 2026-08-29
---

# The rubric

Ten criteria. Eight score 0 to 3 against a written anchor. Two are gates: a zero there fails the
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

**v2 scores are not comparable to v1 scores.** The ledger records the ruler version per round for
exactly this reason.

## What the suite is scoring

Not "did it answer well". The question is whether a run on a deliberately polarised claim
**pushes through the polarisation to an integrated position**: generous to each side, explicit
about the conditions each holds under, honest about what could not be grounded, and willing to
say where things are going.

## The eight scored criteria

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
section in the artefact covering the headline positions is a 2, however good it is. Round 01's two
graders split on this criterion on three of four topics, one reading the artefact and one auditing
the sidecar, so the location is now stated rather than left to the reader.

- **3.** Every claim that survived the adversarial pass carries a `falsifier` in the sidecar,
  specific enough to check. Claims that were refuted or withdrawn do not need one.
- **2.** The artefact states checkable falsifiers for the headline positions, but most surviving
  claims carry none in the sidecar.
- **1.** Vague ("if the data changed").
- **0.** None.

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
- Weighted mean over C1 to C8, out of 3. Gates are pass or fail and are reported separately.
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
