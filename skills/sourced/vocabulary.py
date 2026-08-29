#!/usr/bin/env python3
"""One vocabulary for the book, the sidecar and the claim record.

    python3 vocabulary.py --self-check     thirteen cases, known answers, no network
    python3 vocabulary.py conflicts        where the three systems disagree
    python3 vocabulary.py <file.sourced>   per claim: derived state, label, kind

Three systems hold claims. This repo (SOURCED 1.7) holds them in a `.sourced` sidecar.
Publish holds them in a claim ledger anchored into prose. System C holds them as Claim
Record v1, and that record is the standard its own family of applications writes to.
Until now this file mapped two of the three, so the same claim could still be described
two ways, and that drift is what put "no evidence is offered" into a deck that was one
slide away from the evidence. This file states the mapping once.

**It maps three systems and resolves nine of the ten disagreements.** SOURCED 1.7 is this
repo's implementation. v3, v4, v5, v6, v8, v9 and v10 were decided on 29 August 2026 and
this repo moved to System C's reading on all seven, because System C extracts claims by
machine at corpus scale and its shapes have been tested against more claims than this
repo has written. v2 alone stands open, and this repo has not moved on it.
`conflicts()` below records every difference found, with what each system says, what
leaving it open costs, and what was decided where something was. See
`docs/vocabulary-map.md`.

THREE AXES, NEVER ONE NUMBER
----------------------------
Publish's 0 to 4 is described as one scale and it is not:

    0 unanalysed                          neither axis
    1 evidence sought, none found         PROCESS, and backing of none
    2 single source                       BACKING
    3 multi-source corroborated           BACKING
    4 boundary recorded                   PROCESS

Tiers 1 and 4 are facts about what was DONE TO the claim. Tiers 2 and 3 are facts about
what SUPPORTS it. A claim that carries a boundary record while resting on one
self-interested source is a 4 and a 2 at the same time, and one number cannot say so.
An earlier version of this file put all of 0 to 4 onto a single `strength` axis, which
is precisely the mistake the ADR exists to prevent. `MAP` now reports `backing` and
`process` separately, and the 0 to 4 ladder survives as a PRESENTATION computed from
them rather than as a stored field.

`position` and `story` are KINDS. They carry neither backing nor process, because they
are their own species of sentence and not weak tiers (docs/framework.md, position 7).

Provenance (sourced, recalled, inferred) and fidelity (quotation, paraphrase,
inference) are INDEPENDENT of all seven, so the map says so in every row rather than
leaving them out. Silence in a mapping table reads as "not applicable", which is a
different and wrong statement.

NOTHING IS GUESSED, AND A GAP IS NAMED
--------------------------------------
Where the sidecar cannot answer a System C field, the map says `not-recorded`. It never
infers one. A guessed mapping is indistinguishable from a correct one until somebody
acts on it, which is also why `unmapped()` reports an unknown state by name.

STATE IS DERIVED AND NEVER STORED
---------------------------------
`docs/framework.md` position 7 already requires it, and `publish_state()` below computes
it from the evidence rows. A sidecar carrying a stored `strength` or `tier` on a claim is
REFUSED rather than read, because a stored number goes stale the moment a source moves
and nothing tells the reader that it has.

A DERIVED NUMBER MUST SAY WHY IT IS WHAT IT IS
----------------------------------------------
v10, decided 29 August 2026. A number with no account of itself is the thing this
framework objects to everywhere else, so `backing()` returns the number AND the named
reasons, in the Claim Record's own words: `downgrades` from the seven, `upgrades` from
the four. Only what the sidecar can actually see is derived. `single-source` comes from
one distinct `originGroup`, `self-interested-source` from a row that says so,
`inconsistency` from an opposed pair or a recorded conflict, and `imprecision` from
evidence that carries no quote and no locator. `risk-of-bias`, `indirectness` and
`publication-bias` stay in the vocabulary and stay UNSET, because a sidecar holds nothing
that answers them and a guessed reason reads exactly like a derived one. No upgrade is
derived at all: `originGroup` is a label an author types, so reading independent
replication off it would assert a research fact from a bookkeeping field.

State is not sophistication. Sophistication is an unbounded ladder saying how precisely a
statement is phrased. The two share the habit of reading the evidence rows and nothing
else.

ponytail: dicts and small functions. No registry, no adapters, no schema loader. The
ceiling is a fourth system, and `unmapped()` plus `SYSTEM_C`'s explicit `not-recorded` rows
are what make that arrive as a named report rather than as a silent wrong answer.
"""
import json
import pathlib
import sys
from collections import namedtuple

import boundary
import conflicts as conflicts_mod
import kinds
import shared_claims

# The seven states, exactly as `src/lib/claims/types.ts` `TierSchema` defines them. The
# tiers travel as integers here and as the strings '0' to '4' in Publish's label record.
STATES = (0, 1, 2, 3, 4, "position", "story")

# What a state does NOT decide. Written into every row on purpose: see the module note.
INDEPENDENT = "independent of the state"

# What this repo cannot answer. Never a guess, never an inferred default.
NOT_RECORDED = "not-recorded"

# state -> the axes. Backing and process are separate.
#   kind      position or story, or None when the state is silent on kind
#   assertion the finer rung under `kind`, or None when the state cannot name one. Only
#             `story` can: `narrative` is the only assertion under it. A `position` state
#             covers both `normative` and `interpretive`, so the coarse state does not
#             say which, and that is a fact about the state rather than a gap.
#   backing   what supports the claim: 0 none recorded, 1 none found, 2 single origin,
#             3 corroborated. None when the state reports no backing fact at all.
#   process   what was done to the claim, or None when the state reports no process fact.
MAP = {
    0: {"kind": None, "backing": None, "process": None},
    1: {"kind": None, "backing": 1, "process": "evidence-sought"},
    2: {"kind": None, "backing": 2, "process": None},
    3: {"kind": None, "backing": 3, "process": None},
    4: {"kind": None, "backing": None, "process": "boundary-recorded"},
    "position": {"kind": "position", "backing": None, "process": None},
    "story": {"kind": "story", "backing": None, "process": None},
}
for _row in MAP.values():
    _row["provenance"] = INDEPENDENT
    _row["fidelity"] = INDEPENDENT
    _row["assertion"] = None
# The one state that names its finer rung: `narrative` is the only assertion under `story`.
MAP["story"]["assertion"] = "narrative"

# The plain-English label for each state. These strings are Publish's `TIER_LABEL`
# VERBATIM, which is the whole point of the file: the book and the sidecar say the same
# words about one claim. They are therefore identifiers rather than prose, and the
# American spelling in 'unanalyzed' stays as Publish stores it.
LABELS = {
    0: "unanalyzed",
    1: "no / contradicted evidence",
    2: "single source",
    3: "multi-source",
    4: "boundary recorded",
    "position": "stance (evidence-exempt)",
    "story": "lived experience",
}

# A claim may not store its own state. Both spellings are refused: `tier` is what
# Publish calls it, `strength` is what a well-meaning sidecar author would call it.
STORED_STRENGTH_FIELDS = ("strength", "tier")

REFUSAL = ("strength is derived from the evidence rows and is never stored "
           "(docs/framework.md, position 7). Delete the field and let it be computed.")

