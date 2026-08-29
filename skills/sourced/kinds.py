#!/usr/bin/env python3
"""What species of sentence a claim is, in Publish's words rather than a third set.

    python3 kinds.py --self-check     ten cases, known answers, no network
    python3 kinds.py <file.sourced>   the per-kind tally and the exempt claims

`docs/framework.md` position 7 already says it: Publish grades a claim on tiers 0 to 4,
and it carries **position** (a stance, evidence-exempt by design) and **story**
(author-verified lived experience) as their own species of sentence, not weak tiers. The
sidecar adopts those words unchanged, so one claim is not described two ways and the two
systems stop drifting.

The move this file stops: an author's own stance arriving in a sidecar as a claim that
failed to find a source, and from there into a Limitations line as a confession. A
position is not failed evidence. It is a different kind of sentence.

THREE SEPARATE QUESTIONS, AND NONE IS DERIVED FROM ANOTHER
----------------------------------------------------------
    provenance  does anything back this claim   -> is `evidence[]` empty
    fidelity    how far the wording is from the source -> quotation, paraphrase, inference
    kind        what species of sentence it is  -> this file

A synthesis can be quotation-free and heavily evidenced. A position can quote somebody
and still be a stance. Reading any one of the three off another is the fusing mistake
`sourced_status.py` was written to undo, one axis further out.

EVIDENCE-EXEMPT IS NOT CHECK-EXEMPT
-----------------------------------
A position and a story are exempt from evidence by design, so they need the other kind of
warrant or they become a hiding place, including for the author:

    position  requires a `falsifier`: what would have to be true for the stance to be wrong
    story     requires a `falsifier` AND a `witness`: who lived it, named

Testimony with nobody's name against it has no warrant at all, which is the whole point
of recording lived experience as a story rather than as an unsourced claim.

`kind` itself stays OPTIONAL. A claim with no `kind` passes untouched, which is what keeps
a 1.2 sidecar valid.

TWO RUNGS OF ONE LADDER, NOT TWO RIVAL FIELDS
---------------------------------------------
`kind` is the COARSE rung and it answers the question a person actually asks: did somebody
measure this, did I conclude it, do I hold it, or did I live it. A claim may also carry an
optional `assertion`, the FINER rung, in the knowledge-base application's own eight words.
This is the same move `sophistication.py` makes for a statement: one dimension at two
depths, the way `air quality` and `particulate` are one dimension at two depths.

    kind        empirical   synthesis   position                  story
    assertion   empirical   synthesis   normative                 narrative
                statistical             interpretive
                definitional
                predictive

The mapping is FIXED and TOTAL, so `kind_of()` derives the coarse rung from the fine one
and nothing writes the table twice. A claim carrying both must agree, and a claim carrying
`kind` alone is complete: a 1.6 sidecar has no `assertion` anywhere.

A PREDICTIVE ASSERTION OWES A RESOLUTION
----------------------------------------
An evidence-exempt kind owes a falsifier. A forecast owes the same discipline in its own
words, so a `predictive` assertion requires `resolves`: `{"by": "<date>", "criterion":
"<what would settle it>"}`, both non-empty. An unfalsifiable forecast must never be tiered
as evidence. `resolves.outcome` is optional and records what happened: `true`, `false`,
`ambiguous` or `unresolved`.

WHO ANSWERS FOR THE CLAIM
-------------------------
A claim may carry an `owner`: `{name, checked, since}`. It is optional, and when it is
there `name` and `checked` are both required. `validate_owners` is beside the two warrant
rules above because it is the same kind of rule, a claim that owes something owing it.

An owner is NOT a witness and neither derives from the other. A witness lived the
experience a story records; an owner answers for the claim.

ponytail: a dict and two rules, not a taxonomy engine. Four kinds are the whole domain
(docs/framework.md position 7); a fifth would be a change to the framework first.
"""
import json
import pathlib
import sys

# The value is the plain-English gloss, taken from docs/framework.md position 7.
KINDS = {
    "empirical": "a claim backed by evidence somebody gathered",
    "synthesis": "a conclusion drawn across several claims",
    "position": "a stance, evidence-exempt by design",
    "story": "author-verified lived experience",
}

# The two species of sentence that owe no evidence, and therefore owe a falsifier.
EVIDENCE_EXEMPT = ("position", "story")

