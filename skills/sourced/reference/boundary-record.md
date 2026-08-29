# The boundary record

Read this when a claim has failed against the evidence, or the evidence is conditional. It is the
rule under the S and the O.

**Adversarial is the method, integration is the goal.** When the evidence goes against a
claim, "falsified" is where the work starts, not where it stops. Record the boundary:

- **Holds when:** the conditions under which the claim survives, each one an observed
  moderator, never a story ("it depends on maturity" needs someone to have measured maturity).
- **Fails when:** the conditions under which it does not, with the evidence that showed it.
- **What is true instead:** the claim that replaces it inside the failing region, with its
  own falsifier. A refuted claim with no replacement is a hole, and the reader fills it with
  the prior belief you just refuted. **`replaced_by` is free text, or it names a claim**:
  write `{"claim": "c9"}` and the replacement is a claim in the corpus with its own
  evidence, conditions and level, rather than a sentence stranded in a string. That is the
  form to use when an adversarial pass produced the replacement, because a pass hands you a
  rival claim and not a sentence. A named claim must exist in the same sidecar, and a claim
  may not replace itself. `boundary.validate_replacements(data)` refuses both.
- **Unknown region:** where neither has been tested. Say so; that is usually most of it.

**A rival claim is a claim, and the conflict points at it.** Where the pass produced a
competing claim rather than a competing source, put that claim in `claims[]` and record a
conflict whose side is `{"claim": "c9"}`. The conditions on the two claims then say where
each of them is right, which is how a disagreement becomes a boundary. See
`docs/sidecar.md`.

**Record what the pass found about the claim itself.** A claim may carry `challenged`, one
of `not-attempted`, `attempted-unresolved`, `holds`, `holds-with-boundary` or `refuted`.
Absent reads as `not-attempted`. `holds-with-boundary` is the value that pairs with this
record: the claim came through, and the pass found where it stops holding.

A black-and-white verdict is a polarised answer to a conditional question. The output that
moves a decision is the map of where each side is right. Write the sidecar claim with
`holds_when`, `fails_when` and `replaced_by` where the evidence supports them, and render
the boundary somewhere a reader can see it: a conditions table at minimum, a two-axis map
where the moderators are two. (2026-08-27: "you shot down my idea and stopped there".)

Each condition is an object, `{dimension, value, basis, status}`. **`basis` says who said
it** and is one of `stated-in-source`, `inferred-from-conflict`, `human` or `rule`.
**`status` says how far it has been checked** and is one of `asserted`, `proposed`,
`monitoring`, `confirmed` or `refuted`. `status` is optional and defaults to `asserted`.
**Only a condition whose `status` is `confirmed` may become a formal condition on the
claim.** That is the same rule the record has always carried, said in the field that now
holds it. Once any boundary field is present, `unknown_region` must say something, or the
card reads as a fully mapped space.

The five older basis words still read. `tested` and `replicated` translate to
`stated-in-source` + `confirmed`, `observed` to `stated-in-source` + `monitoring`,
`untested` to `human` + `asserted`, and `inferred` to `inferred-from-conflict` +
`proposed`. The table lives once, in `dimensions.LEGACY`, and it is a reading of intent
rather than a lossless conversion: `tested` and `replicated` arrive as one pair and cannot
be told apart afterwards.

`dimension` is free text, so any subject can name what moderates its claims, and the shape
is fixed so conditions stay comparable. The older `{condition, basis}` shape still reads,
as a dimension-less condition. **New code uses `dimensions.read_condition_full(entry)`**,
which returns `(dimension, value, basis, status)` from every shape.
`dimensions.read_condition(entry)` still returns the three-tuple with the basis as
written, for the callers that already use it. Either way, do not write a second parser.

**A dimension carries a one-sentence definition, and it is required at mint.** A vocabulary
of bare names fails two ways, and they are not symmetric. A **split** is two names for one
dimension: you miss a comparison, the miss is silent, and merging the rows later recovers
it. An **overload** is one name over two meanings, `method` for a research method on one
claim and a manufacturing method on another: you make a **false** comparison, the two
claims read as a conflict, and `integrate.py` refuses a delivery that should have shipped.
A wrong refusal is how a gate gets bypassed. Bare names prevent splits only, so the
definition is what prevents the expensive failure. It is also what makes a near match safe
to offer: `dimensions.register` hands back the existing row **with its definition**, so you
can read what you would be joining before you decide.

**A dimension is itself a claim, so it carries a level.** `air quality` is a level-1
dimension and `particulate` is a finer one whose `coarser` is `air quality`, validated
through `sophistication.validate_statements` like every other statement. `finer` is not
stored; `dimensions.finer_of(name)` computes it from `coarser`.

**Record the conditions while you read the source, not afterwards.** The capture takes them
in the same call, and mapping them later is archaeology that does not happen. Define once,
then capture:

    python3 sourced.py --define "air quality=How clean the air is at the place and time of the observation."
    python3 sourced.py <url> --tier 2 --condition "air quality=clean:observed" \
        --condition "sun angle=high:tested"

Each `--condition` is validated, stored on the source's index row, and counted in the
project's dimension registry. A `--condition` naming a dimension nothing has defined
**warns and records the row as undefined**. It never fails the capture, because capturing
the source is the point and the definition can be written a minute later.

    python3 dimensions.py                  the registry, its levels and its undefined rows
    python3 dimensions.py --sidecar F      write the definitions this file uses into it
    python3 dimensions.py --self-check     seventeen cases, known answers, no network

    python3 boundary.py <file.sourced>     the boundary card, per claim that carries one
    python3 boundary.py --self-check       four cases, known answers, no network

`boundary.card(record)` returns an HTML fragment and `boundary.CSS` the rules it needs,
once per page. `boundary.axis_map(record, x, y, cells)` draws the two-axis map and
refuses unless exactly two conditions carry evidence, which is a status of `confirmed`,
`monitoring` or `refuted`: somebody looked. `boundary.is_formal(entry)` answers the
formal-condition question on its own. The strip on the card is derived from the
conditions and how far each is checked, so it moves only when somebody checks something.

## A conflict resolves into a boundary

When two retrieved sources disagree, a conflict record opens (`docs/sidecar.md`, Conflicts).
It names both evidence rows, the outcome each supports, and the dimensions they differ on. It
is `open` or `resolved`, and nothing else.

`resolved` means it resolved **into** a named claim that carries a boundary record. That is
the same record described above: where the claim holds, where it fails, what is true instead,
and what is unmapped. A conflict cannot resolve into nothing, because resolving it quietly is
what the record exists to stop.

Where the boundary cannot be found, the conflict ships `open` with its `unknown_region` named,
and the delivery discloses it. Both endings are honest. Deleting the disagreement is not.

    python3 conflicts.py <file.sourced>    detected, explained and still open
    python3 conflicts.py --self-check      nine cases, known answers, no network

**A source that cuts both ways is a boundary, not a conflict.** An evidence row may be
recorded `mixed`, meaning it supports the claim in one region and undermines it in
another. It opens no conflict, because it is already saying where the boundary is. What
it raises is a boundary prompt from `integrate.py`, asking whether the boundary has been
written down, and the prompt goes silent as soon as the claim carries a boundary record.

