# The sidecar

Read this when writing, extending or validating a `.sourced` file.

`<artefact>.sourced` is JSON beside the artefact, the way a claim ledger sits beside prose.
Four required parts: a manifest, the claims with a locator into the artefact, the evidence
they rest on, and the disclosure block. `decisions[]`, `opposed`, `dimensions[]` and `conflicts[]` are
optional extra parts. **The first key is always `$schema`, pointing at
`https://peakstate.global/sourced/v1.schema.json`** — the namespace that makes a sidecar
self-explaining to anyone who opens it, and a real JSON Schema (draft 2020-12) that
`jsonschema` can validate against. The schema file is served from the Peak State tenant's
`public/sourced/v1.schema.json`; edit it there, bump `sourced` when a field changes meaning.

```json
{
  "$schema": "https://peakstate.global/sourced/v1.schema.json",
  "sourced": "1.10",
  "artefact": { "path": "deck.pptx", "sha256": "…", "producedAt": "2026-08-26" },
  "claims": [
    { "id": "c1", "statement": "…", "status": "sourced",
      "role": "proposition", "answers": "c1", "reads_as": "…", "basis": "…",
      "impact": "moderate", "domain": "medical", "would_settle": "…", "label": "P2.3",
      "underwriting": [ { "act": "quote-checked", "by": "sourced.py", "at": "…" } ],
      "locator": { "slide": 3 }, "evidence": ["e1"],
      "level": 1, "finer": "c3", "challenged": "holds-with-boundary",
      "kind": "empirical", "assertion": "statistical",
      "replaced_by": { "claim": "c9" },
      "owner": { "name": "…", "checked": "…", "since": "2026-08-29" } }
  ],
  "evidence": [
    { "id": "e1", "url": "…", "quote": "…", "quoteGloss": "…", "locator": "p. 178",
      "retrievedAt": "2026-08-26", "sha256": "…", "textSha256": "…",
      "originGroup": "…", "custodian": "self+third-party", "archiveUrl": "…",
      "selfInterested": false }
  ],
  "dimensions": [
    { "name": "air quality", "definition": "One sentence saying what it means.",
      "level": 1, "firstSeen": "2026-08-29", "uses": 3 },
    { "name": "particulate", "definition": "One sentence saying what this finer one means.",
      "level": 3, "coarser": "air quality", "firstSeen": "2026-08-29", "uses": 1,
      "mintedBy": "model", "mintedModel": "…" }
  ],
  "disclosure": { "attribution": "…", "accountable": "…",
                  "limitations": "…", "references": "…" },
  "opposed": { "grade": "same-model-fresh-thread", "at": "2026-08-28T03:00:00Z",
               "raised": 3, "model": "claude-opus-5", "modelVersion": "1m",
               "thread": "…", "note": "…" },
  "decisions": [
    { "at": "2026-08-28T01:00:00Z", "context": ["e1"],
      "options": ["stdlib", "jsonschema"], "chose": "stdlib",
      "rejected": [ { "option": "jsonschema", "clause": "a pip install nobody runs" } ],
      "model": "claude-opus-5", "modelVersion": "1m",
      "narrative": { "text": "…", "generatedAt": "2026-08-28T01:00:00Z" } }
  ]
}
```

The `evidence[]` shape is deliberately the same object the claim store's Claim Record
stores, so a
sidecar can be ingested and enriched rather than re-captured. `claims[]` is deliberately
thin, with no tier and no assertion type, because those are the fields the platform
implementations disagree about. **A `.sourced` file is a lowest common denominator on
purpose.** If it grows relations and computed tiers it has become the Claim Record with
extra steps, and the right move then is to adopt that instead.

**`dimensions[]` arrives in sourced 1.5 and is optional.** It carries the registry rows
for the dimensions this file's conditions name, so a sidecar that travels on its own can be
read. A row is `{name, definition, level, coarser?, firstSeen, uses, mintedBy?,
mintedModel?, forcedPast?}`. `definition` is one sentence and is required at mint;
`mintedBy` is `author` or `model`, and absent reads as author, the same convention
`supports.by` uses. `finer` is never stored, because it is the exact inverse of `coarser`
and a stored pair of inverses is a pair that can disagree: `dimensions.finer_of(name)`
computes it.

