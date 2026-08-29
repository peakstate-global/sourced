#!/usr/bin/env python3
"""One claim, stated at several levels of sophistication.

"The sky is blue" and "Rayleigh scattering goes as the inverse fourth power of
wavelength" are one claim at two depths, not two unrelated records. A statement
therefore carries a `level`, and may name a `coarser` and a `finer` sibling saying the
same thing at another depth:

    level      any whole number from 1 up. A level is an ordinal and nothing else, so it
               prints as "level 7". The ladder has no top and its rungs have no names.
    coarser    the id of the same statement, said more plainly
    finer      the id of the same statement, said more precisely

    python3 sophistication.py --self-check     eight cases, known answers, no network
    python3 sophistication.py <file.sourced>   the over-claiming report

A CONDITION IS ITSELF A CLAIM
-----------------------------
"Clean air" and "particulate below six parts per million" are one condition at two
depths, so conditions use this mechanism and this validator, with no second
implementation. `validate_statements` is called twice: once over `claims[]`, once over
every condition flattened out of `holds_when` and `fails_when`. A condition may carry an
optional `id` so a sibling can name it; one with no id simply cannot be a sibling target,
and that is fine.

SOPHISTICATION IS NOT STRENGTH
------------------------------
A level-1 statement is a coarser model, not weaker evidence. The two axes stay
orthogonal, and a level-1 claim resting on replicated evidence is not a defect. The check
that matters is the mismatch: a claim stated at level 3 whose evidence supports only
level 1 is over-claiming, and `over_claiming()` reports it. It is a REPORT here and never a
refusal, because the author may be stating a coarse claim on purpose. `integrate.py` is
where the same mismatch becomes a refusal at delivery. Evidence precision is DERIVED from
the evidence rows rather than stored (docs/framework.md, position 7).

ponytail: sibling links are walked with a seen-set per statement, so the cycle check is
O(n * depth). The ceiling is a sidecar of a few hundred claims; if a record ever holds
thousands, colour the graph once instead of walking it per node.
"""
import contextlib
import io
import json
import pathlib
import sys

# THERE IS NO TABLE OF LEVEL NAMES, and that is the decision of 29 August 2026. Levels
# are ordered, not named by audience, because an audience name invites an argument about
# who counts as one. A level is any whole number from 1 up, the integer
# is the whole value, and it prints as "level 7".
#
# The numbers are RELATIVE, NOT ABSOLUTE. Level 3 names no exact quantity of precision,
# and two artefacts do not have to agree about what their level 3 holds. Nothing may
# compare a level across two artefacts. A statement may also need RE-LEVELLING later,
# when something turns up that sits between two rungs already written down, and that is
# expected rather than a defect. See `docs/philosophy.md` position 10.

# The ceiling on evidence precision. On an unbounded ladder there is no meaningful
# "your evidence supports level 47", so the derived number stops at a precise citation.
MAX_PRECISION = 3

SIBLINGS = ("coarser", "finer")


def conditions_of(claim):
    """Every condition object on one claim, both regions, old shape included.

    A bare string carries no level and no id, so it is skipped rather than refused:
    refusing it is `boundary.py`'s job, and a 1.2 sidecar must still validate here.
    """
    return [c for field in ("holds_when", "fails_when")
            for c in (claim.get(field) or []) if isinstance(c, dict)]


def all_conditions(data):
    """Every condition in a sidecar, flattened into one scope."""
    return [c for claim in (data.get("claims") or []) if isinstance(claim, dict)
            for c in conditions_of(claim)]


def level_name(level):
    """How a level prints: "level 3". A level has an ordinal and never a name."""
    return f"level {level}"


def _name(rec, i, what):
    return f"{what}[{rec.get('id') or i}]"


