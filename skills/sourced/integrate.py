#!/usr/bin/env python3
"""Refuse a delivery that hides a disagreement.

    python3 integrate.py <file.sourced>    check that sidecar before it ships
    python3 integrate.py --self-check      thirteen cases, known answers, no network

**Why this exists.** Position 8 of `docs/philosophy.md` holds that adversarial is the
method and integration is the goal. This rule fails by omission: a conflict recorded
in the sidecar and absent from the delivery leaves no trace in the artefact. Nothing
upstream can make that impossible, which is what earns it a gate. It runs before any
statement ships.

WHAT IT REFUSES
---------------
Four refusals. Three are one move, a disagreement that never reached the reader:

  an undisclosed conflict   the sidecar records the disagreement and ships anyway
                            without naming it in Limitations. A conflict that cannot be
                            closed DOES ship open; what is refused is one the reader
                            was never told about
  an unrecorded one         the evidence rows disagree, and nothing in the artefact
                            acknowledges it: no conflict record, no boundary
  a refutation with no      `fails_when` and no `replaced_by`, which leaves the reader
  replacement               holding the belief the artefact just refuted

The fourth is a claim the reader cannot follow back:

  an unsourced precise      a claim stated at level 3 or above whose evidence carries no
  claim                     quote and no locator. A precise claim needs a precise
                            citation, and the two ways out are to cite it or to state it
                            at level 2. The accepted risk is that a hard gate on a stated
                            level creates pressure to under-state the level, and that was
                            chosen over a report nobody reads.

WHAT IT ONLY FLAGS
------------------
Four things. A flag prints and the exit code stays 0.

Evidence that is possibly stale: the study finished before the thing it is cited about
began. That is deliberate. Staleness is read off periods an author wrote by hand, so it
is a soft signal, and a gate that fails on a soft signal is a gate that gets switched off.

A conflict whose two sides both rest on a model-proposed `supports`: the disagreement was
proposed by a model and no person has confirmed either side. It is a flag and never a
refusal, because this gate refuses on the recorded field. A wrong proposal is then a
visible wrong row somebody can fix, where a refusal driven by an inferred contradiction
would be a wrong verdict nobody can see.

A forecast whose date has arrived: a claim whose `assertion` is `predictive`, whose
`resolves.by` is in the past, and which records no `resolves.outcome`. Nobody went back to
check it. It is a flag rather than a refusal, because the forecast was well formed when it
was written and the missing thing is a later act of review, not a defect in the claim.

An evidence row recorded `mixed`, on a claim carrying no boundary record: the source cuts
both ways, which is already a boundary waiting to be written down. The flag asks whether
it was, and it goes silent once the claim carries one, because a question that has been
answered and keeps being asked is a flag people learn to skip.

THIS FILE NEVER JUDGES WHICH SIDE IS RIGHT
------------------------------------------
Same rule as `conflicts.py`. It reports that a disagreement is unmapped; the author maps
it.

ponytail: a period is read from an ordinary condition whose dimension normalises to
`period`, so no new field and no new validator. The ceiling is plain: a period recorded
only in the prose of a quote is invisible here, and always will be. The upgrade path is
to capture the period as a condition at retrieval, which `dimensions.py` already
supports, not to parse dates out of quote text and guess.
"""
import contextlib
import datetime
import io
import json
import pathlib
import re
import sys
from collections import namedtuple

import boundary
import conflicts
import dimensions
import sophistication

# A finding either stops the delivery or it does not. There is no third severity,
# because every third severity anybody proposes is a way of shipping a `fail` quietly.
FAIL, FLAG = "fail", "flag"

Finding = namedtuple("Finding", "severity message")

# The dimension a period is recorded under, after `dimensions.normalise`.
PERIOD = "period"

HINT = ("A disagreement is a first-class object, not a decision made quietly in a draft. "
        "Resolve it into a boundary record, or ship it as an open conflict with its "
        "unknown region named. Both reach the reader; neither is silence.")


def parse_period(value):
    """(first_year, last_year) from a period value, or None when it cannot be read.

    Reads a plain year, a range written with a dash or the word `to`, and an ISO date.
    Anything else comes back None and is reported as unparsed. A date is never invented.
    """
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", text)
    if m:
        # A real date, or nothing. `2019-13-99` is a typo, and reading the year out of
        # it would be inventing the half nobody typed correctly.
        try:
            datetime.date(*(int(g) for g in m.groups()))
        except ValueError:
            return None
        return int(m.group(1)), int(m.group(1))
    m = re.fullmatch(r"(\d{4})\s*(?:[-‐-―]|to|until|through)\s*(\d{4})", text, re.I)
    if m:
        first, last = int(m.group(1)), int(m.group(2))
        return (first, last) if first <= last else (last, first)
    m = re.fullmatch(r"(\d{4})", text)
    if m:
        return int(m.group(1)), int(m.group(1))
    return None


def _periods(record, *fields):
    """[(raw value, parsed or None)] for every period condition on one record."""
    out = []
    for field in fields:
        for entry in record.get(field) or []:
            try:
                dimension, value, _ = dimensions.read_condition(entry)
            except ValueError:
                continue
            if dimension and dimensions.normalise(dimension) == PERIOD:
                out.append((value, parse_period(value)))
    return out


def _pair(record):
    """The evidence ids a conflict record names, as a frozenset.

    A well-formed record names exactly two, and `conflicts.validate_conflicts` is what
    refuses any other count. Here the set is only ever compared, so a malformed record
    simply matches nothing.
    """
    return frozenset(side.get("evidence") for side in record.get("between") or []
                     if isinstance(side, dict))


def _claims(data):
    return {c.get("id"): c for c in (data.get("claims") or []) if isinstance(c, dict)}


def _cited_claims(data, row):
    """The claim ids one evidence row is cited against, from either direction.

    A claim may list the row in its `evidence`, and a row may name a claim in its
    `supports`. Both are read, because a sidecar written before `supports` existed uses
    only the first.
    """
    out = []
    for claim in data.get("claims") or []:
        if isinstance(claim, dict) and row.get("id") in (claim.get("evidence") or []):
            out.append(claim.get("id"))
    try:
        sup = conflicts.supports_of(row)
    except ValueError:
        sup = None
    if sup and sup[0] not in out:
        out.append(sup[0])
    return out