# Why a claim's backing is as low as it is, and why it is as high as it is. The words are
# the Claim Record's `qualifier.downgrades` and `qualifier.upgrades` enums VERBATIM, so
# one claim is not described two ways and neither system has to translate on the way in.
DOWNGRADES = ("risk-of-bias", "inconsistency", "indirectness", "imprecision",
              "publication-bias", "self-interested-source", "single-source")
UPGRADES = ("large-effect", "dose-response", "confounders-would-reduce",
            "replicated-independently")

# The four a sidecar cannot see, listed here so the gap is named rather than left blank.
# `risk-of-bias`, `indirectness` and `publication-bias` are facts about how a study was
# run and what else was published, and nothing in a sidecar records either. The fourth is
# every upgrade: see the module note.
NOT_DERIVABLE = ("risk-of-bias", "indirectness", "publication-bias")

# The number and its reasons travel together, because a number that cannot say why it is
# what it is is exactly what v10 was about. `grade` is None for an evidence-exempt kind.
Backing = namedtuple("Backing", "grade downgrades upgrades")

# The O of SOURCED, per claim. The five words are the shared vocabulary agreed across the
# three systems on 29 August 2026 and are the Claim Record's `analysis.challenged` enum
# verbatim. **Absent reads as `not-attempted`**, the same way an absent `opposed` does: a
# pass nobody recorded is a pass nobody can show ran.
CHALLENGED = ("not-attempted", "attempted-unresolved", "holds", "holds-with-boundary",
              "refuted")
NOT_ATTEMPTED = "not-attempted"

# ---------------------------------------------------------------------------
# SOURCED field -> System C Claim Record v1 field.
#
# `match` is one of:
#   exact      identical values, no translation needed
#   partial    the same idea, different vocabulary or a different cut of it
#   none       System C holds it and this repo does not, or the reverse
# Every row that is not `exact` names what is lost, so a reader can see the cost of the
# translation rather than trusting the arrow.
SYSTEM_C = {
    "status": {
        "system_c": "no direct field; nearest is evidence[].role plus fidelity",
        "match": "partial",
        "note": "sourced/recalled/inferred says whether anything was retrieved. System C "
                "records retrieval per evidence row, not per claim, so a claim with no "
                "evidence rows reads as recalled or inferred and System C cannot say which.",
    },
    "fidelity": {
        "system_c": "fidelity",
        "match": "exact",
        "note": "quotation, paraphrase, inference. The same three values, same meaning.",
    },
    "kind": {
        "system_c": "species + assertionType",
        "match": "partial",
        "note": "System C splits one axis into two: species is claim/position/story, "
                "assertionType is empirical/synthesis/statistical/definitional/normative/"
                "interpretive/predictive/narrative. `kind` is the COARSE rung of that one "
                "ladder and `assertion` is the finer rung beside it, so nothing is lost "
                "in either direction. `synthesis` is now a value on both sides. What "
                "`kind` alone cannot say is which finer assertion a claim carrying no "
                "`assertion` holds.",
    },
    "assertion": {
        "system_c": "assertionType",
        "match": "exact",
        "note": "The same eight words, same meaning, no renames. `kinds.kind_of()` "
                "derives the coarse `kind` from it, and the mapping is total, so an "
                "assertion survives the trip in both directions (v5, decided 29 August "
                "2026).",
    },
    "resolves": {
        "system_c": "calibration.resolvesBy + calibration.resolutionCriterion + "
                 "calibration.resolvedOutcome",
        "match": "partial",
        "note": "Same meanings, shorter names: `by` is resolvesBy, `criterion` is "
                "resolutionCriterion, `outcome` is resolvedOutcome and takes the same "
                "four words. System C also carries priorProbability and currentProbability, "
                "and this repo records neither.",
    },
    "holds_when": {
        "system_c": "scope.holdsWhen[]",
        "match": "partial",
        "note": "Same role. `basis` and `status` now match System C's two fields (v3, "
                "decided 29 August 2026). The dimension and the comparator still "
                "differ: see conflicts() for v1 and v2.",
    },
    "fails_when": {
        "system_c": "scope.failsWhen[]",
        "match": "partial",
        "note": "Same role, same condition-shape differences.",
    },
    "unknown_region": {
        "system_c": "scope.outsideScope",
        "match": "partial",
        "note": "System C types it as unknown/assumed-false/contested. SOURCED writes prose.",
    },
    "supports.direction": {
        "system_c": "evidence[].direction",
        "match": "partial",
        "note": "for, against and mixed in both, since v6 was decided on 29 August "
                "2026. SOURCED reads a mixed row as a boundary rather than as a side "
                "of a conflict, which System C does not say either way.",
    },
    "conflicts[]": {
        "system_c": "relations[] with type 'contradicts'",
        "match": "partial",
        "note": "System C's relation points claim to claim. SOURCED's conflict points at "
                "two evidence rows under one claim, and carries state, differing "
                "dimensions and an unknown region that System C's relation has nowhere to "
                "put.",
    },
    "level": {
        "system_c": "resolutions[].level",
        "match": "exact",
        "note": "Both are ordered whole numbers from 1, both unbounded, and neither "
                "names its rungs since v4 was decided on 29 August 2026. The numbers "
                "are relative to one artefact, so nothing compares a level across two.",
    },
    "evidence[].originGroup": {
        "system_c": "evidence[].originGroup",
        "match": "exact",
        "note": "Sources sharing a group are one source for independence counting.",
    },
    "evidence[].sha256": {
        "system_c": "evidence[].fixity.sha256",
        "match": "exact",
        "note": "Hash of the bytes retrieved.",
    },
    "evidence[].textSha256": {
        "system_c": "evidence[].fixity.textSha256",
        "match": "exact",
        "note": "Hash of the normalised text.",
    },
    "evidence[].custodian": {
        "system_c": "evidence[].fixity.custodian",
        "match": "exact",
        "note": "self, third-party, self+third-party, none.",
    },
    "evidence[].archiveUrl": {
        "system_c": "evidence[].fixity.archiveUrl",
        "match": "exact",
        "note": "The archived copy, where one was taken.",
    },
    "evidence[].retrievedAt": {
        "system_c": "evidence[].retrievedAt",
        "match": "exact",
        "note": "The day the source was actually retrieved.",
    },
    "opposed.grade": {
        "system_c": "analysis.challenged",
        "match": "partial",
        "note": "SOURCED records the grade of pass that ran, for the whole artefact. "
                "System C records the outcome, per claim. Neither is derived from the "
                "other, and both are now recorded here: see `challenged`.",
    },
    "challenged": {
        "system_c": "analysis.challenged",
        "match": "exact",
        "note": "not-attempted, attempted-unresolved, holds, holds-with-boundary, "
                "refuted. The same five words with the same meanings, since v9 was "
                "decided on 29 August 2026. Absent reads as not-attempted in both.",
    },
    "backing reasons": {
        "system_c": "qualifier.downgrades[] and qualifier.upgrades[]",
        "match": "partial",
        "note": "The same two enums, and this repo derives four of the eleven values: "
                "single-source, self-interested-source, inconsistency and imprecision. "
                "A sidecar holds nothing that answers risk-of-bias, indirectness or "
                "publication-bias, and no upgrade is derived, so those read as "
                + NOT_RECORDED + " rather than as absent.",
    },
    "evidence[].selfInterested": {
        "system_c": "evidence[].selfInterested",
        "match": "exact",
        "note": "Does the source benefit from this claim being believed. Optional in "
                "both, and absent means nobody has said either way.",
    },
    "owner": {
        "system_c": "owner{name, verified, since}",
        "match": "partial",
        "note": "A named person who answers for the claim, since v8 was decided on "
                "29 August 2026. SOURCED calls the second field `checked` and requires "
                "it. `witness` stays a separate field on a story, naming who lived it; "
                "neither derives from the other.",
    },
    "disclosure": {
        "system_c": "provenanceBlock, at artefact level",
        "match": "partial",
        "note": "The same four labels. System C generates it from the claims; SOURCED "
                "stores it and checks it with integrate.py.",
    },
    "decisions[]": {
        "system_c": NOT_RECORDED,
        "match": "none",
        "note": "The R of SOURCED as a design log. System C's provenance[] is an event "
                "chain about one claim, which is a different object.",
    },
}


