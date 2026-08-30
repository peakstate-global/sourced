#!/usr/bin/env python3
"""Two sources disagree, so a conflict opens. It closes into a boundary, or it ships open.

    python3 conflicts.py --self-check      twelve cases, known answers, no network
    python3 conflicts.py <file.sourced>    the conflicts found, explained and still open

`docs/philosophy.md` position 8: adversarial is the method, integration is the goal. A
disagreement between two sources is a first-class object, not a decision made quietly in a
draft. It opens when the disagreement is found, it stays open until it resolves into a
boundary, and where it cannot be resolved it ships open with the unknown region named.
Shipping an open conflict is honest. Resolving it silently is not, because the reader
never learns the disagreement was there.

HOW DISAGREEMENT IS MADE COMPUTABLE
-----------------------------------
An evidence row may carry `supports`:

    {"claim": "c1", "direction": "for" | "against" | "mixed",
     "by": "author" | "model", "model": "the model that proposed it"}

Two rows are in opposition when they name the **same claim** with **different
directions**, and neither of them is `mixed`. That is the whole test, and nothing here
reads English.

`claim` and `direction` are required. `by` and `model` are optional and say who put the
support there. A model proposes a support while it reads; a person confirms or corrects
it. `integrate.py` flags a conflict whose two sides both rest on a model-proposed
support, and it never refuses on that alone, because the model proposes and the author
decides.

The dimensions they differ on come from the conditions already on each row, read by
`dimensions.read_condition` and compared through `dimensions.normalise`, so `Clean air`
and `clean-air` are one value rather than two.

**This comparison is the whole reason a dimension carries a definition.** Two rows are
compared because they share a NAME, and nothing here reads what the name means. So one
name over two meanings, `method` for a research method on one row and a manufacturing
method on the other, produces a conflict record for a disagreement that does not exist.
That reading reaches `integrate.py`, which refuses the delivery, and a wrong refusal is
how a gate gets bypassed. `dimensions.register` requires a definition at mint for exactly
this reason, and a sidecar may carry `dimensions[]` so a receiver can read the definitions
rather than guess at them.

Two opposed rows that name **no dimension in common** raise nothing: they disagree, but no dimension is named by both, so there is
nothing yet to say where each is right. `explain()` returns that reason, so the silence is
reported rather than assumed.

A SIDE MAY BE A CLAIM, NOT ONLY AN EVIDENCE ROW
-----------------------------------------------
Since 29 August 2026 a side of a stored conflict is either

    {"evidence": "e1", "outcome": "for"}      an evidence row, exactly as before
    {"claim": "c9"}                           a competing claim

**That is the shape an adversarial pass actually produces.** A pass does not hand you two
sources that disagree. It hands you a rival claim, and until now there was nowhere to put
it, so the rival was flattened into a sentence in `replaced_by` and lost its evidence, its
conditions and its level on the way. A competing claim now lands in `claims[]` like any
other claim, the conflict points at it, and `replaced_by` may name it. The conditions of
the two claims then say where each of them is right, which is the whole point.

A claim side carries no `outcome`. An evidence row votes on a claim; a rival claim does
not vote, it stands against it. The differing dimensions of a claim side are read off its
`holds_when` and `fails_when` rather than off an evidence row's `conditions`, and one
function reads both, because a claim never carries `conditions` and an evidence row never
carries `holds_when`.

`detect()` is UNCHANGED and still reads evidence rows only. A claim-versus-claim conflict
is written by whoever ran the pass; nothing here infers one.

THIS FILE NEVER JUDGES WHICH SIDE IS RIGHT
------------------------------------------
No scoring, no ranking, no winner. The tool finds and records; the author resolves. A
`resolved` conflict must name the claim whose boundary record now holds it, because a
conflict that resolves into nothing is a conflict resolved quietly, which is the move this
file exists to stop.

ponytail: opposition is read off the `supports` field and never inferred from the quote
text. The model-assisted half of the ceiling is now filled: `reference/research-mode.md`
asks the model to propose a `supports` while it captures, marked `by: "model"`, and the
report below says what proportion of a file nobody has confirmed. The remaining ceiling is
that a file with no `supports` at all still yields no conflicts. The upgrade path stays a
proposal a person accepts, never a regex over the quotes; a regex that guesses opposition
would put words in a source's mouth, which is worse than silence.
"""
import json
import pathlib
import sys

import boundary
import dimensions

# Which way an evidence row points at the claim it names. Two rows pointing different ways
# at one claim is a disagreement, and it is the only thing that counts as one here.
#
# `mixed` is a source that supports the claim in one region and undermines it in another,
# and it arrived on 29 August 2026 because it is the most interesting kind of source this
# framework has and there was nowhere to put it. **A `mixed` row never raises a conflict
# on its own.** A source that cuts both ways is already telling you where the boundary is,
# so it does not need another source to disagree with. What it raises instead is a
# boundary prompt, a soft flag in `integrate.py` asking whether the boundary was written
# down, and that flag goes silent once the claim carries a boundary record.
MIXED = "mixed"
DIRECTIONS = ("for", "against", MIXED)

# The two directions a SIDE of a conflict may take. A mixed source is a boundary, not a
# side, so it may not be named by one.
SIDE_DIRECTIONS = ("for", "against")

# A conflict is open or it is resolved. There is no third state, because every third state
# anybody proposes ("noted", "acknowledged") is a way of closing one without a boundary.
STATES = ("open", "resolved")

# Who put a `supports` on the row. A model proposes, a person decides.
AUTHOR, MODEL = "author", "model"
SUPPORT_BY = (AUTHOR, MODEL)

