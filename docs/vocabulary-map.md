# The vocabulary map: SOURCED, System C and Publish

**This document records ten disagreements. Nine have been decided. One stands open.**

Three systems hold claims. This repository holds them in a `.sourced` sidecar at schema
1.7. Publish holds them in a claim ledger anchored into prose. The third is a claim store,
called **System C** throughout this document, and it holds them as Claim Record v1.

System C's Claim Record is the standard its own family of applications writes to, and it
was agreed as that standard on 26 August 2026. SOURCED 1.7 is this repository's
implementation. **On 29 August 2026, v3, v4, v6 and v8 were decided in favour of System C
and shipped in schema 1.4, v9 and v10 were decided and shipped in schema 1.6, and v5 was
closed in both directions and shipped in schema 1.7.** v2 alone stands open, and this
repository has not moved on it. A decided record is not deleted, because the reason this
repository held the other position is the part that stops it drifting back.

The map lives in code as well as prose. `skills/sourced/vocabulary.py` holds it, and
`python3 skills/sourced/vocabulary.py conflicts` prints the disagreements.

---

## 1. The correction this map forced

The first version of `vocabulary.py` mapped only two systems, this repository and
Publish, and it put all of Publish's tiers 0 to 4 onto a single `strength` axis. That is
the exact mistake that splitting backing from process exists to prevent.

Publish's 0 to 4 is described as one scale and it is not:

| Publish state | What it reports | Backing | Process |
|---|---|---|---|
| `0` unanalysed | neither axis | none | none |
| `1` no or contradicted evidence | process **and** backing | 1, none found | evidence was sought |
| `2` single source | backing | 2 | none |
| `3` multi-source | backing | 3 | none |
| `4` boundary recorded | process | none | a boundary was recorded |
| `position` | kind | none | none |
| `story` | kind | none | none |

Tiers 1 and 4 are facts about what was **done to** the claim. Tiers 2 and 3 are facts
about what **supports** it. A claim that carries a boundary record while resting on one
self-interested source is a 4 and a 2 at the same time, and one number cannot say so.

`MAP` in `vocabulary.py` now reports `backing` and `process` separately for every state.
The 0 to 4 ladder survives as a presentation, computed by `publish_state()` and never
stored. `backing()` returns the backing axis alone, so a tier-4 claim still reports the
backing of 3 that it rests on. `process()` reports what the sidecar records about what
was done to the claim.

Provenance and fidelity stay independent of all seven states. The map says so in every
row, because silence in a table reads as "not applicable", which is a different and wrong
statement.

---

## 2. The three-way field map

`match` is `exact` when the values are identical and no translation is needed, `partial`
when the systems mean the same thing in different vocabularies or cut it differently, and
`none` when one system holds the field and the other does not.

