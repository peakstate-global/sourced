---
rubricVersion: 1
frozen: 2026-08-29
---

# The rubric

Ten criteria. Eight score 0 to 3 against a written anchor. Two are gates: a zero there fails the
topic whatever the rest says, because a beautiful answer resting on a fabricated citation is worse
than a poor one.

**This file is frozen before any skill edit.** Writing a rubric to match what the skill already
does is gaming. Writing a skill to match criteria set in advance is alignment. The two are
distinguishable only by which came first, so the commit order is the evidence and this file is
committed first.

## What the suite is scoring

Not "did it answer well". The question is whether a run on a deliberately polarised claim
**pushes through the polarisation to an integrated position**: generous to each side, explicit
about the conditions each holds under, honest about what could not be grounded, and willing to
say where things are going.

## The eight scored criteria

Each anchor describes the artefact, not the process. A grader who cannot point at text scores 0.

### C1 — Integrated view (weight 3)

- **3.** One position that holds the strongest part of each camp and says how the parts fit. A
  reader who arrived holding either view finds their own concern inside it.
- **2.** Synthesis attempted, but one camp is represented only by its weakest form.
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

- **3.** A stated view of where this is and where it is going, resting on the surviving claims,
  with the conditions under which it holds and what would change it.
- **2.** A view stated, links to the evidence thin.
- **1.** A view stated that the body does not support.
- **0.** Refusal to commit, or a summary presented as a view.

### C5 — Charitable reconstruction (weight 3)

The criterion carrying the whole point of the suite.

- **3.** Each position restated in terms its opponents could accept, naming the defensible thing it
  reaches for. Where the stated form is not supportable, the run finds the nearby thing that is,
  rather than stopping at the refutation.
- **2.** One position gets this treatment, the other is handled fairly but not generously.
- **1.** Both positions stated accurately and neither is reconstructed.
- **0.** A position is reduced to its weakest form and dismissed. Straw man, however polite.

**Worked example of a 3**, from the request that produced this suite: asked about spiritual
practice and wellbeing, the supported thing is unlikely to be anything supernatural. A 3 goes
looking for what might be carrying the effect, attention training, contemplative practice, a felt
sense of connection to something larger, purpose, awe, ritual and social belonging, and says which
of those the evidence reaches. A 0 says there is no evidence for the supernatural and stops.

### C6 — Conditional truth mapping (weight 3)

- **3.** For each contested claim, the region where it holds and the region where it fails, with
  the dimension named. "True for whom, when, under what" rather than "60 per cent likely".
- **2.** Conditions named for the headline claim only.
- **1.** Conditions gestured at without dimensions.
- **0.** A single verdict, unconditioned.

### C7 — Mechanism over verdict (weight 2)

- **3.** The causal or transmission channel is named, so a reader can watch the mechanism rather
  than wait for the outcome.
- **2.** Mechanism named for some claims, asserted for others.
- **1.** Correlation or authority standing in for mechanism.
- **0.** A probability or a rating with no mechanism at all.

### C8 — Falsifier stated (weight 2)

- **3.** Each surviving claim carries the observation that would kill it, specific enough to check.
- **2.** Falsifiers for the headline claim only.
- **1.** Vague ("if the data changed").
- **0.** None.

## The two gates

### G1 — Provenance honesty

**Fail if any of:** a citation that does not exist; a reference written from memory rather than
retrieved; a quote that is not in the capture it is attributed to; RECALLED or INFERRED material
presented as sourced; a number without its source.

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