**Why a definition and not just a name.** A vocabulary of bare names fails two ways. A
**split** is two names for one dimension: you miss a comparison, silently, and merging the
rows later recovers it. An **overload** is one name over two meanings, `method` for a
research method here and a manufacturing method there: you make a **false** comparison, two
unrelated claims read as a conflict, and `integrate.py` refuses a delivery that should have
shipped. A wrong refusal is how a gate gets bypassed. Bare names prevent splits only, so
the definition is what prevents the expensive failure, and it is what makes a near match
safe to offer.

**A dimension is a claim, so it carries a level.** `air quality` is level 1; `particulate`
is finer, with `coarser: "air quality"`. Same mechanism, same validator as claims and
conditions, no second implementation. The knowledge-base application's fixed list of
thirteen is not a rival vocabulary; it is the set of level-1 rungs, and free text is the
long tail hanging off them.

**The block is generated, never authored**, by `dimensions.for_sidecar(data)` or
`python3 dimensions.py --sidecar <file>`. It may be partial, because a partial block is
honest. What it must do is resolve on its own: a row's `coarser` must name another row in
the same block. Rows already on disk with no `definition` load as undefined rather than
being refused, so no existing registry breaks.

**`level`, `coarser` and `finer` arrive in sourced 1.3 and are optional.** A statement carries a
`level`, any whole number from 1 up, and may name a `coarser` sibling at a lower level and a
`finer` sibling at a higher one, so the plain version and the precise version of one claim are
recognisably one claim. **A condition is itself a claim**, so a condition uses the same fields,
the same optional `id`, and the same validator; there is no second implementation. **The ladder
has no top:** level 4 and above are valid. Level 4 is not "conditional", because a claim at any
level can carry conditions and each condition carries its own level.

**A level has no name.** The audience names came out in 1.4, on 29 August 2026, because an
audience name invites an argument about who counts as a practitioner.
A level is an ordinal and prints as "level 3". **The numbers are relative, not absolute:** level
3 names no exact quantity of precision, so nothing compares a level across two artefacts, and a
statement may need re-levelling later when something turns up between two rungs already written.
`sophistication.validate_statements()` refuses a level that is not a whole number from 1 up, a
sibling id that does not exist in the same scope, a sibling at the wrong depth, and a cycle in
either direction. A 1.2 sidecar with no levels anywhere validates unchanged.

**Sophistication is not strength.** A level-1 statement is a coarser model, not weaker evidence.
`sophistication.evidence_precision()` reads how precisely a claim is cited: 1 when no evidence row
resolves, 2 when at least one resolves, 3 when at least one carries both a quote and a locator.
**It is a floor and not a ceiling.** On an unbounded ladder nothing can say the evidence supports
level 47, so the number stops at 3 and answers one question: can a precise claim be followed back
to a source. `sophistication.over_claiming()` reports every claim stated at level 3 or above whose
precision is below 3, and a claim at level 1 or 2 can never over-claim. Evidence precision is
**derived, never stored**. The report is a report here, and `integrate.py` turns the same mismatch
into a refusal at delivery: cite the claim precisely, or state the claim at level 2. See
`reference/boundary-record.md` for the conditions themselves.

**`kind`, `falsifier` and `witness` arrive in sourced 1.3 and are optional.** A claim carries a
`kind` of `empirical` (a claim backed by evidence somebody gathered), `synthesis` (a conclusion
drawn across several claims), `position` (a stance, evidence-exempt by design) or `story`
(author-verified lived experience). The values are Publish's own, so one claim is not described
two ways. **Evidence-exempt is not check-exempt:** a `position` requires a non-empty `falsifier`
saying what would have to be true for it to be wrong, and a `story` requires a `falsifier` and a
`witness` naming who lived it. `kinds.validate_kinds()` refuses a kind outside the four, an
evidence-exempt claim with no falsifier, and a story with no witness, naming the claim in the
message. A 1.2 sidecar with no kinds validates unchanged.

**`assertion` arrives in sourced 1.7 and is optional.** `kind` is a hybrid of two axes, so a
mapping to the knowledge-base application used to lose something in both directions. `kind` is now
read as the COARSE rung of one ladder, and `assertion` is the finer rung beside it, taking that
application's eight `assertionType` words exactly: `empirical`, `synthesis`, `statistical`,
`definitional`, `normative`, `interpretive`, `predictive` and `narrative`. It is the same move
`level`, `coarser` and `finer` already make for a statement, so it is a ladder and not a second
rival field.

