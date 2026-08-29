#!/usr/bin/env python3
"""The decision ledger: append while the work happens, fold into the sidecar at the end.

Rejected options leave no trace in the finished artefact. Nothing else in a deliverable
records that an option was considered at all, so once the draft settles, the road not
taken is unrecoverable. That, and not honesty, is why the log is kept: a log written as
you go can be checked against what actually happened, and a log reconstructed at the end
cannot be wrong in any way a reader can detect.

WHAT A RECORD CARRIES, AND WHAT IT MUST NOT
-------------------------------------------
The state, never the story (docs/philosophy.md, section 1):

    context[]     what was retrieved and what was in context
    options[]     which options were enumerated
    chose         which one was chosen
    rejected[]    which were not, each with ONE clause
    model         which model ran, with modelVersion and an optional run id

None of that needs introspection, so all of it is checkable. A justification is still
written, because humans read it, but it lands in `narrative` with its own `generatedAt`
and is labelled as narrative produced at that time, never as cause.

R stays dumb on purpose (philosophy section 2). The only free text is the one clause on
each rejected option, because that is the single thing nothing else preserves. The
hypothesis-and-falsifier structure belongs in O and in the boundary record; putting it
here as well turns a log into a framework.

    python3 decisions.py append <artefact> --option A --option B --chose A \
        --reject "B: needs a second dependency" --model claude-opus-5 --model-version 1m
    python3 decisions.py fold <artefact>     ledger lines -> decisions[] in the sidecar
    python3 decisions.py --self-check        eleven cases, known answers, no network

This file also holds `validate()`, the repo's shape check on a whole sidecar, so the
grades of the adversarial pass are checked here as well. That is one validator rather
than two, and the reason it matters is that an unknown grade string is how a
self-challenge gets written up as an independent review. See
`reference/adversarial-pass.md` for what each grade catches.

ponytail: the ledger is one JSON object per line, appended with open(..., "a"). No index,
no locking, no compaction. Ceiling is a single author on one machine; if two processes
ever append concurrently, move to one file per process and merge at fold time.
"""
import datetime
import json
import pathlib
import sys

# The level mechanism lives in one file and is used by claims and by conditions alike.
# Same side-by-side import style as claims.py: these modules are run as scripts from
# this directory, and evals.py puts it on the path before importing anything here.
import boundary
import conflicts
import dimensions
import kinds
import sophistication
import vocabulary

# A new optional top-level field is a minor bump. An implementation that ignores
# decisions[] or opposed{} still validates the sidecar, which is the whole point of the
# version being minor rather than major. 1.1 added decisions[]; 1.2 added opposed{};
# 1.3 added level, coarser and finer on a statement, where a statement is a claim or a
# condition, `dimension` and `value` on a condition, `supports` on an evidence row and
# conflicts[]. All of them are optional, so a 1.2 sidecar validates unchanged.
# 1.3 also stays 1.3 through `by` and `model` on a `supports`, added 29 August 2026.
# Both are optional fields on an optional object, nothing has been pushed, and an absent
# `by` reads as "author", so every sidecar on disk means exactly what it meant before.
# 1.3 stays 1.3 through the unbounded-level change of 29 August 2026. Nothing had been
# pushed, no file on disk stated a level above 4, and the change is a relaxation of a
# constraint plus a new gate rule rather than a new field. It is not an oversight.
#
# 1.4, 29 August 2026, adopts four decisions from the vocabulary map. All four are
# additive, so a 1.3 or a 1.2 sidecar validates unchanged:
#   v3  a condition's `basis` splits into `basis` (who said it) and `status` (how far it
#       has been checked). The five old basis words still read and translate through
#       `dimensions.LEGACY`. `status` is a new optional field.
#   v4  a level loses its audience names. This removes no field and changes no value; a
#       level was always the integer, and the names were prose.
#   v6  `supports.direction` gains `mixed`, a new value beside the two that already read.
#   v8  a claim gains an optional `owner` of {name, checked, since}.
#
# 1.5, 29 August 2026, adds an optional top-level `dimensions[]`: the registry rows for
# the dimensions this sidecar's conditions actually name. It is additive, so a 1.4, a 1.3
# or a 1.2 sidecar validates unchanged. It exists because a sidecar travels on its own,
# and a dimension defined only in a project registry means nothing to whoever receives the
# file. A row carries `name`, `definition`, `level`, an optional `coarser`, `firstSeen`,
# `uses` and an optional `mintedBy`. The block is GENERATED by `dimensions.for_sidecar`
# and never authored, and it may be partial, because a partial block is honest.
#
# 1.6, 29 August 2026, closes v9 and v10 from the vocabulary map. All three changes are
# additive, so a 1.5, a 1.4, a 1.3 or a 1.2 sidecar validates unchanged:
#   v9  a claim gains an optional `challenged`, one of the five shared words
#       `not-attempted`, `attempted-unresolved`, `holds`, `holds-with-boundary` and
#       `refuted`. Absent reads as `not-attempted`. The artefact-level `opposed` object is
#       UNCHANGED and stays; the two answer different questions and neither derives from
#       the other.
#   v9  a side of a conflict may name a CLAIM as well as an evidence row, because an
#       adversarial pass hands you a rival claim rather than two sources, and
#       `replaced_by` may name that claim instead of describing it in prose.
#   v10 `vocabulary.backing()` returns the number AND its named reasons, in the Claim
#       Record's own `downgrades` and `upgrades` words. That adds no stored field:
#       strength is still derived and never stored, and a stored strength or tier is
#       still refused. `evidence[].selfInterested` is the one new optional field it reads.
#
# 1.7, 29 August 2026, closes v5 in the other direction. Both changes are additive, so a
# 1.6, a 1.5, a 1.4, a 1.3 or a 1.2 sidecar validates unchanged:
#   v5  a claim gains an optional `assertion`, the FINER rung under `kind`, taking the
#       knowledge-base application's eight `assertionType` words exactly: empirical,
#       synthesis, statistical, definitional, normative, interpretive, predictive and
#       narrative. `kind` is unchanged and stays the coarse rung. The mapping between
#       them is fixed and total, `kinds.kind_of()` derives the coarse from the fine, and
#       a claim whose two rungs disagree is refused naming both. The round trip is now
#       lossless in both directions.
#   v5  a claim whose `assertion` is `predictive` must carry `resolves` of {by,
#       criterion}, both non-empty, with an optional `outcome` of true, false, ambiguous
#       or unresolved. An unfalsifiable forecast must never be tiered as evidence.
SCHEMA_VERSION = "1.7"