def _disclosed(data, rec):
    """True when Limitations names the claim this open conflict sits on.

    An open conflict ships through the disclosure and nowhere else, so this asks the one
    question that matters to a reader: were they told. Matching on the claim id keeps the
    check mechanical and keeps the wording the author's own.
    """
    limitations = ((data.get("disclosure") or {}).get("limitations") or "")
    claim = (rec.get("claim") or "").strip()
    return bool(claim) and re.search(rf"\b{re.escape(claim)}\b", limitations) is not None


def findings(data):
    """Every finding in one sidecar, fails first, in document order."""
    out = []
    claims = _claims(data)

    # 1. A conflict the author recorded and left open. An open conflict is allowed to
    #    ship, but only through the disclosure: what is refused is a disagreement the
    #    reader never sees. So the test is whether Limitations names the claim, not
    #    whether the conflict is closed. Closing it to satisfy a gate would be inventing
    #    a resolution, which is the failure this whole standard exists to prevent.
    for rec in conflicts.open_conflicts(data):
        if _disclosed(data, rec):
            continue
        # A side is an evidence row or a competing claim, and the message names either.
        who = " and ".join(conflicts.side_label(data, s)
                           for s in rec.get("between") or [])
        dims = ", ".join(rec.get("dimensions") or [])
        out.append(Finding(FAIL, f"open conflict {rec.get('id')} on claim "
                                 f"{rec.get('claim')}: {who} disagree, and they differ "
                                 f"on {dims}, and Limitations does not mention "
                                 f"{rec.get('claim')}. Either close it into a boundary, or "
                                 f"disclose it: python3 conflicts.py <file.sourced> "
                                 f"prints the sentence to paste into Limitations"))

    # 2. A disagreement in the evidence that nothing in the artefact acknowledges.
    try:
        detected = conflicts.detect(data)
    except ValueError as e:
        detected = []
        out.append(Finding(FAIL, f"a `supports` field cannot be read, so a disagreement "
                                 f"could be hiding behind it: {e}"))
    recorded = {(c.get("claim"), _pair(c)) for c in (data.get("conflicts") or [])
                if isinstance(c, dict)}
    for rec in detected:
        if (rec["claim"], _pair(rec)) in recorded:
            continue
        if boundary.has_boundary(claims.get(rec["claim"]) or {}):
            continue
        who = " and ".join(conflicts._label(data, s["evidence"]) for s in rec["between"])
        dims = ", ".join(rec["dimensions"])
        out.append(Finding(FAIL, f"{who} disagree on claim {rec['claim']} and differ on "
                                 f"{dims}, and no conflict record and no boundary on the "
                                 f"claim says so"))

    # 3. A refutation with no replacement. The reader fills the hole with the belief
    #    that was just refuted, so the artefact leaves them worse than it found them.
    for cid, claim in claims.items():
        if claim.get("fails_when") and not claim.get("replaced_by"):
            out.append(Finding(FAIL, f"claim {cid} records where it fails and does not "
                                     f"say what is true instead, so a reader keeps the "
                                     f"belief it just refuted"))

    # 4. A claim stated precisely that the reader cannot follow back to a source.
    for cid, stated, precision in sophistication.over_claiming(data):
        missing = ("no evidence row resolves against it" if precision == 1
                   else "no evidence row carries both a quote and a locator")
        out.append(Finding(FAIL, f"claim {cid} is stated at "
                                 f"{sophistication.level_name(stated)} and {missing}, so "
                                 f"a reader cannot follow it back. Cite it precisely, or "
                                 f"state the claim at level 2."))

    out.extend(_forecasts(claims))
    out.extend(_unstaked(claims))
    out.extend(_stale(data, claims))
    out.extend(_unconfirmed(data))
    out.extend(_rival_parity(data, claims))
    out.extend(_templated_falsifiers(data, claims))
    out.extend(_custody(data))
    out.extend(_proposition_decomposition(data, claims))
    out.extend(_dimensions_defined(data, claims))
    out.extend(_boundary_prompts(data, claims))
    return out


def _survivors(claims):
    """Claims that came through the adversarial pass and still carry weight.

    Refuted and withdrawn claims are out: a claim the pass killed does not need a
    falsifier, and demanding one produces a fake. Purely definitional claims are out for
    the same reason, since no observation can contradict a statement about what a word
    will mean here.
    """
    out = []
    for cid, claim in claims.items():
        if claim.get("challenged") in ("refuted", "withdrawn"):
            continue
        if (claim.get("kind") or "").strip().lower() in ("definitional", "definition"):
            continue
        out.append((cid, claim))
    return out


def _rival_parity(data, claims):
    """Refuse a claim the adversarial pass wrote that carries less than the ones it replaced.

    Round 02 found this twice, in two topics, through two different graders. One run's ten
    rival claims carried no falsifier at all. Another's three replacement claims, the ones
    holding the integrated position, carried no boundary and were left marked
    `not-attempted`.

    A claim promoted to carry the position is the most load-bearing thing in the sidecar and
    the least externally checkable, so it is the last claim that should be exempt from the
    work. The asymmetry was never a decision; it is what happens when the pass writes claims
    and nothing asks the pass to finish them.
    """
    out = []
    replacements = {str(c.get("replaced_by")) for c in claims.values()
                    if c.get("replaced_by")}
    for cid, claim in _survivors(claims):
        by_pass = claim.get("origin") == "adversarial" or cid in replacements
        if not by_pass:
            continue
        missing = []
        if not (claim.get("falsifier") or "").strip():
            missing.append("`falsifier`")
        if not boundary.has_boundary(claim) and not (claim.get("unknown_region") or "").strip():
            missing.append("boundary (`holds_when` / `fails_when` / `unknown_region`)")
        if missing:
            out.append(Finding(
                FAIL, f"claim {cid} was written by the adversarial pass and survived it, but "
                      f"carries no {' and no '.join(missing)}. A claim the pass promoted "
                      f"carries the position and is the least checkable thing in the sidecar, "
                      f"so it does the same work as the claim it replaced. Record it with "
                      f"`claims.py --falsifier` and `boundary.py`, or mark it refuted."))
    return out