REQUIRED = ("id", "claim", "between", "dimensions", "state")

# The integration moves, from docs/philosophy.md position 8. A RESOLVED conflict names the
# move that resolved it, so a reader can tell a boundary from a verdict wearing one.
# `hold` is absent on purpose: holding IS `state: "open"` with the unknown region named,
# so recording it as a resolution would let an unresolved tension read as a resolved one.
MOVES = ("conditional", "reframe", "redirect", "compromise")
# Two moves cannot be checked by shape alone, so each must say the thing that makes it
# honest. Reframe names the assumption both sides shared, because "a higher-order synthesis
# dissolves the tension" is a sentence anyone can write about anything. Compromise says why
# the other three failed, because the midpoint of two evidenced positions usually has no
# evidence at all: it is the last resort, never the default.
MOVES_NEEDING_NOTE = ("reframe", "compromise")

NO_SHARED_DIMENSION = ("they disagree, but no dimension is named by both, so there is "
                       "nothing yet to say where each is right")
SAME_VALUES = ("they disagree, but every dimension both name carries the same value, so "
               "there is nothing yet to say where each is right")


def supports_of(row):
    """(claim, direction) from an evidence row, or None when it names no claim.

    Raises ValueError on a `supports` that is present and malformed, because a support
    nobody can read is worse than one that is absent: it looks like the author did the
    work.
    """
    sup = row.get("supports")
    if sup is None:
        return None
    if not isinstance(sup, dict):
        raise ValueError(f"supports must be an object, not {sup!r}")
    claim = sup.get("claim")
    if not isinstance(claim, str) or not claim.strip():
        raise ValueError(f"supports is missing a `claim`: {sup!r}")
    direction = sup.get("direction")
    if direction not in DIRECTIONS:
        raise ValueError(
            f"supports for {claim!r} has direction {direction!r}, not one of {list(DIRECTIONS)}")
    return claim.strip(), direction


def support_provenance(row):
    """(by, model) for an evidence row's `supports`, or None when it carries none.

    An absent `by` reads as "author". Every `supports` written before this field existed
    was typed by a person, so a silent default of "model" would retro-label their work as
    a machine's proposal.

    Raises ValueError on a `by` outside the two words, and on a `model` sitting beside
    `by: "author"`, because a person did not run a model to hold an opinion.
    """
    sup = row.get("supports")
    if not isinstance(sup, dict):
        return None
    by = sup.get("by", AUTHOR)
    if by not in SUPPORT_BY:
        raise ValueError(f"supports has by {by!r}, not one of {list(SUPPORT_BY)}")
    model = sup.get("model")
    if model is not None:
        if by != MODEL:
            raise ValueError("supports names a `model` with by 'author', and a person "
                             "did not run a model to hold an opinion")
        if not isinstance(model, str) or not model.strip():
            raise ValueError(f"supports has model {model!r}, which names no model")
        model = model.strip()
    return by, model


# Where a record keeps its conditions. An evidence row keeps them in `conditions`; a claim
# keeps them in `holds_when` and `fails_when`. No record carries both, so one list reads
# either and there is no branch and no second parser.
CONDITION_FIELDS = ("conditions", "holds_when", "fails_when")


def _conditions_of(record):
    """Every condition entry on a record, whichever field it keeps them in."""
    return [entry for field in CONDITION_FIELDS for entry in (record.get(field) or [])]


def _dimensions_of(row):
    """{normalised dimension: (spelling, normalised value)} for one record.

    Reads an evidence row's `conditions` and a claim's `holds_when` and `fails_when`, so
    a conflict between two claims finds its differing dimensions the same way a conflict
    between two evidence rows does.

    Dimension-less conditions are skipped: the old `{condition, basis}` shape names
    nothing two records can be compared on.

    ponytail: a record naming one dimension twice keeps the first spelling and the first
    value, and the later ones are skipped rather than refused. On a claim that means
    `holds_when` wins over `fails_when`, which is the region the claim is asserted in.
    Ceiling is a record that genuinely holds two values on one dimension, which is a
    record that should have been two; revisit if that ever shows up in real evidence.
    """
    out = {}
    for entry in _conditions_of(row):
        dimension, value, _ = dimensions.read_condition(entry)
        if dimension is None:
            continue
        out.setdefault(dimensions.normalise(dimension),
                       (dimension, dimensions.normalise(value)))
    return out


def differing_dimensions(a, b):
    """The dimensions both records name where the values differ, in the first's order.

    `a` and `b` are each an evidence row or a claim. See `_dimensions_of`.
    """
    da, db = _dimensions_of(a), _dimensions_of(b)
    return [da[key][0] for key in da if key in db and da[key][1] != db[key][1]]


def side_of(side):
    """("evidence"|"claim", id) for one side of a stored conflict.

    Raises ValueError on a side that names neither, names both, or hangs an `outcome` on
    a claim. An evidence row votes on a claim and its vote is the outcome; a rival claim
    does not vote, so an outcome on it is a category error and reading past it would let
    the record say something nobody meant.
    """
    if not isinstance(side, dict):
        raise ValueError(f"each side of between must be an object, not {side!r}")
    eid, cid = side.get("evidence"), side.get("claim")
    if (eid is None) == (cid is None):
        raise ValueError(
            f"a side names one evidence row or one claim, not neither and not both: {side!r}")
    if cid is not None:
        if not isinstance(cid, str) or not cid.strip():
            raise ValueError(f"a claim side names no claim: {side!r}")
        if "outcome" in side:
            raise ValueError(
                f"claim side {cid!r} carries an outcome, and a rival claim does not vote "
                f"on the claim it stands against")
        return "claim", cid.strip()
    if not isinstance(eid, str) or not eid.strip():
        raise ValueError(f"an evidence side names no evidence row: {side!r}")
    return "evidence", eid.strip()


