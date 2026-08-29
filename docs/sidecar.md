# The sidecar

`<artefact>.sourced`, JSON beside the artefact, the way a claim ledger sits beside prose.

**What changed in 1.7.** Two additions, both optional, so a 1.6, a 1.5, a 1.4, a 1.3 or a
1.2 sidecar validates unchanged. A claim gains an optional `assertion`, the finer rung
under `kind`, in the other application's own eight words. A claim whose `assertion` is
`predictive` must carry `resolves`, a date and the observation that would settle it. This
closes disagreement v5 in `docs/vocabulary-map.md` in both directions.

**What changed in 1.6.** Three additions, all optional, so a 1.5, a 1.4, a 1.3 or a 1.2
sidecar validates unchanged. A claim gains an optional `challenged`, which is what the
adversarial pass found about that one claim. A side of a conflict may name a **claim** as
well as an evidence row, because a pass hands you a rival claim rather than two sources,
and `replaced_by` may name that claim instead of describing it in prose. `backing()` now
returns the number **and** its named reasons, and an evidence row may carry
`selfInterested`. Strength is still derived and never stored. These close v9 and v10 in
`docs/vocabulary-map.md`.

**What changed in 1.5.** One addition, and it is optional, so a 1.4, a 1.3 or a 1.2
sidecar validates unchanged. A sidecar may carry a top-level `dimensions[]`: the registry
rows for the dimensions its conditions actually name, each with the one sentence that says
what the dimension means. A sidecar travels on its own, and a dimension defined only in a
project registry means nothing to whoever receives the file.

**What changed in 1.4.** Four decisions from `docs/vocabulary-map.md`, all additive, so a
1.3 or a 1.2 sidecar validates unchanged. A condition's `basis` splits into `basis` (who
said it) and `status` (how far it has been checked), and the five old basis words still
read and translate. A level loses its audience names and is an ordinal only.
`supports.direction` gains `mixed`. A claim gains an optional `owner`.

```json
{
  "sourced": "1.7",
  "artefact": { "path": "deck.html", "sha256": "…", "producedAt": "2026-08-26" },
  "claims": [
    { "id": "c1", "statement": "…", "status": "sourced",
      "locator": { "slide": 3 }, "evidence": ["e1"],
      "level": 1, "finer": "c3", "challenged": "holds-with-boundary",
      "kind": "empirical", "assertion": "statistical",
      "owner": { "name": "…", "checked": "…", "since": "2026-08-29" },
      "holds_when": [ { "dimension": "…", "value": "…", "basis": "stated-in-source",
                        "status": "confirmed", "id": "k1", "level": 1, "finer": "k2" } ],
      "fails_when": [ { "condition": "…", "basis": "replicated" } ],
      "replaced_by": { "claim": "c9" }, "unknown_region": "…" }
  ],
  "evidence": [
    { "id": "e1", "url": "…", "quote": "…", "locator": "p. 178",
      "retrievedAt": "2026-08-26", "sha256": "…", "textSha256": "…",
      "originGroup": "…", "custodian": "self+third-party", "archiveUrl": "…",
      "selfInterested": false }
  ],
  "dimensions": [
    { "name": "air quality", "level": 1, "definition": "One sentence saying what it means.",
      "firstSeen": "2026-08-29", "uses": 3 },
    { "name": "particulate", "level": 3, "coarser": "air quality",
      "definition": "One sentence saying what this finer dimension means.",
      "firstSeen": "2026-08-29", "uses": 1, "mintedBy": "model", "mintedModel": "…" }
  ],
  "disclosure": { "attribution": "…", "accountable": "…",
                  "limitations": "…", "references": "…" },
  "opposed": { "grade": "same-model-fresh-thread", "at": "2026-08-28T03:00:00Z",
               "raised": 3, "model": "claude-opus-5", "modelVersion": "1m" },
  "decisions": [
    { "at": "2026-08-28T01:00:00Z", "context": ["e1"],
      "options": ["stdlib", "jsonschema"], "chose": "stdlib",
      "rejected": [ { "option": "jsonschema", "clause": "a pip install nobody runs" } ],
      "model": "claude-opus-5", "modelVersion": "1m",
      "narrative": { "text": "…", "generatedAt": "2026-08-28T01:00:00Z" } }
  ]
}
```

## Claim status

| Status | Means |
|---|---|
| `sourced` | Retrieved in this session, with a verbatim quote and a locator |
| `recalled` | Produced from memory. Legitimate, and it must be labelled |
| `inferred` | Concluded from other claims. Also legitimate, also labelled |

### `status` and `kind` are independent, and `synthesis` survives

**`status` answers where a claim came from. `kind` answers what species of sentence it
is.** Neither is derived from the other, and the proof is that all four cells are real:

| | `sourced` | `inferred` |
|---|---|---|
| **`synthesis`** | You retrieved somebody else's meta-analysis and quoted it | You drew the conclusion yourself, across several sources |
| **`position`** | Not a normal cell: a stance owes no evidence, so it is almost always inferred | A stance, touching no evidence at all |

A `synthesis` is therefore not a provenance value wearing a kind's clothes. It is a
species of sentence, and it can arrive either way.

**Among inferred claims the useful cut is what the sentence does with the evidence.** A
synthesis runs **through** the evidence. A position does **not touch** it. A story comes
from lived experience. Collapsing `synthesis` into `inferred` would lose that cut and
would also lose the retrieved meta-analysis, which is `sourced` and is still a synthesis.