def _dimensions_defined(data, claims):
    """Refuse a delivery whose boundaries name a dimension nobody defined.

    `dimensions.py` was added to research-mode as a named step after round 01 and then ran
    in none of the four round-02 runs either. Eight of eight misses says a step named in a
    reference document is not a step: something has to refuse.

    A dimension named but undefined is a boundary a reader cannot apply, because "holds when
    severity is high" only travels if `severity` says what it is measured with.
    """
    defined = {str(k).strip().lower()
               for k in (data.get("dimensions") or {})} if isinstance(
                   data.get("dimensions"), dict) else {
               str(d.get("name", "")).strip().lower()
               for d in (data.get("dimensions") or []) if isinstance(d, dict)}
    named = {}
    for cid, claim in claims.items():
        for field in ("holds_when", "fails_when"):
            for entry in boundary.conditions(claim, field):
                dim = str(entry.get("dimension") or "").strip()
                if dim and dim.lower() not in defined:
                    named.setdefault(dim.lower(), (dim, cid))
    if not named:
        return []
    shown = ", ".join(sorted(d for d, _ in named.values()))
    return [Finding(
        FAIL, f"{len(named)} dimension(s) are used in a boundary and defined nowhere: "
              f"{shown}. A dimension named but undefined is a boundary a reader cannot "
              f"apply. Run `python3 dimensions.py --sidecar <artefact>.sourced` and write "
              f"what each one is measured with.")]


def _templated_falsifiers(data, claims):
    """Refuse a set of falsifiers that share one stamped phrase.

    Round 03's rival-parity gate made the field mandatory and one run answered it with
    nine claims carrying an identical stem and the specifics swapped out. It passed a
    count and told a reader nothing, which is worse than an honest absence: an absence is
    visible and a template is not.

    The test is a shared prefix across three or more claims. Falsifiers legitimately
    resemble each other on one subject, so the bar is a long identical opening, not a
    similar one.
    """
    STEM, MIN = 45, 3
    seen = {}
    for cid, claim in claims.items():
        f = " ".join((claim.get("falsifier") or "").split())
        if len(f) < STEM:
            continue
        seen.setdefault(f[:STEM].lower(), []).append(cid)
    out = []
    for stem, ids in seen.items():
        if len(ids) < MIN:
            continue
        out.append(Finding(
            FAIL, f"{len(ids)} claims share one falsifier template: {', '.join(sorted(ids)[:6])}"
                  f"{' ...' if len(ids) > 6 else ''}. Each begins {stem.strip()!r}. A falsifier "
                  f"names the observation that would kill THIS claim, so two claims that fail "
                  f"for different reasons cannot share a sentence. Write them per claim, or say "
                  f"the claim cannot be falsified and mark it definitional."))
    return out


def _proposition_decomposition(data, claims):
    """Ask a narrow or contested proposition to say what it splits into.

    A proposition that only ever reads `Holds narrowly` is carrying a disagreement the
    paper has not resolved into anything a reader can use. Pushing the conditionality
    down until each leaf is close to unconditional is what turns "it depends" into two
    things that are both true.

    A flag, not a refusal. Whether a proposition can be split is a judgement about the
    subject, and some genuinely cannot.
    """
    out = []
    answered = {c.get("answers") for c in claims.values() if c.get("answers")}
    for cid, claim in claims.items():
        if claim.get("role") != "proposition":
            continue
        narrow = (boundary.conditions(claim, "holds_when")
                  and boundary.conditions(claim, "fails_when"))
        contested = claim.get("challenged") == "attempted-unresolved"
        if not (narrow or contested):
            continue
        if cid in answered:
            continue
        out.append(Finding(
            FLAG, f"proposition {cid} is "
                  f"{'contested' if contested else 'true in one region and false in another'} "
                  f"and nothing answers it. Split it until each part is close to unconditional, "
                  f"with each child carrying answers={cid!r}, so the reader sees the "
                  f"disagreement resolve into parts that are each straightforwardly true. If it "
                  f"cannot be split, say so in the paper and this flag is answered."))
    return out


def _custody(data):
    """Refuse a delivery where nothing was archived, flag the rows that were missed.

    The capture hash proves a quote matches our own file. It says nothing about whether
    the page said that on the day, which is the first thing an audit asks. `archiveUrl`
    has been in the schema throughout and rounds 01 to 03 wrote zero across 48 cited
    rows, so the entire evidence base was self-attested.

    Refusing per row would block a run whenever the archive service is down. Refusing a
    paper where NOTHING was archived cannot be a service outage.
    """
    rows = [r for r in (data.get("evidence") or []) if isinstance(r, dict) and r.get("url")]
    if not rows:
        return []
    # Custody became a requirement at schema 1.8. An older sidecar predates the rule and
    # is flagged, never refused: a gate that fails a file written before it existed is a
    # gate nobody can adopt.
    try:
        version = tuple(int(x) for x in str(data.get("sourced") or "1.0").split(".")[:2])
    except ValueError:
        version = (1, 0)
    if version < (1, 8):
        return []            # the rule did not exist when this file was written
    archived = [r for r in rows if (r.get("archiveUrl") or "").strip()]
    if not archived:
        return [Finding(
            FAIL, f"none of the {len(rows)} cited sources has an archiveUrl, so every quote "
                  f"rests on a file we hold ourselves. Re-run each with `--archive`. If the "
                  f"archive service refused, say so on the row and in Limitations; a whole "
                  f"paper with nothing archived is not an outage.")]
    missing = [r.get("id") for r in rows if not (r.get("archiveUrl") or "").strip()]
    if missing:
        return [Finding(
            FLAG, f"{len(missing)} cited source(s) have no third-party copy: "
                  f"{', '.join(str(m) for m in missing[:6])}"
                  f"{' ...' if len(missing) > 6 else ''}. Their quotes rest on our capture "
                  f"alone, which is a limit on the evidence and belongs in Limitations.")]
    return []