| `assertion` | sits under `kind` |
|---|---|
| `empirical`, `statistical`, `definitional`, `predictive` | `empirical` |
| `synthesis` | `synthesis` |
| `normative`, `interpretive` | `position` |
| `narrative` | `story` |

The mapping is fixed and total, and `kinds.kind_of()` is the one place it is read. A claim whose
two rungs disagree is refused, and the message names both. A claim carrying a `kind` and no
`assertion` validates, so a 1.6 sidecar passes untouched. The round trip is lossless in both
directions, and `kinds.py --self-check` walks all eight values to hold it.

**`resolves` arrives in sourced 1.7 and is required when `assertion` is `predictive`.** Write
`{"by": "2027-06-30", "criterion": "The published index for June 2027 reads below 40."}`, both
non-empty, or the claim is refused: an unfalsifiable forecast must never be tiered as evidence.
`resolves.outcome` is optional and is one of `true`, `false`, `ambiguous` or `unresolved`. The
three fields are the other application's `calibration.resolvesBy`, `calibration.resolutionCriterion`
and `calibration.resolvedOutcome` under shorter names. `integrate.py` raises a soft flag, never a
failure, when `resolves.by` has passed and no `outcome` is recorded.

**Provenance, fidelity and kind are three separate questions**, and none is derived from another.
Provenance is whether `evidence[]` is empty, fidelity is how far the wording sits from the source,
and kind is what species of sentence it is. A synthesis may be heavily evidenced; a position may
quote somebody and still be a stance. A `position` or `story` claim is disclosed as INFERRED in
the sidecar, which is where our own thinking belongs, so it does not appear in Limitations.

**`supports` on an evidence row says which claim the row votes on and which way**, as
`{claim, direction}` with `direction` of `for`, `against` or `mixed`, and it may also say who put
it there. **`mixed` arrives in 1.4** and means the source supports the claim in one region and
undermines it in another. A `mixed` row never raises a conflict, because a source that cuts both
ways is already saying where the boundary is; `integrate.py` raises a boundary prompt for it
instead, and that prompt is silent once the claim carries a boundary record.
`conflicts.validate_conflicts()` refuses a conflict record naming a mixed row as a side, because
a mixed source is a boundary and not a side. `by` is `author` or `model`, and
`model` names the model that proposed it. Both are optional. **An absent `by` reads as
`author`**, because every `supports` written before the field existed was typed by a person and
a silent default of `model` would retro-label their work. A `model` beside `by` of `author` is
refused. `conflicts.validate_conflicts()` refuses a `by` outside the two words, naming the row.
The model proposes a support while it reads; the author confirms or corrects it.
`integrate.py` flags a stored conflict whose two sides both rest on a model-proposed support,
and it never refuses on that alone. One author-set side clears the flag, and a model-proposed
support on a row in no conflict raises nothing. See `docs/sidecar.md` for the conflict record
itself.

**`owner` arrives in sourced 1.4 and is optional.** A claim may name the person who answers for
it, as `{name, checked, since}`. `name` and `checked` are both required when the object is
present, and `checked` must say what that person personally verified: a signature buys
accountability and never accuracy, so an owner with nothing verified is the exact claim the U of
SOURCED refuses. `since` is optional. `kinds.validate_owners()` refuses a malformed owner, naming
the claim. **An `owner` and a `witness` are different things and neither derives from the other:**
a witness lived the experience a story records, and an owner answers for the claim.

**`opposed` arrives in sourced 1.2 and is optional.** It records which grade of adversarial pass
actually ran: `cross-model-fresh-thread`, `same-model-fresh-thread`, `same-thread-self-challenge`
or `not-performed`. `grade`, `at` and `raised` are required inside it; `model`, `modelVersion`,
`thread` and `note` are not, because a host does not always say which model or thread ran.
`decisions.py validate()` refuses an unknown grade and refuses a `not-performed` record that
claims it raised something, because an unrecognised grade string is how a self-challenge gets
written up as an independent review. A sidecar with no `opposed` is disclosed as `not-performed`.
See `reference/adversarial-pass.md` for what each grade catches and the exact disclosure wording.