**The other application now carries `synthesis` too**, so a conclusion drawn across several
claims no longer arrives there as an ordinary empirical claim. That was the first half of
disagreement v5. The second half is the finer `assertion` rung under `kind`, and 1.7 closes
it. Both directions are now lossless.

## The adversarial pass

`opposed` is an optional top-level object recording which grade of adversarial pass actually ran.
The requirement under O is a **fresh thread**, because an instance that is not holding the draft
has no commitment to defend. A different model is a second layer on top of that, not the
mechanism: it catches shared priors, where a fresh copy of yourself believes the same wrong thing.

| `grade` | What it catches |
|---|---|
| `cross-model-fresh-thread` | Commitment and shared priors |
| `same-model-fresh-thread` | Commitment. The workhorse |
| `same-thread-self-challenge` | Some. The student marking their own homework, and better than nothing |
| `not-performed` | Nothing. It is the honest name for a pass that did not happen |

`grade`, `at` and `raised` are required inside the object. `model`, `modelVersion`, `thread` and
`note` are optional, because a host does not always say which model or thread ran. A lower grade
is never reported as a higher one, and a sidecar with no `opposed` is disclosed as
`not-performed`, because a pass nobody recorded is a pass nobody can show ran.

**`opposed` arrives in sourced 1.2 and is optional.** A sidecar without it still validates, so
every file already on disk stays valid. `decisions.py validate()` refuses an unknown grade and
refuses a `not-performed` record that claims it raised something.

### What the pass found about one claim

`opposed` says which grade of pass ran over the artefact. It cannot say which claims were
attacked, or what happened to any of them. **A claim therefore carries an optional
`challenged`**, in the five words the three systems agreed on 29 August 2026:

| `challenged` | Means |
|---|---|
| `not-attempted` | Nothing attacked this claim |
| `attempted-unresolved` | Something attacked it and the attack settled nothing |
| `holds` | It came through unchanged |
| `holds-with-boundary` | It came through, and the pass found where it stops holding |
| `refuted` | It did not come through |

**Absent reads as `not-attempted`**, the same way an absent `opposed` does. The two records
answer different questions and **neither derives from the other**, so `opposed` is
unchanged by any `challenged` value and a `challenged` value is never read off a grade. A
sixth word is refused, because a sixth word is how a pass that reached no conclusion gets
written up as one that held. `holds` and `holds-with-boundary` are the shared replacements
for `survived` and `survived-caveat`: a label should say what was learned rather than who
won.

### A competing claim becomes a claim

The larger half of v9. **An adversarial pass does not hand you two sources that disagree.
It hands you a rival claim.** Until 1.6 there was nowhere to put it, so the rival was
flattened into a sentence in `replaced_by` and lost its evidence, its conditions and its
level on the way down.

So a competing claim lands in `claims[]` like any other claim, with its own `evidence`,
`holds_when`, `fails_when` and `level`. A conflict then points at it, and `replaced_by`
may name it. The conditions of the two claims are what say where each of them is right,
which is the whole point: adversarial is the method, integration is the goal.

## The decision ledger

Rejected options leave no trace in the finished artefact, so once the draft settles the road not
taken is unrecoverable. `<artefact>.decisions.jsonl` sits beside the artefact while the work
happens, one JSON object per line, appended and never rewritten. At assembly it folds into the
sidecar as `decisions[]`, whose members are the ledger's lines unchanged.

A record is the **state**, not the story: what was in context, which options were enumerated,
which was chosen, which were rejected with one clause each, and which model and version ran. None
of that needs introspection, so all of it is checkable. `run` and `narrative` are optional.

| Field | Holds |
|---|---|
| `at` | When the record was written, UTC |
| `context[]` | What was retrieved and what was in context. Evidence ids or short labels |
| `options[]` | Every option enumerated, the chosen one included |
| `chose` | The one chosen. It carries no clause: the artefact is what it looks like |
| `rejected[]` | `{option, clause}`, one clause each. The only free text in the record |
| `model`, `modelVersion`, `run` | Which model ran, and optionally which run |
| `narrative` | `{text, generatedAt}`. Read as narrative produced at that time, never as cause |

**Keep this dumb.** No hypothesis, no falsifier, no `holds_when`. That structure belongs to the
boundary record below, and duplicating it here turns a log into a framework nobody fills in.

**`decisions[]` arrives in sourced 1.1 and is optional.** A sidecar without it still validates, so
every file already on disk stays valid and an implementation that ignores it is not broken.

    python3 decisions.py append <artefact> --option A --option B --chose A \
        --reject "B: needs a second dependency" --model claude-opus-5 --model-version 1m
    python3 decisions.py fold <artefact>      ledger lines -> decisions[] in the sidecar
    python3 decisions.py --self-check         ten cases, known answers, no network

## The boundary record

Four optional fields on a claim, and the reason they exist is that a refuted claim with no
replacement is a hole, and the reader fills the hole with the prior belief that was just
refuted. Optional as a whole, required as a set: **once any one of them is present,
`unknown_region` must say something**, or the card reads as if the space were fully mapped.