def _boundary_prompts(data, claims):
    """Flags for an evidence row recorded `mixed` on a claim that carries no boundary.

    A source that cuts both ways is already telling you where the boundary is, so it does
    not need another source to disagree with, and `conflicts.py` raises nothing for it.
    What it needs is for somebody to write the boundary down. So this asks, once per row,
    and it goes silent as soon as the claim it names carries a boundary record: the
    question has been answered and repeating it is how a flag gets ignored.

    It is a flag and never a refusal. Whether a boundary can be drawn from one mixed
    source is the author's judgement, and the exit code stays 0.
    """
    out = []
    for row in data.get("evidence") or []:
        if not isinstance(row, dict):
            continue
        try:
            sup = conflicts.supports_of(row)
        except ValueError:
            continue
        if not sup or sup[1] != conflicts.MIXED:
            continue
        cid = sup[0]
        if boundary.has_boundary(claims.get(cid) or {}):
            continue
        out.append(Finding(
            FLAG, f"evidence {conflicts._label(data, row.get('id'))} cuts both ways on "
                  f"claim {cid}: it is recorded {conflicts.MIXED!r}, so it supports the "
                  f"claim in one region and undermines it in another. Has the boundary "
                  f"been recorded? Write `holds_when`, `fails_when`, `replaced_by` and "
                  f"`unknown_region` on {cid}, and this flag goes."))
    return out


def _unconfirmed(data):
    """Flags for a stored conflict whose two sides both rest on a model-proposed support.

    One author-set side is enough to clear it: a person has looked at the disagreement. A
    model-proposed support on a row that is part of no conflict raises nothing, because an
    unused proposal harms nobody.
    """
    out = []
    rows = {r.get("id"): r for r in data.get("evidence") or [] if isinstance(r, dict)}
    for rec in data.get("conflicts") or []:
        if not isinstance(rec, dict):
            continue
        sides = [s.get("evidence") for s in rec.get("between") or [] if isinstance(s, dict)]
        seen = []
        for eid in sides:
            try:
                prov = conflicts.support_provenance(rows.get(eid) or {})
            except ValueError:
                prov = None
            if prov:
                seen.append(prov)
        if len(seen) != 2 or any(by != conflicts.MODEL for by, _ in seen):
            continue
        named = sorted({name for _, name in seen if name})
        who = ", ".join(named) if named else "a model that did not name itself"
        pair = " and ".join(conflicts._label(data, eid) for eid in sides)
        out.append(Finding(
            FLAG, f"conflict {rec.get('id')} on claim {rec.get('claim')} was proposed by "
                  f"{who}: {pair} both carry a model-set `supports`, and no person has "
                  f"confirmed either side. Confirm or correct the two `supports` values "
                  f"and set `by` to \"author\". The gate refuses on the recorded field, "
                  f"so a wrong proposal is a visible wrong row somebody can fix, where a "
                  f"wrong verdict would be invisible."))
    return out


def _forecasts(claims, today=None):
    """Flags for a predictive claim whose resolution date has passed with no outcome.

    `kinds.validate_kinds` already refuses a predictive claim with no resolution, so the
    only thing left to say here is that the date arrived and nobody checked.
    """
    today = today or datetime.date.today()
    out = []
    for cid, claim in claims.items():
        if claim.get("assertion") != "predictive":
            continue
        resolves = claim.get("resolves") or {}
        if resolves.get("outcome"):
            continue
        try:
            by = datetime.date.fromisoformat(str(resolves.get("by")))
        except ValueError:
            # An unreadable date is not a missed review. A date is never invented here.
            continue
        if by < today:
            out.append(Finding(FLAG, f"claim {cid} was to resolve by {resolves['by']} "
                                     f"and records no outcome, so a forecast whose date "
                                     f"has arrived has not been checked"))
    return out


# Words that only appear in a claim because the argument has a direction in it. A claim
# using one is asserting movement, and movement is a forecast whether or not it is
# written as one.
# ponytail: a word list, not a classifier. It catches the article that argues a trend
# and stakes nothing on it, which is the case this gate was added for; a parser that
# understood tense would catch more, and can replace this the day it earns its keep.
DIRECTION = ("decay", "decays", "decaying", "declin", "shrink", "erod", "rising",
             "falling", "heading toward", "heading towards", "trajectory",
             "will stop", "stops predicting", "is becoming", "increasingly",
             "every year", "year on year", "over time")


def _unstaked(claims):
    """Flags an argument that turns on a direction while staking nothing on it.

    A claim about movement is a forecast in the present tense. If the sidecar carries one
    and no claim anywhere is `predictive`, the direction is being asserted rather than
    made: nothing carries a date, nothing carries a criterion, and no reader can ever
    hold it to anything. The burden is symmetric, so this catches the claim that things
    will continue as readily as the claim that they will change.
    """
    if any(c.get("assertion") == "predictive" for c in claims.values()):
        return []
    out = []
    for cid, claim in claims.items():
        # Only lived experience is exempt. A `position` is NOT: demoting a directional
        # claim to a stance to escape the resolution is the exact move rule S names, and
        # an earlier version of this check skipped positions and therefore passed the
        # artefact it was written for.
        if claim.get("kind") == "story":
            continue
        statement = (claim.get("statement") or "").lower()
        hit = next((w for w in DIRECTION if w in statement), None)
        if hit:
            out.append(Finding(FLAG, f"claim {cid} turns on a direction ({hit!r}) and no "
                                     f"claim in this file is predictive, so the argument "
                                     f"rests on movement it never stakes: give one claim "
                                     f"an assertion of \"predictive\" with a resolves "
                                     f"date and criterion, or reword it as a state"))
    return out[:1]  # One finding names the fault; a list of them is the same fault.


