#!/usr/bin/env python3
"""The boundary record, rendered: where a claim holds, where it fails, and how much
of the space nobody has looked at.

A refuted claim with no replacement is a hole, and the reader fills the hole with the
prior belief that was just refuted. So a claim that fails carries four things, and this
file turns them into the card a reader can actually see:

    holds_when[]     {dimension, value, basis, status} ...  where it survives
    fails_when[]     {dimension, value, basis, status} ...  where it does not, and why
    replaced_by      the claim that is true instead, inside the failing region. Free text,
                 or {"claim": "c9"} naming a claim in the same sidecar
    unknown_region   where neither has been tested. Usually most of it.

    python3 boundary.py --self-check       five cases, known answers, no network
    python3 boundary.py <file.sourced>     print a card per claim that carries a boundary

WHY THE STRIP IS DERIVED AND NOT STORED
---------------------------------------
A hand-set "70% unknown" is a number nobody can check and everybody rounds down. The
strip here comes from the conditions themselves: each one buys a slice of the space in
proportion to how it is known, and whatever is left over is unknown. A record of four
guesses therefore renders as almost entirely unknown, which is the honest picture, and
it moves only when somebody tests something.

ponytail: stdlib, string templates, no template engine. The card is six rows.
"""
import html
import json
import pathlib
import re
import sys

# One parser for every condition shape, and one place the vocabularies are listed.
# `dimensions.py` imports nothing from here, so there is no cycle.
import dimensions

# Rule 3, in the fields as they stand after the basis split of 29 August 2026: **a formal
# condition on the claim is one whose `status` is `confirmed`, and nothing else is.** The
# rule has not changed. `tested` and `replicated` are exactly the two old basis words that
# translate to `confirmed` (see `dimensions.LEGACY`), so a record written before the split
# is graded the same way it always was. The rest are candidates, and the chip says so at a
# glance.
FORMAL = "confirmed"

# A condition carries the answer only if somebody looked, and a refutation is somebody
# looking. Exactly two of these is the case where a two-axis map is worth drawing.
EVIDENCED = {"confirmed", "monitoring", "refuted"}

CHIP = {"confirmed": "t", "monitoring": "o", "refuted": "o", "asserted": "x",
        "proposed": "x"}

# How much of the condition space one condition is worth, by how far it has been checked.
# A coarse ladder on purpose: it is a reading aid, not a measurement, and the caption says
# so. An order of magnitude between "somebody checked this" and "somebody asserted it" is
# the point. Percentages of the whole space.
STATUS_WEIGHT = {"confirmed": 20.0, "monitoring": 10.0, "refuted": 10.0,
                 "asserted": 2.0, "proposed": 2.0}

# The weights the five old basis words carried before the split, kept because they said
# one thing the pair cannot: `replicated` was worth more than `tested`, and both now read
# as `confirmed`. A record written in the old words therefore renders exactly as it did
# before, and a record written in the new pair is weighed by its status.
WEIGHT = {"replicated": 20.0, "tested": 12.0, "observed": 10.0, "untested": 2.0,
          "inferred": 2.0}

BOUNDARY_FIELDS = ("holds_when", "fails_when", "replaced_by", "unknown_region")
# reads_as is the reader-facing sentence for the Conditions column. It is not a
# boundary field: a claim carrying only reads_as has documented nothing.

# `replaced_by` may name a claim instead of describing one. That is what makes a competing
# claim first class: the thing that is true instead is a claim in the corpus with its own
# evidence, conditions and level, not a sentence stranded in a string. Free text still
# reads, unchanged, because most replacements never become their own claim.
REPLACED_BY_CLAIM = "claim"