# The four grades of adversarial pass, best first. The identifier is the string that
# travels: it is what goes in the sidecar, what the check compares, and what the
# disclosure names. See reference/adversarial-pass.md for what each grade catches and
# for the exact sentence the disclosure uses.
#
# `not-performed` is not a grade of review. It is the honest name for a pass that did
# not happen, and it exists so that a skipped pass has somewhere to be recorded rather
# than nowhere, because an unrecorded pass and a passed review read identically.
OPPOSED_GRADES = ("cross-model-fresh-thread", "same-model-fresh-thread",
                  "same-thread-self-challenge", "not-performed")
NOT_PERFORMED = "not-performed"

# What an opposed{} record must carry. `model`, `modelVersion`, `thread` and `note` are
# optional, because a host does not always tell you which model or thread ran.
OPPOSED_REQUIRED = ("grade", "at", "raised")

# The keys a record must carry. `narrative` and `run` are optional: a decision with no
# story is still a complete record, and it is the state that is load-bearing.
REQUIRED = ("at", "context", "options", "chose", "rejected", "model", "modelVersion")

# The keys a sidecar must carry to validate. Deliberately the lowest common denominator
# the repo already documents; decisions[] is NOT here, because it is optional.
SIDECAR_REQUIRED = ("sourced", "artefact", "claims", "evidence", "disclosure")


def ledger_path(artefact):
    """The ledger sits beside the artefact, so it travels with it and is obvious to find."""
    return pathlib.Path(str(artefact) + ".decisions.jsonl")


def sidecar_path(artefact):
    return pathlib.Path(str(artefact) + ".sourced")


def record(options, chose, rejected, model, model_version, context=(), narrative="",
           run="", at=None):
    """Build one record. `rejected` is a mapping of option to its one clause.

    Every enumerated option other than the chosen one must appear in `rejected` with a
    clause. The chosen option needs none: the artefact itself is what it looks like."""
    at = at or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    options = list(options)
    if chose not in options:
        raise ValueError(f"the chosen option {chose!r} is not among the options enumerated")
    missing = [o for o in options if o != chose and not rejected.get(o, "").strip()]
    if missing:
        raise ValueError(f"a rejected option needs its one clause: {missing}")
    rec = {"at": at, "context": list(context), "options": options, "chose": chose,
           "rejected": [{"option": o, "clause": rejected[o]} for o in options if o != chose],
           "model": model, "modelVersion": model_version}
    if run:
        rec["run"] = run
    if narrative:
        # The key names what it is. A reader who sees `narrative` alongside its own
        # timestamp cannot mistake it for the cause of the choice.
        rec["narrative"] = {"text": narrative, "generatedAt": at}
    return rec