def unmapped(states):
    """The states with no row in MAP, by name. Reported, never guessed at.

    An eighth state arriving from Publish must show up here rather than being folded
    into whichever row looks closest, because a guessed mapping is indistinguishable
    from a correct one until somebody acts on it.
    """
    return [s for s in states if s not in MAP]


def refuse_stored_strength(data):
    """Raise AssertionError if any claim stores a strength. Returns True otherwise."""
    for i, claim in enumerate(data.get("claims") or []):
        if not isinstance(claim, dict):
            continue
        for field in STORED_STRENGTH_FIELDS:
            assert field not in claim, (
                f"claims[{claim.get('id') or i}] stores {field!r}: {REFUSAL}")
    return True


def _rows(claim, evidence_by_id):
    ids = [e for e in (claim.get("evidence") or []) if isinstance(e, str)]
    return ids, [evidence_by_id[e] for e in ids if e in evidence_by_id]


def publish_state(claim, evidence_by_id):
    """Publish's 0 to 4 presentation state, or None for an evidence-exempt kind.

    0  nothing was recorded
    1  evidence was sought and none was found, or a row contradicts the claim
    2  a single origin
    3  two or more distinct `originGroup` values
    4  tier 3, and a boundary is recorded on the claim

    This is a PRESENTATION, computed and never stored. It mixes the two axes on purpose,
    because that is what Publish's colour overlay reads. Read `backing()` and `process()`
    for the axes themselves. Tier 4 is `boundary recorded` and not `survived
    adversarial`, because what raises a claim is knowing where it holds and where it
    fails, not knowing that it won.
    """
    for field in STORED_STRENGTH_FIELDS:
        assert field not in claim, f"claims[{claim.get('id')}] stores {field!r}: {REFUSAL}"
    if claim.get("kind") in ("position", "story"):
        return None
    ids, rows = _rows(claim, evidence_by_id)
    if not ids:
        return 0
    cid = claim.get("id")
    for row in rows:
        sup = conflicts_mod.supports_of(row)
        if sup and sup[0] == cid and sup[1] == "against":
            return 1
    if not rows:
        return 1  # ids were written, so evidence was sought, and none of it is here
    # One collapse rule for origins, shared with claims.py, so a press release written up
    # ten times cannot become ten sources on either side of the wall. It lives in
    # shared_claims, which imports nothing local, so there is no cycle to defer around.
    if len(shared_claims.origins({"evidence": rows})) < 2:
        return 2
    # boundary.py owns the field list, so tier 4 cannot drift from what a boundary is.
    return 3 + int(boundary.has_boundary(claim))


# Kept as the old name because docs/framework.md and docs/sidecar.md still say it.
# It derives the presentation state, not the backing axis: use backing() for that.
strength = publish_state


def _inconsistent(claim, evidence_by_id, data):
    """True when this claim carries an opposed pair or a recorded conflict.

    Both are the same fact said two ways: the sources under this claim do not agree. A
    malformed `supports` is read as no opposition here rather than raised, because
    `conflicts.validate_conflicts` is what refuses it and a reason-lister is not a gate.
    """
    cid = claim.get("id")
    try:
        for a, _b in conflicts_mod.opposed_pairs({"evidence": list(evidence_by_id.values())}):
            if conflicts_mod.supports_of(a)[0] == cid:
                return True
    except ValueError:
        pass
    for rec in (data or {}).get("conflicts") or []:
        if isinstance(rec, dict) and rec.get("claim") == cid:
            return True
    return False


def backing(claim, evidence_by_id, data=None):
    """The BACKING axis, as a `Backing(grade, downgrades, upgrades)`.

    `grade` is 0, 1, 2 or 3, and None for an evidence-exempt kind. A tier-4 claim is a
    tier-3 claim with a boundary record, so its backing is 3. The boundary is a process
    fact and lives on the other axis. This is the whole point of splitting the axes: a
    claim can be a 4 and a 2 at once, and only two fields can say so.

    `downgrades` and `upgrades` are the named reasons, in the Claim Record's own words.
    v10, decided 29 August 2026: a derived number that gives no account of itself is the
    move this framework objects to everywhere else, and the reason is the part a reader
    needs. **Only what the sidecar can see is derived.** The four reasons this repo can
    honestly assert are `single-source`, `self-interested-source`, `inconsistency` and
    `imprecision`; `NOT_DERIVABLE` names the three downgrades a sidecar holds nothing
    about, and no upgrade is derived at all. Pass `data` to let `inconsistency` read
    `conflicts[]` as well as the evidence rows.

    ponytail: reasons are a tuple built by four one-line tests, not a rule engine. The
    ceiling is that a claim store with study metadata can derive the other three; the
    upgrade path is to read them from that store, never to guess them from here.
    """
    grade = publish_state(claim, evidence_by_id)
    if grade is None:
        return Backing(None, (), ())
    grade = 3 if grade == 4 else grade
    ids, rows = _rows(claim, evidence_by_id)
    down = []
    if _inconsistent(claim, evidence_by_id, data):
        down.append("inconsistency")
    if rows and not any(r.get("quote") and r.get("locator") for r in rows):
        down.append("imprecision")
    if any(r.get("selfInterested") is True for r in rows):
        down.append("self-interested-source")
    if len(shared_claims.origins({"evidence": rows})) == 1:
        down.append("single-source")
    # No upgrade is derivable from a sidecar. See NOT_DERIVABLE and the module note.
    return Backing(grade, tuple(down), ())


def challenged_of(claim):
    """What the adversarial pass found about THIS claim, in the shared five words.

    **Absent reads as `not-attempted`**, the same way an absent `opposed` does. Nothing
    derives this from `opposed` and nothing derives `opposed` from this: `opposed` says
    which grade of pass ran over the artefact, and `challenged` says what the pass found
    about one claim. Neither answers the other's question.
    """
    return claim.get("challenged") or NOT_ATTEMPTED