CSS = """
.bcard { border:1px solid #d8dae0; border-radius:8px; overflow:hidden; font-size:.85rem; }
.bcard .hd { padding:.55rem .8rem; background:#fafbfc; border-bottom:1px solid #d8dae0; }
.bcard .row { display:grid; grid-template-columns:7.5rem 1fr; border-bottom:1px solid #d8dae0; }
.bcard .row:last-child { border-bottom:0; }
.bcard .k { padding:.5rem .8rem; font-weight:600; }
.bcard .k.h { color:#2e9e5b; } .bcard .k.f { color:#c0392b; }
.bcard .k.i { color:#b8800f; } .bcard .k.u { color:#6b7280; }
.bcard .v { padding:.5rem .8rem; }
.chip { display:inline-block; font-size:.7rem; padding:.05rem .45rem; border-radius:99px;
        border:1px solid #d8dae0; margin-left:.3rem; color:#6b7280; }
.chip.t { border-color:#2e9e5b; color:#2e9e5b; }
.chip.o { border-color:#e6a01e; color:#b8800f; }
.strip { display:flex; height:1.4rem; border-radius:6px; overflow:hidden;
         border:1px solid #d8dae0; font-size:.7rem; margin:.5rem 0; }
.strip div { display:flex; align-items:center; justify-content:center; color:#fff; }
.strip .h { background:#2e9e5b; } .strip .u { background:#8a8f98; } .strip .f { background:#c0392b; }
.bcap { font-size:.72rem; color:#6b7280; }
.bmap { display:grid; grid-template-columns:auto 1fr 1fr; gap:.4rem; margin:.6rem 0; font-size:.8rem; }
.bmap .ax { color:#6b7280; font-size:.72rem; text-transform:uppercase;
            letter-spacing:.05em; align-self:center; }
.bmap .cell { border:1px solid #d8dae0; border-radius:6px; padding:.5rem .6rem; min-height:4.2rem; }
.bmap .holds { border-color:#2e9e5b; } .bmap .fails { border-color:#c0392b; }
.bmap .unk { border-style:dashed; }
.bmap .cell b { display:block; font-size:.78rem; margin-bottom:.2rem; }
@media (max-width:800px){ .bmap { grid-template-columns:1fr; } .bcard .row { grid-template-columns:1fr; } }
""".strip()

STRIP_CAPTION = ("Strip widths come from the conditions on the record and how each one is "
                 "known. They are a reading aid, not a measurement; they exist to stop a "
                 "reader assuming the claim is mostly settled.")


def has_boundary(record):
    """True once any part of the boundary record is present."""
    return any(record.get(f) for f in BOUNDARY_FIELDS)


def replaced_claim(record):
    """The claim id `replaced_by` names, or None when it is free text or absent.

    Raises ValueError on an object that is neither, because a replacement nobody can read
    is worse than none: it looks like the author named the claim that is true instead.
    """
    value = record.get("replaced_by")
    if value is None or isinstance(value, str):
        return None
    if not isinstance(value, dict) or set(value) != {REPLACED_BY_CLAIM}:
        raise ValueError(
            f"replaced_by is free text or {{\"claim\": \"c9\"}}, not {value!r}")
    cid = value[REPLACED_BY_CLAIM]
    if not isinstance(cid, str) or not cid.strip():
        raise ValueError(f"replaced_by names no claim: {value!r}")
    return cid.strip()


def replacement_label(record):
    """What is true instead, as text a reader sees. Empty when nothing is recorded."""
    cid = replaced_claim(record)
    if cid:
        return f"claim {cid}"
    return record.get("replaced_by") or ""


def validate_replacements(data):
    """Raise AssertionError when a `replaced_by` names a claim that does not exist.

    Free text is never checked, because there is nothing to check it against. A named
    claim is, because naming one that is not there is a replacement the reader cannot
    follow, which is the hole this field exists to fill.
    """
    claims = [c for c in (data.get("claims") or []) if isinstance(c, dict)]
    ids = {c.get("id") for c in claims}
    for i, claim in enumerate(claims):
        here = f"claims[{claim.get('id') or i}]"
        try:
            cid = replaced_claim(claim)
        except ValueError as e:
            raise AssertionError(f"{here}: {e}") from None
        if cid is None:
            continue
        assert cid in ids, (
            f"{here}: replaced_by names claim {cid!r}, which is not a claim in this "
            f"sidecar, so a reader cannot follow the replacement")
        assert cid != claim.get("id"), (
            f"{here}: replaced_by names the claim itself, which replaces nothing")
    return True