# The finer rung under `kind`. The keys are the knowledge-base application's
# `assertionType` enum VERBATIM, with nothing added and nothing renamed, and the value is
# the coarse `kind` the finer word sits under. The mapping is total, so every assertion
# has a kind and the round trip loses nothing in either direction.
ASSERTIONS = {
    "empirical": "empirical",
    "synthesis": "synthesis",
    "statistical": "empirical",
    "definitional": "empirical",
    "normative": "position",
    "interpretive": "position",
    "predictive": "empirical",
    "narrative": "story",
}

# What a forecast owes instead of evidence. `by` is the date it resolves, `criterion` is
# the observation that would settle it. `outcome` is optional and its four words are the
# other application's `calibration.resolvedOutcome` enum verbatim.
RESOLVES_REQUIRED = ("by", "criterion")
OUTCOMES = ("true", "false", "ambiguous", "unresolved")

UNFALSIFIABLE = ("An unfalsifiable forecast must never be tiered as evidence.")


def kind_of(assertion):
    """The coarse rung a finer assertion sits under. The one place the table is read."""
    return ASSERTIONS[assertion]


def _name(claim, i):
    """Name the offending claim so the message points at something editable."""
    statement = (claim.get("statement") or "").strip()
    if len(statement) > 90:
        statement = statement[:87] + "..."
    return f"claims[{claim.get('id') or i}] {statement!r}"


def _text(claim, field):
    value = claim.get(field)
    return value.strip() if isinstance(value, str) else ""


def _validate_assertion(claim, here):
    """The finer rung, and the two rules that hang off it. Raises AssertionError."""
    assertion = claim["assertion"]
    assert assertion in ASSERTIONS, (
        f"{here}: assertion {assertion!r} is not one of {sorted(ASSERTIONS)}")
    if "kind" in claim:
        expected = kind_of(assertion)
        assert claim["kind"] == expected, (
            f"{here}: assertion {assertion!r} sits under kind {expected!r}, and this "
            f"claim states kind {claim['kind']!r}. The coarse rung and the finer rung "
            f"must agree, because they are one ladder and not two fields.")
    if assertion != "predictive":
        return
    resolves = claim.get("resolves")
    assert isinstance(resolves, dict), (
        f"{here}: a predictive assertion needs `resolves` with a `by` date and a "
        f"`criterion`. {UNFALSIFIABLE}")
    for field in RESOLVES_REQUIRED:
        value = resolves.get(field)
        assert isinstance(value, str) and value.strip(), (
            f"{here}: `resolves.{field}` says nothing. {UNFALSIFIABLE}")
    if "outcome" in resolves:
        assert resolves["outcome"] in OUTCOMES, (
            f"{here}: resolves.outcome {resolves['outcome']!r} is not one of "
            f"{sorted(OUTCOMES)}")


def validate_kinds(claims):
    """Shape check on `kind`. Raises AssertionError naming the first offending claim.

    Refuses a kind outside the four, an evidence-exempt kind with no falsifier, and a
    story with no witness. It also refuses an `assertion` outside the eight, an assertion
    that disagrees with the kind beside it, and a predictive assertion with no resolution.
    A claim carrying neither field is not touched.
    """
    for i, claim in enumerate(claims):
        if not isinstance(claim, dict):
            continue
        if "assertion" in claim:
            _validate_assertion(claim, _name(claim, i))
        if "kind" not in claim:
            continue
        kind, here = claim["kind"], _name(claim, i)
        assert kind in KINDS, (
            f"{here}: kind {kind!r} is not one of {sorted(KINDS)}")
        if kind not in EVIDENCE_EXEMPT:
            continue
        assert _text(claim, "falsifier"), (
            f"{here}: a {kind} owes no evidence, so it owes a `falsifier`: what would "
            f"have to be true for it to be wrong. Without one it is a hiding place.")
        if kind == "story":
            assert _text(claim, "witness"), (
                f"{here}: a story needs a `witness` naming who lived it. Testimony with "
                f"no name against it has no warrant.")
    return True


# The claim's accountable person. Optional, and when it is present `name` and `checked`
# are both required. `since` is the date that person took it on, and it is optional.
OWNER_FIELDS = ("name", "checked", "since")


