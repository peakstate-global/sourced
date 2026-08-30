# The adversarial pass

Read this when you are about to run O, or when you are writing the disclosure line that says
which grade of adversarial pass happened.

**The requirement is a fresh thread, explicitly adversarial.** The dominant effect is the fresh
context, because an instance that is not holding the draft has no commitment to defend and finds
holes in reasoning, structure and consistency reliably. A different model is a second layer on top
of that, not the mechanism: it catches shared priors, where a fresh copy of yourself believes the
same wrong thing. Both are worth having and they catch different faults, so the grade is recorded
rather than assumed.

## The three grades

In descending order. The identifier is the string that goes in the sidecar, and it is the same
string everywhere: in the record, in the check, and in the disclosure.

| Identifier | Grade | What it catches |
|---|---|---|
| `cross-model-fresh-thread` | Different model, fresh thread | Commitment and shared priors |
| `same-model-fresh-thread` | Same model, fresh thread | Commitment. The workhorse |
| `same-thread-self-challenge` | Same thread, self-challenge | Some. The student marking their own homework, and better than nothing |
| `not-performed` | No pass ran | Nothing. Say so plainly |

The third grade exists because it always works, in every host, with no setup. **It is never
presented as equivalent to the other two.** The fourth is not a grade of review at all. It is the
honest name for a pass that did not happen, and it is there so that a skipped pass has somewhere
to be recorded instead of nowhere.

## Picking the grade

Take the best grade the host actually offers. The skill asks what its host can do and records the
answer; it does not detect models and it does not orchestrate anything.

i) **Can this host spawn a sub-agent or thread on a different model?** Run the brief there.
   `cross-model-fresh-thread`.
ii) **Can it spawn a fresh sub-agent or thread on the same model?** Run the brief there.
   `same-model-fresh-thread`.
iii) **Neither.** Emit the handoff block below, so the user can run the brief by hand in a fresh
   thread and paste the result back. The grade is whichever of the first two they ran, and it is
   recorded only once their sidecar fragment comes back.
iv) **The user declines the handoff, or wants a result now.** Run the self-challenge in this
   thread against the brief below. `same-thread-self-challenge`.
v) **Nothing ran at all.** `not-performed`. Never leave it unrecorded, because an unrecorded pass
   and a passed review look identical to a reader.

**A lower grade is never reported as a higher one.** The grade in the disclosure is the grade that
ran, not the grade that was available or intended. If the handoff block was emitted and no
fragment came back, the pass that ran is the self-challenge or nothing, and that is what is
recorded.

## The brief

This is what the fresh thread is asked to do, and it is the same five steps whichever grade runs.
**The output is a map, not a verdict.** The pass is no less ruthless for that; it is ruthless about
finding the boundary rather than about naming a winner.

**Generosity is a method here, not a courtesy.** The strongest version of an argument is the only
one worth testing, and it is usually not the version its own advocates state. Reading a position
generously is how the boundary gets found in the right place, so it is the first step rather than
a tone to adopt while doing the others.

- **First, reconstruct each position at its strongest, before attacking anything.** State what
  it is reaching for, in words the people who disagree with it could accept. Where the position as
  stated cannot be supported, do not stop at the refutation: go and find the nearby thing that
  can. Asked whether spiritual practice improves wellbeing, the supported thing is unlikely to be
  anything supernatural, and it may well be attention training, contemplative practice, ritual, a
  felt sense of connection to something larger, purpose, awe or belonging. Say which of those the
  evidence reaches. A position knocked down in its weakest form has not been opposed, it has been
  dodged, and the claim that survives is worth nothing because it never met the real argument.
- **Argue the strongest case against each load-bearing claim**, once you have it at its
  strongest. A weak counter-argument is worse than none, because it makes the claim look tested.
- **Hunt the places where one word covers two mechanisms.** A single term standing over two
  different causes is how a claim passes a challenge it should have failed.