def conditions(record, field):
    """The condition entries of one region, rejecting a bare string.

    A bare string carries no basis, so an untested guess and a replicated interaction
    read the same, which is the whole failure the basis field exists to prevent.

    Both shapes are accepted, `{dimension, value, basis}` and the older
    `{condition, basis}`, because `dimensions.read_condition` is the only parser and it
    reads either. The entries come back untouched; use `dimensions.label(entry)` for the
    text a reader sees.
    """
    out = []
    for entry in record.get(field) or []:
        try:
            dimensions.read_condition(entry)
        except ValueError as e:
            raise ValueError(f"{field}: {e}") from None
        out.append(entry)
    return out


def status_of(entry):
    """How far one condition has been checked, in the current vocabulary."""
    return dimensions.read_condition_full(entry)[3]


def is_formal(entry):
    """True when this condition may become a formal condition on the claim."""
    return status_of(entry) == FORMAL


def weight(entry):
    """How much of the condition space this condition buys.

    An old basis word is weighed by the word itself, because it drew a line between
    `replicated` and `tested` that the translated pair no longer draws. Everything else
    is weighed by its status.
    """
    written = entry.get("basis")
    if written in WEIGHT and "status" not in entry:
        return WEIGHT[written]
    return STATUS_WEIGHT[status_of(entry)]


def strip(record):
    """(holds, unknown, fails) as whole percentages summing to 100.

    Each condition buys WEIGHT[basis] percent of the space. What neither region has
    bought is unknown. When the conditions claim more than the whole space, the two
    known regions are scaled down to fit rather than the unknown region going negative:
    a record cannot buy certainty by listing more conditions.
    """
    holds = sum(weight(c) for c in conditions(record, "holds_when"))
    fails = sum(weight(c) for c in conditions(record, "fails_when"))
    if holds + fails > 100:
        holds, fails = holds * 100 / (holds + fails), fails * 100 / (holds + fails)
    holds, fails = round(holds), round(fails)
    return holds, 100 - holds - fails, fails


def moderators(record):
    """The conditions somebody actually looked at. Two of them is a map."""
    return [c for f in ("holds_when", "fails_when") for c in conditions(record, f)
            if status_of(c) in EVIDENCED]


def _chips(entries):
    return " · ".join(
        f'{html.escape(dimensions.label(c))} '
        f'<span class="chip {CHIP[status_of(c)]}">'
        f'{html.escape(c.get("basis_note") or c["basis"])}</span>' for c in entries)


def _row(cls, key, value):
    return (f'<div class="row"><div class="k {cls}">{key}</div>'
            f'<div class="v">{value}</div></div>') if value else ""


def card(record, title=None):
    """One claim's boundary as an HTML fragment. Pair it with CSS once per page.

    `record` is any mapping carrying the four boundary fields: a sidecar claim, or a
    hypothesis record from a claim register. Anything else on it is ignored, so one
    renderer serves both.
    """
    if not has_boundary(record):
        raise ValueError(f"{record.get('id', '<claim>')} carries no boundary record")
    h, u, f = strip(record)
    head = html.escape(title or record.get("id") or "Claim")
    parts = [f'<div class="bcard"><div class="hd"><b>{head}</b>']
    if record.get("statement"):
        parts.append(f'<br><span>{html.escape(record["statement"])}</span>')
    parts.append('<div class="strip">')
    for cls, pct, label in (("h", h, "holds"), ("u", u, "unknown"), ("f", f, "fails")):
        if pct:
            parts.append(f'<div class="{cls}" style="width:{pct}%">{label}</div>')
    parts.append(f'</div><span class="bcap">{STRIP_CAPTION}</span></div>')
    parts.append(_row("h", "Holds when", _chips(conditions(record, "holds_when"))))
    parts.append(_row("f", "Fails when", _chips(conditions(record, "fails_when"))))
    parts.append(_row("i", "True instead", html.escape(replacement_label(record))))
    parts.append(_row("u", "Unknown", html.escape(record.get("unknown_region") or "")))
    parts.append("</div>")
    return "".join(parts)