def validate_challenged(data):
    """Raise AssertionError on a claim whose `challenged` is outside the five words.

    A sixth word is how a pass that reached no conclusion gets written up as one that
    held, so an unrecognised value is refused rather than read.
    """
    for i, claim in enumerate(data.get("claims") or []):
        if not isinstance(claim, dict) or "challenged" not in claim:
            continue
        value = claim["challenged"]
        assert value in CHALLENGED, (
            f"claims[{claim.get('id') or i}]: challenged {value!r} is not one of "
            f"{list(CHALLENGED)}")
    return True


def process(claim, data=None):
    """The PROCESS axis: what was done to this claim, from what the sidecar records.

    The sidecar records the grade of adversarial pass for the whole artefact in
    `opposed`, and records a boundary per claim. It does NOT record a per-claim challenge
    outcome, so System C's `analysis.challenged` reads as `not-recorded` whenever a pass ran.
    That gap is stated rather than filled, because the alternative is inventing a verdict.

    Since v9 was decided on 29 August 2026 a claim MAY carry its own `challenged`, and
    when it does that value is the answer and nothing is guessed. Where it does not, the
    old reading stands: `not-attempted` is the one value this repo can honestly assert
    from an artefact-wide record, because no `opposed` object, or a grade of
    `not-performed`, means nothing attacked the claim; a pass that did run says nothing
    about which claims it touched, so the per-claim outcome is `not-recorded`.
    """
    opposed = (data or {}).get("opposed") or {}
    grade = opposed.get("grade") or "not-performed"
    attempted = grade != "not-performed"
    recorded = claim.get("challenged")
    return {
        "opposed_grade": grade,
        "attempted": attempted,
        "boundary_recorded": bool(boundary.has_boundary(claim)),
        # The word `survived` is not written here. docs/philosophy.md position 8 removed
        # it, and the shared five words replaced it on 29 August 2026.
        "system_c_challenged": recorded if recorded else (
            NOT_RECORDED if attempted else NOT_ATTEMPTED),
    }