def _stale(data, claims):
    """Flags for evidence whose period ends before the period of the claim it is cited for."""
    out = []
    for row in data.get("evidence") or []:
        if not isinstance(row, dict):
            continue
        for raw, parsed in _periods(row, "conditions"):
            label = conflicts._label(data, row.get("id"))
            if parsed is None:
                out.append(Finding(FLAG, f"evidence {label} records a period of {raw!r}, "
                                         f"which cannot be read as a year, so staleness "
                                         f"was not checked"))
                continue
            for cid in _cited_claims(data, row):
                for subject_raw, subject in _periods(claims.get(cid) or {},
                                                     "holds_when", "fails_when"):
                    if subject and parsed[1] < subject[0]:
                        out.append(Finding(
                            FLAG, f"evidence {label} covers {raw}, and claim {cid} is "
                                  f"about {subject_raw}, so the evidence finished before "
                                  f"the subject it is cited for began"))
    return out


def check_sidecar(path):
    """True when nothing fails. Prints every finding, flags included.

    A file that cannot be read or parsed fails the gate rather than raising. This
    script runs on the way out of a delivery, and a traceback there reads as a broken
    tool rather than as a refusal.
    """
    try:
        data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError) as e:
        print(f"UNREADABLE: {path}\n\n  {e}\n")
        print(f"FAILED: {path}")
        return False
    if not isinstance(data, dict):
        print(f"UNREADABLE: {path}\n\n  a sidecar is a JSON object, not {type(data).__name__}\n")
        print(f"FAILED: {path}")
        return False
    found = findings(data)
    bad = [f for f in found if f.severity == FAIL]
    soft = [f for f in found if f.severity == FLAG]
    if bad:
        print(f"UNINTEGRATED: {len(bad)} disagreement(s) this delivery does not show "
              f"the reader.\n")
        for f in bad:
            print(f"  {f.message}\n")
        print(HINT + "\n")
    for f in soft:
        print(f"  flag  {f.message}")
    if soft:
        print("\nA flag does not fail this gate. It is a soft signal read off periods "
              "written by hand, and it is for the author to judge.\n")
    print(("clean" if not bad else "FAILED") + f": {path}")
    return not bad