| Field | Holds |
|---|---|
| `holds_when[]` | Conditions under which the claim survives. Each entry `{dimension, value, basis}` |
| `fails_when[]` | Conditions under which it does not, with the evidence that showed that |
| `replaced_by` | The claim that is true instead, inside the failing region. Free text, or `{"claim": "c9"}` naming a claim in this sidecar |
| `unknown_region` | Where neither has been tested. Usually most of it |

**`basis` says who said it and `status` says how far it has been checked.** They were one
field until 29 August 2026, and one field could not tell a condition somebody measured
from a condition somebody guessed once it crossed into another system.

| Field | Values |
|---|---|
| `basis` | `stated-in-source`, `inferred-from-conflict`, `human`, `rule` |
| `status` | `asserted`, `proposed`, `monitoring`, `confirmed`, `refuted` |

`status` is optional and a condition that states none reads as `asserted`. **Only a
condition whose `status` is `confirmed` may become a formal condition on the claim**; the
rest stay labelled candidates, so an unchecked guess and a measured interaction never read
the same. That is the same rule the format has always carried, said in the new field. A
bare string in place of the object is refused, because a bare string carries no basis.

**The five old basis words still read.** A condition written `tested`, `replicated`,
`observed`, `untested` or `inferred` validates, and it is read through one translation
table, `dimensions.LEGACY`:

| Old `basis` | Reads as `basis` | Reads as `status` |
|---|---|---|
| `replicated` | `stated-in-source` | `confirmed` |
| `tested` | `stated-in-source` | `confirmed` |
| `observed` | `stated-in-source` | `monitoring` |
| `untested` | `human` | `asserted` |
| `inferred` | `inferred-from-conflict` | `proposed` |

**The table is a reading of intent and it is not a lossless conversion.** `tested` and
`replicated` both arrive as `confirmed`, and nothing downstream can tell them apart again.
No file is ever rewritten by it; a file is read through it. `replicated` and `tested` are
the strong pair, `observed` is weaker, and `untested` and `inferred` were never checked at
all. An explicit `status` beside an old word wins over the table, because the author who
wrote it down knew more than the table does.

`dimensions.read_condition_full(entry)` returns `(dimension, value, basis, status)` in the
current vocabulary from every shape, and **new code uses that one**.
`dimensions.read_condition(entry)` still returns `(dimension, value, basis)` with the basis
as written, for the callers that already use it.

`dimension` is **free text**, and `value` is what that dimension was set to. The shape is
fixed so conditions stay comparable; the dimension is open so any subject can name what
actually moderates its claims.

**A threshold lives inside `value`, not in a field of its own.** Write
`{"dimension": "particulate", "value": "below 6 ppm", "basis": "tested"}`, or
`"value": "< 6 ppm"` if you prefer the symbol. A separate `comparator` field was considered
and rejected: it doubles the shape for the subset of dimensions that are numeric, and it
still cannot express "clean", "overhead" or "near the horizon", which are the conditions
this repo actually had to record. Comparison stays legible to a reader and opaque to the
tool, and the tool never needed it: two values are compared for **difference**, never for
order. A fixed list of five condition fields was rejected on
28 August 2026 (`docs/philosophy.md` position 9), because the sky is blue when the air is
clean and the sun is high, and neither of those is population or tooling.

The older `{condition, basis}` shape still reads, as a **dimension-less condition**: the
old `condition` string becomes the `value` and the dimension is absent. Nothing already
written breaks. `dimensions.read_condition_full(entry)` reads every shape, and it is the
only parser, so no reader has to know which shape it got.

**The dimensions a project uses accrete into a registry**, `dimensions.json` beside the
source index, written as sources are captured. Two claims can only be compared on a
dimension they both name, so `tooling` and `tool-generation` recorded as two dimensions is
what makes a conflict uncomputable. A first-seen dimension is added, a repeat counts a
use, and a near-identical spelling is added **and reported**. Nothing is ever rejected: a
dimension with one claim against it is still a legitimate dimension.

    python3 dimensions.py                     the registry, with its probable duplicates
    python3 dimensions.py --self-check        eighteen cases, known answers, no network

Conditions are recorded in the call that captures the source, because that is the only
moment they are in front of the reader:

    python3 sourced.py <url> --tier 2 --condition "air quality=clean:observed"

`boundary.py` renders a record as the boundary card, and as a two-axis map where exactly
two conditions carry evidence. The card's strip is **derived** from the conditions and
their basis, never stored: a hand-set "70% unknown" is a number nobody can check.

    python3 boundary.py --self-check          five cases, known answers, no network
    python3 boundary.py <file.sourced>        a card per claim that carries a boundary

## Dimensions carry a definition, because overload is the expensive failure

A condition is `{dimension, value, basis, status}` and the dimension is free text
(`docs/philosophy.md` position 9). First use writes it into a per-project registry, later
uses match against it, and until 29 August 2026 a registry row was three bare fields:
`name`, `firstSeen`, `uses`.

**A vocabulary of bare names fails in two ways, and they are not symmetric.**

A **split** is two names for one dimension. `tooling` and `tool-generation` recorded
separately is a spelling accident and not a disagreement. The cost is a comparison you
never make. The failure is silent, and it is recoverable: merge the two rows later and the
comparison comes back.