def conflicts():
    """Where the three systems disagree, and which disagreements have been decided.

    docs/philosophy.md position 8: a disagreement is a first-class object, not a decision
    made quietly in a draft. It applies to the vocabularies themselves. Each record says
    what SOURCED holds, what System C holds, what Publish holds where it has a view, and
    what leaving the disagreement open costs.

    A record that has been decided also carries `resolved`: what was decided and when. The
    record is not deleted, because the reason a repo held the other position is the part
    that stops it drifting back. Seven were decided on 29 August 2026 and shipped here:
    v3, v4, v6 and v8 in SOURCED 1.4, v9 and v10 in 1.6, and v5 in 1.7. v1 and v7 were
    decided in favour of work in the other two applications. v2 alone stands open, and
    this repo has not moved on it.
    """
    return [
        {
            "id": "v1",
            "topic": "condition dimension",
            "sourced": "Free text. docs/philosophy.md position 9 rejected a fixed list "
                       "on 28 August 2026, because conditions are as varied as the "
                       "subject matter. A per-project registry keeps them comparable.",
            "system_c": "A fixed enum of thirteen: place, time, population, sector, "
                     "organisation-size, technology, regulation, market, method, unit, "
                     "magnitude, role, other.",
            "publish": "No conditions at all. The agreed direction is that it gains them.",
            "cost": "A SOURCED condition on a dimension outside the thirteen lands in "
                    "System C as `other`, so two different boundaries become one bucket and "
                    "the contradiction graph stops being able to compare them.",
            "resolved": "29 August 2026, in favour of SOURCED, with work on the other "
                        "side. Free text and the per-project registry stay here, because "
                        "philosophy position 9 rejected a fixed list and the reasons have "
                        "not changed. The closed list stays there, because that "
                        "application extracts claims by machine at corpus scale with no "
                        "author present, so a registry has nobody to accrete it. Instead "
                        "of dumping into `other` it gains a documented mapping with an "
                        "explicit unmapped answer. FINDING: air quality, particulate and "
                        "sun angle, the three dimensions in this repo's own worked "
                        "example, all come back unmapped. The thirteen carry no "
                        "dimension for a physical or environmental condition. Rather "
                        "than adding a fourteenth, the argument dissolved: a dimension "
                        "is a claim, so it carries a level, and the thirteen are the "
                        "level-1 rungs. The closed enum opened into a registry with the "
                        "thirteen seeded at level 1 with written definitions, and the "
                        "long tail hangs off them by naming a `coarser` rung. Both "
                        "systems now mint freely and check first. A definition is "
                        "required at mint, because a registry of bare strings prevents "
                        "a split and does nothing about an overload, and an overload is "
                        "the failure that makes a false comparison.",
        },
        {
            "id": "v2",
            "topic": "condition comparator",
            "sourced": "No comparator. A threshold sits inside `value` as text, such as "
                       "'particulate below six parts per million'.",
            "system_c": "A typed `condition.op`: eq, neq, in, not-in, gt, lt, between, "
                     "before, after, matches, exists.",
            "publish": "No view.",
            "cost": "A machine cannot answer 'which claims apply when X' over SOURCED "
                    "conditions, and the text has to be parsed on the way into System C, "
                    "which is a guess at the author's meaning.",
        },
        {
            "id": "v3",
            "topic": "condition basis",
            "sourced": "Before the decision: one field, `basis`, one of tested, "
                       "replicated, observed, untested, inferred. It mixed how strong "
                       "the condition was with who said it.",
            "system_c": "Two fields. `condition.basis` is stated-in-source, "
                     "inferred-from-conflict, human or rule, which is who said it. "
                     "`condition.status` is asserted, proposed, monitoring, confirmed or "
                     "refuted, which is how far it has been checked.",
            "publish": "No view.",
            "cost": "`tested` and `observed` both translate to a System C basis of "
                    "stated-in-source with no status, so the strength of the condition is "
                    "dropped in translation and cannot be recovered.",
            "resolved": "29 August 2026, in favour of System C. SOURCED 1.4 splits the "
                        "field: `basis` is who said it, `status` is how far it has been "
                        "checked. The five old words still read and translate through "
                        "`dimensions.LEGACY`, which is a reading of intent and not a "
                        "lossless conversion. A formal condition is now one whose status "
                        "is `confirmed`.",
        },
        {
            "id": "v4",
            "topic": "level naming",
            "sourced": "Before the decision: levels 1 to 3 were named by audience, and "
                       "above 3 a level had no name (philosophy position 10).",
            "system_c": "Ordered integers with no names. The reason is that audience "
                        "names invite argument about who is a practitioner.",
            "publish": "No view.",
            "cost": "The names are load-bearing in this repo's prose and its checks read "
                    "'level 3 or above'. Adopting the ADR means the names come out of the "
                    "docs, and until then a reader of both sees one ladder described two "
                    "ways. Both systems agree the ladder is unbounded.",
            "resolved": "29 August 2026, in favour of System C. SOURCED 1.4 removes the "
                        "names from the format and from every rule, message and "
                        "validator. A level is an ordinal and prints as 'level 3'. The "
                        "numbers are relative and not absolute, so nothing compares a "
                        "level across two artefacts, and a statement may need "
                        "re-levelling later.",
        },
        {
            "id": "v5",
            "topic": "kind versus species",
            "sourced": "One field, `kind`, with four values: empirical, synthesis, "
                       "position, story.",
            "system_c": "Two fields. `species` is claim, position or story. "
                     "`assertionType` is empirical, statistical, definitional, "
                     "normative, interpretive, predictive or narrative.",
            "publish": "Marks position and story as species, not weak tiers. This is "
                       "the one place the two models had already converged.",
            "cost": "`synthesis` has no System C value, so a conclusion drawn across several "
                    "claims arrives as an ordinary empirical claim and loses the fact "
                    "that it is derived. Going the other way, System C's statistical, "
                    "definitional and predictive claims all flatten to `empirical`.",
            "resolved": "29 August 2026, RESOLVED BOTH WAYS, shipped in SOURCED 1.7. "
                        "First direction: `synthesis` survives here and was added to the "
                        "knowledge-base application's `assertionType` on the same day, so "
                        "a conclusion drawn across claims no longer flattens into "
                        "`empirical` on the way in. It is graded on its evidence like any "
                        "empirical claim and always carries `indirectness`, because a "
                        "conclusion drawn across claims is one step removed from that "
                        "evidence by construction. Recorded with it: kind and provenance "
                        "are independent questions, and the proof is that a synthesis can "
                        "be inferred, when you drew it across sources, or sourced, when "
                        "you retrieved somebody else's meta-analysis with a quote. Second "
                        "direction, decided the same day: `kind` is a hybrid of two axes, "
                        "which is why either mapping lost something. It is now read as "
                        "the COARSE rung of one ladder, and a claim gains an optional "
                        "finer `assertion` taking that application's eight "
                        "`assertionType` words exactly. The coarse rung is derived from "
                        "the finer one by `kinds.kind_of()`, one total mapping read one "
                        "way, and a claim whose two rungs disagree is refused naming "
                        "both. This is the same move `sophistication.py` already makes "
                        "for a statement, so it is a ladder and not a second rival field. "
                        "THE ROUND TRIP IS NOW LOSSLESS IN BOTH DIRECTIONS, and the test "
                        "that holds it is `kinds.py --self-check`, case `all eight "
                        "assertions round-trip losslessly under a kind`, with the same "
                        "eight walked again here in `case_v5_round_trip`. A `predictive` "
                        "assertion carries `resolves` of {by, criterion}, matching "
                        "`calibration.resolvesBy` and `calibration.resolutionCriterion`, "
                        "because an unfalsifiable forecast must never be tiered as "
                        "evidence.",
        },
        {
            "id": "v6",
            "topic": "evidence direction",
            "sourced": "Before the decision: `supports.direction` was for or against. "
                       "Two values, nothing else.",
            "system_c": "`evidence[].direction` is supports, undermines or mixed.",
            "publish": "No view.",
            "cost": "A source that cuts both ways cannot be recorded honestly in a "
                    "sidecar. It must be forced to one side or split into two rows, and "
                    "either move changes what the conflict detector sees.",
            "resolved": "29 August 2026, in favour of System C. SOURCED 1.4 accepts "
                        "`mixed`. A mixed row raises no conflict, because a source that "
                        "cuts both ways is already saying where the boundary is. It "
                        "raises a boundary prompt instead, and a conflict record may not "
                        "name it as a side.",
        },
        {
            "id": "v7",
            "topic": "the word survived",
            "sourced": "Removed deliberately on 28 August 2026 (philosophy position 8). "
                       "The output of an adversarial pass is a map, not a verdict. Tier 4 "
                       "reads 'boundary recorded'.",
            "system_c": "`analysis.challenged` still stores survived and survived-caveat, "
                     "beside not-attempted, attempted-unresolved and refuted.",
            "publish": "`verdicts[].verdict` stores survives, survives-caveat, weakest, "
                       "refine, killed and unverified.",
            "cost": "A contest word with one winner, reintroduced at the storage layer. A "
                    "pass that hunts a verdict stops when it has one, which is the "
                    "failure the position was written after: eight findings framed as "
                    "defeats when at least three were boundaries.",
            "resolved": "29 August 2026, harmonise all three. One shared vocabulary: "
                        "`holds`, `holds-with-boundary`, `refuted`. The knowledge-base "
                        "application renames analysis.challenged, the publishing "
                        "application renames its verdict kinds and keeps `weakest`, "
                        "`refine` and `unverified`, which are not contest words. Both "
                        "read an old value and write the new one, so nothing already "
                        "written becomes unreadable. The verdict SHAPE is unchanged: "
                        "replacing it with the conflict-and-boundary model was offered "
                        "and deferred as its own project. Both changes sit on branches "
                        "and neither is merged.",
        },
        {
            "id": "v8",
            "topic": "owner",
            "sourced": "Before the decision: no owner. `witness` existed on a story "
                       "only, naming who lived it.",
            "system_c": "`owner` with name, what that person personally checked, and since "
                     "when. It is the U of SOURCED, made into a field.",
            "publish": "No view.",
            "cost": "Nobody answers for a claim in a sidecar. The framework's own U says "
                    "a signature buys accountability, and this repo currently has no "
                    "field for the accountable person, so it is asserting a principle it "
                    "does not implement.",
            "resolved": "29 August 2026, in favour of System C. SOURCED 1.4 adds an "
                        "optional `owner` of {name, checked, since}. `checked` is "
                        "required, because a signature with nothing verified beside it "
                        "is the move the U rule refuses. An owner is not a witness and "
                        "neither derives from the other.",
        },
        {
            "id": "v9",
            "topic": "the adversarial record",
            "sourced": "`opposed` is one object for the whole artefact: which grade of "
                       "pass ran, when, and how many findings it raised.",
            "system_c": "Per claim: `analysis.challenged`, `verdicts[]` and a "
                     "`provenance[]` event chain with a `challenged` event.",
            "publish": "Per claim verdicts.",
            "cost": "A sidecar cannot say which claims were attacked, only that a pass "
                    "ran over the artefact. Translating to System C must leave "
                    "`analysis.challenged` as not-recorded, so the O of SOURCED is "
                    "artefact-wide here and claim-wide there.",
            "resolved": "29 August 2026, in favour of System C, and taken further. SOURCED "
                        "1.6 adds an optional `challenged` on a claim, carrying the five "
                        "shared words agreed with both other systems: `not-attempted`, "
                        "`attempted-unresolved`, `holds`, `holds-with-boundary`, "
                        "`refuted`. Absent reads as `not-attempted`. The artefact-level "
                        "`opposed` object is UNCHANGED and stays: it says which grade of "
                        "pass ran, and `challenged` says what that pass found about one "
                        "claim. Neither derives from the other. The further half is that "
                        "a competing claim the pass uncovers becomes a CLAIM in the same "
                        "sidecar, with its own evidence, conditions and level, so a "
                        "conflict may now be between two claims and not only between two "
                        "evidence rows, and `replaced_by` may name that claim. An "
                        "adversarial pass does not hand you two sources; it hands you a "
                        "rival claim, and until now there was nowhere to put it.",
        },
        {
            "id": "v10",
            "topic": "the claim strength number",
            "sourced": "Derived 0 to 4, computed from the evidence rows and refused if "
                       "stored.",
            "system_c": "`qualifier.grade` (high, moderate, low, very-low, not-applicable) "
                     "with named `downgrades[]`, computed at write time. The 0 to 4 tier "
                     "is kept as an output for the display.",
            "publish": "Stores the 0 to 4 tier.",
            "cost": "SOURCED cannot say WHY a claim is weak. System C names the reason, such "
                    "as self-interested-source or single-source, and the sidecar drops "
                    "that reason on the way in, which is the part a reader needs.",
            "resolved": "29 August 2026, in favour of System C. SOURCED 1.6 adopts both "
                        "enums verbatim, and `backing()` returns the number AND the "
                        "named reasons. Four are derived, from what the sidecar actually "
                        "holds: `single-source` from one distinct originGroup, "
                        "`self-interested-source` from a row that says so, "
                        "`inconsistency` from an opposed pair or a recorded conflict, "
                        "and `imprecision` from evidence carrying no quote and no "
                        "locator. `risk-of-bias`, `indirectness` and `publication-bias` "
                        "stay in the vocabulary and stay unset, because a sidecar records "
                        "nothing that answers them and a claim store does. No upgrade is "
                        "derived at all: `originGroup` is a label an author types, so "
                        "reading independent replication off it would assert a research "
                        "fact from a bookkeeping field. Strength is still DERIVED and "
                        "never stored, and a stored strength or tier is still refused.",
        },
    ]