def axis_map(record, x, y, cells):
    """The two-axis map, for the claim where exactly two moderators carry the answer.

    Refuses to render otherwise, which is the rule rather than a preference: with one
    moderator the map is a table with ceremony, and with three it is a slide nobody can
    read. Which two axes to draw, and what to say in each cell, are the author's
    judgement and are passed in; the record does not hold them.

        x, y   (axis title, positive column/row label, negative column/row label)
        cells  four (label, body, kind) in reading order, kind in holds|fails|unk
    """
    n = len(moderators(record))
    if n != 2:
        raise ValueError(f"a two-axis map needs exactly two evidenced conditions, found {n}")
    if len(cells) != 4:
        raise ValueError("a two-axis map has four cells")
    out = [f'<div class="bmap"><div class="ax">{html.escape(y[0])}</div>',
           f'<div class="ax">{html.escape(x[1])}</div>',
           f'<div class="ax">{html.escape(x[2])}</div>']
    for i, row_label in enumerate((y[1], y[2])):
        out.append(f'<div class="ax">{html.escape(row_label)}</div>')
        for label, body, kind in cells[i * 2:i * 2 + 2]:
            if kind not in ("holds", "fails", "unk"):
                raise ValueError(f"cell kind must be holds, fails or unk, got {kind!r}")
            out.append(f'<div class="cell {kind}"><b>{html.escape(label)}</b>'
                       f'{html.escape(body)}</div>')
    out.append("</div>")
    return "".join(out)