An **overload** is one name covering two meanings. `method` meaning a research method on
one claim and a manufacturing method on another is one name over two dimensions. The cost
is a comparison you make **wrongly**. Two claims look like they conflict when they are
about different things, `conflicts.py` compares them because they share a name and nothing
reads what the name means, the false conflict reaches `integrate.py`, and `integrate.py`
refuses the delivery. **A wrong refusal is how a gate gets bypassed**, because a gate that
refuses good work is a gate somebody switches off.

**Overload is the expensive one, and a registry of bare strings prevents only splits.** So
a dimension carries a one-sentence **definition**, required at mint. The definition is also
what makes a near match safe to offer: matching on names alone, with nothing to read,
is exactly how an overload happens. `dimensions.register` returns the existing row
**including its definition**, so the author can see what they would be joining and decide.

### A dimension is a claim, so it carries a level

`air quality` is a level-1 dimension. `particulate concentration` is a finer one whose
`coarser` is `air quality`. That is the same mechanism claims and conditions use, run
through the same validator in `sophistication.py`, with no second implementation.

This resolves the free-text-versus-fixed-list argument rather than winning it. The
knowledge-base application's fixed list of thirteen is not a rival vocabulary. **It is the
set of level-1 rungs.** Coarse dimensions recur across projects and are stable enough for
machine extraction with no author present. The long tail hangs off them as finer children,
and the long tail is what free text is for.

`finer` is **not** stored. It is the exact inverse of `coarser`, and a stored pair of
inverses is a pair that can disagree. `dimensions.finer_of(name)` computes it.

### The registry row

| Field | |
|---|---|
| `name` | Free text. Unchanged. |
| `definition` | One sentence. **Required at mint.** |
| `level` | A whole number from 1 up. Absent reads as 1. |
| `coarser` | Optional. The `name` of a coarser dimension that already exists. |
| `firstSeen`, `uses` | Unchanged. |
| `mintedBy` | `author` or `model`. Absent reads as author, the same convention `supports.by` uses. |
| `mintedModel` | Optional, and refused on an author mint. |
| `forcedPast` | Written when a mint was forced past a near match, naming the row it was forced past. |

**Every row already on disk still loads.** A row with no `definition` reads as an
undefined legacy row, never a refused one. Refusing them would break the registry that
already exists. `python3 dimensions.py` lists them under a heading saying they predate the
requirement and should be defined.

**A mint is never refused for existing.** A dimension with one claim against it is
legitimate. Only a missing definition refuses.

### The block on the sidecar

`dimensions[]` is optional, **generated and never authored**, and it may be partial,
because a partial block is honest. It carries the rows for the dimensions the file's
conditions actually name, plus the coarser rung of any finer dimension it carries, because
a child shipped without its parent names something the receiver cannot resolve.

```
python3 skills/sourced/dimensions.py --sidecar deck.html.sourced
```

### Capturing does not stop for it

Typing a definition on every capture is friction that gets the feature switched off, so
the definition is a separate flag and it is typed once:

```
python3 sourced.py --define "air quality=How clean the air is at the place and time of the observation."
python3 sourced.py <url> --condition "air quality=clean:stated-in-source"
```

A `--condition` naming a dimension nothing has defined **warns** and records the row as
undefined. It never fails the capture. Capturing the source is the point, and the
definition can be written a minute later.

## Conflicts

Two retrieved sources disagree, so a conflict opens. `docs/philosophy.md` position 8: a
disagreement is a first-class object, not a decision made quietly in a draft. It opens when
the disagreement is found, it stays open until it resolves into a boundary, and where it
cannot be resolved it ships open with the unknown region named. A disagreement resolved in a
draft is a disagreement the reader never learns about.

**How disagreement is made computable.** An evidence row may carry `supports`:

| Field | Holds |
|---|---|
| `supports.claim` | The id of the claim this row speaks to |
| `supports.direction` | `for`, `against` or `mixed` |
| `supports.by` | Who put it there: `author` or `model`. Optional |
| `supports.model` | The model that proposed it. Optional, and only with `by` of `model` |

Two rows are in opposition when they name the **same claim** with **different directions**,
and neither of them is `mixed`. That is the whole test. Nothing reads the quote text, because
a guess at what a source means puts words in its mouth, and that is worse than silence.

**`mixed` is a source that supports the claim in one region and undermines it in another.**
It arrived in 1.4 because it is the most interesting kind of source this framework has and
there was nowhere to put it. **A `mixed` row never raises a conflict on its own.** A source
that cuts both ways is already telling you where the boundary is, so it does not need another
source to disagree with. `conflicts.opposed_pairs()` ignores it on both sides. What it raises
instead is a **boundary prompt**: a soft flag in `integrate.py` asking whether the boundary
has been recorded, which goes silent as soon as the claim it names carries a boundary record.
A conflict record may not name a `mixed` row as a side, and `validate_conflicts()` refuses one
that does, because a mixed source is a boundary and not a side.

**Who set the support.** `claim` and `direction` are required. `by` and `model` are optional.
**An absent `by` reads as `author`.** Every `supports` written before the field existed was
typed by a person, and a silent default of `model` would retro-label their work as a machine's
proposal. A `model` beside `by` of `author` is refused, because a person did not run a model to
hold an opinion. The model proposes a support while it reads, and the author confirms or
corrects it. The proposing is automated and the deciding is not.
`python3 conflicts.py <file.sourced>` prints how many supports are author-set and how many are
model-proposed, and says plainly when every support in the file is model-proposed.