- **For every claim, state the observation that would make it false.** A claim with no falsifier
  has not been tested; it has been agreed with.
- **For every claim, record where it holds, where it fails, what is true instead** in the failing
  region, and which part of the space nobody has tested. A refuted claim with no replacement is a
  hole, and the reader fills the hole with the belief that was just refuted. Write it into the
  claim as `holds_when`, `fails_when`, `replaced_by` and `unknown_region`; see
  `reference/boundary-record.md`.
- **Where you can state the rival claim, state it as a claim.** A pass does not usually hand you
  two sources that disagree; it hands you a claim that is true instead. Write it out with its own
  statement, its own evidence, its own `holds_when` and `fails_when` and its own level, so it
  lands in `claims[]` as a claim and not as a sentence inside somebody else's `replaced_by`. Then
  record the disagreement as a conflict whose side is that claim, and point the original claim's
  `replaced_by` at it. The conditions on the two claims are what say where each of them is right.
- **Say what you found about each claim, in one word.** `challenged` is `not-attempted`,
  `attempted-unresolved`, `holds`, `holds-with-boundary` or `refuted`. It is not a verdict about
  who won: `holds-with-boundary` is the ordinary good outcome, and it means the claim came
  through and you found where it stops holding.
- **Where two pieces of evidence disagree, do not pick one.** Give the conditions each side held
  under, say where each is right, and record the disagreement as a conflict: `conflicts.py` holds
  the record and `docs/sidecar.md` describes it. Adversarial is the method, integration is the
  goal. A conflict that cannot be closed ships open with its unknown region named.
- **Mark every support you set as yours.** Any evidence you introduce carries `supports`, the
  claim it votes on and which way, with `by` of `model` and your model name. You propose and you
  never decide: the gate refuses on the recorded field, so a wrong proposal is a visible wrong
  row somebody can fix, where a wrong verdict would be invisible. `integrate.py` flags a
  conflict whose two sides are both model-proposed, so the author knows what nobody has
  confirmed.

## Resolving what the pass found

A pass that returns objections has done half the work. Every finding resolves with one of the four
moves, or is recorded as open:

- **Conditional** — each side holds in a nameable region. State the region, and the observation
  that places a case in it.
- **Reframe** — both sides share a hidden assumption, and dropping it removes the trade-off.
  **Name the assumption.** If you cannot name it, this is not a reframe.
- **Redirect** — the observation is sound and the conclusion drawn from it is not. Say what the
  evidence does support, not merely what it fails to support.
- **Hold** — nothing available settles it. Name the evidence that would, and ship the tension open.

Splitting the difference is not a move. Before choosing, check whether the two claims are about
the same level of description at all; when they are not, that is a level confusion, and it routes
to Conditional with the level as the region, or to Hold.

Record which move produced each resolution. A resolution with no named move is the shape a
verdict takes when it is pretending to be a boundary.

## What is recorded

The optional top-level `opposed` object on the sidecar, in `sourced` 1.2:

    grade           one of the four identifiers above. Required
    at              when the pass ran, UTC. Required
    raised          how many challenges it raised. Required, and 0 when nothing ran
    model           which model ran the pass, where it is known. Optional
    modelVersion    that model's version. Optional
    thread          the thread, run or sub-agent id, where the host gives one. Optional
    note            one sentence, for the case where nothing ran or the pass was cut short. Optional

Beside it, and per claim rather than per artefact, the optional `challenged` field in `sourced`
1.6: one of `not-attempted`, `attempted-unresolved`, `holds`, `holds-with-boundary`, `refuted`.
Absent reads as `not-attempted`. **`opposed` and `challenged` answer different questions and
neither derives from the other**: `opposed` says which grade of pass ran over the artefact, and
`challenged` says what that pass found about one claim.

`decisions.py validate()` refuses an unknown grade, a missing required key, a
`not-performed` record claiming it raised something, and a `challenged` outside the five words. The object is optional as a whole, so every
sidecar already on disk stays valid and an implementation that has never heard of `opposed` is
not broken.