| SOURCED 1.7 | System C Claim Record v1 | Match | What the translation costs |
|---|---|---|---|
| `fidelity` | `fidelity` | **exact** | Nothing. Both are `quotation`, `paraphrase`, `inference`, with the same meaning. |
| `level` | `resolutions[].level` | **exact** | Nothing. Both are ordered whole numbers from 1, both unbounded, and neither names its rungs since v4 was decided. The numbers are relative to one artefact, so nothing compares a level across two. |
| `evidence[].originGroup` | `evidence[].originGroup` | **exact** | Nothing. Sources sharing a group count as one source for independence. |
| `evidence[].sha256` | `evidence[].fixity.sha256` | **exact** | Nothing. Hash of the bytes retrieved. |
| `evidence[].textSha256` | `evidence[].fixity.textSha256` | **exact** | Nothing. Hash of the normalised text. |
| `evidence[].custodian` | `evidence[].fixity.custodian` | **exact** | Nothing. `self`, `third-party`, `self+third-party`, `none`. |
| `evidence[].archiveUrl` | `evidence[].fixity.archiveUrl` | **exact** | Nothing. |
| `evidence[].retrievedAt` | `evidence[].retrievedAt` | **exact** | Nothing. |
| `status` | no direct field; nearest is `evidence[].role` with `fidelity` | partial | `sourced`, `recalled` and `inferred` say whether anything was retrieved for the claim. System C records retrieval per evidence row, so a System C claim with no evidence rows is either recalled or inferred and the record cannot say which. |
| `kind` | `species` **and** `assertionType` | partial | System C splits one axis into two. `kind` is the coarse rung of that one ladder, so on its own it cannot say which finer assertion a claim holds. See disagreement v5. |
| `assertion` | `assertionType` | **exact** | Nothing. The same eight words, same meaning, no renames. `kinds.kind_of()` derives the coarse `kind` from it. |
| `resolves` | `calibration.resolvesBy`, `calibration.resolutionCriterion`, `calibration.resolvedOutcome` | partial | Same meanings under shorter names: `by`, `criterion`, `outcome`. System C also carries `priorProbability` and `currentProbability`, and this repository records neither. |
| `holds_when` | `scope.holdsWhen[]` | partial | Same role. `basis` and `status` now match System C's two fields, since v3 was decided. The dimension and the comparator still differ: v1 and v2. |
| `fails_when` | `scope.failsWhen[]` | partial | Same role, same two remaining condition differences. |
| `unknown_region` | `scope.outsideScope` | partial | System C types it as `unknown`, `assumed-false` or `contested`. SOURCED writes prose, so the type is lost. |
| `supports.direction` | `evidence[].direction` | partial | `for`, `against` and `mixed` in both, since v6 was decided. SOURCED reads a mixed row as a boundary rather than as a side of a conflict, which System C does not say either way. |
| `conflicts[]` | `relations[]` with `type: contradicts` | partial | System C's relation points claim to claim. A SOURCED conflict points at two evidence rows under one claim, and carries `state`, the differing dimensions and an `unknown_region` that a System C relation has nowhere to put. |
| `opposed.grade` | `analysis.challenged` | partial | SOURCED records the grade of pass that ran, once, for the whole artefact. System C records the outcome, per claim. Both are now recorded here: see `challenged`. |
| `challenged` | `analysis.challenged` | **exact** | Nothing. The same five words with the same meanings since v9 was decided: `not-attempted`, `attempted-unresolved`, `holds`, `holds-with-boundary`, `refuted`. Absent reads as `not-attempted` in both. |
| backing reasons | `qualifier.downgrades[]` and `qualifier.upgrades[]` | partial | The same two enums since v10 was decided. This repository derives four of the eleven values from what a sidecar holds. The other seven are `not-recorded` rather than absent. |
| `evidence[].selfInterested` | `evidence[].selfInterested` | **exact** | Nothing. Does the source benefit from this claim being believed. Optional in both. |
| `disclosure` | `provenanceBlock` at the artefact level | partial | The same four labels. System C generates the block from the claims. SOURCED stores it and checks it with `integrate.py`. |
| `owner` | `owner` | partial | A named person who answers for the claim, since v8 was decided. SOURCED calls the second field `checked` rather than `verified`, and requires it. |
| `witness` (story only) | not recorded | **none** | Who lived the experience a story records. It is not an owner and neither derives from the other. |
| `decisions[]` | not recorded | **none** | The design log has no System C equivalent. System C's `provenance[]` is an event chain about one claim, which is a different object. |

### Where the sidecar cannot answer

The map never guesses. Where the sidecar holds nothing that answers a System C field, the
map reports `not-recorded`:

- **`analysis.challenged`, per claim, where the claim does not record one.** Since v9 a
  claim may carry `challenged` and that value is the answer. Where it does not, the older
  reading stands: an `opposed` grade of `not-performed` or absent reads honestly as
  `not-attempted`, and a pass that did run leaves the per-claim outcome `not-recorded`,
  because the artefact-wide record never says which claims were attacked.
- **`qualifier.downgrades[]` beyond the four this repository can derive.**
  `risk-of-bias`, `indirectness` and `publication-bias` are facts about how a study was run
  and about what else was published, and a sidecar records neither. Every `upgrades[]` value
  is the same case: `originGroup` is a label an author types, so reading
  `replicated-independently` off two of them would assert a research fact from a bookkeeping
  field.
- **`decisions[]` going the other way.** System C has nowhere to put it.

A guessed mapping is indistinguishable from a correct one until somebody acts on it.
That is also why `vocabulary.unmapped()` reports an unknown state by name rather than
folding it into whichever row looks closest.

---

## 3. The disagreements

Each of these is a place where two or three systems say different things about the same
idea. `docs/philosophy.md` position 8 holds that a disagreement is a first-class object
and not a decision made quietly in a draft. That applies to the vocabularies themselves,
so they are recorded here and in `vocabulary.conflicts()`. Nine carry a **RESOLVED** line
saying what was decided and when. One carries none, and one of the nine is resolved in only
one direction and says so.

