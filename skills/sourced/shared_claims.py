#!/usr/bin/env python3
"""Which claims are used in more than one artefact, and do they still agree?

Built 26 August 2026, the day the same MIT figure was found wrong in a third deck.
A4 and A5 were corrected in the morning; A1 still carried the original error that
afternoon, because nothing connected them. The correction had nowhere to propagate.

    python3 shared_claims.py                 # scan every .sourced under the cwd
    SOURCED_ROOT=/path/to/repo python3 shared_claims.py
    python3 shared_claims.py --self-check

WHY THIS IS COMPUTED AND NOT A FIELD
------------------------------------
The obvious fix is an `instances[]` list on each claim saying where it is used.
That is a field somebody has to maintain, and a maintained cross-reference goes
stale exactly the way the correction did: silently, at the moment it matters.

Everything needed is already in the sidecars. Evidence entries carry
`originGroup`, which is the same across artefacts by design, because it exists to
stop ten write-ups of one press release counting as ten sources. So the shared
claims can be derived, and a derived answer cannot be out of date.

It reports two things, and only the second is a defect:

  SHARED    one origin group, used by several artefacts. Normal and healthy.
  DIVERGED  those artefacts state the claim DIFFERENTLY. One of them is stale,
            or they are genuinely different claims resting on one source and
            should say so.

ponytail: stdlib, one pass, no index to keep. The corpus is the index.
"""
import json
import os
import pathlib
import re
import sys
from collections import defaultdict

# Scan wherever it is pointed, defaulting to the working directory. The tool lives
# in one repo and is run against many, so it must not assume its own layout.
ROOT = pathlib.Path(os.environ.get("SOURCED_ROOT", pathlib.Path.cwd()))


def origins(doc):
    """The distinct sources a sidecar rests on, collapsed by `originGroup`.

    Ten write-ups of one press release are one source, so the number a reader is
    entitled to see is the count of distinct origin groups, not the count of evidence
    rows. A row carrying no `originGroup` stands alone, because nothing has said it
    shares an origin with anything else, and guessing that it does would understate the
    breadth rather than overstate it."""
    return {e.get("originGroup") or "url:" + str(e.get("url") or e.get("id", ""))
            for e in doc.get("evidence", [])}


def normalise(text):
    """Compare meaning, not typography. Numbers are kept: they are the thing that
    goes stale, so a changed figure must read as a divergence, not a formatting
    difference."""
    t = re.sub(r"[‘’“”]", "'", text.lower())
    t = re.sub(r"\bper cent\b", "%", t)
    t = re.sub(r"[^a-z0-9%.]+", " ", t)
    # "95 %" and "95%" are the same number written two ways, and a false divergence
    # trains people to ignore the real ones.
    return re.sub(r"\s+%", "%", t).strip()


def load(root=ROOT):
    """Every sidecar in the tree, as (path, doc)."""
    return [(p, json.loads(p.read_text())) for p in sorted(root.rglob("*.sourced"))]


def index(sidecars):
    """origin group -> {artefact -> [claim statements resting on it]}"""
    by_origin = defaultdict(lambda: defaultdict(list))
    for path, doc in sidecars:
        artefact = doc["artefact"]["path"]
        origin_of = {e["id"]: e.get("originGroup") for e in doc.get("evidence", [])}
        for claim in doc.get("claims", []):
            for eid in claim.get("evidence", []):
                origin = origin_of.get(eid)
                if origin:
                    by_origin[origin][artefact].append(claim["statement"])
    return by_origin


def figures(text):
    """The numbers in a statement. These are what goes stale; the words around
    them are style."""
    return {f.rstrip(".") for f in re.findall(r"\d[\d,]*\.?\d*", text.replace(",", ""))}


def report(by_origin):
    """Returns (shared, diverged).

    A first version flagged any wording difference and produced three alerts of
    which one was real. An alert that is usually noise is an alert people switch
    off, which is the failure this whole toolchain exists to avoid. So the rule
    narrowed to the thing that actually rots:

      DIVERGED  one artefact carries a figure that appears nowhere in the fullest
                statement. 82.3 against 82 is a divergence. Quoting two of four
                numbers is not. High confidence, look at these first.
      VARIANT   same figures, different sentence. Usually style. Sometimes not:
                the MIT error that prompted this tool lives HERE, because "95% of
                organisations" and "95% of 300 initiatives" carry the same
                numbers and attach them to different things. A machine comparing
                figures cannot see that. A person reading two sentences side by
                side can, in about four seconds, which is why they are printed.
      SHARED    one artefact only quotes it, or every statement is identical.
    """
    shared, variant, diverged = [], [], []
    for origin, artefacts in sorted(by_origin.items()):
        if len(artefacts) < 2:
            continue
        row = (origin, {a: stmts for a, stmts in artefacts.items()})
        sets = [set().union(*(figures(s) for s in stmts)) for stmts in artefacts.values()]
        widest = max(sets, key=len)
        if any(not f <= widest for f in sets):
            diverged.append(row)
        elif len({normalise(s) for stmts in artefacts.values() for s in stmts}) > 1:
            variant.append(row)
        else:
            shared.append(row)
    return shared, variant, diverged