def _self_check():
    """Seventeen cases with known answers, no network. The threshold is all sixteen: this
    file is the last thing between a hidden disagreement and a reader."""

    def cond(dimension, value, basis="observed"):
        return {"dimension": dimension, "value": value, "basis": basis}

    def ev(eid, claim, direction, *conditions):
        return {"id": eid, "quote": "…", "locator": f"p. {eid[1:]}",
                "supports": {"claim": claim, "direction": direction},
                "conditions": list(conditions)}

    clean = ev("e1", "c1", "for", cond("air quality", "clean"))
    dirty = ev("e2", "c1", "against", cond("air quality", "hazy"))
    plain = {"claims": [{"id": "c1", "statement": "The sky is blue."}],
             "evidence": [clean, dirty]}

    # Every fixture defines the dimensions its conditions use. The dimensions gate is a
    # refusal, so a fixture that skipped it would fail for a reason the case is not about.
    # `case_dimensions_undefined` is the one that deliberately does not.
    DIMS = {"air quality": "visible haze, clear or hazy",
            "sun angle": "degrees above the horizon",
            "night": "sun below the horizon",
            "severity": "baseline score on the trial's own scale",
            "period": "calendar years the observation covers"}

    cond_free = {"statement": "s", "challenged": "holds", "origin": "adversarial",
                 "holds_when": [{"dimension": "air quality", "value": "clean", "basis": "observed"}]}

    def defined(data):
        return dict(data, dimensions=DIMS) if "dimensions" not in data else data

    def severities(data, severity):
        return [f for f in findings(defined(data)) if f.severity == severity]

    def case_open_conflict():
        rec = dict(conflicts.detect(plain)[0], unknown_region="nobody has looked at dusk.")
        bad = severities(dict(plain, conflicts=[rec]), FAIL)
        assert len(bad) == 1, bad
        for part in ("e1", "p. 1", "e2", "p. 2", "c1", "air quality", "x1"):
            assert part in bad[0].message, f"the message must name {part}: {bad[0].message}"

    def case_open_conflict_disclosed():
        """An open conflict the reader was told about ships. That is the documented path."""
        rec = dict(conflicts.detect(plain)[0], unknown_region="nobody has looked at dusk.")
        told = dict(plain, conflicts=[rec],
                    disclosure={"limitations": "On c1, two readings disagree on air quality, "
                                               "and dusk is unmapped."})
        assert severities(told, FAIL) == [], severities(told, FAIL)
        # ... and the same conflict with a disclosure that names some other claim does not.
        wrong = dict(told, disclosure={"limitations": "On c9, something else entirely."})
        assert len(severities(wrong, FAIL)) == 1, severities(wrong, FAIL)

    def case_unrecorded():
        bad = severities(plain, FAIL)
        assert len(bad) == 1, bad
        for part in ("e1", "p. 1", "e2", "p. 2", "c1", "air quality"):
            assert part in bad[0].message, f"the message must name {part}: {bad[0].message}"

    def case_boundary_recorded():
        held = {"id": "c1", "statement": "The sky is blue.",
                "holds_when": [cond("air quality", "clean", "tested")],
                "fails_when": [cond("air quality", "hazy", "tested")],
                "replaced_by": "c2",
                "unknown_region": "dusk, and every latitude above 60 degrees."}
        # c2 is a replacement claim, so the rival-parity gate asks it for the same work
        # as the claim it replaced: a falsifier and a region.
        replacement = {"id": "c2", "statement": "The sky is white in haze.",
                       "holds_when": [cond("air quality", "hazy", "tested")],
                       "falsifier": "a hazy sky photographed as blue at midday"}
        data = {"claims": [held, replacement],
                "evidence": plain["evidence"]}
        assert severities(data, FAIL) == [], severities(data, FAIL)
        # The same disagreement written up as a resolved conflict passes as well.
        resolved = dict(conflicts.detect(plain)[0], state="resolved", resolved_into="c1")
        assert severities(dict(data, conflicts=[resolved]), FAIL) == []

    def case_no_replacement():
        data = {"claims": [{"id": "c1", "statement": "The sky is blue.",
                            "fails_when": [cond("air quality", "hazy", "tested")]}],
                "evidence": []}
        bad = severities(data, FAIL)
        assert len(bad) == 1 and "c1" in bad[0].message, bad
        assert "true instead" in bad[0].message, bad[0].message
        # An empty `replaced_by` is no replacement at all.
        empty = {"claims": [dict(data["claims"][0], replaced_by="")], "evidence": []}
        assert len(severities(empty, FAIL)) == 1, severities(empty, FAIL)

    def case_periods():
        assert parse_period("2019") == (2019, 2019)
        assert parse_period("2019-2021") == (2019, 2021)
        assert parse_period("2019 to 2021") == (2019, 2021)
        assert parse_period("2019–2021") == (2019, 2021)
        assert parse_period("2021-2019") == (2019, 2021)
        assert parse_period("2019-03-04") == (2019, 2019)
        for text in ("recently", "", None, "the 2020s", "19th century", "2019-13"):
            assert parse_period(text) is None, text

    def case_stale_flags_only():
        old = {"id": "e3", "locator": "p. 3", "conditions": [cond("period", "2010-2012")]}
        claim = {"id": "c1", "statement": "Agents write most code.", "evidence": ["e3"],
                 "holds_when": [cond("Period", "2026", "observed")]}
        data = {"claims": [claim], "evidence": [old]}
        soft = severities(data, FLAG)
        assert len(soft) == 1, soft
        for part in ("e3", "2010-2012", "c1", "2026"):
            assert part in soft[0].message, f"the message must name {part}: {soft[0].message}"
        assert severities(data, FAIL) == [], "a flag never fails the gate"
        # Evidence that overlaps the subject is not stale.
        fresh = dict(data, evidence=[dict(old, conditions=[cond("period", "2026")])])
        assert severities(fresh, FLAG) == [], severities(fresh, FLAG)
        # A period nobody can parse is reported as unparsed, never guessed.
        vague = dict(data, evidence=[dict(old, conditions=[cond("period", "recently")])])
        unparsed = severities(vague, FLAG)
        assert len(unparsed) == 1 and "cannot be read" in unparsed[0].message, unparsed

    def case_precise_claim_needs_a_precise_citation():
        cited = {"id": "e9", "quote": "Scattering varies as the inverse fourth power.",
                 "locator": "p. 178"}
        claim = {"id": "c3", "level": 3, "evidence": ["e9"],
                 "statement": "Rayleigh scattering goes as the inverse fourth power."}
        good = {"claims": [claim], "evidence": [cited]}
        assert severities(good, FAIL) == [], severities(good, FAIL)
        # The same claim with a quote and no locator cannot be followed back.
        thin = {"claims": [claim], "evidence": [{"id": "e9", "quote": cited["quote"]}]}
        bad = severities(thin, FAIL)
        assert len(bad) == 1, bad
        for part in ("c3", "level 3", "quote and a locator", "level 2"):
            assert part in bad[0].message, f"the message must name {part}: {bad[0].message}"
        # Stating the same claim coarsely on the same thin evidence is allowed.
        low = {"claims": [dict(claim, level=2)], "evidence": thin["evidence"]}
        assert severities(low, FAIL) == [], severities(low, FAIL)

    def case_model_proposed_conflict():
        def proposed(row):
            return dict(row, supports=dict(row["supports"], by="model",
                                           model="claude-opus-5"))

        rec = dict(conflicts.detect(plain)[0], state="resolved", resolved_into="c1")
        held = {"id": "c1", "statement": "The sky is blue.",
                "holds_when": [cond("air quality", "clean", "tested")],
                "unknown_region": "dusk."}
        both = {"claims": [held], "evidence": [proposed(clean), proposed(dirty)],
                "conflicts": [rec]}
        soft = severities(both, FLAG)
        assert len(soft) == 1, soft
        for part in ("x1", "e1", "e2", "c1", "claude-opus-5", "supports"):
            assert part in soft[0].message, f"the message must name {part}: {soft[0].message}"
        assert severities(both, FAIL) == [], "a proposal never fails the gate"
        with contextlib.redirect_stdout(io.StringIO()):
            import tempfile
            with tempfile.TemporaryDirectory() as d:
                f = pathlib.Path(d) / "x.sourced"
                f.write_text(json.dumps(defined(both)), encoding="utf-8")
                assert check_sidecar(f) is True, "the flag must not change the exit code"
        # One author-set side is enough: a person has looked at the disagreement.
        one = dict(both, evidence=[clean, proposed(dirty)])
        assert severities(one, FLAG) == [], severities(one, FLAG)
        # A model-proposed support on a row in no conflict raises nothing.
        loose = {"claims": [held], "evidence": [proposed(clean)]}
        assert severities(loose, FLAG) == [], severities(loose, FLAG)

    def case_rival_claim_carries_its_own_work():
        # A claim the pass wrote and promoted, with nothing on it. Round 02 shipped ten of
        # these in one topic and three in another, and the three were holding the position.
        bare = {"id": "r1", "statement": "The sky reads grey under haze.",
                "origin": "adversarial", "challenged": "holds"}
        data = {"claims": [{"id": "c1", "statement": "The sky is blue."}, bare],
                "evidence": []}
        bad = severities(data, FAIL)
        assert len(bad) == 1 and "r1" in bad[0].message, bad
        assert "falsifier" in bad[0].message and "boundary" in bad[0].message, bad[0].message

        # Finish it and the refusal goes.
        done = dict(bare, falsifier="a hazy sky measured as blue at midday",
                    holds_when=[cond("air quality", "hazy", "tested")])
        assert severities(dict(data, claims=[data["claims"][0], done]), FAIL) == []

        # A claim the pass refuted needs neither: it is not carrying anything.
        dead = dict(bare, challenged="refuted")
        assert severities(dict(data, claims=[data["claims"][0], dead]), FAIL) == []

        # Nor does a definitional claim, which no observation can contradict.
        word = dict(bare, kind="definitional")
        assert severities(dict(data, claims=[data["claims"][0], word]), FAIL) == []

    def case_dimensions_must_be_defined():
        # dimensions.py was named as a step after round 01 and ran in none of the eight
        # runs across two rounds. A step nothing refuses on is not a step.
        claim = {"id": "c1", "statement": "The sky is blue.",
                 "holds_when": [cond("air quality", "clean", "tested")]}
        undefined = {"claims": [claim], "evidence": []}
        bad = [f for f in findings(undefined) if f.severity == FAIL]
        assert len(bad) == 1 and "air quality" in bad[0].message, bad
        assert "dimensions.py" in bad[0].message, bad[0].message

        # Defined as a map, and as a list of records: both are accepted.
        as_map = dict(undefined, dimensions={"air quality": "visible haze"})
        assert [f for f in findings(as_map) if f.severity == FAIL] == []
        as_list = dict(undefined, dimensions=[{"name": "Air Quality", "definition": "visible haze"}])
        assert [f for f in findings(as_list) if f.severity == FAIL] == [], "matching is case-insensitive"

    def case_falsifier_template_refused():
        # Round 03: nine rival claims, one stamped stem, specifics swapped out. It passed
        # a count and told a reader nothing.
        stem = "An observation showing this distinction makes no difference to the estimate"
        many = {"claims": [dict(cond_free, id=f"r{i}", falsifier=f"{stem}: c{i} fails to separate them")
                           for i in range(1, 5)], "evidence": []}
        bad = severities(many, FAIL)
        assert len(bad) == 1 and "template" in bad[0].message, bad
        assert "r1" in bad[0].message, bad[0].message

        # Two is not a pattern; distinct falsifiers pass however long they are.
        pair = dict(many, claims=many["claims"][:2])
        assert severities(pair, FAIL) == [], "two claims are not a template"
        varied = dict(many, claims=[dict(c, falsifier=f"A trial in population {i} reporting no gap")
                                    for i, c in enumerate(many["claims"])])
        assert severities(varied, FAIL) == [], severities(varied, FAIL)

    def case_narrow_proposition_asks_to_be_split():
        prop = {"id": "p1", "statement": "The sky is blue.", "role": "proposition",
                "falsifier": "a blue sky photographed grey at noon",
                "holds_when": [cond("air quality", "clean", "tested")],
                "fails_when": [cond("air quality", "hazy", "tested")],
                "replaced_by": "p1x", "unknown_region": "dusk"}
        lone = {"claims": [prop, {"id": "p1x", "statement": "The sky is grey in haze.",
                                  "falsifier": "a hazy sky measured blue",
                                  "holds_when": [cond("air quality", "hazy", "tested")]}],
                "evidence": []}
        soft = severities(lone, FLAG)
        assert any("p1" in f.message and "Split it" in f.message for f in soft), soft
        assert severities(lone, FAIL) == [], "asking for a split never fails the gate"

        # A proposition with a child answering it is satisfied.
        answered = dict(lone, claims=[prop, dict(lone["claims"][1], answers="p1")])
        assert not any("Split it" in f.message for f in severities(answered, FLAG))

    def case_mixed_asks_for_the_boundary():
        both = ev("e9", "c1", "mixed", cond("air quality", "hazy"))
        naked = {"claims": [{"id": "c1", "statement": "The sky is blue."}],
                 "evidence": [both]}
        soft = severities(naked, FLAG)
        assert len(soft) == 1, soft
        for part in ("e9", "p. 9", "c1", "mixed", "boundary"):
            assert part in soft[0].message, f"the message must name {part}: {soft[0].message}"
        assert severities(naked, FAIL) == [], "a mixed row never fails the gate"
        with contextlib.redirect_stdout(io.StringIO()):
            import tempfile
            with tempfile.TemporaryDirectory() as d:
                f = pathlib.Path(d) / "x.sourced"
                f.write_text(json.dumps(defined(naked)), encoding="utf-8")
                assert check_sidecar(f) is True, "the flag must not change the exit code"
        # The same row on a claim that already carries a boundary asks nothing, because
        # the question has been answered.
        held = {"id": "c1", "statement": "The sky is blue.",
                "holds_when": [cond("air quality", "clean", "tested")],
                "fails_when": [cond("air quality", "hazy", "tested")],
                "replaced_by": "The sky reads grey under haze.",
                "unknown_region": "dusk, and every latitude above 60 degrees."}
        answered = {"claims": [held], "evidence": [both]}
        assert severities(answered, FLAG) == [], severities(answered, FLAG)
        # And a mixed row raises no conflict beside a row pointing the other way.
        beside = {"claims": [{"id": "c1", "statement": "The sky is blue."}],
                  "evidence": [clean, both]}
        assert severities(beside, FAIL) == [], severities(beside, FAIL)

    def case_claim_against_claim():
        # An adversarial pass hands you a rival claim, not two sources. An open conflict
        # between two claims fails the gate like any other, and the message names both.
        rival = {"id": "c9", "statement": "The sky reads grey under haze.",
                 "holds_when": [cond("air quality", "hazy", "tested")],
                 "unknown_region": "dusk under haze."}
        held = {"id": "c1", "statement": "The sky is blue.",
                "holds_when": [cond("air quality", "clean", "tested")],
                "fails_when": [cond("sun angle", "near the horizon", "tested")],
                "replaced_by": {"claim": "c9"}, "challenged": "holds-with-boundary",
                "unknown_region": "dusk, and every latitude above 60 degrees."}
        rec = {"id": "x2", "claim": "c1",
               "between": [{"evidence": "e1", "outcome": "for"}, {"claim": "c9"}],
               "dimensions": ["air quality"], "state": "open",
               "unknown_region": "dusk under haze."}
        data = {"claims": [held, rival], "evidence": [clean], "conflicts": [rec]}
        bad = severities(data, FAIL)
        assert len(bad) == 1, bad
        for part in ("x2", "e1", "p. 1", "claim c9", "grey under haze", "air quality"):
            assert part in bad[0].message, f"the message must name {part}: {bad[0].message}"
        # Resolved into the claim that carries the boundary, it passes.
        closed = dict(rec, state="resolved", resolved_into="c1")
        del closed["unknown_region"]
        assert severities(dict(data, conflicts=[closed]), FAIL) == []
        # A `replaced_by` naming a claim is a replacement, so the refutation is answered.
        assert not any("true instead" in f.message
                       for f in severities(dict(data, conflicts=[closed]), FAIL))

    def case_unreadable():
        # A file the gate cannot read fails it, and does so without a traceback.
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            bad = pathlib.Path(d) / "broken.sourced"
            bad.write_text("not json at all", encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                assert check_sidecar(bad) is False, "unreadable must fail the gate"
                assert check_sidecar(pathlib.Path(d) / "absent.sourced") is False
        # and a date that is not a date is unparsed rather than half read
        assert parse_period("2019-13-99") is None, "an impossible date is not a period"

    def case_plain_sidecar():
        old = json.loads(pathlib.Path(__file__).resolve().parents[2]
                         .joinpath("README.md.sourced").read_text(encoding="utf-8"))
        assert findings(old) == [], findings(old)
        assert findings({}) == [] and findings({"claims": [], "evidence": []}) == []

    def case_forecast_past_its_date():
        def forecast(by, **extra):
            resolves = {"by": by, "criterion": "The published index for that month."}
            resolves.update(extra)
            return {"claims": [{"id": "c1", "statement": "The index falls.",
                                "kind": "empirical", "assertion": "predictive",
                                "resolves": resolves}], "evidence": []}
        past = forecast("2020-01-31")
        assert severities(past, FAIL) == [], severities(past, FAIL)
        soft = severities(past, FLAG)
        assert len(soft) == 1 and "c1" in soft[0].message, soft
        assert "2020-01-31" in soft[0].message, soft
        # A date still ahead of us says nothing, and a recorded outcome closes it.
        assert findings(forecast("2999-01-31")) == []
        for word in ("true", "false", "ambiguous", "unresolved"):
            assert findings(forecast("2020-01-31", outcome=word)) == [], word
        # An unreadable date is not a missed review, and a date is never invented.
        assert findings(forecast("early next year")) == []
        # An empirical claim with no assertion is not a forecast and is never flagged.
        assert findings({"claims": [{"id": "c1", "kind": "empirical"}],
                         "evidence": []}) == []

    def case_unstaked_direction():
        # A claim that argues movement while the file stakes nothing on it flags once...
        moving = {"claims": [{"id": "c1", "kind": "empirical",
                              "statement": "The signal decays as the systems improve."}]}
        flagged = severities(moving, FLAG)
        assert len(flagged) == 1, flagged
        assert "predictive" in flagged[0].message, flagged[0].message
        # ... and goes quiet as soon as one claim carries a date and a criterion.
        staked = {"claims": moving["claims"] + [
            {"id": "c2", "kind": "empirical", "assertion": "predictive",
             "statement": "It reaches zero on bounded work.",
             "resolves": {"by": "2028-01-01", "criterion": "the published rate reads 0"}}]}
        assert severities(staked, FLAG) == [], severities(staked, FLAG)
        # A stance is NOT exempt: demoting a direction to a position to dodge the
        # resolution is the move the rule exists to catch.
        stance = {"claims": [{"id": "c1", "kind": "position", "falsifier": "a flat year",
                              "statement": "The signal decays as systems improve."}]}
        assert len(severities(stance, FLAG)) == 1, severities(stance, FLAG)
        # Lived experience is exempt.
        told = {"claims": [{"id": "c1", "kind": "story", "witness": "Andrew",
                            "statement": "It decayed on me over time."}]}
        assert severities(told, FLAG) == [], severities(told, FLAG)

    cases = [("an argument that turns on a direction stakes a forecast",
              case_unstaked_direction),
             ("an open conflict fails, and the message names both sources", case_open_conflict),
             ("an open conflict named in Limitations ships, an undisclosed one does not",
              case_open_conflict_disclosed),
             ("evidence that disagrees with nothing recorded fails", case_unrecorded),
             ("the same disagreement with a boundary recorded passes", case_boundary_recorded),
             ("fails_when with no replaced_by fails", case_no_replacement),
             ("a period is read, a range is read, and nothing else is guessed", case_periods),
             ("stale evidence flags and does not fail", case_stale_flags_only),
             ("a plain 1.2 sidecar passes untouched", case_plain_sidecar),
             ("a level-3 claim without a quote and a locator fails",
              case_precise_claim_needs_a_precise_citation),
             ("a conflict proposed by a model on both sides flags and does not fail",
              case_model_proposed_conflict),
             ("a rival claim the pass wrote carries a falsifier and a region",
              case_rival_claim_carries_its_own_work),
             ("a boundary naming an undefined dimension fails the delivery",
              case_dimensions_must_be_defined),
             ("falsifiers sharing one stamped template are refused",
              case_falsifier_template_refused),
             ("a narrow proposition is asked to split, and it is a flag not a refusal",
              case_narrow_proposition_asks_to_be_split),
             ("a mixed row asks for the boundary, and stops once it is recorded",
              case_mixed_asks_for_the_boundary),
             ("an unreadable file fails without a traceback", case_unreadable),
             ("an open conflict against a competing claim fails, and names it",
              case_claim_against_claim),
             ("a forecast past its date with no outcome flags and does not fail",
              case_forecast_past_its_date)]
    passed = 0
    for label, fn in cases:
        try:
            fn()
            passed += 1
            print(f"pass  {label}")
        except AssertionError as e:
            print(f"FAIL  {label}: {e}")
    total = len(cases)
    print(f"\nintegrate: self-check {'passed' if passed == total else 'FAILED'} "
          f"({passed} of {total} cases; the threshold is {total} of {total})")
    return passed == total


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or "--self-check" in args:
        sys.exit(0 if _self_check() else 1)
    sys.exit(0 if check_sidecar(args[0]) else 1)