def _self_check():
    """Six cases with known answers. The threshold is all six: this renders the
    record a reader trusts, so one wrong region is one wrong decision, and there is no
    partial credit."""
    # Case 1: the worked example. Four untested conditions and two observed ones must
    # render as a mostly-unknown space, NOT as a claim that is half settled.
    night = {"id": "H10", "statement": "The AI night shift.",
             "holds_when": [{"condition": f"c{i}", "basis": "untested"} for i in range(4)],
             "fails_when": [{"condition": "morning review is per item", "basis": "observed"},
                            {"condition": "checks miss the class", "basis": "observed"}],
             "replaced_by": "The constraint is the morning, not the night.",
             "unknown_region": "Everything about overnight regimes in software."}
    assert strip(night) == (8, 72, 20), strip(night)
    out = card(night)
    assert 'style="width:72%"' in out and "unknown" in out
    assert out.count('class="row"') == 4, "four rows: holds, fails, true instead, unknown"
    assert out.count("chip") >= 6, "one evidence chip per condition"

    # Case 2: the failure this file exists to prevent. Drop the unknown region and the
    # card must not render, because holds-when plus fails-when reads as a mapped space.
    mapped = dict(night, unknown_region="")
    assert strip(mapped) == (8, 72, 20), "the strip is unchanged; it is the ROW that goes"
    assert 'class="k u"' not in card(mapped), "an empty unknown region draws no row"
    bare = {"id": "H99", "statement": "no boundary here"}
    try:
        card(bare)
    except ValueError:
        pass
    else:
        raise AssertionError("a claim with no boundary record must not render as a card")

    # Case 3: the map is gated on the evidence, not on taste. Two evidenced conditions
    # render; adding a third refuses, because a three-axis map is a slide nobody reads.
    axes = (("Morning review", "sampled", "per item"), ("Spec", "reviewed", "not reviewed"))
    cells = [("Claimed region", "Untested. This is the experiment.", "unk"),
             ("Automation bias", "Mechanism evidenced in three domains.", "fails"),
             ("Unknown", "Nobody has measured it.", "unk"),
             ("Both mechanisms", "Do not run it here.", "fails")]
    assert len(moderators(night)) == 2
    m = axis_map(night, axes[0], axes[1], cells)
    assert m.count('class="cell') == 4 and "Automation bias" in m
    third = dict(night, holds_when=night["holds_when"] + [
        {"condition": "blind first review", "basis": "replicated"}])
    assert len(moderators(third)) == 3
    try:
        axis_map(third, axes[0], axes[1], cells)
    except ValueError:
        pass
    else:
        raise AssertionError("three moderators must refuse the two-axis map")
    # and the replicated condition moves the strip, which is the only way it moves
    assert strip(third)[0] == 28 and strip(third)[1] == 52

    # A bare string in a region carries no basis and must be refused, not rendered.
    try:
        card(dict(night, fails_when=["the reviewer is tired"]))
    except ValueError:
        pass
    else:
        raise AssertionError("a bare string condition must be refused")

    # Both condition shapes render through the one parser, and the dimension is on the
    # chip when there is one. The strip does not care which shape it was written in.
    mixed = dict(night, holds_when=[{"dimension": "air quality", "value": "clean",
                                     "basis": "observed"},
                                    {"condition": "the weather is fine", "basis": "untested"}])
    out = card(mixed)
    assert "air quality: clean" in out and "the weather is fine" in out
    assert strip(mixed) == (12, 68, 20), strip(mixed)

    # Case 4: the basis split. Only a `confirmed` condition is formal, which is the same
    # rule the two old strong words carried, said in the new field.
    def cond(basis, status=None):
        c = {"dimension": "air quality", "value": "clean", "basis": basis}
        return c if status is None else dict(c, status=status)

    assert is_formal(cond("tested")) and is_formal(cond("replicated"))
    for weak in ("observed", "untested", "inferred"):
        assert not is_formal(cond(weak)), weak
    assert is_formal(cond("human", "confirmed"))
    for weak in ("asserted", "proposed", "monitoring", "refuted"):
        assert not is_formal(cond("human", weak)), weak
    # An unchecked condition in the current vocabulary is a candidate, not a formal one.
    assert not is_formal({"dimension": "d", "value": "v", "basis": "stated-in-source"})
    # The chip follows the status, so a reader sees the same three grades as before.
    pair = {"id": "H11", "statement": "The pair shape.",
            "holds_when": [cond("stated-in-source", "confirmed")],
            "fails_when": [cond("human", "asserted")],
            "replaced_by": "Something else.", "unknown_region": "Almost all of it."}
    assert strip(pair) == (20, 78, 2), strip(pair)
    assert 'class="chip t"' in card(pair) and 'class="chip x"' in card(pair)
    assert len(moderators(pair)) == 1, "an asserted condition carries no answer"
    # An unknown status is refused rather than graded, because a status nobody can read
    # would otherwise fall through to whatever the chip table happens to hold.
    try:
        card(dict(pair, holds_when=[cond("human", "checked")]))
    except ValueError as e:
        assert "status" in str(e), e
    else:
        raise AssertionError("an unknown status must be refused")

    # Case 5: `replaced_by` may name a claim as well as carrying free text. That is what
    # makes a competing claim first class rather than a sentence stranded in a string.
    assert replaced_claim(night) is None, "free text names no claim, and still reads"
    assert replacement_label(night) == "The constraint is the morning, not the night."
    named = dict(night, replaced_by={"claim": "c9"})
    assert replaced_claim(named) == "c9"
    assert replacement_label(named) == "claim c9"
    assert has_boundary(named), "a named claim is a replacement like any other"
    assert "claim c9" in card(named)
    assert replaced_claim({}) is None and replacement_label({}) == ""
    for bad in ({"claim": " "}, {"claim": 4}, {"statement": "c9"},
                {"claim": "c9", "extra": 1}, ["c9"], 9):
        try:
            replaced_claim({"replaced_by": bad})
        except ValueError:
            continue
        raise AssertionError(f"replaced_by of {bad!r} must be refused")
    # A named claim must exist, and it may not be the claim itself.
    good = {"claims": [dict(named, id="c1"), {"id": "c9", "statement": "Something else."}]}
    assert validate_replacements(good)
    assert validate_replacements({"claims": [night, "not a dict"]}), \
        "free text is never checked, because there is nothing to check it against"
    for claims, word in (([dict(named, id="c1")], "not a claim in this sidecar"),
                         ([dict(night, id="c1", replaced_by={"claim": "c1"})],
                          "the claim itself"),
                         ([dict(night, id="c1", replaced_by={"claim": ""})],
                          "names no claim")):
        try:
            validate_replacements({"claims": claims})
        except AssertionError as e:
            assert word in str(e), f"the message must name {word!r}: {e}"
            continue
        raise AssertionError(f"{claims!r} must be refused")

    # Case 6: the verdict table reads the ledger and nothing else. `status` says where a
    # claim came from, not whether it survived, so it must not move the verdict.
    obs = [{"dimension": "latitude", "value": "below 60", "basis": "observed"}]
    both = dict(night, id="c1", holds_when=obs, fails_when=obs, status="inferred")
    assert verdict(both) == "Holds narrowly", verdict(both)
    assert verdict(dict(both, holds_when=[])) == "Falsified", "fails plus a replacement"
    assert verdict(dict(both, fails_when=[], replaced_by="")) == "Holds"
    assert verdict({"id": "c2", "statement": "x"}) == "Unevaluated"
    assert verdict(dict(both, challenged="refuted")) == "Falsified", "the pass outranks the regions"
    assert verdict(dict(both, challenged="attempted-unresolved")) == "Contested"
    assert verdict(dict(both), open_claims={"c1"}) == "Contested", "an open conflict outranks all"
    assert verdict(dict(both, status="recalled")) == "Holds narrowly", "provenance is not a verdict"

    # ... and the table names the reading when there is one, so a paragraph in a cell is
    # a sign the question was never split, not a rendering fault.
    md = table({"claims": [dict(both, reading="Reserve share")],
                "conflicts": [{"claim": "c9", "state": "open"}]})
    assert "| Reserve share | Holds narrowly |" in md, md
    assert md.splitlines()[1] == "|---|---|---|---|", md
    assert table({"claims": [{"id": "c3", "statement": "no boundary here"}]}) == "", \
        "a claim with no boundary and no open conflict earns no row"

    # The Conditions column: a written sentence wins, the field dump is the fallback.
    written = dict(night, id="c9", reads_as="  Holds indoors.\n  Fails outdoors.  ")
    assert _region(written) == "Holds indoors. Fails outdoors.", "reads_as is used, whitespace collapsed"
    assert _region(dict(night, id="c9")).startswith(("holds when", "fails when", "not tested")), \
        "no reads_as falls back to the fields"

    # The table restates the proposition, and answering claims render beneath it.
    keyed = {"claims": [
        dict(night, id="p1", role="proposition", statement="The sky is blue", reads_as="x"),
        dict(night, id="c9", answers="p1", statement="It is blue at noon", reads_as="y"),
        dict(night, id="p2", role="proposition", statement="The sky is grey", reads_as="z"),
    ]}
    md = table(keyed)
    assert md.splitlines()[0] == "| Proposition | Verdict | Conditions | Evidence and reasoning |", md
    body = md.splitlines()[2:]
    assert body[0].startswith("| P1 - The sky is blue |"), body
    assert body[1].startswith("| P1.1 - It is blue at noon |"), body
    assert body[2].startswith("| P2 - The sky is grey |"), body

    # A claim with no boundary at all says Unconditional, and the word beats prose.
    bare = {"id": "c1", "statement": "s", "challenged": "holds"}
    assert _region(bare) == "Unconditional", _region(bare)
    assert _region(dict(bare, reads_as="holds everywhere, unconditionally")) == "Unconditional", \
        "no boundary means the word, not a sentence about the word"
    assert _region({"id": "c2", "reads_as": "holds indoors",
                    "holds_when": [cond("place", "indoors")]}) == "holds indoors", \
        "with a real boundary, the written sentence is used"

    # A body label that names a different claim from the table's row is caught.
    import tempfile as _tf
    with _tf.TemporaryDirectory() as _d:
        a = pathlib.Path(_d) / "a.md"
        a.write_text("## P5. Head\n\n**P5.2 also holds.** Unconditional priority of the limit\n")
        tbl = "| P5.2 - a planning claim about capital allocation | Falsified | x | y |"
        warn = check_labels(tbl, a)
        assert warn and "P5.2" in warn[0], warn
        ok = "| P5.2 - unconditional priority of the limit over provision | Holds | x | y |"
        assert check_labels(ok, a) == [], check_labels(ok, a)

    print("boundary: self-check passed (14 of 14 cases; the threshold is 14 of 14)")