def side_record(data, side):
    """The evidence row or claim one side names, or None when it is not in the sidecar."""
    kind, sid = side_of(side)
    key = "evidence" if kind == "evidence" else "claims"
    for row in data.get(key) or []:
        if isinstance(row, dict) and row.get("id") == sid:
            return row
    return None


def opposed_pairs(data):
    """[(row, row)] for every pair of evidence rows naming one claim in different
    directions, in document order so the answer is the same on every run.

    A row whose direction is `mixed` is ignored on both sides, so it never raises a
    conflict. `integrate.py` raises a boundary prompt for it instead.
    """
    rows = []
    for row in data.get("evidence") or []:
        if not isinstance(row, dict):
            continue
        sup = supports_of(row)
        # A `mixed` row is skipped on both sides. It disagrees with itself, which is a
        # boundary the author writes down, not a disagreement between two sources.
        if sup and sup[1] != MIXED:
            rows.append((row, sup))
    out = []
    for i, (a, sa) in enumerate(rows):
        for b, sb in rows[i + 1:]:
            if sa[0] == sb[0] and sa[1] != sb[1]:
                out.append((a, b))
    return out


def detect(data):
    """Proposed conflict records, one per opposed pair that differs on a shared dimension.

    Each comes back `open` with an id of `x1`, `x2` and no `unknown_region`: the author
    writes that, and `validate_conflicts` refuses an open conflict without one. So the
    output of this function is a proposal to store, not a record that already validates.
    """
    taken = {c.get("id") for c in (data.get("conflicts") or []) if isinstance(c, dict)}
    out, n = [], 0

    def _next_id():
        nonlocal n
        while True:
            n += 1
            if f"x{n}" not in taken:
                return f"x{n}"

    for a, b in opposed_pairs(data):
        dims = differing_dimensions(a, b)
        if not dims:
            continue
        out.append({
            "id": _next_id(),
            "claim": supports_of(a)[0],
            "between": [{"evidence": a.get("id"), "outcome": supports_of(a)[1]},
                        {"evidence": b.get("id"), "outcome": supports_of(b)[1]}],
            "dimensions": dims,
            "state": "open",
        })
    return out


def explain(data):
    """[(id, id, reason)] for every opposed pair that raised nothing, and why.

    This is the half that keeps the silence honest. Two sources that disagree and share no
    dimension are still a disagreement; what is missing is anywhere to put it.
    """
    out = []
    for a, b in opposed_pairs(data):
        if differing_dimensions(a, b):
            continue
        shared = set(_dimensions_of(a)) & set(_dimensions_of(b))
        out.append((a.get("id"), b.get("id"), SAME_VALUES if shared else NO_SHARED_DIMENSION))
    return out