## The exact disclosure wording

One sentence, generated from the record rather than written by hand. Fill the braces from the
`opposed` object.

| Grade | Label | Sentence |
|---|---|---|
| `cross-model-fresh-thread` | Attribution | The adversarial pass ran in a fresh thread on a different model ({model}) on {at}, and raised {raised} challenges. |
| `same-model-fresh-thread` | Attribution | The adversarial pass ran in a fresh thread on the same model ({model}) on {at}, and raised {raised} challenges. A fresh thread has no commitment to the draft, so it does not catch a belief this model already holds. |
| `same-thread-self-challenge` | Limitations | The adversarial pass was a self-challenge in the same thread, on {at}, and raised {raised} challenges. It is the weakest of the three grades, because the instance challenging the draft is the instance that wrote it. |
| `not-performed` | Limitations | No adversarial pass was performed on this artefact. |

Grades one and two are process facts a reader can check against the sidecar, so they sit in
Attribution. Grades three and four are limits on the evidence: a reader would decide differently
knowing them, which is the test Limitations obeys. **A sidecar with no `opposed` object is
disclosed as `not-performed`**, because a pass nobody recorded is a pass nobody can show ran.

## The handoff block

Emit this when the host cannot spawn a fresh thread. It is **one fenced code block with no inner
fence**, because an inner triple backtick closes the outer block early and breaks one-click copy.
That is why the return format below is described in plain text instead of being shown as fenced
JSON. Fill the braces before emitting it. It asks for conditions and regions, and it never asks
which claim survived, which side is stronger, or which one to keep.