An evidence row may also carry `conditions[]`, the same `{dimension, value, basis}` shape a
claim uses. The **differing dimensions** of a conflict are the dimensions both rows name where
the values differ, compared through `dimensions.normalise`, so `Clean air` and `clean-air` are
one value rather than two. Two opposed rows that name no dimension in common raise nothing:
they disagree, but no dimension is named by both, so there is nothing yet to say where each is
right. `conflicts.explain()` returns that reason, so the silence is reported rather than
assumed.

**The record.** `conflicts[]` is an optional top-level array. A sidecar without it validates
unchanged.

| Field | Holds |
|---|---|
| `id` | `x1`, `x2`, unique inside the sidecar |
| `claim` | The claim the two sources disagree about |
| `between[]` | Exactly two sides. A side is `{evidence, outcome}` with `outcome` `for` or `against`, never `mixed`, or `{claim}` naming a competing claim |
| `dimensions[]` | The dimensions the two sides differ on, at least one |
| `state` | `open` or `resolved`, and nothing else |
| `resolved_into` | Required when resolved: the claim whose boundary record now holds it |
| `unknown_region` | Required when open: where nobody has looked |

```json
{"id": "x1", "claim": "c1",
 "between": [{"evidence": "e1", "outcome": "for"},
             {"evidence": "e2", "outcome": "against"}],
 "dimensions": ["air quality"], "state": "open",
 "unknown_region": "dusk, and every latitude above 60 degrees"}
```

**A side may be a claim, not only an evidence row.** The evidence-row form above is
unchanged and still works exactly as it did. Beside it, a side may be `{"claim": "c9"}`,
which is the shape an adversarial pass actually produces:

```json
{"id": "x2", "claim": "c1",
 "between": [{"evidence": "e1", "outcome": "for"}, {"claim": "c9"}],
 "dimensions": ["air quality"], "state": "resolved", "resolved_into": "c1"}
```

**A claim side carries no `outcome`.** An evidence row votes on a claim, and the outcome is
its vote. A rival claim does not vote; it stands against the claim, so an outcome on it is
refused. A claim side must name a claim that exists, and it may not name the conflict's own
claim, because nothing is a rival to itself.

**The differing dimensions of a claim side are read off its `holds_when` and `fails_when`**,
where an evidence row's are read off its `conditions`. One function reads both, because no
record carries both sets of fields, so there is no second parser to drift.

**`detect()` is unchanged and still reads evidence rows only.** A claim-versus-claim conflict
is written by whoever ran the pass. Nothing infers a rival claim, because a rival claim is a
thing somebody thought of.

**`replaced_by` may name that claim.** Write `"replaced_by": {"claim": "c9"}` and the thing
that is true instead is a claim in the corpus with its own evidence, conditions and level,
rather than a sentence stranded in a string. Free text still reads, unchanged, because most
replacements never become their own claim. A named claim that is not in the sidecar is
refused, and so is a claim naming itself.

**Why `resolved` needs a boundary.** A conflict that resolves into nothing is a conflict
resolved quietly, which is the move this record exists to stop. So `resolved_into` must name a
claim that exists and that carries a boundary record: any of `holds_when`, `fails_when`,
`replaced_by` or `unknown_region`. The disagreement becomes a map of where each side is right.

**Why `open` needs an unknown region.** Shipping an open conflict is honest only when the
reader is told what is unmapped. An open conflict at delivery is disclosed, never dropped, and
`conflicts.disclosure_lines()` writes the sentence for the Limitations line. It is a limit on
the **evidence**, not on our own thinking, which is what that label carries.

Nothing here judges which side is right. The tool finds and records; the author resolves.

    python3 conflicts.py --self-check      twelve cases, known answers, no network
    python3 conflicts.py <file.sourced>    detected, explained and still open

## The integration gate

A conflict record and a boundary record are only worth having if something checks that they were
written. `integrate.py` is that check. It runs before any statement ships,
and it refuses a delivery that hides a disagreement.

    python3 integrate.py <file.sourced>    check that sidecar before it ships
    python3 integrate.py --self-check      twelve cases, known answers, no network

What it refuses, and why each one is a disagreement the reader never sees:

| An open conflict in `conflicts[]` | The sidecar records the disagreement and the delivery says nothing about it |
| Evidence rows that disagree with no conflict record and no boundary on the claim | The disagreement is already in the evidence, and nothing in the artefact acknowledges it |
| A claim with `fails_when` and no `replaced_by` | A refutation with no replacement leaves the reader holding the belief it just refuted |
| A claim at level 3 or above whose evidence carries no quote and no locator | A precise claim the reader cannot follow back to a source |

A disagreement in the evidence is matched to a stored conflict by the claim plus the pair of
evidence ids, in either order. A boundary record on the claim counts as acknowledgement, because
the conflict has already become the map it was supposed to become.

**Three things are flagged rather than refused. The first is possibly stale evidence.** A period is an ordinary
condition whose dimension normalises to `period`, carrying a year, a year range or an ISO date.
When an evidence row's period ends before the period of the claim it is cited for begins, the
study finished before the thing it is cited about began, and the gate says so. It prints and the
exit code stays 0. Staleness is read off periods written by hand, so it is a soft signal, and a
gate that fails on a soft signal is a gate that gets switched off. A period value that cannot be
read as a year is reported as unparsed, never guessed.