def append(artefact, rec):
    """Append one record. Append mode only: the file is never read, so an earlier line
    cannot be rewritten by a truncating write or lost to a crash mid-rewrite."""
    for key in REQUIRED:
        if key not in rec:
            raise ValueError(f"record is missing {key!r}")
    line = json.dumps(rec, sort_keys=True)
    assert "\n" not in line, "a record must be one line"
    path = ledger_path(artefact)
    with path.open("a", encoding="utf-8") as fh:
        # Heal a missing final newline before writing. A run that was killed
        # mid-write, or a file somebody edited by hand, leaves the last line
        # unterminated, and appending to that fuses two records into one line
        # that no longer parses. Healing costs one seek and cannot lose a line.
        if fh.tell() and path.read_bytes()[-1:] != b"\n":
            fh.write("\n")
        fh.write(line + "\n")
    return path


def read_ledger(artefact):
    """Every record, in the order it was written. A blank line is skipped, not an error."""
    path = ledger_path(artefact)
    if not path.is_file():
        return []
    out = []
    for n, ln in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not ln.strip():
            continue
        try:
            out.append(json.loads(ln))
        except json.JSONDecodeError as e:
            # Loudly, and naming the line. A ledger that quietly drops a record
            # is worse than no ledger: the rejected option it held is exactly
            # the thing nothing else in the artefact preserves.
            raise SystemExit(f"{path}:{n} is not one JSON object per line ({e})")
    return out