def validate_owners(claims):
    """Shape check on `owner`. Raises AssertionError naming the first offending claim.

    An `owner` is a named person who answers for the claim, what that person personally
    checked, and since when. `checked` is required and must say something, because "I own
    this" with no "here is what I verified" is the signature-buys-accuracy move the U of
    SOURCED exists to refuse. A signature buys accountability, never accuracy.

    **An `owner` and a `witness` are different things and neither derives from the other.**
    A witness lived the experience a story records. An owner answers for the claim. One
    claim may carry both, either, or neither.

    `owner` is optional, so a sidecar written before it existed passes untouched.
    """
    for i, claim in enumerate(claims):
        if not isinstance(claim, dict) or "owner" not in claim:
            continue
        owner, here = claim["owner"], _name(claim, i)
        assert isinstance(owner, dict), (
            f"{here}: owner must be an object with a `name` and a `checked`, not "
            f"{owner!r}")
        assert isinstance(owner.get("name"), str) and owner["name"].strip(), (
            f"{here}: owner needs a `name`, because a claim nobody is named against has "
            f"nobody answering for it")
        assert isinstance(owner.get("checked"), str) and owner["checked"].strip(), (
            f"{here}: owner {owner.get('name')!r} names no `checked`. A signature buys "
            f"accountability and never accuracy, so an owner must say what they "
            f"personally verified.")
    return True


def owners(claims):
    """[(id, name, checked, since)] for every claim that names an owner."""
    return [(c.get("id"), c["owner"]["name"], c["owner"]["checked"],
             c["owner"].get("since", ""))
            for c in claims if isinstance(c, dict) and isinstance(c.get("owner"), dict)]


def exempt(claims):
    """[(id, kind, falsifier, witness)] for every position and story."""
    return [(c.get("id"), c["kind"], _text(c, "falsifier"), _text(c, "witness"))
            for c in claims
            if isinstance(c, dict) and c.get("kind") in EVIDENCE_EXEMPT]


def tally(claims):
    """kind -> count, over the four known kinds plus the claims that state none."""
    counts = {k: 0 for k in KINDS}
    counts["(none)"] = 0
    for c in claims:
        if isinstance(c, dict):
            counts[c["kind"] if c.get("kind") in KINDS else "(none)"] += 1
    return counts


def _report(path):
    data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    claims = data.get("claims") or []
    counts = tally(claims)
    print(f"{path}: {len(claims)} claims")
    for kind, gloss in KINDS.items():
        print(f"  {counts[kind]:>3}  {kind:<10} {gloss}")
    print(f"  {counts['(none)']:>3}  (none)     no kind stated")
    for cid, name, checked, since in owners(claims):
        when = f" since {since}" if since else ""
        print(f"  owner {cid}: {name}{when}\n    checked: {checked}")
    finer = [(c.get("id"), c["assertion"], (c.get("resolves") or {}).get("by", ""))
             for c in claims if isinstance(c, dict) and c.get("assertion")]
    for cid, assertion, by in finer:
        when = f", resolves by {by}" if by else ""
        print(f"  assertion {cid}: {assertion} under kind {kind_of(assertion)}{when}")
    rows = exempt(claims)
    if not rows:
        print("  no position or story claims")
        return 0
    for cid, kind, falsifier, witness in rows:
        who = f", witness {witness}" if witness else ""
        print(f"  {kind} {cid}{who}\n    falsifier: {falsifier}")
    return 0