def main():
    sidecars = load()
    if not sidecars:
        print("no .sourced files found")
        return 0
    shared, variant, diverged = report(index(sidecars))
    print(f"{len(sidecars)} sidecars · {len(shared)} shared · {len(variant)} variant "
          f"· {len(diverged)} diverged\n")

    for tag, group in (("DIVERGED", diverged), ("VARIANT ", variant)):
        for origin, artefacts in group:
            print(f"{tag}  {origin}")
            for a, stmts in artefacts.items():
                print(f"            {a}")
                for st in stmts:
                    print(f"              {st}")
            print()
    for origin, artefacts in shared:
        print(f"SHARED    {origin} -> {len(artefacts)} artefacts, stated identically")
    return 1 if diverged else 0


def _self_check():
    docs = [
        (pathlib.Path("a.sourced"), {"artefact": {"path": "a"}, "claims": [
            {"id": "c1", "statement": "95 per cent of organisations get no return.", "evidence": ["e1"]}],
            "evidence": [{"id": "e1", "originGroup": "mit"}]}),
        (pathlib.Path("b.sourced"), {"artefact": {"path": "b"}, "claims": [
            {"id": "c1", "statement": "95% of organisations get no return.", "evidence": ["e9"]}],
            "evidence": [{"id": "e9", "originGroup": "mit"}]}),
        (pathlib.Path("c.sourced"), {"artefact": {"path": "c"}, "claims": [
            {"id": "c1", "statement": "95 per cent of 300 initiatives showed no return.", "evidence": ["e2"]}],
            "evidence": [{"id": "e2", "originGroup": "mit"}]}),
    ]
    shared, variant, diverged = report(index(docs[:2]))
    assert len(shared) == 1, "'per cent' and '%' are the same claim, not a difference"
    shared, variant, diverged = report(index(docs))
    # The case that prompted the tool: same figures, different denominator, so a
    # figure comparison CANNOT see it. It must still surface, as VARIANT.
    assert len(variant) == 1 and not diverged, "a changed denominator surfaces as VARIANT"
    assert len(variant[0][1]) == 3, "all three artefacts named, so the stale one is findable by eye"
    # Shorter and longer statements of the same figures are style, not drift.
    brief = [(pathlib.Path("d.sourced"), {"artefact": {"path": "d"}, "claims": [
        {"id": "c1", "statement": "They were 19% slower, having forecast 24%.", "evidence": ["e1"]}],
        "evidence": [{"id": "e1", "originGroup": "metr"}]}),
        (pathlib.Path("e.sourced"), {"artefact": {"path": "e"}, "claims": [
        {"id": "c1", "statement": "16 developers over 246 tasks were 19% slower, forecasting 24%.",
         "evidence": ["e1"]}], "evidence": [{"id": "e1", "originGroup": "metr"}]})]
    shared, variant, diverged = report(index(brief))
    assert len(variant) == 1 and not diverged, "quoting fewer of the same figures is variant, not drift"
    rounded = [(pathlib.Path("f.sourced"), {"artefact": {"path": "f"}, "claims": [
        {"id": "c1", "statement": "Accuracy fell from 82.3 to 45.5%.", "evidence": ["e1"]}],
        "evidence": [{"id": "e1", "originGroup": "rsna"}]}),
        (pathlib.Path("g.sourced"), {"artefact": {"path": "g"}, "claims": [
        {"id": "c1", "statement": "Accuracy fell from 82 to 45%.", "evidence": ["e1"]}],
        "evidence": [{"id": "e1", "originGroup": "rsna"}]})]
    shared, variant, diverged = report(index(rounded))
    assert len(diverged) == 1, "a rounded figure in one artefact and not the other is a divergence"
    solo = report(index(docs[:1]))
    assert solo == ([], [], []), "one artefact using a source is not a shared claim"
    print("shared_claims: self-check passed")


if __name__ == "__main__":
    if "--self-check" in sys.argv:
        _self_check()
    else:
        sys.exit(main())