**`challenged` arrives in sourced 1.6 and is optional.** A claim may record what the
adversarial pass found about it: `not-attempted`, `attempted-unresolved`, `holds`,
`holds-with-boundary` or `refuted`. The five words are shared across the three systems since
v9 was decided on 29 August 2026, and they match `analysis.challenged` in the claim standard
exactly. **Absent reads as `not-attempted`**, the same way an absent `opposed` does.
`vocabulary.challenged_of(claim)` reads it and `vocabulary.validate_challenged(data)` refuses
a sixth word, because a sixth word is how a pass that reached no conclusion gets written up as
one that held. **`opposed` is unchanged and stays:** it records which grade of pass ran over
the artefact, `challenged` records what that pass found about one claim, and neither derives
from the other.

**A resolved conflict names its move, in sourced 1.7.** `move` is required when `state` is
`resolved`, and must be one of `conditional`, `reframe`, `redirect`, `compromise` — the
integration moves in position 8 of `docs/philosophy.md`. Two of them cannot be checked by shape,
so each carries a required `move_note`: `reframe` names the assumption both sides shared, because
"a higher-order synthesis dissolves the tension" is a sentence anyone can write about anything;
`compromise` says why conditional, reframe and redirect each failed, because it is the last resort
and not the default.

`hold` is deliberately not a value. Holding IS a conflict left `open` with its `unknown_region`
named, so an open conflict carries no `move` at all. Allowing both forms would let an unresolved
tension read as a resolved one, which is the failure the move exists to prevent.
`conflicts.validate_conflicts()` refuses a resolution with no move, a move outside the four,
`hold` in either position, a missing or blank `move_note` on the two that need one, and a move on
an open conflict.

**A conflict side may name a claim, in sourced 1.6.** `between` still holds exactly two sides,
and a side is `{"evidence": "e1", "outcome": "for"}` exactly as before, or `{"claim": "c9"}`
naming a competing claim. That is the shape an adversarial pass produces: it does not hand you
two sources, it hands you a rival claim, which now lands in `claims[]` with its own evidence,
conditions and level. A claim side carries **no** `outcome`, because a rival claim does not
vote; it must name a claim that exists; and it may not name the conflict's own claim.
`conflicts.side_of(side)` parses either form, `conflicts.side_record(data, side)` resolves it,
and the differing dimensions of a claim side are read off its `holds_when` and `fails_when`
rather than an evidence row's `conditions`. `conflicts.detect()` is unchanged and still reads
evidence rows only: nothing infers a rival claim.

**`replaced_by` may name a claim, in sourced 1.6.** Write `{"claim": "c9"}` and the thing that
is true instead is a claim in the corpus with its own evidence and conditions, not a sentence
stranded in a string. Free text still reads unchanged. `boundary.replaced_claim(record)` returns
the id or None, and `boundary.validate_replacements(data)` refuses a named claim that is not in
the sidecar, and a claim naming itself.

**`backing()` returns the number and its reasons, in sourced 1.6.** `vocabulary.backing(claim,
evidence_by_id, data)` returns `Backing(grade, downgrades, upgrades)`, with the words taken
verbatim from `qualifier.downgrades` and `qualifier.upgrades` in the claim standard. Four are
derived from what the sidecar holds: `single-source` from one distinct `originGroup`,
`self-interested-source` from a row carrying `"selfInterested": true`, `inconsistency` from an
opposed pair or a conflict record naming the claim, and `imprecision` from evidence carrying no
quote and no locator. **`risk-of-bias`, `indirectness` and `publication-bias` stay unset**,
because a sidecar records nothing that answers them and a guessed reason reads exactly like a
derived one; a claim store with study metadata can derive them. **No upgrade is derived at
all**, because `originGroup` is a label an author types. `selfInterested` is a new optional
boolean on an evidence row, absent meaning nobody has said either way. **Strength is still
derived and never stored**, and a stored `strength` or `tier` on a claim is still refused.

**`decisions[]` arrives in sourced 1.1 and is optional.** A sidecar without it validates, so every
file already on disk stays valid and an implementation that ignores the array is not broken. It is
folded in from `<artefact>.decisions.jsonl` by `decisions.py`; see `reference/decision-ledger.md`
for the record shape and why the chosen option carries no clause.


## 1.8 — propositions, custody, and what was actually done

**`role` and `answers` carry the propositions.** A proposition is a claim: same statement, same
verdict, same conditions, same falsifier. It differs only in coming from the question rather than
from the evidence, and in having other claims hang off it. So it lives in `claims[]` with
`role: "proposition"`, and a claim answering it carries `answers: "<its id>"`. There is no separate
array, because two homes for one truth is how they drift apart — which is exactly what happened
when the propositions lived only in the artefact's prose and the verdict table could not restate
them.