def describe(data):
    """[(claim_id, publish state, label, kind)] for every claim in a sidecar."""
    refuse_stored_strength(data)
    ev = {e.get("id"): e for e in (data.get("evidence") or []) if isinstance(e, dict)}
    out = []
    for claim in (data.get("claims") or []):
        if not isinstance(claim, dict):
            continue
        kind = claim.get("kind")
        state = kind if kind in ("position", "story") else publish_state(claim, ev)
        out.append((claim.get("id"), publish_state(claim, ev), LABELS[state], kind))
    return out


def _report(path):
    data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    rows = describe(data)
    ev = {e.get("id"): e for e in (data.get("evidence") or []) if isinstance(e, dict)}
    by_id = {c.get("id"): c for c in (data.get("claims") or []) if isinstance(c, dict)}
    print(f"{path}: {len(rows)} claims")
    for cid, tier, label, kind in rows:
        shown = "—" if tier is None else str(tier)
        back = backing(by_id[cid], ev, data)
        proc = process(by_id[cid], data)
        why = (" because " + ", ".join(back.downgrades)) if back.downgrades else ""
        axes = (f"backing {'—' if back.grade is None else back.grade}{why}  "
                f"challenged {proc['system_c_challenged']}")
        print(f"  {cid:<10} state {shown}  {label:<28} kind {kind or '(none)':<10} {axes}")
    return 0


def _print_conflicts():
    records = conflicts()
    done = [r for r in records if r.get("resolved")]
    print(f"{len(records)} recorded disagreements between SOURCED 1.7, System C Claim "
          f"Record v1 and Publish's ledger.")
    print(f"{len(done)} decided, {len(records) - len(done)} still open.\n")
    for r in records:
        state = "RESOLVED" if r.get("resolved") else "open"
        print(f"{r['id']}  {r['topic']}  [{state}]")
        print(f"  SOURCED:  {r['sourced']}")
        print(f"  System C: {r['system_c']}")
        print(f"  Publish:  {r['publish']}")
        print(f"  Cost:     {r['cost']}")
        if r.get("resolved"):
            print(f"  Decided:  {r['resolved']}")
        print()
    return 0