def _self_check():
    """Ten cases with known answers, no network. The threshold is all ten: this
    decides whether an author's own contribution is recorded as a stance or as failed
    evidence, and getting it wrong is the move the whole ticket exists to stop."""
    position = {"id": "c1", "kind": "position", "statement": "Adversarial is the method.",
                "falsifier": "A pass that returned only defeats and lost nothing."}
    story = {"id": "c2", "kind": "story",
             "statement": "The draft shipped with the disputed sentence.",
             "falsifier": "The commit history shows no such sentence.",
             "witness": "the author"}

    def case_good():
        assert validate_kinds([{"id": "c0", "kind": "empirical"},
                               {"id": "c3", "kind": "synthesis"}, position, story])

    def case_unknown_kind():
        for bad in ("opinion", "Position", "", None, 3):
            try:
                validate_kinds([{"id": "c1", "kind": bad, "statement": "x"}])
            except AssertionError:
                continue
            raise AssertionError(f"kind {bad!r} must be refused")

    def case_no_falsifier():
        for kind in EVIDENCE_EXEMPT:
            for rec in ({"id": "c1", "kind": kind, "statement": "x", "witness": "A"},
                        {"id": "c1", "kind": kind, "falsifier": "  "},
                        {"id": "c1", "kind": kind, "falsifier": None}):
                try:
                    validate_kinds([rec])
                except AssertionError as e:
                    assert "c1" in str(e), f"the message must name the claim: {e}"
                    continue
                raise AssertionError(f"a {kind} with no falsifier must be refused")

    def case_story_needs_witness():
        try:
            validate_kinds([dict(story, witness="")])
        except AssertionError as e:
            assert "witness" in str(e) and "c2" in str(e), e
        else:
            raise AssertionError("a story with no witness must be refused")
        # A position does NOT need a witness. Only the story is testimony.
        assert validate_kinds([{k: v for k, v in position.items()}])

    def case_1_2_sidecar():
        old = [{"id": "c1", "statement": "…", "evidence": ["e1"]},
               {"id": "c2", "statement": "…"}, "a claim that is not even a dict"]
        assert validate_kinds(old), "a sidecar with no kinds must validate"
        assert validate_owners(old), "a sidecar with no owners must validate"
        assert tally(old)["(none)"] == 2
        assert exempt(old) == [] and owners(old) == []

    def case_owner():
        owned = {"id": "c5", "kind": "empirical", "statement": "The sky is blue.",
                 "owner": {"name": "A. Ramsden", "checked": "Read the 1899 paper and "
                                                            "confirmed the exponent.",
                           "since": "2026-08-29"}}
        assert validate_owners([owned])
        assert owners([owned]) == [("c5", "A. Ramsden",
                                    "Read the 1899 paper and confirmed the exponent.",
                                    "2026-08-29")]
        # `since` is optional; `name` and `checked` are not, and an empty `checked` is
        # the signature-buys-accuracy move the U rule refuses.
        assert validate_owners([{"id": "c6", "owner": {"name": "A. Ramsden",
                                                       "checked": "Re-ran the numbers."}}])
        bad = [({"name": "A. Ramsden"}, "checked"),
               ({"name": "A. Ramsden", "checked": "   "}, "checked"),
               ({"name": "A. Ramsden", "checked": None}, "checked"),
               ({"checked": "Re-ran the numbers."}, "name"),
               ({"name": "", "checked": "Re-ran the numbers."}, "name"),
               ("A. Ramsden", "object"),
               (None, "object")]
        for owner, word in bad:
            try:
                validate_owners([{"id": "c7", "statement": "x", "owner": owner}])
            except AssertionError as e:
                assert word in str(e) and "c7" in str(e), e
                continue
            raise AssertionError(f"owner {owner!r} must be refused")
        # An owner and a witness are different things. A story keeps needing its witness
        # whether or not somebody owns the claim, and an owner needs no witness.
        story_owned = dict(story, owner={"name": "A. Ramsden",
                                         "checked": "Re-read the transcript."})
        assert validate_owners([story_owned]) and validate_kinds([story_owned])
        try:
            validate_kinds([dict(story_owned, witness="")])
        except AssertionError as e:
            assert "witness" in str(e), e
        else:
            raise AssertionError("an owner does not stand in for a witness")

    def case_assertion_round_trip():
        # All eight, both directions, and this is the case that closes disagreement v5.
        # Fine -> coarse -> fine loses nothing, because the mapping is total and the
        # finer word is stored rather than derived.
        assert len(ASSERTIONS) == 8, sorted(ASSERTIONS)
        for assertion in ASSERTIONS:
            kind = kind_of(assertion)
            assert kind in KINDS, f"{assertion} maps to {kind}, which is not a kind"
            claim = {"id": "c1", "statement": "x", "kind": kind, "assertion": assertion}
            if kind in EVIDENCE_EXEMPT:
                claim["falsifier"] = "The opposite turns out to hold."
            if kind == "story":
                claim["witness"] = "A. Ramsden"
            if assertion == "predictive":
                claim["resolves"] = {"by": "2027-06-30",
                                     "criterion": "The published index for June 2027."}
            assert validate_kinds([claim]), assertion
            assert claim["assertion"] == assertion, "the finer rung must read back whole"
        # Every kind is reachable from some assertion, so the coarse rung loses nothing
        # either: a kind names the set of assertions that sit under it.
        assert set(ASSERTIONS.values()) == set(KINDS), set(ASSERTIONS.values())
        # A claim with a kind and no assertion still validates. A 1.6 sidecar has none.
        assert validate_kinds([{"id": "c2", "kind": "empirical", "statement": "x"}])
        assert validate_kinds([{"id": "c3", "kind": "synthesis", "statement": "x"}])

    def case_assertion_must_agree():
        for assertion, wrong in (("normative", "empirical"), ("narrative", "position"),
                                 ("statistical", "synthesis"), ("synthesis", "empirical"),
                                 ("predictive", "story")):
            try:
                validate_kinds([{"id": "c1", "statement": "x", "kind": wrong,
                                 "assertion": assertion, "falsifier": "f",
                                 "witness": "A. Ramsden"}])
            except AssertionError as e:
                assert assertion in str(e) and wrong in str(e), (
                    f"the message must name both rungs: {e}")
                continue
            raise AssertionError(f"assertion {assertion} under kind {wrong} must be refused")
        for bad in ("opinion", "Empirical", "", None, 3):
            try:
                validate_kinds([{"id": "c1", "statement": "x", "assertion": bad}])
            except AssertionError:
                continue
            raise AssertionError(f"assertion {bad!r} must be refused")
        # An assertion with no kind beside it is legal: the coarse rung is optional too.
        assert validate_kinds([{"id": "c4", "statement": "x", "assertion": "statistical"}])

    def case_predictive_needs_resolution():
        good = {"id": "c1", "statement": "x", "kind": "empirical",
                "assertion": "predictive",
                "resolves": {"by": "2027-06-30", "criterion": "The June 2027 index."}}
        assert validate_kinds([good])
        for word in OUTCOMES:
            assert validate_kinds([dict(good, resolves=dict(good["resolves"],
                                                            outcome=word))])
        bad = [{}, None, "2027-06-30",
               {"by": "2027-06-30"}, {"criterion": "The June 2027 index."},
               {"by": "  ", "criterion": "The June 2027 index."},
               {"by": "2027-06-30", "criterion": ""},
               {"by": "2027-06-30", "criterion": "c", "outcome": "maybe"}]
        for resolves in bad:
            rec = dict(good)
            if resolves is None:
                rec.pop("resolves")
            else:
                rec["resolves"] = resolves
            try:
                validate_kinds([rec])
            except AssertionError as e:
                assert "c1" in str(e), e
                continue
            raise AssertionError(f"a predictive claim with resolves {resolves!r} "
                                 f"must be refused")

    def case_three_questions():
        # kind is not read off provenance or fidelity, and neither is read off kind.
        # A position with retrieved evidence and a quotation fidelity is still a position.
        quoting_position = dict(position, evidence=["e1"], fidelity="quotation")
        assert validate_kinds([quoting_position])
        assert exempt([quoting_position])[0][1] == "position"
        # And an empirical claim with no evidence rows is not refused here: that is
        # provenance's question, and sourced_status.py answers it.
        assert validate_kinds([{"id": "c9", "kind": "empirical", "statement": "x"}])

    cases = [("the four kinds, with warrants, validate", case_good),
             ("a kind outside the four is refused", case_unknown_kind),
             ("an evidence-exempt claim with no falsifier is refused", case_no_falsifier),
             ("a story with no witness is refused, a position needs none",
              case_story_needs_witness),
             ("a 1.2 sidecar with no kinds and no owner still validates", case_1_2_sidecar),
             ("an owner names a person and what they checked", case_owner),
             ("provenance, fidelity and kind stay independent", case_three_questions),
             ("all eight assertions round-trip losslessly under a kind",
              case_assertion_round_trip),
             ("an assertion that disagrees with its kind is refused, naming both",
              case_assertion_must_agree),
             ("a predictive assertion with no resolution is refused",
              case_predictive_needs_resolution)]
    passed = 0
    for label, fn in cases:
        try:
            fn()
            passed += 1
            print(f"pass  {label}")
        except AssertionError as e:
            print(f"FAIL  {label}: {e}")
    total = len(cases)
    print(f"\nkinds: self-check {'passed' if passed == total else 'FAILED'} "
          f"({passed} of {total} cases; the threshold is {total} of {total})")
    return passed == total


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or "--self-check" in args:
        sys.exit(0 if _self_check() else 1)
    sys.exit(_report(args[0]))