VERDICTS = ("Holds", "Holds narrowly", "Falsified", "Unevaluated", "Contested")


def verdict(claim, open_claims=()):
    """Which of the five words this claim's own fields have already earned.

    A reading of the ledger, never a second opinion about it. Two fields decide it: what
    the adversarial pass returned (`challenged`), and which regions the boundary record
    carries. `status` is deliberately not consulted, because it says where the claim came
    from, sourced or recalled or inferred, and not whether it survived.

    Order matters. An unresolved disagreement outranks everything, because a conflict
    nobody closed is not a verdict we get to state.
    """
    challenged = claim.get("challenged")
    if claim.get("id") in open_claims or challenged == "attempted-unresolved":
        return "Contested"
    if challenged == "refuted":
        return "Falsified"
    holds = bool(conditions(claim, "holds_when"))
    fails = bool(conditions(claim, "fails_when"))
    if challenged == "holds-with-boundary" or (holds and fails):
        return "Holds narrowly"
    if fails and claim.get("replaced_by"):
        return "Falsified"
    if holds or challenged == "holds":
        return "Holds"
    return "Unevaluated"


def _region(claim):
    """The Conditions cell: what the author wrote, or the fields if they wrote nothing.

    `reads_as` is a sentence a person can read. The fallback concatenates the machine
    conditions, which is what round 02 shipped, and it reads like a field dump because
    that is what it is. The fallback stays because a table with an ugly cell beats a
    table with a missing row, and `table()` warns about every row that took it.
    """
    # No boundary at all is a fact about the claim, not a matter of phrasing, so the word
    # wins over whatever prose was written. Round 04 wrote reads_as on unconditional
    # claims too and the word appeared in none of four papers: "holds in the indexed
    # literature, unconditionally" is a sentence where `Unconditional` is a signal.
    if not (has_boundary(claim) or (claim.get("unknown_region") or "").strip()):
        return "Unconditional"
    written = (claim.get("reads_as") or "").strip()
    if written:
        return " ".join(written.split())
    for field, lead in (("fails_when", "fails when"), ("holds_when", "holds when")):
        entries = conditions(claim, field)
        if entries:
            return f"{lead} {'; '.join(dimensions.label(e) for e in entries[:2])}"
    unknown = (claim.get("unknown_region") or "").strip()
    if unknown:
        return unknown
    # No boundary at all. Say so in a word rather than leaving the cell to be filled
    # with the reasoning, which is what round 03 did: a blank reads as an omission and
    # a restated justification reads as a condition that is not there.
    return "Unconditional"