**`reads_as` is the Conditions column in a sentence.** The machine conditions stay in `holds_when`
and `fails_when` because `dimensions.py` needs them; `reads_as` is what a person reads.

**`basis` is the evidence in a few words**, for the table's fourth column.

**`quoteGloss` on an evidence row** says what a non-prose quote means. `claims.py` asks for one when
a quote is under 60 per cent letters, after a run recorded `"8 8 0"` — a search response with its
tags stripped — against a claim about how many trials exist.

**`archiveUrl` is expected on every cited row from 1.8**, and `integrate.py` refuses a 1.8 sidecar
where nothing was archived. Rounds 01 to 03 wrote zero across 48 cited rows, so the whole evidence
base was self-attested: the hash proved a quote matched *our own file* and nothing more. An
individual source the archive refused is a disclosed limit; a paper with none is nobody trying.

**Several rows may share a `url`.** One row per quote, sharing the capture hash and the
`originGroup`, because they are the same file read twice. Nothing ever forbade this and no run had
done it.

**`underwriting` records acts, not identities.** Each entry is a thing that was done — the quote
checked, the arithmetic recomputed, a challenge survived — with the actor and the time on it. The
assurance level is derived from the acts by `underwrite.py` and is never stored, because a stored
level is an assertion and a derived one can be argued with. `impact` and `domain` feed the risk
rating; both are optional and both default conservatively.


## 1.9 — untested is not contested

**`Contested` now requires an open `conflicts` record naming two sides.** It previously also fired
on `challenged: "attempted-unresolved"`, which means the adversarial pass could not settle the
question — usually because nothing settles it. Round 04 shipped 18 claims carrying that flag, 15 of
them with no conflict record at all, and every one rendered `Contested` in the verdict table. Both
graders passed all fifteen; a reader caught it and asked how a verdict could be contested when
nothing contests it. `attempted-unresolved` with no open conflict now reads `Unevaluated`.

**A `fails_when` entry with `basis` of `untested`, `absent` or `no-evidence` does not make a claim
fail.** A region nobody has measured is untested, not failed, and "fails as a claim about
active-control trials, because none exist" is an absence of trials.

**`would_settle` says what would answer an untested claim** — the study, dataset or measurement.
`integrate.py` asks for it on any claim carrying an `unknown_region` or the unresolved flag. It is a
flag and not a refusal, because sometimes nobody knows what would settle a question, but that should
be said rather than left blank.

**A proposition may not contain a verdict word**, and `integrate.py` refuses one that does. A
proposition states what might be true; the verdict says how it fared, and a proposition already
carrying a verdict reads as a double negative underneath one.

**A genuinely contested proposition must be split**, one sub-proposition per side, each with its own
boundary. That is the integration step, and it is now a refusal rather than a prompt.


## 1.10 — the label, the gloss, and what counts as a second source

**`label` is the P-number the paper shows for a claim.** A verdict table renders `P2.3` and, until
now, nothing in `claims[]` carried that string, so a sub-row id resolved to prose and no check could
tell whether the body's `P2.3` was the table's. Two round-05 graders found this independently on two
papers each. Set it with `claims.py set --id c9 --label P2.3`.

**`quoteGloss` is now written.** `claims.py` had demanded a gloss for a non-prose quote since 1.8 and
never stored it, so a round-05 run had six rows to hand-patch. A gate that extracts work and discards
it is worse than no gate.

**`Contested` requires both sides of the conflict to rest on a retrieved source.** A conflict between
an evidence row and a claim the adversarial pass wrote is the pass arguing with itself: worth
recording, and not two sources disagreeing, which is what the word tells a reader. Round 05 shipped
one, where the row's own evidence cell said no retrieved source decomposed the quantity at all.

**The archive URL is checked against the URL it claims to snapshot.** The save endpoint follows
redirects, so a page that redirects returns a snapshot of the destination; a round-05 run was handed
a snapshot of a different page than the one it cited. A wrong archive URL is worse than none, because
it reads as independent custody of a document nobody archived.

**Write the fine word in `assertion`, not the coarse one in `kind`.** `kind` takes `empirical`,
`synthesis`, `position` or `story`. `assertion` takes `definitional`, `normative`, `predictive` and
the rest, and `kinds.kind_of()` derives the coarse rung from it. `research-mode` was asking for the
fine words under the coarse field, and a run spent a gate failure discovering it.