def validate_conflicts(data):
    """Shape check on `conflicts[]`. Raises AssertionError naming the offending conflict.

    `conflicts` is OPTIONAL, so a sidecar without it validates unchanged. The `supports`
    field on an evidence row is checked either way, because a malformed one silently
    removes that row from every conflict this file could have found.
    """
    for i, row in enumerate(data.get("evidence") or []):
        if not isinstance(row, dict):
            continue
        try:
            supports_of(row)
            support_provenance(row)
        except ValueError as e:
            raise AssertionError(f"evidence[{row.get('id') or i}]: {e}") from None
    if "conflicts" not in data:
        return True
    records = data["conflicts"]
    assert isinstance(records, list), "conflicts[] must be an array"
    claims = {c.get("id"): c for c in (data.get("claims") or []) if isinstance(c, dict)}
    evidence = {e.get("id"): e for e in (data.get("evidence") or []) if isinstance(e, dict)}
    seen = set()
    for i, rec in enumerate(records):
        here = f"conflicts[{rec.get('id') if isinstance(rec, dict) else i}]"
        assert isinstance(rec, dict), f"conflicts[{i}] must be an object"
        for key in REQUIRED:
            assert key in rec, f"{here} is missing {key!r}"
        assert rec["id"] not in seen, f"{here}: id {rec['id']!r} is used twice"
        seen.add(rec["id"])
        assert rec["claim"] in claims, (
            f"{here}: claim {rec['claim']!r} is not a claim in this sidecar")
        between = rec["between"]
        assert isinstance(between, list) and len(between) == 2, (
            f"{here}: between must name exactly two sides, not {len(between) if isinstance(between, list) else between!r}")
        outcomes, sides = [], []
        for side in between:
            try:
                kind, sid = side_of(side)
            except ValueError as e:
                raise AssertionError(f"{here}: {e}") from None
            sides.append((kind, sid))
            if kind == "claim":
                # A competing claim, which is what an adversarial pass actually produces.
                assert sid in claims, (
                    f"{here}: {sid!r} is not a claim in this sidecar, so this conflict "
                    f"stands against nothing")
                assert sid != rec["claim"], (
                    f"{here}: claim {sid!r} cannot be a rival to itself")
                continue
            assert sid in evidence, (
                f"{here}: {sid!r} is not an evidence id in this sidecar")
            assert side.get("outcome") in SIDE_DIRECTIONS, (
                f"{here}: outcome {side.get('outcome')!r} is not one of "
                f"{list(SIDE_DIRECTIONS)}; a mixed source is a boundary and not a side")
            # The outcome is a readback of the row, never a second opinion about it.
            # A conflict written by hand with the sides swapped would otherwise pass,
            # and every reader after it would have the disagreement backwards.
            row = evidence[sid]
            sup = supports_of(row)
            assert sup, (
                f"{here}: evidence row {sid!r} carries no `supports`, so it "
                f"cannot be a side of a conflict")
            assert sup[1] != MIXED, (
                f"{here}: evidence row {sid!r} is recorded {MIXED!r} on that "
                f"claim, and a mixed source is a boundary and not a side")
            assert sup[0] == rec["claim"], (
                f"{here}: evidence row {sid!r} supports claim {sup[0]!r}, "
                f"not {rec['claim']!r}")
            assert sup[1] == side["outcome"], (
                f"{here}: evidence row {sid!r} is recorded {sup[1]!r} on that "
                f"claim, but this conflict says {side['outcome']!r}")
            outcomes.append(side["outcome"])
        assert sides[0] != sides[1], f"{here}: a side cannot disagree with itself"
        # Two evidence rows must point different ways. Two claims, or a claim against a
        # row, are different things standing against each other, so there is no pair of
        # outcomes to compare and nothing to check here.
        if len(outcomes) == 2:
            assert outcomes[0] != outcomes[1], (
                f"{here}: both sides are recorded {outcomes[0]!r} on the claim, which is "
                f"not a disagreement")
        dims = rec["dimensions"]
        assert isinstance(dims, list) and dims and all(
            isinstance(d, str) and d.strip() for d in dims), (
            f"{here}: dimensions must name at least one dimension the two sides differ on")
        assert rec["state"] in STATES, (
            f"{here}: state {rec['state']!r} is not one of {list(STATES)}")
        if rec["state"] == "resolved":
            target = rec.get("resolved_into")
            assert isinstance(target, str) and target in claims, (
                f"{here}: a resolved conflict must name the claim it resolved into, and "
                f"{target!r} is not a claim in this sidecar")
            assert boundary.has_boundary(claims[target]), (
                f"{here}: claim {target!r} carries no boundary record, so this conflict "
                f"resolved into nothing")
            move = rec.get("move")
            assert move in MOVES, (
                f"{here}: a resolved conflict names the move that resolved it, and "
                f"{move!r} is not one of {list(MOVES)}. Holding is not a resolution: "
                f"leave the conflict open with its unknown region named")
            if move in MOVES_NEEDING_NOTE:
                note = rec.get("move_note")
                assert isinstance(note, str) and note.strip(), (
                    f"{here}: move {move!r} requires `move_note` — "
                    + ("the assumption both sides shared, which dropping removed"
                       if move == "reframe"
                       else "why conditional, reframe and redirect each failed"))
        else:
            assert "move" not in rec, (
                f"{here}: an open conflict carries no move. Holding is what an open "
                f"conflict already is, so naming a move here would read as resolved")
            assert "resolved_into" not in rec, (
                f"{here}: an open conflict cannot already name what it resolved into")
            assert isinstance(rec.get("unknown_region"), str) and rec["unknown_region"].strip(), (
                f"{here}: an open conflict ships only with its unknown region named")
    return True


def open_conflicts(data):
    """The conflicts still open, in document order."""
    return [c for c in (data.get("conflicts") or [])
            if isinstance(c, dict) and c.get("state") == "open"]


def _label(data, evidence_id):
    """How a reader recognises the source: its id, and its locator or url when it has one."""
    for row in data.get("evidence") or []:
        if isinstance(row, dict) and row.get("id") == evidence_id:
            where = (row.get("locator") or row.get("url") or "").strip()
            return f"{evidence_id} ({where})" if where else str(evidence_id)
    return str(evidence_id)


def side_label(data, side):
    """How a reader recognises one side: a source with its locator, or a rival claim.

    A malformed side is printed as it stands rather than raising, because this is the
    reporting half and `validate_conflicts` is the refusing half.
    """
    try:
        kind, sid = side_of(side)
    except ValueError:
        return str(side)
    if kind == "evidence":
        return _label(data, sid)
    record = side_record(data, side) or {}
    statement = (record.get("statement") or "").strip()
    return f"claim {sid} ({statement})" if statement else f"claim {sid}"


def disclosure_lines(data):
    """One sentence per open conflict, ready for the Limitations line of the block.

    This is a limit on the EVIDENCE, which is what Limitations carries. It says who
    disagrees, about what, on which dimensions, and what is still unmapped, and it says
    nothing about our own thinking.
    """
    out = []
    for rec in open_conflicts(data):
        sides = rec.get("between") or []
        who = " and ".join(side_label(data, s) for s in sides)
        dims = ", ".join(rec.get("dimensions") or [])
        out.append(f"On {rec.get('claim')}, {who} disagree, and they differ on {dims}; "
                   f"the region nobody has mapped is {rec.get('unknown_region', '').rstrip('.')}.")
    return out


def support_census(data):
    """(author-set count, model-proposed count, [model names]) across the evidence rows.

    A file whose every support is model-proposed has a conflict layer nobody has read, so
    the proportion is worth printing rather than assuming.
    """
    author = model = 0
    names = []
    for row in data.get("evidence") or []:
        if not isinstance(row, dict):
            continue
        prov = support_provenance(row)
        if prov is None or supports_of(row) is None:
            continue
        by, name = prov
        if by == MODEL:
            model += 1
            if name and name not in names:
                names.append(name)
        else:
            author += 1
    return author, model, names