def _sort_key(claim, order):
    """Proposition order, then claim order within a proposition.

    A claim with no proposition sorts after every labelled one, so an unkeyed ledger
    still produces a table rather than an error.
    """
    label = (claim.get("proposition") or "").strip().upper()
    m = re.match(r"P(\d+)", label)
    if not m:
        return (1, 0, order)
    return (0, int(m.group(1)), order)


def table(data):
    """The verdict table, as markdown, keyed to the propositions.

    Four columns: the proposition restated beside its label, the verdict word alone, the
    conditions or `Unconditional`, and the evidence in a few words.

    Column one carries the PROPOSITION's own sentence, not the claim's. Round 03 printed
    the claim wording under a proposition label, so a reader had to scroll back to learn
    what P1 was, and on one paper the label and the wording had drifted far enough that
    the verdict was wrong for the proposition it was filed under.

    A claim answering a proposition renders beneath it as P2.1, P2.2, in ledger order.
    """
    claims = data.get("claims") or []
    by_id = {c.get("id"): c for c in claims if isinstance(c, dict)}
    contested = {c.get("claim") for c in (data.get("conflicts") or [])
                 if isinstance(c, dict) and c.get("state") == "open"}

    props = [c for c in claims if c.get("role") == "proposition"]
    labelled, order = {}, []
    for i, prop in enumerate(props, 1):
        labelled[prop.get("id")] = f"P{i}"
        order.append(prop)

    def text_of(claim):
        return (claim.get("reading") or claim.get("statement")
                or claim.get("assertion") or claim.get("id") or "").strip().rstrip(".")

    def row(label, claim):
        head = f"{label} - {text_of(claim)}" if label else text_of(claim)
        return (f"| {head} | {verdict(claim, contested)} "
                f"| {_region(claim)} | {(claim.get('basis') or '').strip()} |")

    out = ["| Proposition | Verdict | Conditions | Evidence and reasoning |",
           "|---|---|---|---|"]
    dumped, placed = [], set()

    for prop in order:
        pid, tag = prop.get("id"), labelled[prop.get("id")]
        out.append(row(tag, prop)); placed.add(pid)
        if not (prop.get("reads_as") or "").strip() and has_boundary(prop):
            dumped.append(pid)
        n = 0
        for c in claims:
            if c.get("answers") != pid or c.get("id") == pid:
                continue
            if not (has_boundary(c) or c.get("id") in contested):
                continue
            n += 1
            out.append(row(f"{tag}.{n}", c)); placed.add(c.get("id"))
            if not (c.get("reads_as") or "").strip():
                dumped.append(c.get("id"))

    # Anything carrying a boundary that no proposition claimed. Round 03's papers were
    # entirely this, which is why the table read as a flat list.
    orphans = [c for c in claims if c.get("id") not in placed
               and (has_boundary(c) or c.get("id") in contested)]
    for c in orphans:
        out.append(row("", c))
        if not (c.get("reads_as") or "").strip():
            dumped.append(c.get("id"))

    if len(out) == 2:
        return ""
    if dumped:
        print(f"boundary: {len(dumped)} row(s) fell back to the raw conditions because no "
              f"reads_as was written: {', '.join(str(d) for d in dumped[:6])}"
              f"{' ...' if len(dumped) > 6 else ''}", file=sys.stderr)
    if not props:
        print("boundary: no claim carries role='proposition', so the table cannot restate "
              "what each row is about. Set role and answers (reference/research-mode.md).",
              file=sys.stderr)
    elif orphans:
        print(f"boundary: {len(orphans)} claim(s) carry a boundary and answer no proposition, "
              f"so they render unkeyed: {', '.join(str(c.get('id')) for c in orphans[:6])}",
              file=sys.stderr)
    return "\n".join(out)