def validate_statements(records, what="claims"):
    """Shape check on the level mechanism. Raises AssertionError naming the first fault.

    Every field is optional. A record with no `level` and no sibling passes untouched,
    which is what keeps a 1.2 sidecar valid.
    """
    records = [r for r in records if isinstance(r, dict)]
    by_id = {}
    for i, rec in enumerate(records):
        rid = rec.get("id")
        if not rid:
            continue
        assert rid not in by_id, (
            f"{_name(rec, i, what)}: id {rid!r} is used twice, so a sibling naming it "
            f"cannot say which record it means")
        by_id[rid] = rec
    for i, rec in enumerate(records):
        here = _name(rec, i, what)
        if "level" in rec:
            lvl = rec["level"]
            assert isinstance(lvl, int) and not isinstance(lvl, bool) and lvl >= 1, (
                f"{here}: level {lvl!r} is not a whole number from 1 up")
        for side in SIBLINGS:
            if side not in rec:
                continue
            target = rec[side]
            assert isinstance(target, str) and target in by_id, (
                f"{here}: {side} names {target!r}, which is not an id in {what}")
            assert target != rec.get("id"), f"{here}: {side} names itself"
            other = by_id[target]
            # Only checked when both carry a level. Half a record is still a record.
            if "level" in rec and "level" in other:
                if side == "coarser":
                    assert other["level"] < rec["level"], (
                        f"{here}: coarser sibling {target!r} is level {other['level']}, "
                        f"not lower than {rec['level']}")
                else:
                    assert other["level"] > rec["level"], (
                        f"{here}: finer sibling {target!r} is level {other['level']}, "
                        f"not higher than {rec['level']}")
    # Cycles, one walk per side. A ring of siblings is not a ladder of depths, and left
    # alone it is an infinite walk for anything that later follows the links.
    for side in SIBLINGS:
        for i, rec in enumerate(records):
            seen, cur = {rec.get("id")}, rec
            while side in cur:
                cur = by_id[cur[side]]
                assert cur.get("id") not in seen, (
                    f"{_name(rec, i, what)}: {side} links form a cycle at {cur['id']!r}")
                seen.add(cur.get("id"))
    return True


# Precision is not sophistication and must not borrow its names. These describe how far
# a reader can follow the citation, not how deep the claim is.
PRECISION_NAMES = {1: "no evidence row", 2: "a source, without a quote and a locator",
                   3: "a quote and a locator"}


def evidence_precision(claim, evidence_by_id):
    """How precisely this claim is cited, 1 to 3. Derived, never stored.

    1 no evidence row resolves · 2 at least one resolves · 3 at least one carries both a
    non-empty quote and a non-empty locator.

    THIS IS A FLOOR AND NOT A CEILING. The ladder of sophistication has no top, so there
    is no reading of the evidence that says "this supports level 47". What is checkable
    without judgement is the other direction: a precise claim needs a precise citation.
    So the number stops at 3, and it is used to ask one question only, whether a claim
    stated at level 3 or above can be followed back to a quote and a locator.
    """
    ids = [e for e in (claim.get("evidence") or []) if e in evidence_by_id]
    # A row that names this claim in `supports` cites it just as hard, whether or not the
    # claim lists the row back. The gate refuses deliveries, so it reads every row that
    # points at the claim rather than only the ones the claim happens to point at.
    cid = claim.get("id")
    for eid, row in evidence_by_id.items():
        if eid in ids or not isinstance(row, dict):
            continue
        sup = row.get("supports")
        if isinstance(sup, dict) and cid is not None and sup.get("claim") == cid:
            ids.append(eid)
    rows = [evidence_by_id[e] for e in ids]
    if not rows:
        return 1
    quoted = any((r.get("quote") or "").strip() and (r.get("locator") or "").strip()
                 for r in rows)
    return MAX_PRECISION if quoted else 2


def over_claiming(data):
    """[(claim_id, stated, precision)] for every claim stated at 3 or above on thin citation.

    A claim stated at level 1 or 2 can never over-claim, because a coarse statement is a
    coarser model and not weaker evidence.
    """
    ev = {e.get("id"): e for e in (data.get("evidence") or []) if isinstance(e, dict)}
    out = []
    for claim in (data.get("claims") or []):
        stated = claim.get("level")
        if not isinstance(stated, int) or isinstance(stated, bool):
            continue
        precision = evidence_precision(claim, ev)
        if stated >= MAX_PRECISION and precision < MAX_PRECISION:
            out.append((claim.get("id"), stated, precision))
    return out


def _report(path):
    data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    rows = over_claiming(data)
    levelled = sum(1 for c in data.get("claims") or [] if "level" in c)
    print(f"{path}: {levelled} of {len(data.get('claims') or [])} claims state a level")
    for cid, stated, precision in rows:
        print(f"  over-claiming  {cid}: stated at {level_name(stated)}, "
              f"cited at precision {precision} of 3 ({PRECISION_NAMES[precision]})")
    if not rows:
        print("  no claim is stated at level 3 or above without a precise citation")
    return 0