### v1. Condition dimension — **RESOLVED, 29 August 2026. The argument dissolved.**

Neither side won, because the two systems were not disagreeing about openness. They were
sitting at different levels of one ladder.

**A dimension is a claim, so it carries a level.** The thirteen are not a rival vocabulary.
They are the **level-1 rungs**: the coarse dimensions that recur and are stable enough for
machine extraction. The long tail hangs off them as finer dimensions, each naming the
`coarser` rung it refines. `air quality` is a level-1 dimension; `particulate concentration`
is a finer one whose `coarser` is `air quality`. Machine extraction keeps a stable coarse
vocabulary, and an author writes "particulate below six parts per million" without asking
permission.

**Both systems now mint freely and check first.** Three rungs: a normalised exact match
reuses the existing dimension; a near match hands back the existing row **with its
definition** and does not mint unless the caller asks again; anything else mints. A mint is
never refused for already existing, because position 9 holds that a dimension with one claim
against it is legitimate, and the count was never the problem.

**A definition is required at mint, and that is the load-bearing half.** A vocabulary fails
two ways and they are not symmetric. A **split** is two names for one dimension: a missed
comparison, silent, and recoverable by merging them later. An **overload** is one name
covering two meanings, say `method` meaning a research method in one claim and a
manufacturing method in another: a **false** comparison, which reaches contradiction
detection and can refuse a delivery that was fine. A registry of bare strings prevents only
splits. A closed enum is worse than that, because it manufactures overloads: thirteen buckets
for an unbounded space turns `method`, `magnitude` and `other` into catch-alls holding
unrelated things under one name.

**Where each half of the matching lives, and why.** This repository matches on normalised
names and on `difflib` similarity over the definitions. It has no network and no
dependencies, and it stops there deliberately. True semantic matching lives in the
knowledge-base application, which already has embeddings and vector search. That half
measured its threshold rather than choosing one: near-duplicates such as geography against
place scored 0.958 and cohort against population 0.950, while the closest pair of genuinely
different seeds scored 0.893, and `manufacturing method` against `method` scored 0.866. The
threshold sits at 0.92, between them. **The overload this whole change exists to prevent is
the one the measurement caught.**

**That 0.92 is provisional, and it is to be re-measured once fifty real dimensions have been
minted.** Thirteen hand-written seeds are not a sample. They were written to be distinct from
each other, so they cannot show what the long tail does, and a near miss in the long tail is the
failure that matters: two dimensions that are genuinely different and score just above the line
are a false merge nobody sees. **The two measurements that exist already disagree.** The offline
run that chose 0.92 saw a gap of **0.052** between the closest genuinely different pair and the
nearest true duplicate. A live query against the real rows saw **0.164**. A threshold that sits
safely inside the wider gap is not safely inside the narrower one, and neither run says which
gap fifty real dimensions produce. The re-measurement is the check; until it runs, the number is
a working figure and not a finding. This repository's own `NEAR` of 0.85 over names and 0.80
over definitions is `difflib` and not embeddings, and it carries the same note beside it in
`skills/sourced/dimensions.py`.

### v2. Condition comparator

- **SOURCED.** No comparator. A threshold sits inside `value` as text, such as
  "particulate below six parts per million".
- **System C.** A typed `condition.op`: `eq`, `neq`, `in`, `not-in`, `gt`, `lt`, `between`,
  `before`, `after`, `matches`, `exists`.
- **Publish.** No view.
- **Cost of leaving it open.** A machine cannot answer "which claims apply when X" over
  SOURCED conditions. The text has to be parsed on the way into System C, and that parse is
  a guess at the author's meaning.

### v3. Condition basis — **RESOLVED, 29 August 2026**

**Decided in favour of System C, and shipped in SOURCED 1.4.** `basis` splits into two fields:
`basis` is who said it, `status` is how far it has been checked. The five old basis words
still read and translate through one table, `dimensions.LEGACY`, which is a reading of
intent and not a lossless conversion. A formal condition on a claim is now one whose
`status` is `confirmed`, which is the same rule the format always carried, said in the
field that now holds it.

- **SOURCED, before the decision.** One field, `basis`, one of `tested`, `replicated`,
  `observed`, `untested`, `inferred`. It mixed how strong a condition was with who said it.
- **System C.** Two fields. `condition.basis` is `stated-in-source`,
  `inferred-from-conflict`, `human` or `rule`, which is who said it.
  `condition.status` is `asserted`, `proposed`, `monitoring`, `confirmed` or `refuted`,
  which is how far it has been checked.