def _report(path):
    data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    found = detect(data)
    print(f"{path}: {len(found)} conflict(s) detected from the evidence")
    for rec in found:
        sides = " vs ".join(f"{s['evidence']} {s['outcome']}" for s in rec["between"])
        print(f"  {rec['id']}  {rec['claim']}: {sides}   differ on "
              f"{', '.join(rec['dimensions'])}")
    for a, b, reason in explain(data):
        print(f"  no conflict  {a} and {b}: {reason}")
    stored = [c for c in (data.get("conflicts") or []) if isinstance(c, dict)]
    for rec in stored:
        who = " vs ".join(side_label(data, s) for s in rec.get("between") or [])
        print(f"  {rec.get('id')}  recorded on {rec.get('claim')} [{rec.get('state')}]: {who}")
    still_open = open_conflicts(data)
    print(f"  {len(still_open)} conflict(s) recorded and still open")
    for line in disclosure_lines(data):
        print(f"    {line}")
    author, proposed, names = support_census(data)
    who = f" ({', '.join(names)})" if names else ""
    print(f"  supports: {author} author-set, {proposed} model-proposed{who}")
    if proposed and not author:
        print("    every support in this file is model-proposed, so no person has "
              "confirmed any of them")
    return 0


def _self_check():
    """Twelve cases with known answers, no network. The threshold is all twelve: this file
    decides whether a disagreement between two sources reaches the reader at all, and a
    conflict it fails to open is one the author resolves without deciding to."""

    def ev(eid, claim, direction, *conditions):
        return {"id": eid, "quote": "…", "locator": f"p. {eid[1:]}",
                "supports": {"claim": claim, "direction": direction},
                "conditions": list(conditions)}

    def cond(dimension, value, basis="observed"):
        return {"dimension": dimension, "value": value, "basis": basis}

    clean = ev("e1", "c1", "for", cond("air quality", "clean"))
    dirty = ev("e2", "c1", "against", cond("Air-Quality", "hazy"))
    base = {"claims": [{"id": "c1", "statement": "The sky is blue."}],
            "evidence": [clean, dirty]}

    def case_detect():
        found = detect(base)
        assert len(found) == 1, found
        rec = found[0]
        assert rec == {"id": "x1", "claim": "c1",
                       "between": [{"evidence": "e1", "outcome": "for"},
                                   {"evidence": "e2", "outcome": "against"}],
                       "dimensions": ["air quality"], "state": "open"}, rec
        # Two rows pointing the same way are not a disagreement, whatever else differs.
        agree = {"claims": base["claims"],
                 "evidence": [clean, ev("e3", "c1", "for", cond("air quality", "hazy"))]}
        assert detect(agree) == [], detect(agree)
        # Nor are two rows about different claims.
        apart = {"claims": base["claims"],
                 "evidence": [clean, ev("e4", "c2", "against", cond("air quality", "hazy"))]}
        assert detect(apart) == [] and explain(apart) == []

    def case_no_shared_dimension():
        far = {"claims": base["claims"],
               "evidence": [clean, ev("e5", "c1", "against", cond("sun angle", "low"))]}
        assert detect(far) == [], detect(far)
        assert explain(far) == [("e1", "e5", NO_SHARED_DIMENSION)], explain(far)
        # A shared dimension carrying the same value is a different silence, said so.
        same = {"claims": base["claims"],
                "evidence": [clean, ev("e6", "c1", "against", cond("air-quality", "Clean"))]}
        assert detect(same) == [], detect(same)
        assert explain(same) == [("e1", "e6", SAME_VALUES)], explain(same)
        # A dimension-less condition names nothing to compare on.
        old = {"claims": base["claims"],
               "evidence": [{"id": "e7", "supports": {"claim": "c1", "direction": "for"},
                             "conditions": [{"condition": "clean air", "basis": "observed"}]},
                            dirty]}
        assert detect(old) == [] and explain(old)[0][2] == NO_SHARED_DIMENSION

    def case_normalised():
        # `Air-Quality` and `air quality` are one dimension, `Clean` and `clean` one value.
        assert differing_dimensions(clean, dirty) == ["air quality"]
        twin = ev("e8", "c1", "against", cond("air qualities", "clean"))
        assert differing_dimensions(clean, twin) == [], "one value spelt two ways is one value"

    def case_overload_is_a_false_conflict():
        # One name over two meanings is compared as if it were one dimension, and a
        # disagreement that does not exist is recorded. Nothing here can see it, because
        # nothing here reads what a name means. This case exists to pin the failure down:
        # the fix is the definition on the registry row, not a change to this file.
        research = ev("e9", "c1", "for", cond("method", "randomised trial"))
        factory = ev("e10", "c1", "against", cond("method", "injection moulding"))
        assert differing_dimensions(research, factory) == ["method"], \
            "the comparison is by name alone, so an overload reads as a disagreement"
        raised = detect(dict(base, evidence=[research, factory]))
        assert len(raised) == 1 and raised[0]["dimensions"] == ["method"]
        # And the same two rows under two DEFINED names raise nothing, which is what a
        # definition buys: it is the thing that stops the author reusing the name.
        renamed = ev("e10", "c1", "against", cond("moulding method", "injection moulding"))
        assert differing_dimensions(research, renamed) == []
        assert detect(dict(base, evidence=[research, renamed])) == []

    def case_states():
        data = dict(base, conflicts=[dict(detect(base)[0],
                                          unknown_region="nobody has looked at dusk.")])
        assert validate_conflicts(data)
        assert [c["id"] for c in open_conflicts(data)] == ["x1"]
        for state in ("noted", "closed", "resolving", "", None, 1):
            bad = dict(base, conflicts=[dict(data["conflicts"][0], state=state)])
            try:
                validate_conflicts(bad)
            except AssertionError as e:
                assert "state" in str(e), e
                continue
            raise AssertionError(f"state {state!r} must be refused")

    def case_resolution():
        held = {"id": "c2", "statement": "The sky is blue in clean air.",
                "holds_when": [cond("air quality", "clean", "tested")],
                "unknown_region": "dusk, and every latitude above 60 degrees."}
        naked = {"id": "c3", "statement": "Something with no boundary record."}
        rec = dict(detect(base)[0], state="resolved", resolved_into="c2",
                   move="conditional")
        data = {"claims": base["claims"] + [held, naked], "evidence": base["evidence"],
                "conflicts": [rec]}
        assert validate_conflicts(data)
        assert open_conflicts(data) == [], "a resolved conflict is not open"
        for target, word in ((None, "resolved into"), ("c9", "resolved into"),
                             ("c3", "boundary")):
            bad = dict(data, conflicts=[dict(rec, resolved_into=target)
                                        if target else {k: v for k, v in rec.items()
                                                        if k != "resolved_into"}])
            try:
                validate_conflicts(bad)
            except AssertionError as e:
                assert word in str(e), e
                continue
            raise AssertionError(f"resolving into {target!r} must be refused")
        # An open conflict with no unknown region is the same failure from the other side.
        try:
            validate_conflicts(dict(base, conflicts=[detect(base)[0]]))
        except AssertionError as e:
            assert "unknown region" in str(e), e
            return
        raise AssertionError("an open conflict with no unknown region must be refused")

    def case_moves():
        """The move is how a reader tells a boundary from a verdict wearing one.

        Four rules, and each exists because of a way the letter was got wrong in practice:
        a resolution with no move, holding recorded as a resolution, a reframe that names
        no assumption, and a compromise reached without trying anything else first.
        """
        held = {"id": "c2", "statement": "The sky is blue in clean air.",
                "holds_when": [cond("air quality", "clean", "tested")],
                "unknown_region": "dusk, and every latitude above 60 degrees."}
        base_data = {"claims": base["claims"] + [held], "evidence": base["evidence"]}
        rec = dict(detect(base)[0], state="resolved", resolved_into="c2")

        # every listed move is accepted, with a note where the move needs one
        for move in MOVES:
            row = dict(rec, move=move)
            if move in MOVES_NEEDING_NOTE:
                row["move_note"] = "Both sides assumed the reading was taken outdoors."
            assert validate_conflicts(dict(base_data, conflicts=[row])), move

        # a resolution with no move, and a move that is not one of the four
        for bad_move, word in ((None, "names the move"), ("hold", "Holding is not"),
                               ("transcend", "names the move")):
            row = dict(rec)
            if bad_move is not None:
                row["move"] = bad_move
            try:
                validate_conflicts(dict(base_data, conflicts=[row]))
            except AssertionError as e:
                assert word in str(e), e
                continue
            raise AssertionError(f"move {bad_move!r} must be refused")

        # reframe and compromise each have to say the thing that makes them honest
        for move in MOVES_NEEDING_NOTE:
            for note in (None, "   "):
                row = dict(rec, move=move)
                if note is not None:
                    row["move_note"] = note
                try:
                    validate_conflicts(dict(base_data, conflicts=[row]))
                except AssertionError as e:
                    assert "move_note" in str(e), e
                    continue
                raise AssertionError(f"{move} without a note must be refused")

        # holding is state open, so an open conflict carries no move at all
        open_rec = dict(detect(base)[0], state="open",
                        unknown_region="every reading taken indoors")
        assert validate_conflicts(dict(base_data, conflicts=[open_rec]))
        try:
            validate_conflicts(dict(base_data,
                                    conflicts=[dict(open_rec, move="conditional")]))
        except AssertionError as e:
            assert "open conflict carries no move" in str(e), e
        else:
            raise AssertionError("a move on an open conflict must be refused")

    def case_refusals():
        good = dict(detect(base)[0], unknown_region="nobody has looked at dusk.")
        bad = [
            (dict(good, claim="c9"), "claim"),
            (dict(good, between=[good["between"][0]]), "exactly two"),
            (dict(good, between=[{"evidence": "e1", "outcome": "for"},
                                 {"evidence": "e9", "outcome": "against"}]), "e9"),
            (dict(good, between=[{"evidence": "e1", "outcome": "for"},
                                 {"evidence": "e2", "outcome": "maybe"}]), "outcome"),
            (dict(good, between=[{"evidence": "e1", "outcome": "for"},
                                 {"evidence": "e2", "outcome": "for"}]), "recorded"),
            (dict(good, dimensions=[]), "dimensions"),
            (dict(good, dimensions="air quality"), "dimensions"),
            ({k: v for k, v in good.items() if k != "id"}, "id"),
        ]
        for rec, word in bad:
            try:
                validate_conflicts(dict(base, conflicts=[rec]))
            except AssertionError as e:
                assert word in str(e), f"the message must name {word}: {e}"
                continue
            raise AssertionError(f"{rec!r} must be refused")
        # A conflict whose sides say the opposite of what the rows themselves record is
        # refused, because a hand-written record is a readback, never a second opinion.
        agreeing = dict(base, evidence=[dict(row, supports={"claim": "c1", "direction": "for"})
                                        if row.get("id") == "e2" else row
                                        for row in base["evidence"]])
        try:
            validate_conflicts(dict(agreeing, conflicts=[
                dict(good, between=[{"evidence": "e1", "outcome": "for"},
                                    {"evidence": "e2", "outcome": "for"}])]))
        except AssertionError as e:
            assert "not a disagreement" in str(e), e
        else:
            raise AssertionError("two rows pointing the same way must be refused")
        # Two conflicts under one id, and a malformed `supports`, are refused as well.
        try:
            validate_conflicts(dict(base, conflicts=[good, dict(good)]))
        except AssertionError as e:
            assert "twice" in str(e), e
        for sup in ({"claim": "c1"}, {"claim": "c1", "direction": "maybe"},
                    {"direction": "for"}, "c1"):
            try:
                validate_conflicts({"claims": base["claims"],
                                    "evidence": [dict(clean, supports=sup)]})
            except AssertionError as e:
                assert "supports" in str(e), e
                continue
            raise AssertionError(f"supports {sup!r} must be refused")

    def case_who_set_the_support():
        # Absent `by` reads as author, because every support written before the field
        # existed was typed by a person.
        assert support_provenance(clean) == ("author", None)
        assert support_provenance({}) is None
        by_author = dict(clean, supports={"claim": "c1", "direction": "for", "by": "author"})
        assert support_provenance(by_author) == ("author", None)
        by_model = dict(dirty, supports={"claim": "c1", "direction": "against",
                                         "by": "model", "model": "claude-opus-5"})
        assert support_provenance(by_model) == ("model", "claude-opus-5")
        # `supports_of` still answers exactly what it answered before.
        assert supports_of(by_model) == ("c1", "against")
        mixed = {"claims": base["claims"], "evidence": [clean, by_model]}
        assert validate_conflicts(mixed)
        assert support_census(mixed) == (1, 1, ["claude-opus-5"])
        assert support_census(base) == (2, 0, [])
        assert support_census({"evidence": [{"id": "e0"}]}) == (0, 0, [])
        bad = [({"claim": "c1", "direction": "for", "by": "the intern"}, "by"),
               ({"claim": "c1", "direction": "for", "by": "author",
                 "model": "claude-opus-5"}, "model"),
               ({"claim": "c1", "direction": "for", "model": "claude-opus-5"}, "model"),
               ({"claim": "c1", "direction": "for", "by": "model", "model": ""}, "model")]
        for sup, word in bad:
            try:
                validate_conflicts({"claims": base["claims"],
                                    "evidence": [dict(clean, supports=sup)]})
            except AssertionError as e:
                assert word in str(e), e
                continue
            raise AssertionError(f"supports {sup!r} must be refused")

    def case_optional_and_disclosed():
        # A 1.2 sidecar has no conflicts[] and no supports, and validates untouched.
        old = {"claims": [{"id": "c1", "statement": "…"}], "evidence": [{"id": "e1"}]}
        assert validate_conflicts(old)
        assert detect(old) == [] and explain(old) == [] and disclosure_lines(old) == []
        data = dict(base, conflicts=[dict(detect(base)[0],
                                          unknown_region="dusk, and the horizon")])
        lines = disclosure_lines(data)
        assert len(lines) == 1, lines
        line = lines[0]
        for part in ("e1", "e2", "c1", "air quality", "dusk", "disagree"):
            assert part in line, f"the disclosure must name {part}: {line}"
        # It is a limit on the evidence, not a statement about our own thinking, so it
        # belongs in Limitations as written.
        assert "framework" not in line and "our own" not in line, line

    def case_claim_against_claim():
        # What an adversarial pass actually produces: not two sources, a rival claim.
        rival = {"id": "c9", "statement": "The sky reads grey under haze.",
                 "kind": "empirical", "evidence": ["e2"],
                 "holds_when": [cond("air quality", "hazy", "stated-in-source")],
                 "unknown_region": "dusk under haze."}
        held = {"id": "c1", "statement": "The sky is blue.",
                "holds_when": [cond("Air-Quality", "clean", "tested")],
                "fails_when": [cond("sun angle", "near the horizon", "tested")],
                "replaced_by": {"claim": "c9"},
                "unknown_region": "dusk, and every latitude above 60 degrees."}
        rec = {"id": "x1", "claim": "c1",
               "between": [{"evidence": "e1", "outcome": "for"}, {"claim": "c9"}],
               "dimensions": ["air quality"], "state": "resolved", "resolved_into": "c1",
               "move": "conditional"}
        data = {"claims": [held, rival], "evidence": [clean, dirty], "conflicts": [rec]}
        assert validate_conflicts(data), "a conflict naming a claim as a side must validate"
        # The differing dimensions come off the two claims' own conditions.
        assert differing_dimensions(held, rival) == ["Air-Quality"], \
            differing_dimensions(held, rival)
        assert side_of({"claim": "c9"}) == ("claim", "c9")
        assert side_of({"evidence": "e1", "outcome": "for"}) == ("evidence", "e1")
        assert side_record(data, {"claim": "c9"}) is rival
        assert side_record(data, {"evidence": "e1", "outcome": "for"}) is clean
        assert side_record(data, {"claim": "c404"}) is None
        # Claim against claim on both sides is a conflict too.
        pair = dict(rec, between=[{"claim": "c9"}, {"claim": "c10"}])
        other = {"id": "c10", "statement": "The sky reads white under haze.",
                 "holds_when": [cond("air quality", "very hazy", "human")],
                 "unknown_region": "everything else."}
        assert validate_conflicts({"claims": [held, rival, other],
                                   "evidence": [clean, dirty], "conflicts": [pair]})
        # The reader can tell which side is which.
        opened = {k: v for k, v in rec.items() if k != "resolved_into"}
        opened = dict(opened, state="open", unknown_region="dusk under haze.")
        line = disclosure_lines(dict(data, conflicts=[opened]))[0]
        for part in ("e1", "claim c9", "grey under haze", "air quality"):
            assert part in line, f"the disclosure must name {part}: {line}"
        bad = [
            (dict(rec, between=[{"evidence": "e1", "outcome": "for"},
                                {"claim": "c404"}]), "not a claim"),
            (dict(rec, between=[{"evidence": "e1", "outcome": "for"},
                                {"claim": "c1"}]), "rival to itself"),
            (dict(rec, between=[{"evidence": "e1", "outcome": "for"},
                                {"claim": "c9", "outcome": "against"}]), "does not vote"),
            (dict(rec, between=[{"evidence": "e1", "outcome": "for"},
                                {"evidence": "e2", "claim": "c9"}]), "not both"),
            (dict(rec, between=[{"evidence": "e1", "outcome": "for"}, {}]), "not both"),
            (dict(rec, between=[{"claim": "c9"}, {"claim": "c9"}]), "itself"),
            (dict(rec, between=[{"evidence": "e1", "outcome": "for"},
                                {"claim": " "}]), "names no claim"),
        ]
        for record, word in bad:
            try:
                validate_conflicts(dict(data, conflicts=[record]))
            except AssertionError as e:
                assert word in str(e), f"the message must name {word!r}: {e}"
                continue
            raise AssertionError(f"{record['between']!r} must be refused")
        # detect() is unchanged: nothing infers a rival claim, somebody writes one.
        assert detect(base)[0]["between"] == [{"evidence": "e1", "outcome": "for"},
                                              {"evidence": "e2", "outcome": "against"}]

    def case_the_evidence_row_form_is_unchanged():
        # Every assertion the old shape carried, still exactly as it was.
        good = dict(detect(base)[0], unknown_region="nobody has looked at dusk.")
        assert validate_conflicts(dict(base, conflicts=[good]))
        assert good["between"] == [{"evidence": "e1", "outcome": "for"},
                                   {"evidence": "e2", "outcome": "against"}]
        assert _dimensions_of(clean) == {"air quality": ("air quality", "clean")}
        assert differing_dimensions(clean, dirty) == ["air quality"]
        for record, word in ((dict(good, between=[good["between"][0]]), "exactly two"),
                             (dict(good, between=[{"evidence": "e1", "outcome": "for"},
                                                  {"evidence": "e1", "outcome": "for"}]),
                              "itself")):
            try:
                validate_conflicts(dict(base, conflicts=[record]))
            except AssertionError as e:
                assert word in str(e), e
                continue
            raise AssertionError(f"{record!r} must be refused")

    def case_mixed_is_a_boundary_not_a_side():
        # A source that cuts both ways raises no conflict, against either direction.
        both = ev("e9", "c1", "mixed", cond("air quality", "hazy"))
        assert supports_of(both) == ("c1", "mixed")
        for other in (clean, dirty):
            data = {"claims": base["claims"], "evidence": [other, both]}
            assert detect(data) == [], detect(data)
            assert explain(data) == [], "a mixed row is not a silent disagreement either"
        # Nor against a second mixed row.
        two = {"claims": base["claims"],
               "evidence": [both, ev("e10", "c1", "mixed", cond("air quality", "clean"))]}
        assert detect(two) == [] and explain(two) == []
        # A file holding a mixed row still validates.
        assert validate_conflicts({"claims": base["claims"], "evidence": [both]})
        # A conflict naming a mixed row is refused, whichever way it is written.
        good = dict(detect(base)[0], unknown_region="nobody has looked at dusk.")
        data = {"claims": base["claims"], "evidence": [clean, both]}
        for side in ({"evidence": "e9", "outcome": "mixed"},
                     {"evidence": "e9", "outcome": "against"}):
            try:
                validate_conflicts(dict(data, conflicts=[
                    dict(good, between=[{"evidence": "e1", "outcome": "for"}, side])]))
            except AssertionError as e:
                assert "boundary and not a side" in str(e), e
                continue
            raise AssertionError(f"a conflict naming {side!r} must be refused")
        # and an unknown direction is still refused
        try:
            validate_conflicts({"claims": base["claims"],
                                "evidence": [dict(clean, supports={"claim": "c1",
                                                                   "direction": "sort of"})]})
        except AssertionError as e:
            assert "direction" in str(e), e
        else:
            raise AssertionError("an unknown direction must be refused")

    cases = [("opposed rows differing on a shared dimension raise one", case_detect),
             ("a mixed row raises no conflict and cannot be a side",
              case_mixed_is_a_boundary_not_a_side),
             ("no dimension in common raises nothing, and says why", case_no_shared_dimension),
             ("one dimension spelt two ways is one dimension", case_normalised),
             ("one name over two meanings is a false conflict, by name alone",
              case_overload_is_a_false_conflict),
             ("a conflict is open or resolved, and nothing else", case_states),
             ("resolved requires a claim that carries a boundary", case_resolution),
             ("a resolved conflict names its move, and reframe and compromise "
              "must say why", case_moves),
             ("a malformed conflict or support is refused", case_refusals),
             ("a support records who set it, and absent reads as author",
              case_who_set_the_support),
             ("conflicts[] is optional, and an open one is disclosed",
              case_optional_and_disclosed),
             ("a side may be a competing claim, and its dimensions come from its "
              "conditions", case_claim_against_claim),
             ("the evidence-row form of a conflict is unchanged",
              case_the_evidence_row_form_is_unchanged)]
    passed = 0
    for label, fn in cases:
        try:
            fn()
            passed += 1
            print(f"pass  {label}")
        except AssertionError as e:
            print(f"FAIL  {label}: {e}")
    total = len(cases)
    print(f"\nconflicts: self-check {'passed' if passed == total else 'FAILED'} "
          f"({passed} of {total} cases; the threshold is {total} of {total})")
    return passed == total


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or "--self-check" in args:
        sys.exit(0 if _self_check() else 1)
    sys.exit(_report(args[0]))