def _self_check():
    """Thirteen cases with known answers, no network. The threshold is all thirteen: this
    is the file that stops three systems describing one claim three ways, and a wrong row
    here is a wrong label everywhere it is read."""
    ev = [{"id": "e1", "originGroup": "mit", "quote": "…", "locator": "p. 1"},
          {"id": "e2", "originGroup": "metr", "quote": "…", "locator": "p. 2"},
          {"id": "e3", "originGroup": "mit", "quote": "…", "locator": "p. 3"}]
    by_id = {e["id"]: e for e in ev}
    boundaried = {"id": "c1", "evidence": ["e1", "e2"],
                  "holds_when": [{"dimension": "air", "value": "clean",
                                  "basis": "tested"}],
                  "unknown_region": "everywhere else"}

    def case_all_seven_mapped():
        assert unmapped(STATES) == [], unmapped(STATES)
        assert set(MAP) == set(STATES), "MAP holds exactly the seven, nothing left over"
        assert set(LABELS) == set(STATES), "every state has a label"
        assert unmapped([0, "hearsay", "position", 9]) == ["hearsay", 9], \
            "an unknown state is reported by name, never folded into a near row"
        for state, row in MAP.items():
            assert set(row) == {"kind", "assertion", "backing", "process", "provenance",
                                "fidelity"}, \
                f"{state} must report every axis, including the ones it does not decide"

    def case_axes():
        # Backing and process are separate, and 0 to 4 is not one scale.
        assert MAP[1]["process"] and MAP[1]["backing"] == 1, \
            "tier 1 is a process fact (evidence sought) and a backing fact (none found)"
        for tier in (2, 3):
            assert MAP[tier]["backing"] == tier and MAP[tier]["process"] is None, \
                "tiers 2 and 3 report backing only"
        assert MAP[4]["process"] == "boundary-recorded" and MAP[4]["backing"] is None, \
            "tier 4 sets process without setting backing: a claim can be a 4 and a 2"
        assert MAP[0]["backing"] is None and MAP[0]["process"] is None, \
            "tier 0 is neither axis: it means unanalysed"
        for tier in (0, 1, 2, 3, 4):
            assert MAP[tier]["kind"] is None, "a tier decides no kind"
        for kind in ("position", "story"):
            assert MAP[kind]["kind"] == kind, "a stance is a kind, not a weak tier"
            assert MAP[kind]["backing"] is None and MAP[kind]["process"] is None, \
                "an evidence-exempt kind reports neither axis"
        for row in MAP.values():
            assert row["provenance"] == INDEPENDENT and row["fidelity"] == INDEPENDENT, \
                "provenance and fidelity must be stated as independent, not omitted"

    def case_v5_round_trip():
        # Disagreement v5, both directions, and this is the case that holds it closed.
        # `kind` is the coarse rung and `assertion` is the finer one, so the eight words
        # of the other application's `assertionType` survive the trip whole.
        assert set(kinds.ASSERTIONS) == {"empirical", "synthesis", "statistical",
                                         "definitional", "normative", "interpretive",
                                         "predictive", "narrative"}, sorted(kinds.ASSERTIONS)
        for assertion in kinds.ASSERTIONS:
            coarse = kinds.kind_of(assertion)
            record = {"kind": coarse, "assertion": assertion}
            assert record["assertion"] == assertion, "the finer rung reads back whole"
            assert coarse in kinds.KINDS, coarse
        # And the coarse rung is never guessed at from a state that cannot name it. Only
        # `story` has one assertion under it; `position` has two, so MAP says nothing.
        assert MAP["story"]["assertion"] == "narrative"
        assert MAP["position"]["assertion"] is None, \
            "normative and interpretive both sit under position, so the state cannot say"
        for tier in (0, 1, 2, 3, 4):
            assert MAP[tier]["assertion"] is None, "a tier decides no assertion"
        # The map row names the counterpart rather than describing the loss.
        assert SYSTEM_C["assertion"]["system_c"] == "assertionType"
        assert SYSTEM_C["assertion"]["match"] == "exact"
        assert SYSTEM_C["resolves"]["system_c"].startswith("calibration.resolvesBy")

    def case_label_is_boundary_recorded():
        assert LABELS[4] == "boundary recorded", LABELS[4]
        assert "surviv" not in " ".join(str(v) for v in LABELS.values()).lower()

    def case_derived_tiers():
        assert strength({"id": "c1"}, by_id) == 0, "no evidence recorded is tier 0"
        assert strength({"id": "c1", "evidence": ["nope"]}, by_id) == 1, \
            "evidence sought and none found is tier 1"
        assert strength({"id": "c1", "evidence": ["e1", "e3"]}, by_id) == 2, \
            "two rows from one origin group are a single origin"
        assert strength({"id": "c1", "evidence": ["e1", "e2"]}, by_id) == 3
        assert strength(boundaried, by_id) == 4, "tier 3 plus a boundary record is tier 4"
        # A boundary on thin evidence does not buy tier 4.
        assert strength(dict(boundaried, evidence=["e1"]), by_id) == 2
        assert strength is publish_state, "the old name still resolves"

    def case_backing_and_process_are_separate():
        # The defect in one number: a 4 is also a 2 or a 3, and one number cannot say so.
        assert publish_state(boundaried, by_id) == 4
        assert backing(boundaried, by_id).grade == 3, \
            "a tier-4 claim still rests on its backing, and the boundary is not backing"
        thin = dict(boundaried, evidence=["e1"])
        assert backing(thin, by_id).grade == 2 and process(thin)["boundary_recorded"], \
            "a boundary on one source is a process fact with backing of 2"
        assert backing({"id": "c1", "kind": "position"}, by_id).grade is None
        # process() reads what the sidecar holds and refuses to invent the rest.
        assert process(boundaried)["system_c_challenged"] == "not-attempted", \
            "no opposed record means nothing attacked the claim"
        ran = {"opposed": {"grade": "cross-model-fresh-thread"}}
        got = process(boundaried, ran)
        assert got["attempted"] and got["system_c_challenged"] == NOT_RECORDED, \
            "a pass ran over the artefact, so the per-claim outcome is not-recorded"
        assert process(boundaried, {"opposed": {"grade": "not-performed"}})[
            "system_c_challenged"] == "not-attempted"

    def case_contradicted():
        against = {"id": "e9", "originGroup": "x",
                   "supports": {"claim": "c1", "direction": "against"}}
        rows = dict(by_id, e9=against)
        assert strength({"id": "c1", "evidence": ["e1", "e2", "e9"]}, rows) == 1, \
            "a row that contradicts the claim drops it to tier 1 whatever else backs it"
        # …and a row arguing against a DIFFERENT claim does not.
        other = dict(against, supports={"claim": "c2", "direction": "against"})
        assert strength({"id": "c1", "evidence": ["e1", "e2", "e9"]},
                        dict(by_id, e9=other)) == 3

    def case_stored_strength_refused():
        for field in STORED_STRENGTH_FIELDS:
            doc = {"claims": [{"id": "c1", field: 4}], "evidence": []}
            try:
                refuse_stored_strength(doc)
            except AssertionError as e:
                assert "c1" in str(e) and "derived" in str(e), e
            else:
                raise AssertionError(f"a stored {field!r} must be refused")
            for fn in (strength, backing):
                try:
                    fn({"id": "c1", field: 4}, by_id)
                except AssertionError:
                    continue
                raise AssertionError(f"{fn.__name__}() must refuse a stored {field!r}")
        assert refuse_stored_strength({"claims": [{"id": "c1"}, "not a dict"]})

    def case_exempt_kinds():
        stance = {"id": "c1", "kind": "position", "falsifier": "…"}
        assert strength(stance, by_id) is None, "a position has no strength"
        rows = describe({"claims": [stance, {"id": "c2", "evidence": ["e1", "e2"]}],
                         "evidence": ev})
        assert rows[0] == ("c1", None, "stance (evidence-exempt)", "position"), rows[0]
        assert rows[1] == ("c2", 3, "multi-source", None), rows[1]

    def case_backing_names_its_reasons():
        # v10: the number and the reasons travel together, in the Claim Record's words.
        assert set(DOWNGRADES) == {"risk-of-bias", "inconsistency", "indirectness",
                                   "imprecision", "publication-bias",
                                   "self-interested-source", "single-source"}
        assert set(UPGRADES) == {"large-effect", "dose-response",
                                 "confounders-would-reduce", "replicated-independently"}
        assert set(NOT_DERIVABLE) < set(DOWNGRADES)
        # single-source fires on one origin group and not on two.
        one = backing({"id": "c1", "evidence": ["e1", "e3"]}, by_id)
        assert one.grade == 2 and "single-source" in one.downgrades, one
        two = backing({"id": "c1", "evidence": ["e1", "e2"]}, by_id)
        assert two.grade == 3 and "single-source" not in two.downgrades, two
        # A reason the data cannot support is NEVER emitted, in either direction.
        for got in (one, two, backing(boundaried, by_id)):
            assert set(got.downgrades) <= set(DOWNGRADES), got
            assert not set(got.downgrades) & set(NOT_DERIVABLE), \
                "a sidecar records nothing that answers these, so they stay unset"
            assert got.upgrades == (), "no upgrade is derivable from a sidecar"
        # self-interested-source fires only where a row says so.
        assert "self-interested-source" not in two.downgrades
        vendor = dict(by_id, e2=dict(by_id["e2"], selfInterested=True))
        assert "self-interested-source" in backing(
            {"id": "c1", "evidence": ["e1", "e2"]}, vendor).downgrades
        assert "self-interested-source" not in backing(
            {"id": "c1", "evidence": ["e1", "e2"]},
            dict(by_id, e2=dict(by_id["e2"], selfInterested=False))).downgrades
        # imprecision fires when no row carries both a quote and a locator.
        vague = {"q1": {"id": "q1", "originGroup": "a", "quote": "…"},
                 "q2": {"id": "q2", "originGroup": "b", "url": "https://example.org"}}
        assert "imprecision" in backing({"id": "c1", "evidence": ["q1", "q2"]},
                                        vague).downgrades
        assert "imprecision" not in two.downgrades
        # inconsistency fires on an opposed pair, and on a recorded conflict.
        rows = dict(by_id,
                    a1={"id": "a1", "originGroup": "x", "quote": "…", "locator": "p. 1",
                        "supports": {"claim": "c1", "direction": "for"}},
                    a2={"id": "a2", "originGroup": "y", "quote": "…", "locator": "p. 2",
                        "supports": {"claim": "c1", "direction": "against"}})
        assert "inconsistency" in backing({"id": "c1", "evidence": ["a1"]},
                                          rows).downgrades
        assert "inconsistency" not in two.downgrades
        recorded = {"conflicts": [{"id": "x1", "claim": "c1"}]}
        assert "inconsistency" in backing({"id": "c1", "evidence": ["e1", "e2"]},
                                          by_id, recorded).downgrades
        # An evidence-exempt kind carries no grade and no reasons.
        assert backing({"id": "c1", "kind": "story"}, by_id) == Backing(None, (), ())

    def case_challenged_is_per_claim():
        # v9: the five shared words, and absent reads as not-attempted.
        assert CHALLENGED == ("not-attempted", "attempted-unresolved", "holds",
                              "holds-with-boundary", "refuted")
        assert challenged_of({"id": "c1"}) == NOT_ATTEMPTED, \
            "absent reads as not-attempted, the same way an absent `opposed` does"
        for word in CHALLENGED:
            assert challenged_of({"id": "c1", "challenged": word}) == word
            assert validate_challenged({"claims": [{"id": "c1", "challenged": word}]})
        for sixth in ("survived", "survives-caveat", "held", "", None, 4):
            try:
                validate_challenged({"claims": [{"id": "c1", "challenged": sixth}]})
            except AssertionError as e:
                assert "c1" in str(e) and "challenged" in str(e), e
                continue
            raise AssertionError(f"challenged {sixth!r} must be refused")
        assert validate_challenged({"claims": [{"id": "c1"}, "not a dict"]})
        # A per-claim record answers, where the artefact-wide grade could not.
        ran = {"opposed": {"grade": "cross-model-fresh-thread"}}
        assert process(boundaried, ran)["system_c_challenged"] == NOT_RECORDED
        held = dict(boundaried, challenged="holds-with-boundary")
        assert process(held, ran)["system_c_challenged"] == "holds-with-boundary"
        # …and the two records stay independent: `opposed` is unchanged by either.
        assert process(held, ran)["opposed_grade"] == "cross-model-fresh-thread"
        assert process(held)["system_c_challenged"] == "holds-with-boundary", \
            "a per-claim outcome is not derived from the artefact-wide grade"

    def case_system_c_rows():
        exact = {k for k, v in SYSTEM_C.items() if v["match"] == "exact"}
        assert "fidelity" in exact, "System C's fidelity has the identical three values"
        for field in ("evidence[].originGroup", "evidence[].sha256",
                      "evidence[].textSha256", "evidence[].custodian",
                      "evidence[].archiveUrl"):
            assert field in exact, f"{field} already matches System C's fixity block"
        assert SYSTEM_C["kind"]["match"] == "partial"
        assert "synthesis" in SYSTEM_C["kind"]["note"]
        assert SYSTEM_C["assertion"]["match"] == "exact", (
            "the finer rung takes the other application's eight words exactly, so the "
            "translation costs nothing")
        assert SYSTEM_C["owner"]["match"] == "partial", (
            "this repo has an owner since 29 August 2026, and its second field is "
            "called `checked` rather than `verified`")
        note = SYSTEM_C["owner"]["note"]
        assert "checked" in note and "witness" in note
        for field, row in SYSTEM_C.items():
            assert set(row) == {"system_c", "match", "note"}, field
            assert row["match"] in ("exact", "partial", "none"), field
            assert row["note"].strip(), f"{field} must say what the translation costs"
        # A gap is named, never guessed at.
        assert SYSTEM_C["decisions[]"]["system_c"] == NOT_RECORDED

    def case_conflicts_recorded():
        records = conflicts()
        assert records, "conflicts() must not be empty: the disagreements are real"
        topics = {r["topic"] for r in records}
        for expected in ("condition dimension", "condition comparator", "condition basis",
                         "level naming", "kind versus species", "evidence direction",
                         "the word survived", "owner"):
            assert expected in topics, f"{expected} is missing from conflicts()"
        ids = [r["id"] for r in records]
        assert len(set(ids)) == len(ids), "conflict ids must be unique"
        for r in records:
            assert set(r) <= {"id", "topic", "sourced", "system_c", "publish", "cost",
                              "resolved"}, r["id"]
            for key in ("id", "topic", "sourced", "system_c", "publish", "cost"):
                assert r.get(key, "").strip(), f"{r['id']} must carry {key}"

        survived = [r for r in records if r["topic"] == "the word survived"][0]
        assert "survived" in survived["system_c"] and "survives" in survived["publish"], \
            "both other systems still store the word this repo removed"

    def case_eight_decided():
        # Eight were decided on 29 August 2026. v3, v4, v6 and v8 shipped here in 1.4,
        # v9 and v10 in 1.6, and the second half of v5 in 1.7. v1 and v7 were decided in
        # favour of work in the other two applications and sit on branches there. v2
        # alone stands open. A decided
        # record is never deleted: the reason this repo held the other position is what
        # stops it drifting back to it.
        records = conflicts()
        decided = {r["id"] for r in records if r.get("resolved")}
        assert decided == {"v1", "v3", "v4", "v5", "v6", "v7", "v8", "v9", "v10"}, decided
        for r in records:
            if r["id"] == "v9":
                assert "challenged" in r["resolved"] and "opposed" in r["resolved"]
            if r["id"] == "v10":
                assert "single-source" in r["resolved"] and "derived" in r["resolved"].lower()
            if r["id"] == "v5":
                assert "BOTH WAYS" in r["resolved"] and "assertion" in r["resolved"], \
                    "v5 is closed in both directions, and the record must say so"
                assert "kinds.py --self-check" in r["resolved"], \
                    "a resolved record names the test that holds it"
        for r in records:
            if r["id"] in decided:
                assert "29 August 2026" in r["resolved"], r["id"]
                # The record still says what the disagreement WAS, both ways.
                assert r["sourced"].strip() and r["system_c"].strip(), r["id"]
        # An open record carries no `resolved`, so nothing reads as decided by accident.
        for r in records:
            if r["id"] not in decided:
                assert "resolved" not in r, r["id"]

    cases = [("all seven states are mapped and nothing is left over", case_all_seven_mapped),
             ("backing and process are separate axes", case_axes),
             ("the eight assertions round-trip losslessly, both ways (v5)",
              case_v5_round_trip),
             ("tier 4 reads 'boundary recorded'", case_label_is_boundary_recorded),
             ("the presentation state is derived from the evidence rows", case_derived_tiers),
             ("a tier-4 claim still reports its backing", case_backing_and_process_are_separate),
             ("a contradicting row drops the claim to tier 1", case_contradicted),
             ("a stored strength or tier is refused", case_stored_strength_refused),
             ("an evidence-exempt kind carries no strength", case_exempt_kinds),
             ("backing returns the number and its named reasons, and invents none",
              case_backing_names_its_reasons),
             ("challenged is per claim, in five words, and absent is not-attempted",
              case_challenged_is_per_claim),
             ("every SOURCED field names its System C counterpart or the gap",
              case_system_c_rows),
             ("every disagreement is recorded, and none is deleted",
              case_conflicts_recorded),
             ("the nine decided records say what was decided and when",
              case_eight_decided)]
    passed = 0
    for label, fn in cases:
        try:
            fn()
            passed += 1
            print(f"pass  {label}")
        except AssertionError as e:
            print(f"FAIL  {label}: {e}")
    total = len(cases)
    print(f"\nvocabulary: self-check {'passed' if passed == total else 'FAILED'} "
          f"({passed} of {total} cases; the threshold is {total} of {total})")
    return passed == total


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "conflicts":
        sys.exit(_print_conflicts())
    if not args or "--self-check" in args:
        sys.exit(0 if _self_check() else 1)
    sys.exit(_report(args[0]))