- **Publish.** No view.
- **Cost of leaving it open.** `tested` and `observed` both translate to a System C basis of
  `stated-in-source` with no status. The strength of the condition is dropped in
  translation and cannot be recovered from the record.

### v4. Level naming — **RESOLVED, 29 August 2026**

**Decided in favour of System C, and shipped in SOURCED 1.4.** The audience names came out of
the format and out of every rule, message and validator. A level is an ordinal and prints
as "level 3". They may survive as a teaching gloss in prose, said as a gloss. A point was
added while deciding it: the numbers are **relative, not absolute**, so nothing compares a
level across two artefacts, and re-levelling a statement later is expected rather than a
defect. See `docs/philosophy.md` position 10.

- **SOURCED, before the decision.** Levels 1 to 3 were named conversational, informed and
  practitioner. Above 3 a level had no name.
- **System C.** Ordered integers with no names. The reason is that audience names invite
  argument about who is a practitioner.
- **Publish.** No view.
- **Both agree the ladder is unbounded.**
- **Cost of leaving it open.** The names are load-bearing in this repository's prose, and
  its checks read "level 3 or above". Adopting System C's reading means the names come
  out of the docs. Until then a reader of both systems sees one ladder described two ways.

### v5. Kind versus species — **RESOLVED both ways, 29 August 2026**

**Decided: `synthesis` survives, and it was added to the knowledge-base application's
`assertionType` on the same day.** A conclusion drawn across claims no longer flattens into
`empirical` on the way in. It is graded on the evidence underneath it like any empirical
claim, and it always carries the `indirectness` downgrade, because a conclusion drawn across
claims is one step removed from that evidence by construction. It is not a weaker claim. It
is a claim whose backing is mediated.

**Recorded with it, because it was asked and the answer is not obvious.** Kind and provenance
are independent questions, and `synthesis` is not another word for `inferred`. Provenance says
where a claim came from; kind says what species of sentence it is. The proof is that all four
cells are populated: a synthesis can be `inferred`, when you drew it across sources, or
`sourced`, when you retrieved somebody else's published meta-analysis and quoted it. And an
`inferred` claim can be a `position`, which touches no evidence at all. Among inferred claims
the useful cut is that a synthesis runs **through** the evidence, a position does not touch
it, and a story comes from lived experience.

**Decided the other direction too, and shipped in SOURCED 1.7.** The reason a mapping lost
something in both directions is that `kind` is a hybrid of two axes. That application carries
`species` (claim, position, story) and `assertionType` (eight words). This repository's `kind`
takes `position` and `story` from the first, and `empirical` and `synthesis` from the second.

**The fix is a ladder, not a second field.** `kind` is unchanged and stays the coarse rung,
because it answers the question a person actually asks: did somebody measure this, did I
conclude it, do I hold it, or did I live it. A claim gains an optional `assertion`, the finer
rung, taking that application's eight `assertionType` values exactly, with nothing added and
nothing renamed. It is the same move `sophistication.py` already makes, where a statement
carries a `level` with a `coarser` and a `finer` sibling, and the same move v1 made when the
closed dimension enum opened into a registry of coarse and fine rungs.

| `assertion` | sits under `kind` |
|---|---|
| `empirical`, `statistical`, `definitional`, `predictive` | `empirical` |
| `synthesis` | `synthesis` |
| `normative`, `interpretive` | `position` |
| `narrative` | `story` |

The mapping is fixed and total. `kinds.kind_of()` derives the coarse rung from the finer one
and is the one place the table is read, so nothing writes it twice, and the same function does
the compatibility check. A claim whose two rungs disagree is refused, and the message names
both. A claim carrying a `kind` and no `assertion` validates, so a 1.6 sidecar passes untouched.

**A `predictive` assertion requires a resolution.** The extraction contract in that application
refuses an unfalsifiable forecast dressed as evidence, and this repository already refuses an
evidence-exempt kind with no falsifier, so the same discipline applies here. A predictive claim
must carry `resolves` of `{by, criterion}`, both non-empty, or it is refused. Those are
`calibration.resolvesBy` and `calibration.resolutionCriterion` under shorter names, and the
optional `resolves.outcome` is `calibration.resolvedOutcome` with the same four words.
`integrate.py` raises a soft flag, and never a failure, for a predictive claim whose date has
passed and which records no outcome.