def check_labels(md, artefact_path):
    """Warn where a P-label in the paper names a different claim from the table's.

    Two round-04 graders split on exactly this and the split was settled by looking: one
    paper's body said "P5.2 also holds" of unconditional priority while the table's P5.2
    was a falsified planning claim. A label that exists everywhere and points at different
    things in two places is invisible to anyone checking that labels exist.
    """
    art = pathlib.Path(artefact_path)
    if not art.exists():
        return []
    text = art.read_text(errors="replace")
    in_table = {}
    for line in md.splitlines():
        m = re.match(r"\|\s*(P\d+(?:\.\d+)?)\s*-\s*(.+?)\s*\|", line)
        if m:
            in_table[m.group(1)] = m.group(2).lower()
    out = []
    for m in re.finditer(r"(?:^#{2,4}\s*|\*\*)(P\d+\.\d+)\b[.:]?\s*(.{0,60})", text, re.M):
        label, following = m.group(1), m.group(2).strip().lower()
        row = in_table.get(label)
        if not row or not following:
            continue
        head = [w for w in re.findall(r"[a-z]{4,}", following)[:4]]
        if head and not any(w in row for w in head):
            out.append(f"boundary: the paper's {label} ({following[:40]}...) does not look like "
                       f"the table's {label} ({row[:40]}...). One of them is mislabelled.")
    return out


def main(paths, as_table=False):
    shown = 0
    for p in paths:
        doc = json.loads(pathlib.Path(p).read_text())
        if as_table:
            md = table(doc)
            if md:
                print(md)
                shown += 1
                # The artefact sits beside its sidecar: a.md.sourced -> a.md
                for w in check_labels(md, str(p)[:-len(".sourced")] if str(p).endswith(".sourced") else ""):
                    print(w, file=sys.stderr)
            continue
        for claim in doc.get("claims", []):
            if has_boundary(claim):
                print(card(claim))
                shown += 1
    if not shown:
        print("no claim in those sidecars carries a boundary record", file=sys.stderr)
    return 0 if shown else 1


if __name__ == "__main__":
    argv = [a for a in sys.argv[1:] if a != "table"]
    if "--self-check" in sys.argv or not argv:
        _self_check()
    else:
        sys.exit(main(argv, as_table="table" in sys.argv[1:]))