def fold(artefact):
    """Fold the ledger into the sidecar as a top-level decisions[] array.

    The members are the ledger's lines, unchanged. Folding twice is safe: it replaces the
    array rather than extending it, so a re-run after two more appends is still correct."""
    side = sidecar_path(artefact)
    if not side.is_file():
        raise SystemExit(f"no sidecar at {side}; audit the artefact before folding")
    data = json.loads(side.read_text(encoding="utf-8"))
    data["decisions"] = read_ledger(artefact)
    # A sidecar carrying a field from this version says this version. Nothing else about it changes.
    data["sourced"] = SCHEMA_VERSION
    # Write to a temporary file and rename. The sidecar is the deliverable, and a
    # fold interrupted halfway through a truncating write leaves nothing to ship.
    tmp = side.with_suffix(side.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(side)
    return len(data["decisions"])


def opposed_grade(data):
    """The grade of adversarial pass a sidecar records.

    A sidecar with no opposed{} reports `not-performed`, and that is deliberate. A pass
    nobody recorded is a pass nobody can show ran, so the absence must read as the
    weakest answer rather than as silence the disclosure can skip over."""
    return (data.get("opposed") or {}).get("grade", NOT_PERFORMED)


def validate(data):
    """Shape check on a sidecar. Raises AssertionError naming the first thing that is wrong.

    ponytail: an explicit shape check, not `jsonschema`. The real JSON Schema is served
    from the Peak State tenant and is not in this repo, and a validator that needs a pip
    install is one nobody runs. Upgrade path is to fetch that schema and validate against
    it if the shape ever grows past what these few lines can hold."""
    for key in SIDECAR_REQUIRED:
        assert key in data, f"sidecar is missing {key!r}"
    assert isinstance(data["claims"], list), "claims[] must be an array"
    assert isinstance(data["evidence"], list), "evidence[] must be an array"
    # The level mechanism, on claims and on the conditions inside them. One validator,
    # called twice, because a condition is itself a claim. Every field it reads is
    # optional, so a sidecar with no levels anywhere passes through untouched.
    sophistication.validate_statements(data["claims"], "claims")
    # What species of sentence each claim is, in Publish's words. `kind` is optional, and
    # it is a THIRD question: not provenance, not fidelity, and never read off either.
    kinds.validate_kinds(data["claims"])
    # Who answers for each claim. `owner` is optional, and when it is present it must say
    # what that person personally checked: a signature buys accountability, never
    # accuracy, and an owner with nothing verified is that claim made in the schema.
    kinds.validate_owners(data["claims"])
    # Where two retrieved sources disagree. `conflicts[]` and the `supports` field on an
    # evidence row are optional, so a 1.2 sidecar passes untouched; what is refused is a
    # conflict resolved into nothing, or shipped open with no unknown region named.
    conflicts.validate_conflicts(data)
    # What the adversarial pass found about each claim. `challenged` is optional and
    # absent reads as `not-attempted`; a sixth word is refused, because that is how a
    # pass that reached no conclusion gets written up as one that held.
    vocabulary.validate_challenged(data)
    # What is true instead. `replaced_by` is free text, or it names a claim in this
    # sidecar, and a named claim that is not here is a replacement nobody can follow.
    boundary.validate_replacements(data)
    # Strength is one of Publish's seven states and it is DERIVED from the evidence
    # rows, so a claim storing its own `strength` or `tier` is refused, not read.
    vocabulary.refuse_stored_strength(data)
    # Per claim, not pooled. Two claims may each carry a condition called `c1`, and
    # pooling them would let one claim's sibling link resolve against the other's.
    for i, claim in enumerate(data["claims"]):
        if isinstance(claim, dict):
            here = f"conditions of claims[{claim.get('id') or i}]"
            sophistication.validate_statements(sophistication.conditions_of(claim), here)
            # The condition's own shape: a free-text dimension and value, or the older
            # dimension-less `condition`, and a basis from the five. One parser, in
            # `dimensions.py`, so `boundary.py` and this validator cannot drift apart.
            for region in ("holds_when", "fails_when"):
                for entry in claim.get(region) or []:
                    try:
                        dimensions.validate_condition(entry)
                    except ValueError as e:
                        raise AssertionError(f"{here}: {region}: {e}") from None
    # dimensions[] is optional. When it is present, every row must be shaped as the
    # registry shapes one, and its `coarser` must resolve inside the block: a finer
    # dimension shipped without its coarser rung names a parent the receiver cannot read.
    # Completeness is NOT required. A sender may ship only the rows a receiver could not
    # otherwise resolve, and a partial block is honest.
    try:
        dimensions.validate_sidecar_dimensions(data)
    except ValueError as e:
        raise AssertionError(str(e)) from None
    # decisions[] is optional. Its absence is not a defect: a sidecar written by an
    # implementation that has never heard of the decision ledger still validates.
    if "decisions" in data:
        assert isinstance(data["decisions"], list), "decisions[] must be an array"
        for i, rec in enumerate(data["decisions"]):
            for key in REQUIRED:
                assert key in rec, f"decisions[{i}] is missing {key!r}"
            assert rec["chose"] in rec["options"], f"decisions[{i}]: chose is not an option"
            for r in rec["rejected"]:
                assert r.get("clause", "").strip(), (
                    f"decisions[{i}]: rejected option {r.get('option')!r} carries no clause")
    # opposed{} is optional too. When it is present the grade must be one of the four
    # known identifiers, because an unrecognised grade is how a self-challenge gets
    # written up as an independent review without anybody noticing.
    if "opposed" in data:
        op = data["opposed"]
        assert isinstance(op, dict), "opposed{} must be an object"
        for key in OPPOSED_REQUIRED:
            assert key in op, f"opposed is missing {key!r}"
        assert op["grade"] in OPPOSED_GRADES, (
            f"opposed: unknown grade {op['grade']!r}; one of {list(OPPOSED_GRADES)}")
        assert isinstance(op["raised"], int) and op["raised"] >= 0, (
            "opposed: raised must be a count, and a count is a whole number")
        assert not (op["grade"] == NOT_PERFORMED and op["raised"]), (
            "opposed: a pass that did not run cannot have raised anything")
    return True


def _cli(argv):
    if not argv or argv[0] not in ("append", "fold"):
        raise SystemExit(__doc__.strip().splitlines()[0])
    mode, artefact, rest = argv[0], argv[1], argv[2:]
    opts, chose, rejected, model, mver, ctx, narrative, run = [], "", {}, "", "", [], "", ""
    while rest:
        flag, rest = rest[0], rest[1:]
        val, rest = (rest[0], rest[1:]) if rest else ("", [])
        if flag == "--option":
            opts.append(val)
        elif flag == "--chose":
            chose = val
        elif flag == "--reject":
            # "OPTION: one clause". The colon keeps the pairing in one shell argument.
            name, _, clause = val.partition(":")
            rejected[name.strip()] = clause.strip()
            if name.strip() not in opts:
                opts.append(name.strip())
        elif flag == "--context":
            ctx.append(val)
        elif flag == "--model":
            model = val
        elif flag == "--model-version":
            mver = val
        elif flag == "--narrative":
            narrative = val
        elif flag == "--run":
            run = val
        else:
            raise SystemExit(f"unknown flag {flag}")
    if mode == "fold":
        print(f"folded {fold(artefact)} decisions into {sidecar_path(artefact)}")
        return 0
    path = append(artefact, record(opts, chose, rejected, model, mver, ctx, narrative, run))
    print(f"appended to {path}")
    return 0


def _self_check():
    """Nine cases with known answers, no network. The threshold is all nine: a ledger that
    loses a line, a version bump that invalidates every sidecar already written, or a
    grade of adversarial pass nobody checked, is a silent failure nobody notices until
    the rejected options are already gone or a self-challenge has shipped as a review."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        art = pathlib.Path(tmp) / "deck.html"
        art.write_text("<html></html>")

        # Case 1: two appends produce two lines, and the FIRST line is byte-identical
        # afterwards. This is the criterion the append-only mode exists to meet.
        r1 = record(["stdlib", "jsonschema"], "stdlib",
                    {"jsonschema": "a pip install nobody runs"},
                    "claude-opus-5", "1m", context=["e1", "the ticket"], at="2026-08-28T01:00:00Z")
        append(art, r1)
        first = ledger_path(art).read_bytes()
        r2 = record(["one file", "one file per process"], "one file",
                    {"one file per process": "no concurrent authors today"},
                    "claude-opus-5", "1m", narrative="Simplest thing that holds.",
                    at="2026-08-28T02:00:00Z")
        append(art, r2)
        after = ledger_path(art).read_bytes()
        assert after.count(b"\n") == 2, "two appends, two lines"
        assert after.startswith(first), "the first line was rewritten by the second append"
        assert read_ledger(art) == [r1, r2], "the ledger does not read back what was written"
        assert r2["narrative"]["generatedAt"] == r2["at"], "narrative carries its own time"
        assert "clause" not in json.dumps(r1["chose"]), "the chosen option needs no clause"
        # A run killed mid-write leaves the last line unterminated. Appending to that
        # must not fuse two records into one line that no longer parses.
        with ledger_path(art).open("a", encoding="utf-8") as fh:
            fh.write('{"truncated": true')
        ledger_path(art).write_text(after.decode() + '{"truncated": tru')
        append(art, r1)
        try:
            read_ledger(art)
        except SystemExit as e:
            assert "not one JSON object per line" in str(e), str(e)
        else:
            raise AssertionError("a half-written line must be reported, never dropped")
        assert ledger_path(art).read_text().count("\n") == 4, "the healed line stands alone"
        ledger_path(art).write_bytes(after)

        # Case 2: folding puts the ledger's lines in the sidecar, unchanged.
        base = {"sourced": "1.0", "artefact": {"path": "deck.html", "sha256": "ab"},
                "claims": [], "evidence": [], "disclosure": {"attribution": "…"}}
        sidecar_path(art).write_text(json.dumps(base))
        assert fold(art) == 2
        folded = json.loads(sidecar_path(art).read_text())
        assert folded["decisions"] == [r1, r2], "decisions[] must equal the ledger's lines"
        assert folded["sourced"] == SCHEMA_VERSION, "a sidecar carrying a field from this version says so"
        assert folded["claims"] == [] and folded["disclosure"] == base["disclosure"]

        # Case 3: both validation cases. WITH decisions[] validates, and WITHOUT it still
        # validates, so an implementation that ignores the array is not broken by the bump.
        assert validate(folded)
        assert validate(base | {"sourced": SCHEMA_VERSION})
        assert validate(base), "a 1.0 sidecar already on disk must stay valid"

        # Case 4: a rejected option with no clause is refused, at both ends. The clause is
        # the only thing the ledger preserves that the artefact does not.
        for bad in (lambda: record(["a", "b"], "a", {"b": "  "}, "m", "v"),
                    lambda: record(["a", "b"], "c", {"b": "no"}, "m", "v")):
            try:
                bad()
            except ValueError:
                pass
            else:
                raise AssertionError("a record missing its clause or its choice must be refused")
        hollow = dict(folded)
        hollow["decisions"] = [dict(r1, rejected=[{"option": "jsonschema", "clause": ""}])]
        try:
            validate(hollow)
        except AssertionError:
            pass
        else:
            raise AssertionError("validate must refuse a rejected option with no clause")

        # Case 5: every grade validates and reports itself, and a sidecar with no
        # opposed{} still validates while reporting `not-performed`. The absence must
        # read as the weakest answer, never as a pass the disclosure can stay quiet about.
        assert opposed_grade(base) == NOT_PERFORMED, "an absent record is not a pass"
        assert validate(base), "a sidecar with no opposed{} must still validate"
        for grade in OPPOSED_GRADES:
            raised = 0 if grade == NOT_PERFORMED else 3
            withop = folded | {"opposed": {"grade": grade, "at": "2026-08-28T03:00:00Z",
                                           "raised": raised, "model": "claude-opus-5"}}
            assert validate(withop), grade
            assert opposed_grade(withop) == grade, "the grade reported is the grade recorded"

        # Case 6: the three ways a grade lies are refused. An unknown identifier, a
        # missing required key, and a pass that did not run yet claims it raised
        # something. Each one would let a lower grade be read as a higher one.
        for bad in ({"grade": "second-opinion", "at": "2026-08-28T03:00:00Z", "raised": 1},
                    {"grade": "same-model-fresh-thread", "raised": 1},
                    {"grade": NOT_PERFORMED, "at": "2026-08-28T03:00:00Z", "raised": 2}):
            try:
                validate(folded | {"opposed": bad})
            except AssertionError:
                pass
            else:
                raise AssertionError(f"validate must refuse {bad}")

        # Case 7: the level mechanism reaches validate() for claims AND for the
        # conditions inside them, from one implementation. A sidecar with no level
        # anywhere still validates, which is what keeps every 1.2 file on disk valid.
        levelled = base | {"claims": [
            {"id": "c1", "statement": "The sky is blue.", "level": 1, "finer": "c3"},
            {"id": "c3", "statement": "Rayleigh scattering.", "level": 3, "coarser": "c1",
             "holds_when": [{"condition": "clean air", "basis": "observed", "id": "k1",
                             "level": 1, "finer": "k2"},
                            {"condition": "particulate below 6 ppm", "basis": "tested",
                             "id": "k2", "level": 3, "coarser": "k1"}]}]}
        assert validate(levelled), "levels on claims and conditions must validate"
        assert validate(base), "a sidecar with no level anywhere must still validate"
        assert validate(base | {"claims": [{"id": "c1", "level": 47}]}), (
            "the sophistication ladder has no top")
        for bad in ({"id": "c1", "level": 0},
                    {"id": "c1", "level": 2, "coarser": "nobody"},
                    {"id": "c1", "level": 1, "finer": "c1"}):
            try:
                validate(base | {"claims": [bad]})
            except AssertionError:
                pass
            else:
                raise AssertionError(f"validate must refuse the claim {bad}")
        # and the same refusal on a condition, because it is the same validator
        try:
            validate(base | {"claims": [{"id": "c1", "holds_when": [
                {"condition": "clean air", "basis": "tested", "id": "k1", "level": 0}]}]})
        except AssertionError:
            pass
        else:
            raise AssertionError("validate must refuse a bad level on a condition")

        # And `kind` reaches validate() the same way. It is optional, so `base` and every
        # 1.2 file on disk stay valid; a position with no falsifier does not.
        assert validate(base | {"claims": [
            {"id": "c1", "statement": "Adversarial is the method.", "kind": "position",
             "falsifier": "A pass that returned only defeats."}]})
        for bad in ({"id": "c1", "statement": "x", "kind": "opinion"},
                    {"id": "c1", "statement": "x", "kind": "position"},
                    {"id": "c1", "statement": "x", "kind": "story", "falsifier": "y"}):
            try:
                validate(base | {"claims": [bad]})
            except AssertionError:
                pass
            else:
                raise AssertionError(f"validate must refuse the claim {bad}")

        # And the condition's own shape, through the one parser in `dimensions.py`. The
        # new shape and the old one both validate; a missing field or an unknown basis
        # does not.
        assert validate(base | {"claims": [{"id": "c1", "holds_when": [
            {"dimension": "air quality", "value": "clean", "basis": "observed"},
            {"condition": "the weather is fine", "basis": "untested"}]}]})
        for bad in ({"value": "clean", "basis": "observed"},
                    {"dimension": "air quality", "basis": "observed"},
                    {"dimension": "air quality", "value": "clean", "basis": "guessed"}):
            try:
                validate(base | {"claims": [{"id": "c1", "fails_when": [bad]}]})
            except AssertionError:
                pass
            else:
                raise AssertionError(f"validate must refuse the condition {bad}")

        # Case 8: schema 1.4. All four changes are additive, so a 1.2 sidecar on disk
        # still validates, and each new field is refused only when it is malformed.
        old_1_2 = base | {"sourced": "1.2", "claims": [
            {"id": "c1", "statement": "The sky is blue.", "status": "sourced",
             "evidence": ["e1"],
             "holds_when": [{"condition": "clean air", "basis": "observed"}],
             "fails_when": [{"condition": "haze", "basis": "tested"}],
             "replaced_by": "The sky reads grey.", "unknown_region": "dusk"}],
            "evidence": [{"id": "e1", "quote": "…", "locator": "p. 1"}]}
        assert validate(old_1_2), "a 1.2 sidecar must still validate at 1.4"
        # v3: the condition pair, and an unknown status refused.
        assert validate(base | {"claims": [{"id": "c1", "holds_when": [
            {"dimension": "air quality", "value": "clean", "basis": "human",
             "status": "confirmed"}]}]})
        # v6: a mixed row is additive, and a conflict may not name one as a side.
        mixed = base | {"claims": [{"id": "c1", "statement": "x"}],
                        "evidence": [{"id": "e1", "quote": "…", "locator": "p. 1",
                                      "supports": {"claim": "c1", "direction": "mixed"}}]}
        assert validate(mixed)
        # v8: an owner is optional, and one with no `checked` is refused.
        assert validate(base | {"claims": [
            {"id": "c1", "statement": "x",
             "owner": {"name": "A. Ramsden", "checked": "Re-ran the numbers.",
                       "since": "2026-08-29"}}]})
        for bad in ({"name": "A. Ramsden"}, {"checked": "Re-ran the numbers."},
                    {"name": "A. Ramsden", "checked": " "}, "A. Ramsden"):
            try:
                validate(base | {"claims": [{"id": "c1", "statement": "x", "owner": bad}]})
            except AssertionError:
                pass
            else:
                raise AssertionError(f"validate must refuse the owner {bad!r}")

        # Case 9: schema 1.5, the optional dimensions[] block. It is additive, so a
        # 1.4 file with no block still validates; what is refused is a block that does
        # not resolve on its own, because a receiver has nothing else to read it against.
        old_1_4 = base | {"sourced": "1.4", "claims": [
            {"id": "c1", "statement": "The sky is blue.",
             "holds_when": [{"dimension": "air quality", "value": "clean",
                             "basis": "tested"}]}]}
        assert validate(old_1_4), "a 1.4 sidecar with no dimensions[] must still validate"
        air = "How clean the air is at the place and time of the observation."
        pm = "The mass of suspended particulate matter in the air, in parts per million."
        block = [{"name": "air quality", "definition": air, "level": 1,
                  "firstSeen": "2026-08-29", "uses": 2},
                 {"name": "particulate", "definition": pm, "level": 3,
                  "coarser": "air quality", "firstSeen": "2026-08-29", "uses": 1,
                  "mintedBy": "model", "mintedModel": "claude-opus-5"}]
        assert validate(old_1_4 | {"sourced": "1.5", "dimensions": block})
        # Partial is honest: the coarse rung alone validates.
        assert validate(old_1_4 | {"dimensions": block[:1]})
        # A row that predates the definition requirement is undefined, never refused.
        assert validate(old_1_4 | {"dimensions": [
            {"name": "tooling", "firstSeen": "2026-08-28", "uses": 4}]})
        for bad in ("not an array", [{"definition": air}], [{"name": " "}],
                    [{"name": "a", "finer": "b"}], [{"name": "a"}, {"name": "A"}],
                    [{"name": "a", "level": 0}], [{"name": "a", "coarser": "nobody"}],
                    [{"name": "a", "mintedBy": "robot"}],
                    [{"name": "a", "mintedModel": "claude-opus-5"}],
                    block[1:]):
            try:
                validate(old_1_4 | {"dimensions": bad})
            except AssertionError:
                pass
            else:
                raise AssertionError(f"validate must refuse dimensions[] of {bad!r}")

        # Case 10: schema 1.6, closing v9 and v10. All three changes are additive, so a
        # 1.2 and a 1.5 sidecar both still validate untouched.
        assert validate(old_1_2 | {"sourced": "1.2"}), "a 1.2 sidecar must validate at 1.6"
        old_1_5 = old_1_4 | {"sourced": "1.5", "dimensions": block}
        assert validate(old_1_5), "a 1.5 sidecar must validate at 1.6"
        # v9, first half: `challenged` on a claim, five words, absent reads as
        # not-attempted, and a sixth word refused.
        for word in vocabulary.CHALLENGED:
            assert validate(base | {"claims": [{"id": "c1", "statement": "x",
                                                "challenged": word}]})
        assert vocabulary.challenged_of({"id": "c1"}) == "not-attempted"
        for sixth in ("survived", "survives-caveat", "", None):
            try:
                validate(base | {"claims": [{"id": "c1", "challenged": sixth}]})
            except AssertionError:
                pass
            else:
                raise AssertionError(f"validate must refuse challenged {sixth!r}")
        # v9, second half: a conflict side may name a claim, and `replaced_by` may name
        # one. A named claim that is not in the sidecar is refused.
        rival = {"id": "c9", "statement": "The sky reads grey under haze.",
                 "holds_when": [{"dimension": "air quality", "value": "hazy",
                                 "basis": "human", "status": "confirmed"}],
                 "unknown_region": "dusk under haze."}
        held = {"id": "c1", "statement": "The sky is blue.",
                "holds_when": [{"dimension": "air quality", "value": "clean",
                                "basis": "human", "status": "confirmed"}],
                "fails_when": [{"dimension": "air quality", "value": "hazy",
                                "basis": "human", "status": "confirmed"}],
                "replaced_by": {"claim": "c9"}, "challenged": "holds-with-boundary",
                "unknown_region": "dusk."}
        rivalry = base | {"claims": [held, rival], "evidence": [], "conflicts": [
            {"id": "x1", "claim": "c1", "between": [{"claim": "c9"}],
             "dimensions": ["air quality"], "state": "resolved", "resolved_into": "c1"}]}
        rivalry["conflicts"][0]["between"] = [
            {"claim": "c9"},
            {"claim": "c10"}]
        rivalry["claims"] = [held, rival, dict(rival, id="c10")]
        assert validate(rivalry), "a claim-versus-claim conflict must validate"
        # `replaced_by` as free text still works, and a named claim that is absent does not.
        assert validate(base | {"claims": [dict(held, replaced_by="The sky reads grey.")]})
        for bad in ({"claim": "c404"}, {"claim": "c1"}, {"claim": " "}, ["c9"]):
            try:
                validate(base | {"claims": [dict(held, replaced_by=bad)], "evidence": []})
            except AssertionError:
                pass
            else:
                raise AssertionError(f"validate must refuse replaced_by of {bad!r}")
        # v10 stores nothing: a strength or a tier on a claim is still refused.
        for field in vocabulary.STORED_STRENGTH_FIELDS:
            try:
                validate(base | {"claims": [{"id": "c1", field: 4}]})
            except AssertionError:
                pass
            else:
                raise AssertionError(f"validate must still refuse a stored {field!r}")

        # Case 11: schema 1.7, closing v5 the other way. Both changes are additive, so a
        # 1.2 and a 1.6 sidecar both still validate untouched.
        assert validate(old_1_2 | {"sourced": "1.2"}), "a 1.2 sidecar must validate at 1.7"
        old_1_6 = old_1_5 | {"sourced": "1.6", "claims": [
            {"id": "c1", "statement": "x", "challenged": "holds"}]}
        assert validate(old_1_6), "a 1.6 sidecar must validate at 1.7"
        # The eight finer words, each under the coarse kind it derives, all validate.
        for assertion, coarse in kinds.ASSERTIONS.items():
            claim = {"id": "c1", "statement": "x", "kind": coarse,
                     "assertion": assertion}
            if coarse in kinds.EVIDENCE_EXEMPT:
                claim["falsifier"] = "The opposite turns out to hold."
            if coarse == "story":
                claim["witness"] = "A. Ramsden"
            if assertion == "predictive":
                claim["resolves"] = {"by": "2027-06-30",
                                     "criterion": "The June 2027 index."}
            assert validate(base | {"claims": [claim]}), assertion
        # A claim with a kind and no assertion is complete, which is what a 1.6 file is.
        assert validate(base | {"claims": [{"id": "c1", "kind": "empirical"}]})
        # Two rungs that disagree, a ninth word, and a forecast with no resolution.
        for bad in ({"kind": "empirical", "assertion": "normative"},
                    {"kind": "story", "assertion": "empirical", "witness": "A",
                     "falsifier": "f"},
                    {"assertion": "conjectural"},
                    {"kind": "empirical", "assertion": "predictive"},
                    {"kind": "empirical", "assertion": "predictive",
                     "resolves": {"by": "2027-06-30"}}):
            try:
                validate(base | {"claims": [{"id": "c1", "statement": "x"} | bad]})
            except AssertionError:
                pass
            else:
                raise AssertionError(f"validate must refuse the claim {bad!r}")

    print(f"decisions: self-check passed (11 of 11 cases; the threshold is 11 of 11; "
          f"schema {SCHEMA_VERSION}, decisions[], opposed{{}}, dimensions[], level, "
          f"kind, assertion, status, owner and challenged optional)")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("--self-check", "--check"):
        _self_check()
    else:
        sys.exit(_cli(sys.argv[1:]))
