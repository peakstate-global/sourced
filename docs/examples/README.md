# Worked examples

`sky-deck.sourced` is one sidecar at schema 1.7 with every optional field populated:
levels and siblings on a claim and on a condition, the four kinds with a finer
`assertion` under three of them, a predictive claim with its resolution, conditions in the
`{dimension, value, basis}` shape, an `owner` on a claim, a conflict resolved into a
boundary, one support set by the author, one proposed by a model, one recorded `mixed`,
an `opposed` grade, a `challenged` value per claim, a conflict between a source and a
competing claim, and a `replaced_by` naming that claim. It is not a real artefact. It
exists so the format can be read rather than described.

**What arrived in 1.7 is the finer rung, `assertion`.** `kind` is the coarse rung and answers
what a person asks. `assertion` sits under it in the knowledge-base application's own eight
words, and the mapping between the two is fixed and total.

- **`c2` carries `"assertion": "statistical"` under `"kind": "empirical"`.** It states an
  exponent, which is a finer thing than "somebody measured this", and nothing about `c2`
  changed apart from saying so.
- **`c3` carries `normative` under `position`, and `c4` carries `narrative` under `story`.**
  Those two used to flatten on the way out, because `position` covers both `normative` and
  `interpretive`. Now the coarse rung and the finer rung both travel.
- **`c1` and `c5` carry no `assertion` at all**, and that is deliberate. A claim with a kind
  and no assertion is complete, which is what every 1.6 sidecar is.

**`c6` is the predictive claim.** Its `assertion` is `predictive`, so it must carry `resolves`:
`by` is the date it settles, `criterion` is the observation that would settle it, and `outcome`
is `unresolved` because 2027 has not happened. A predictive claim with no resolution is refused,
because an unfalsifiable forecast must never be tiered as evidence. Its date is still ahead, so
the integration gate says nothing about it. Move the date into the past and drop the outcome, and
`integrate.py` raises a soft flag saying the date arrived and nobody went back to check.

**What arrived in 1.6 is the rival claim, `c5`.** An adversarial pass on `c1` did not hand
back two sources that disagree. It handed back a claim that is true instead: near the
horizon the sky is red. In 1.5 that sentence sat inside `c1`'s `replaced_by` as a string,
where it had no evidence, no conditions and no level of its own. It is now a claim in
`claims[]`, `c5`, with its own evidence row `e4`, its own `holds_when` on sun angle, and its
own `unknown_region`.

Three things follow from that, and they are the point of the change:

- **`c1` carries `"replaced_by": {"claim": "c5"}`**, not a sentence. A reader can follow the
  replacement to a claim and check it. `boundary.validate_replacements` refuses a
  `replaced_by` naming a claim the sidecar does not hold.
- **Conflict `x2` is between a source and a claim.** Its sides are
  `{"evidence": "e1", "outcome": "for"}` and `{"claim": "c5"}`. The claim side carries no
  `outcome`, because a rival claim does not vote on the claim it stands against. Conflict
  `x1`, between two evidence rows, is untouched and still reads exactly as it did.
- **`c1` carries `"challenged": "holds-with-boundary"` and `c5` carries `"holds"`.** That is
  what the pass found about each claim, in the five shared words. It is not derived from the
  artefact-wide `opposed` grade and it does not change it: `opposed` says a cross-model pass
  ran, and `challenged` says what it found about one claim. A claim with neither, like `c2`,
  reads as `not-recorded` here, because a pass ran over the artefact and nothing says whether
  it touched that claim.

`e4` also shows `"selfInterested": false`: does the source benefit from this claim being
believed. Absent means nobody has said either way, and absence never fires the
`self-interested-source` downgrade.

**The `dimensions[]` block is what arrived in 1.5.** It carries the registry rows for the
four dimensions the conditions in this file name, each with the one sentence that says what
it means, because a sidecar travels on its own and a dimension defined only in a project
registry means nothing to whoever receives the file.

- `air quality` is at **level 1** and defined. It is a coarse rung: it recurs across
  projects and is stable enough for machine extraction.
- `particulate` is at **level 3** with `"coarser": "air quality"`. It is the same condition
  said more precisely, and it hangs off the coarse rung rather than sitting beside it. That
  is the long tail free text is for. `finer` is not stored, because it is the exact inverse
  of `coarser` and a stored pair of inverses is a pair that can disagree.
- `sun angle` carries `"mintedBy": "model"` with the model named, the same convention
  `supports.by` uses. Absent means the author minted it.

The definition is required at mint, and the reason is that the two ways a vocabulary fails
are not symmetric. Two names for one dimension is a **split**: a comparison you never make,
silent, recoverable. One name over two meanings is an **overload**: a comparison you make
**wrongly**, two unrelated claims recorded as a conflict, and the integration gate refusing
a delivery that should have shipped. Bare names prevent splits only.

Write the block from the registry rather than by hand:

    python3 skills/sourced/dimensions.py --sidecar docs/examples/sky-deck.sourced

Three things in it show the shapes that arrived in 1.4:

- **A condition in the split shape.** `k4` carries `"basis": "stated-in-source"` and
  `"status": "confirmed"`, which is who said it and how far it has been checked. The other
  conditions still use the older single words, `tested` and `observed`, and they read
  through the translation table in `dimensions.LEGACY`. Both shapes render on one card.
- **An evidence row recorded `mixed`.** `e3` supports `c1` overhead through the afternoon
  and undermines it at dusk. It raises no conflict, because a source that cuts both ways
  is already saying where the boundary is. It raises a boundary prompt instead, and that
  prompt is silent here because `c1` already carries a boundary record. Move the row to a
  claim without one and `integrate.py` asks the question.
- **An `owner` on `c1`.** A named person, what that person personally checked, and since
  when. `checked` names the two sources read and says one of them was read through an
  abstract, because "I own this" with nothing verified beside it is the move the U rule
  refuses. An owner is not a witness: `c4` names a witness, who lived the experience.

Every checker runs on it, and this is what each one says:

    python3 skills/sourced/decisions.py   # validate() returns True
    python3 skills/sourced/integrate.py docs/examples/sky-deck.sourced
    python3 skills/sourced/vocabulary.py docs/examples/sky-deck.sourced
    python3 skills/sourced/sophistication.py docs/examples/sky-deck.sourced
    python3 skills/sourced/kinds.py docs/examples/sky-deck.sourced
    python3 skills/sourced/conflicts.py docs/examples/sky-deck.sourced

`conflicts.py` reports the one conflict detected from the evidence, both stored conflicts
with their sides named, none still open, and that of the four supports three are author-set
and one is model-proposed. The `mixed` row
is not counted as a side of anything. `sophistication.py` reports that 4 of 6 claims state
a level and that no claim is stated at level 3 or above without a precise citation.
`kinds.py` prints the owner beside the two evidence-exempt claims, and prints each finer
assertion with the kind it sits under. `vocabulary.py` prints,
per claim, the derived backing **with the reasons for it**: `c1` reads backing 1 because
`inconsistency`, and `c2` and `c5` read backing 2 because `single-source`. The number is
still derived and still never stored. The integration gate
passes it and raises one flag: a source from 1899 is cited for a claim about 2015 to 2026,
so the evidence finished before its subject began. A flag is a soft signal and does not
fail the gate.