A period recorded only in the prose of a quote is invisible to this check. Record it as a
condition at retrieval and it becomes checkable.

**The second flag is a conflict nobody has confirmed.** When both sides of a stored conflict
rest on a `supports` marked `by` of `model`, the disagreement was proposed by a model and no
person has looked at it. The flag names the conflict, both evidence rows and the model, and the
action is to confirm or correct the two `supports` values. One author-set side clears it. A
model-proposed support on a row that is part of no conflict raises nothing. It is a flag and
never a refusal, because the gate refuses on the recorded field: a wrong proposal is then a
visible wrong row somebody can fix, where a refusal driven by an inferred contradiction would
be a wrong verdict nobody can see.

**The third flag is a source that cuts both ways.** An evidence row recorded `mixed` on a
claim that carries no boundary record raises a boundary prompt: this row supports the claim in
one region and undermines it in another, so has the boundary been written down? It goes silent
once the claim carries any of `holds_when`, `fails_when`, `replaced_by` or `unknown_region`,
because the question has been answered and a question that keeps being asked after that is a
flag people learn to skip. Whether one mixed source is enough to draw a boundary is the
author's judgement, so it never fails the gate.

## One claim, stated at several levels

"The sky is blue" and "Rayleigh scattering goes as the inverse fourth power of wavelength" are
one claim at two depths, not two unrelated records. A statement therefore carries a `level`, and
may name a `coarser` and a `finer` sibling saying the same thing at another depth.

| Field | Holds |
|---|---|
| `level` | Any whole number from `1` up. A level is an ordinal and has no name. It prints as "level 3" |
| `coarser` | The id of the same statement, said more plainly. Its level must be lower |
| `finer` | The id of the same statement, said more precisely. Its level must be higher |

**A condition is itself a claim, so it uses the same mechanism.** "Clean air" and "particulate
below six parts per million" are one condition at two depths. A condition may carry an optional
`id` so a sibling can name it; one with no id cannot be a sibling target, and that is fine. There
is one implementation and one validator: `sophistication.validate_statements()` runs over
`claims[]` and then over every condition flattened out of `holds_when` and `fails_when`.

**The ladder has no top and its rungs have no names.** There is no end to stating a claim more
precisely, so level 4 and above are valid. A level prints as "level 7". Level 4 is not called
"conditional". A claim at any level can carry conditions, and each condition carries its own level,
so naming a level after conditions confused the ladder with the thing hanging off it.

**The audience names came out on 29 August 2026.** The reason is that an audience name
invites an argument about who counts as a practitioner. As a teaching gloss, and
only as a gloss, level 1 is roughly the sentence somebody says at a barbecue and level 3 is
roughly the sentence somebody says at work. That is a gloss and never a definition, and no rule,
message or validator carries it.

**The numbers are relative, not absolute.** Level 3 names no exact quantity of precision. Two
artefacts do not have to agree about what their level 3 holds, and consistency across artefacts is
not maintainable, so **nothing may compare a level across two artefacts**. A level is a position in
one artefact's ladder. A statement may also need **re-levelling** later, when something turns up
that sits between two rungs already written down, and that is expected rather than a defect. See
`docs/philosophy.md` position 10.

The validator refuses a level that is not a whole number from 1 up, a `coarser` or `finer`
naming an id that does not exist in the same scope, a sibling at the wrong depth, and a cycle in
either direction. Sibling links describe a ladder of depths, and a ring is not a ladder.

**Sophistication is not strength.** A level-1 statement is a coarser model, not weaker evidence,
and the two axes stay orthogonal. A level-1 claim resting on replicated evidence is not a defect.
The check that matters is the mismatch: a claim stated at level 3 or above whose evidence is not
precise enough to follow back is **over-claiming**, and `sophistication.py` reports it.

| Evidence precision | What the evidence has to carry |
|---|---|
| 1 | No evidence row resolves |
| 2 | At least one evidence row resolves |
| 3 | At least one row carries both a quote and a locator |

**This is a floor and not a ceiling.** On an unbounded ladder no reading of the evidence can say
"this supports level 47". What is checkable without judgement is the other direction: a precise
claim needs a precise citation. So the number stops at 3, and a claim stated at level 1 or 2 can
never over-claim. Evidence precision is **derived, never stored**, the same rule strength already
follows.

**`integrate.py` refuses it at delivery.** A claim stated at level 3 or above whose evidence carries
no quote and no locator fails the integration gate. The message names the claim, its stated level,
what is missing, and the two ways out: cite the claim precisely, or state the claim at level 2. The
accepted risk is that a hard gate on a stated level creates pressure to under-state the level. That
was chosen deliberately over a report nobody reads.

**`level`, `coarser` and `finer` arrive in sourced 1.3 and are optional.** A 1.2 sidecar with no
levels anywhere validates unchanged, and so does a `holds_when` entry in the old
`{condition, basis}` shape. **1.4 removed the level names and added no field**, because a level
was always the integer and the names were prose.

    python3 sophistication.py --self-check     eight cases, known answers, no network
    python3 sophistication.py <file.sourced>   the over-claiming report

## Kinds

A claim carries a `kind`: what species of sentence it is. The words are Publish's, unchanged, so
one claim is not described two ways and the two systems stop drifting.