def _self_check():
    """Eight cases with known answers, no network. The threshold is all eight: this decides
    whether two records are one claim, and a wrong answer either splits one claim in two
    or fuses two claims into one."""
    sky1 = {"id": "c1", "statement": "The sky is blue.", "level": 1, "finer": "c3"}
    sky3 = {"id": "c3", "level": 3, "coarser": "c1", "evidence": ["e1"],
            "statement": "Rayleigh scattering goes as the inverse fourth power of wavelength.",
            "holds_when": [{"condition": "clean air", "basis": "tested", "id": "k1",
                            "level": 1, "finer": "k2"},
                           {"condition": "particulate below 6 ppm", "basis": "tested",
                            "id": "k2", "level": 3, "coarser": "k1"}]}
    ev = [{"id": "e1", "quote": "…", "locator": "p. 178"}]
    good = {"claims": [sky1, sky3], "evidence": ev}

    def case_good():
        assert validate_statements(good["claims"])
        assert validate_statements(all_conditions(good), "conditions")

    def case_bad_level():
        # The ladder has no top: a big level is a legitimate level.
        for good_level in (3, 4, 5, 47, 900, 1000):
            assert validate_statements([{"id": "c1", "level": good_level}])
        # and a level has an ordinal, never a name, in every message this file prints
        assert level_name(3) == "level 3" and level_name(900) == "level 900"
        assert not hasattr(sys.modules[__name__], "LEVELS"), "the name table is gone"
        # and a ladder may skip rungs, because depth is ordered and not consecutive
        assert validate_statements([{"id": "a", "level": 1, "finer": "b"},
                                    {"id": "b", "level": 3, "coarser": "a", "finer": "c"},
                                    {"id": "c", "level": 9, "coarser": "b"}])
        for bad in (0, -1, "3", 2.5, 2.0, True):
            try:
                validate_statements([{"id": "c1", "level": bad}])
            except AssertionError:
                continue
            raise AssertionError(f"level {bad!r} must be refused")
        # and the same validator refuses it on a condition, not a second implementation
        try:
            validate_statements([{"id": "k1", "level": 0}], "conditions")
        except AssertionError:
            return
        raise AssertionError("a bad level on a condition must be refused")

    def case_missing_sibling():
        for rec in ({"id": "c1", "coarser": "nope"}, {"id": "c1", "finer": "nope"},
                    {"id": "c1", "finer": "c1"}):
            try:
                validate_statements([rec])
            except AssertionError:
                continue
            raise AssertionError(f"{rec} must be refused")
        # a sibling at the wrong depth is the quieter fault, and is refused too
        try:
            validate_statements([{"id": "a", "level": 3, "coarser": "b"},
                                 {"id": "b", "level": 3}])
        except AssertionError:
            return
        raise AssertionError("a coarser sibling at the same level must be refused")

    def case_cycle():
        for side in ("coarser", "finer"):
            ring = [{"id": "a", side: "b"}, {"id": "b", side: "c"}, {"id": "c", side: "a"}]
            try:
                validate_statements(ring)
            except AssertionError:
                continue
            raise AssertionError(f"a {side} cycle must be refused")

    def case_1_2_sidecar():
        old = {"claims": [{"id": "c1", "statement": "…", "status": "sourced",
                           "evidence": ["e1"],
                           "holds_when": [{"condition": "clean air", "basis": "observed"}],
                           "fails_when": ["a bare string boundary.py would refuse"]}],
               "evidence": ev}
        assert validate_statements(old["claims"])
        assert validate_statements(all_conditions(old), "conditions")
        assert over_claiming(old) == [], "a claim with no level cannot over-claim"

    def case_over_claiming():
        assert evidence_precision(sky1, {}) == 1, "no evidence rows is precision 1"
        assert evidence_precision({"evidence": ["e1"]}, {"e1": {"id": "e1"}}) == 2
        assert evidence_precision({"evidence": ["e1"]}, {"e1": ev[0]}) == 3
        # A quote with no locator, and a locator with no quote, are both precision 2.
        assert evidence_precision({"evidence": ["e1"]}, {"e1": {"id": "e1", "quote": "…"}}) == 2
        assert evidence_precision(sky3, {"e1": ev[0]}) == 3, "precision has a ceiling of 3"
        assert over_claiming(good) == [], "a level-3 claim on quoted evidence is not over-claiming"
        thin = {"claims": [{"id": "c9", "level": 3, "evidence": ["e2"]}],
                "evidence": [{"id": "e2"}]}
        assert over_claiming(thin) == [("c9", 3, 2)], over_claiming(thin)
        naked = {"claims": [{"id": "c8", "level": 47}], "evidence": []}
        assert over_claiming(naked) == [("c8", 47, 1)], over_claiming(naked)
        # Below 3 there is nothing to over-claim, however thin the citation.
        low = {"claims": [{"id": "c6", "level": 2, "evidence": []}], "evidence": []}
        assert over_claiming(low) == [], "a level-2 claim on no evidence is not over-claiming"
        # A row that names the claim in `supports` cites it, even when the claim does not
        # list the row back. Missing this would refuse a properly cited claim at the gate.
        one_way = {"claims": [{"id": "c5", "level": 3}],
                   "evidence": [{"id": "e5", "quote": "the words", "locator": "p. 2",
                                 "supports": {"claim": "c5", "direction": "for"}}]}
        assert over_claiming(one_way) == [], over_claiming(one_way)
        # and a row supporting a DIFFERENT claim does not rescue this one
        other = {"claims": [{"id": "c5", "level": 3}],
                 "evidence": [{"id": "e5", "quote": "the words", "locator": "p. 2",
                               "supports": {"claim": "c4", "direction": "for"}}]}
        assert over_claiming(other) == [("c5", 3, 1)], over_claiming(other)
        # Orthogonality: a coarse claim on strong evidence is not a defect.
        coarse = {"claims": [dict(sky3, id="c7", level=1)], "evidence": ev}
        assert over_claiming(coarse) == [], "level 1 on strong evidence is a coarser model"

    def case_no_names_anywhere():
        # A level is an ordinal. No audience name may appear in anything this file
        # prints, because a name invites an argument about who counts as one.
        thin = {"claims": [{"id": "c9", "level": 3, "evidence": ["e2"]},
                           {"id": "c8", "level": 900}],
                "evidence": [{"id": "e2"}]}
        with contextlib.redirect_stdout(io.StringIO()) as buf:
            import tempfile
            with tempfile.TemporaryDirectory() as d:
                f = pathlib.Path(d) / "x.sourced"
                f.write_text(json.dumps(thin), encoding="utf-8")
                _report(f)
        printed = buf.getvalue()
        assert "level 3" in printed and "level 900" in printed, printed
        for name in ("conversational", "informed", "practitioner"):
            assert name not in printed, f"{name!r} must not appear: {printed}"

    def case_duplicate_ids():
        # Two records under one id makes every sibling naming it ambiguous, and a cycle
        # can hide behind the one the dict kept.
        try:
            validate_statements([{"id": "c1", "level": 1}, {"id": "c1", "level": 3}])
        except AssertionError:
            return
        raise AssertionError("a duplicate id must be refused")

    cases = [("levels and siblings on claims and conditions", case_good),
             ("a level is an ordinal, and no name is printed", case_no_names_anywhere),
             ("a duplicate id inside one scope is refused", case_duplicate_ids),
             ("the ladder has no top, and a level below 1 is refused", case_bad_level),
             ("a sibling that does not exist is refused", case_missing_sibling),
             ("a cycle is refused on both sides", case_cycle),
             ("a 1.2 sidecar with no levels still validates", case_1_2_sidecar),
             ("over-claiming is reported, coarseness is not", case_over_claiming)]
    passed = 0
    for label, fn in cases:
        try:
            fn()
            passed += 1
            print(f"pass  {label}")
        except AssertionError as e:
            print(f"FAIL  {label}: {e}")
    total = len(cases)
    print(f"\nsophistication: self-check {'passed' if passed == total else 'FAILED'} "
          f"({passed} of {total} cases; the threshold is {total} of {total})")
    return passed == total


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or "--self-check" in args:
        sys.exit(0 if _self_check() else 1)
    sys.exit(_report(args[0]))