**The round trip is now lossless in both directions.** Every one of the eight assertion values
derives its kind and reads back the same value, and a claim carrying only a `kind` still
validates. The test that holds it is `python3 skills/sourced/kinds.py --self-check`, case
"all eight assertions round-trip losslessly under a kind", walked again in
`vocabulary.py --self-check`, case "the eight assertions round-trip losslessly, both ways (v5)".

### v6. Evidence direction — **RESOLVED, 29 August 2026**

**Decided in favour of System C, and shipped in SOURCED 1.4.** `supports.direction` accepts
`mixed`. A mixed row raises no conflict, because a source that cuts both ways is already
saying where the boundary is and does not need another source to disagree with. It raises
a boundary prompt instead, a soft flag asking whether the boundary has been recorded, and
that flag is silent once the claim carries a boundary record. A conflict record may not
name a mixed row as a side.

- **SOURCED, before the decision.** `supports.direction` was `for` or `against`. Two values,
  nothing else.
- **System C.** `evidence[].direction` is `supports`, `undermines` or `mixed`.
- **Publish.** No view.
- **Cost of leaving it open.** A source that cuts both ways cannot be recorded honestly in
  a sidecar. It must be forced to one side or split into two rows, and either move changes
  what `conflicts.py` sees when it looks for opposed rows.

### v7. The word survived — **RESOLVED, 29 August 2026**

**Decided: harmonise all three.** One shared vocabulary, `holds`,
`holds-with-boundary` and `refuted`. The knowledge-base application renames
`analysis.challenged`; the publishing application renames its verdict kinds and keeps
`weakest`, `refine` and `unverified`, which rank a result rather than declare a winner.
Both read an old value and write the new one, so nothing already written becomes
unreadable.

**The shape is unchanged and that was deliberate.** Replacing the verdict model with
the conflict-and-boundary model was offered as a separate project and was not taken, so
a verdict per claim remains. Both changes sit on branches and neither is merged.


- **SOURCED.** Removed deliberately on 28 August 2026 (`docs/philosophy.md` position 8).
  The output of an adversarial pass is a map, not a verdict. Tier 4 reads "boundary
  recorded".
- **System C.** `analysis.challenged` still stores `survived` and `survived-caveat`, beside
  `not-attempted`, `attempted-unresolved` and `refuted`.
- **Publish.** `verdicts[].verdict` stores `survives`, `survives-caveat`, `weakest`,
  `refine`, `killed` and `unverified`.
- **Cost of leaving it open.** A contest word with one winner is reintroduced at the
  storage layer. A pass that hunts a verdict stops when it has one, which is the exact
  failure the position was written after: eight findings framed as defeats when at least
  three were boundaries.

### v8. Owner — **RESOLVED, 29 August 2026**

**Decided in favour of System C, and shipped in SOURCED 1.4.** A claim may carry an optional
`owner` of `{name, checked, since}`. `name` and `checked` are both required when the object
is present, and `checked` must say something, because a signature buys accountability and
never accuracy. An `owner` and a `witness` are different things and neither derives from
the other.

- **SOURCED, before the decision.** No owner. `witness` existed on a story only, naming who
  lived it.
- **System C.** `owner` with a name, what that person personally checked, and since when.
  It is the U of SOURCED, made into a field.
- **Publish.** No view.
- **Cost of leaving it open.** Nobody answers for a claim in a sidecar. The framework's own
  U says a signature buys accountability rather than accuracy, and this repository has no
  field for the accountable person, so it asserts a principle it does not implement.

### v9. The adversarial record — **RESOLVED, 29 August 2026**

**Decided in favour of System C, and taken further, shipped in SOURCED 1.6.** A claim carries an
optional `challenged`, one of the five shared words: `not-attempted`, `attempted-unresolved`,
`holds`, `holds-with-boundary`, `refuted`. Absent reads as `not-attempted`, the same way an
absent `opposed` does. **The artefact-level `opposed` object is unchanged and stays.** The two
answer different questions and neither derives from the other: `opposed` says which grade of
pass ran over the artefact, and `challenged` says what that pass found about one claim.

**The larger half was not the question that was asked.** An adversarial pass does not hand you
two sources that disagree. It hands you a **rival claim**, and until 1.6 there was nowhere to
put it, so the rival was flattened into a sentence in `replaced_by` and lost its evidence, its
conditions and its level on the way down. So a competing claim the pass uncovers now becomes
part of the corpus of claims in the sidecar, with its own evidence, conditions and level:

- **A conflict may be between two claims**, not only between two evidence rows. A side is
  `{"evidence": "e1", "outcome": "for"}` exactly as before, or `{"claim": "c9"}`. A claim side
  carries no `outcome`, because a rival claim does not vote on the claim it stands against.
- **`replaced_by` may name a claim**, as `{"claim": "c9"}`, and free text still reads. A named
  claim that is not in the sidecar is refused.
- **The differing dimensions of a claim side come from its `holds_when` and `fails_when`**, so
  the two claims' own conditions are what say where each of them is right. That is the point:
  adversarial is the method, integration is the goal.
- **`detect()` is unchanged.** It reads evidence rows only. Nothing infers a rival claim,
  because a rival claim is a thing somebody thought of.

- **SOURCED, before the decision.** `opposed` was one object for the whole artefact: which
  grade of pass ran, when, and how many findings it raised. Nothing per claim.
- **System C.** Per claim: `analysis.challenged`, `verdicts[]` and a `provenance[]` event
  chain carrying a `challenged` event.
- **Publish.** Per claim verdicts.
- **Cost of leaving it open.** A sidecar cannot say which claims were attacked, only that
  a pass ran over the artefact. Translation to System C must leave `analysis.challenged` as
  `not-recorded`, so the O of SOURCED is artefact-wide here and claim-wide there.

### v10. The claim strength number — **RESOLVED, 29 August 2026**

**Decided in favour of System C, and shipped in SOURCED 1.6.** `vocabulary.backing()`
returns the number **and** its named reasons, as `Backing(grade, downgrades, upgrades)`.
Both enums are adopted verbatim from `qualifier.downgrades` and `qualifier.upgrades`, so
one claim is not described two ways. A derived number that gives no account of itself is
the thing this framework objects to everywhere else.

**Four reasons are derived, from what a sidecar actually holds:** `single-source` from one
distinct `originGroup`, `self-interested-source` from an evidence row carrying
`"selfInterested": true`, `inconsistency` from an opposed pair or a conflict record naming the
claim, and `imprecision` from evidence carrying no quote and no locator.

**`risk-of-bias`, `indirectness` and `publication-bias` stay in the vocabulary and stay unset.**
They are facts about how a study was run and about what else was published, and a sidecar records
neither. A claim store that holds study metadata can derive them; this format cannot, and a
guessed reason reads exactly like a derived one. **No upgrade is derived at all**, because
`originGroup` is a label an author types.

**Strength is still derived and never stored.** The reasons are computed beside the number on
every read, neither is a field on a claim, and a stored `strength` or `tier` is still refused.

- **SOURCED, before the decision.** A derived 0 to 4, computed from the evidence rows, refused
  if stored, and giving no account of itself.
- **System C.** `qualifier.grade` is `high`, `moderate`, `low`, `very-low` or
  `not-applicable`, with named `downgrades[]` such as `self-interested-source` and
  `single-source`, computed at write time. The 0 to 4 tier is kept as an output for the
  display.
- **Publish.** Stores the 0 to 4 tier.
- **Cost of leaving it open.** SOURCED cannot say **why** a claim is weak. System C names the
  reason, the sidecar drops it on the way in, and the reason is the part a reader needs.

---

## 4. What this map does not do

It does not migrate anything. It does not add a field to the sidecar. It does not pick a
winner in code, and `vocabulary.conflicts()` deliberately returns records rather than
resolutions.

It put eight decisions in front of a human: v1, v3, v4, v6, v7, v8, v9 and v10, eight
places where harmonising means changing something one of the three systems holds on
purpose. **All eight were decided on 29 August 2026 and are marked RESOLVED above.** Four
shipped here in schema 1.4, two in schema 1.6, and v5 was closed in both directions and
shipped in schema 1.7. Two, v1 and v7, were decided in favour of work in the other two
applications and sit on branches there, unmerged. **v2 alone stands open.**

## References

- The Claim Record v1, in the knowledge-base application that owns it:
  `docs/specs/claim-standard/README.md` and `claim.schema.json`.
- `docs/specs/claim-standard/tier_rule.py`, the computed tier, also in that application.
- `docs/framework.md` position 7, claim strength as a separate axis.
- `docs/philosophy.md` positions 8, 9 and 10.
- `docs/sidecar.md`, the `.sourced` schema.
- `skills/sourced/vocabulary.py`, the map in code.