| `kind` | Plain English |
|---|---|
| `empirical` | A claim backed by evidence somebody gathered |
| `synthesis` | A conclusion drawn across several claims |
| `position` | A stance, evidence-exempt by design |
| `story` | Author-verified lived experience |

`position` and `story` are their own species of sentence, not weak tiers. An author's own stance
stops being recorded as a claim that failed to find a source.

**Evidence-exempt is not check-exempt.** A position and a story owe no evidence, so they owe the
other kind of warrant, or they become a hiding place, including for the author.

- **A position requires a `falsifier`**: what would have to be true for the stance to be wrong.
- **A story requires a `falsifier` and a `witness`** naming who lived it. Testimony with nobody's
  name against it has no warrant at all, which is the reason for recording it as a story.

`kinds.validate_kinds()` refuses a kind outside the four, an evidence-exempt claim with no
falsifier, and a story with no witness. It names the offending claim by id and statement.

**A Limitations line that names one of our own positions or stories is refused**, alongside the six
the wrong question asked in the wrong place. Our own stance and our own lived experience are the value
of the piece, and INFERRED in the sidecar is the whole disclosure they need.

**Provenance, fidelity and kind are three separate questions**, and none is derived from another:
provenance asks whether anything backs the claim, fidelity asks how far the wording sits from the
source, and kind asks what species of sentence it is.

**`kind`, `falsifier` and `witness` arrive in sourced 1.3 and are optional.** A 1.2 sidecar with no
kinds validates unchanged.

### The finer rung: `assertion`

`kind` is a hybrid of two axes, and that is why translating it in either direction used to lose
something. The other application carries `species` (claim, position, story) and `assertionType`
(eight words). This repository's `kind` takes `position` and `story` from the first, and
`empirical` and `synthesis` from the second.

**The fix is a ladder, not a second field.** `kind` stays the coarse rung and answers the question
a person actually asks: did somebody measure this, did I conclude it, do I hold it, or did I live
it. A claim may also carry an optional `assertion`, the finer rung, taking the other application's
eight `assertionType` words exactly, with nothing added and nothing renamed. This is the same move
a statement already makes with `level`, `coarser` and `finer`. `air quality` and `particulate` are
one dimension at two depths, and `empirical` and `statistical` are one axis at two depths.

| `assertion` | sits under `kind` |
|---|---|
| `empirical` | `empirical` |
| `statistical` | `empirical` |
| `definitional` | `empirical` |
| `predictive` | `empirical` |
| `synthesis` | `synthesis` |
| `normative` | `position` |
| `interpretive` | `position` |
| `narrative` | `story` |

The mapping is fixed and total. `kinds.kind_of()` derives the coarse rung from the finer one, and
it is the one place the table is read, so nothing writes it twice. A claim whose two rungs disagree
is refused, and the message names both. A claim carrying a `kind` and no `assertion` is complete. A
1.6 sidecar has no `assertion` anywhere and validates unchanged.

The round trip is now lossless in both directions. `python3 skills/sourced/kinds.py --self-check`
walks all eight values, derives the kind, and reads the assertion back. `vocabulary.py` walks the
same eight again against the map row.

### A predictive assertion owes a resolution

An evidence-exempt kind owes a `falsifier`. A forecast owes the same discipline in its own words.

**A claim whose `assertion` is `predictive` must carry `resolves`.**

```json
{ "id": "c7", "statement": "The index falls below 40 before July 2027.",
  "kind": "empirical", "assertion": "predictive",
  "resolves": { "by": "2027-06-30",
                "criterion": "The published index for June 2027 reads below 40.",
                "outcome": "unresolved" } }
```

`by` is the date it resolves. `criterion` is the observation that would settle it, specific enough
to be checked by somebody who does not care who was right. Both must say something, or the claim is
refused. An unfalsifiable forecast must never be tiered as evidence. `outcome` is optional and is
one of `true`, `false`, `ambiguous` or `unresolved`.

These are the other application's `calibration` fields under shorter names: `by` is
`calibration.resolvesBy`, `criterion` is `calibration.resolutionCriterion`, and `outcome` is
`calibration.resolvedOutcome` with the same four words.

**`integrate.py` raises a soft flag**, never a failure, for a predictive claim whose `resolves.by`
has passed and which records no `outcome`. The date arrived and nobody went back to check. The exit
code is unchanged.

**`assertion` and `resolves` arrive in sourced 1.7 and are optional.** A 1.6 sidecar validates
unchanged.

## Who answers for the claim

A claim may carry an `owner`: a named person who answers for it, what that person personally
checked, and since when.

```json
{"name": "A. Ramsden", "checked": "Read the 1899 paper in full and confirmed the exponent.",
 "since": "2026-08-29"}
```

| Field | Holds |
|---|---|
| `name` | The person who answers for the claim. Required when `owner` is present |
| `checked` | What that person personally verified. Required, and it must say something |
| `since` | The day they took it on. Optional |

**`checked` is required because a signature buys accountability and never accuracy.** "I own
this" with no "here is what I verified" beside it is precisely the move the U of SOURCED exists
to refuse, so the schema refuses it too. `kinds.validate_owners()` names the offending claim.

**An `owner` and a `witness` are different things, and neither derives from the other.** A
witness lived the experience a story records. An owner answers for the claim. One claim may carry
both, either, or neither, and a story still needs its witness whether or not somebody owns it.