<!-- handoff-template:start -->
```
You are running an adversarial pass on work you did not write. Do not improve it, do not agree
with it, and do not restate it. Press hard on every claim, then map what you found: the
conditions each claim holds under, and the conditions it fails under. Do not pick a winner. Your
output is a map, not a verdict.

The artefact: {artefact}
The load-bearing claims, one per line, each with its id:
{claims}

Do this, in order:
1. For each claim, argue the strongest case against it. A weak counter-argument is worse than
   none, because it makes the claim look tested when it is not.
2. Hunt the places where one word covers two different mechanisms. That is how a claim passes a
   challenge it should have failed.
3. For each claim, state the observation that would make it false.
4. For each claim, give the conditions it holds under, the conditions it fails under, what is
   true instead inside the failing region, and the part of the space nobody has tested.
5. Wherever two pieces of evidence disagree, do not choose between them. Give the conditions
   each side held under and say where each of them is right.
6. For any source you bring in that is not already in the artefact, say which claim it votes on
   and which way. You are proposing that vote, not settling it, so mark it as yours.
7. Wherever you can state what is true instead, state it as a claim of its own, with its own
   statement, its own evidence and its own conditions. A rival claim is a claim, not a sentence
   inside somebody else's record.

Return one JSON object and nothing else. Do not wrap it in a code fence. Its shape, described in
words so that this block stays copyable:

  "opposed": an object. "grade" is cross-model-fresh-thread if you are a different model from
    {model}, otherwise same-model-fresh-thread. "at" is the UTC time you ran, as
    YYYY-MM-DDTHH:MM:SSZ. "model" is your model name. "raised" is the number of challenges you
    raised, as an integer.
  "boundaries": an array, one entry per claim you touched. Each entry has "id" copied from the
    list above; "challenge", one sentence naming the strongest case against the claim;
    "falsifier", the observation that would make it false; "challenged", exactly one of
    not-attempted, attempted-unresolved, holds, holds-with-boundary or refuted, saying what
    you found about that claim; "holds_when" and "fails_when", each an array of condition
    objects; "replaced_by", what is true instead inside the failing region, which is either a
    sentence or an object of the form "claim" pointing at the id of a competing claim you
    wrote in the array below, or null where you found nowhere it fails; and
    "unknown_region", one sentence naming the part of the space nobody has tested, or null.
  "claims": an array, one entry per COMPETING CLAIM you uncovered, and an empty array when you
    uncovered none. This is the array that matters most. An adversarial pass does not usually
    hand back two sources that disagree; it hands back a claim that is true instead, and a
    claim written into somebody else's replaced_by as a sentence loses its evidence and its
    conditions. Each entry has "id", any short string unique in this array and different from
    every id in the list above; "statement", the claim in one sentence; "kind", one of
    empirical, synthesis, position or story; "status", one of sourced, recalled or inferred;
    "evidence", an array of ids from your evidence array below, or an empty array; "level", a
    whole number from 1 up saying how precisely it is stated; "holds_when" and "fails_when",
    each an array of condition objects; and "unknown_region", one sentence. A competing claim
    that is a position or a story also needs "falsifier", and a story also needs "witness".
  A condition object has "dimension", the thing that varies, such as air quality or firm size;
    "value", the value that dimension takes on this side; and "basis", exactly one of tested,
    replicated, observed, untested or inferred.
  "evidence": an array, one entry per source you bring in that the artefact did not already
    cite, and an empty array when you brought none. Each entry has "id", any short string
    unique in this array; "url"; "quote", the verbatim sentence; "locator", such as p. 12; and
    "supports", an object with "claim", the id of the claim it votes on, "direction", either
    for or against, "by", the exact string model, and "model", your model name. Set by to
    model on every one of them, because you proposed the vote and no person has confirmed it.
    Leave "supports" out where the source votes on no claim in the list, and never invent a
    claim id that is not in the list above.
  "conflicts": an array, one entry per disagreement you found between two pieces of evidence,
    and an empty array when you found none. Each entry has "id", any short string unique in
    this array; "claim", the id of the claim they disagree about; "between", an array of exactly
    two sides; "dimensions", an array naming the dimensions on which the two sides differ; and
    "state", either open or resolved. A side is one of two shapes. An evidence side has
    "evidence", the evidence id or source name, and "outcome", either for or against, and where
    both sides are evidence the two outcomes must differ. A claim side has "claim", the id of a
    competing claim from the array above, and NO outcome, because a rival claim does not vote on
    the claim it stands against. Use the claim side wherever what you found was a rival claim
    rather than a rival source. An open conflict also
    has "unknown_region", one sentence naming what neither side covers. A resolved conflict
    instead has "resolved_into", the id of the claim whose holds_when and fails_when now carry
    the disagreement.
```
<!-- handoff-template:end -->

The block asks for a sidecar fragment rather than prose so that what comes back is integrated
rather than read. Fold `opposed` in as it stands. Fold each entry of `boundaries` into the
matching `claims[]` member: `holds_when`, `fails_when`, `replaced_by`, `unknown_region` and
`challenged` go on the claim, and the challenge and the falsifier belong in the artefact's own
prose, because that is where a reader meets them.

**Fold each entry of `claims` into the sidecar's `claims[]` array as a claim in its own right**,
with its evidence, its conditions and its level intact, renaming its id if that id is already
taken. That is the whole point of asking for it: a competing claim the pass uncovered becomes
part of the corpus of claims in the sidecar, and it is the conditions on the two claims that
say where the boundary between them lies. A `replaced_by` of the form `{"claim": "c9"}` then
points at it, and `boundary.validate_replacements` refuses one naming a claim you did not fold in.

Fold each entry of `evidence` into the sidecar's `evidence[]` array, `supports` and all, so
the vote is recorded as a model's proposal that you confirm or correct rather than as a fact.
Fold `conflicts` in as the top-level `conflicts[]` array, then run
`python3 conflicts.py <file.sourced>`, which refuses a malformed record and lists what is still
open. An open conflict is disclosed, never dropped.

    python3 skill_check.py --self-check     asserts this template carries no inner fence