**`owner` arrives in sourced 1.4 and is optional.** A 1.3 sidecar with no owner validates
unchanged.

    python3 kinds.py --self-check     seven cases, known answers, no network
    python3 kinds.py <file.sourced>   the per-kind tally, the owners and the exempt claims

## Why `claims[]` is thin

No tier, no assertion type, no relations. Those are the fields platform implementations disagree
about, and a lowest common denominator that everybody can emit is worth more than a rich schema only
one system produces.

**If it grows relations and computed tiers it has become a claim record with extra steps**, and the
right move then is to adopt that instead. `evidence[]` is deliberately shaped to match what a
claim-record store keeps, so a sidecar can be ingested and enriched rather than re-captured.

## Claim strength is a separate axis

Do not build strength grading into the sidecar. A claim tier, the lifecycle state of a claim, and the
event chain behind it are a different model with a different owner. **Tiers grade a claim. The
provenance block covers the artefact.** Two scales, and merging them loses both.

### One vocabulary for the book and the sidecar

Separate axis does not mean separate words. The book and the sidecar now use one vocabulary, so one
claim is not described two ways. `skills/sourced/vocabulary.py` holds the mapping, and
`docs/framework.md` position 7 carries the same table.

| State | Label | Kind | Strength |
|---|---|---|---|
| `0` | `unanalyzed` | not decided by the state | 0 |
| `1` | `no / contradicted evidence` | not decided by the state | 1 |
| `2` | `single source` | not decided by the state | 2 |
| `3` | `multi-source` | not decided by the state | 3 |
| `4` | `boundary recorded` | not decided by the state | 4 |
| `position` | `stance (evidence-exempt)` | position | none, evidence-exempt |
| `story` | `lived experience` | story | none, evidence-exempt |

The labels are the book's stored strings, quoted verbatim, which is why `unanalyzed` keeps its
American spelling. Tier 4 is `boundary recorded` rather than `survived adversarial`, because a label
should say what was learned rather than who won.

**Tiers 0 to 4 are strength and decide no kind. `position` and `story` are kinds and carry no
strength**, because they are their own species of sentence and not weak tiers. **Provenance and
fidelity stay independent of all seven states**, and the map says so in every row rather than
leaving it out.

**Strength is derived from the evidence rows and is never stored.** 0 nothing recorded · 1 evidence
sought and none found, or a row that argues against the claim · 2 a single origin group · 3 two or
more distinct origin groups · 4 tier 3 with a boundary record on the claim. `decisions.py validate()`
refuses a sidecar that stores `strength` or `tier` on a claim, and `vocabulary.unmapped()` reports a
state it does not know by name rather than guessing at it.

### Backing says why it is what it is

A derived number that gives no account of itself is the thing this framework objects to
everywhere else. So `vocabulary.backing()` returns the number **and** the named reasons,
as `Backing(grade, downgrades, upgrades)`. The words are the claim standard's own
`qualifier.downgrades` and `qualifier.upgrades` enums, verbatim, so one claim is not
described two ways.

| Downgrades | Upgrades |
|---|---|
| `risk-of-bias`, `inconsistency`, `indirectness`, `imprecision`, `publication-bias`, `self-interested-source`, `single-source` | `large-effect`, `dose-response`, `confounders-would-reduce`, `replicated-independently` |

**Only what the sidecar can see is derived, and nothing else is ever emitted.** Four
reasons come out of what the file actually holds:

| Reason | Derived from |
|---|---|
| `single-source` | The claim's evidence resolves to one distinct `originGroup` |
| `self-interested-source` | An evidence row carries `"selfInterested": true` |
| `inconsistency` | The claim has an opposed pair in its evidence, or a conflict record naming it |
| `imprecision` | The claim has evidence, and no row of it carries both a quote and a locator |

**`risk-of-bias`, `indirectness` and `publication-bias` stay in the vocabulary and stay
unset.** They are facts about how a study was run and about what else was published, and a
sidecar records neither. A claim store that holds study metadata can derive them; this
format cannot, and a guessed reason reads exactly like a derived one.

**No upgrade is derived at all.** `originGroup` is a label an author types, so reading
`replicated-independently` off two of them would assert a research fact from a bookkeeping
field.

**`selfInterested` is a new optional boolean on an evidence row**, the same field name the
claim standard uses: does the source benefit from this claim being believed. Absent means
nobody has said either way, and absence never fires the downgrade.

**Strength is still derived and never stored.** The reasons are computed beside the number
on every read; neither is a field on a claim, and a stored `strength` or `tier` is still
refused.

## A thin capture is not evidence

The capture tool counts the words sitting in sentence-length lines and warns `THIN` below 300 of
them. Below that an HTML capture is almost always navigation: the site rendered its body in the
browser and `curl` saw the shell.

**The hash is real and the evidence is not there.** Open the `.txt` and confirm the quote is in it
before citing the page. The row carries `proseWords` and `thin` so a later audit can find every
hollow capture without re-fetching.

This is not theoretical. Chasing one vendor-neutral trace schema took three captures: the website
rendered its tables in the browser, the obvious repository path returned a 396-byte "this has moved"
stub, and only the third held the specification. **Both failures hashed cleanly**, and a re-check
would have called them unchanged forever, because a stub that does not move is a stub that does not
move.
