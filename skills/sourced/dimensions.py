#!/usr/bin/env python3
"""The dimensions a condition names, and the per-project registry they accrete into.

    python3 dimensions.py --self-check       seventeen cases, known answers, no network
    python3 dimensions.py                    the registry, with its undefined rows
    python3 dimensions.py --sidecar F.sourced   write the definitions this file uses into it

`docs/philosophy.md` position 9 rejected a fixed set of five condition fields, because
conditions are as varied as the subject matter. The sky is blue when the weather is fine,
the sun is high, the air is clean, and you are looking overhead rather than at the
horizon. None of those is population or tooling.

So the **shape is fixed** and the **dimension is free text**:

    {dimension, value, basis, status}

`basis` is **who said it** and `status` is **how far it has been checked**. They were one
field until 29 August 2026, and one field could not say that a condition somebody
measured and a condition somebody guessed came from the same place. `status` is optional,
because a sidecar written before the split carries none.

The old `{condition, basis}` shape is read as a dimension-less condition, and the five old
basis words still read. So nothing already written breaks. `read_condition()` returns the
same triple from every shape, and `read_condition_full()` adds the status.

WHY THERE IS A REGISTRY AT ALL
------------------------------
Two claims can only be compared on a dimension they both name. So first use of a dimension
writes it into a per-project registry beside the source index, and later uses match
against it.

A dimension vocabulary fails in two ways, and they are not symmetric.

A **split** is two names for one dimension. `tooling` and `tool-generation` recorded
separately is a spelling accident, not a disagreement. You miss a comparison, the miss is
silent, and it is recoverable: merge the two rows later and the comparison comes back.

An **overload** is one name covering two meanings. `method` meaning a research method in
one claim and a manufacturing method in another is one name over two dimensions. You make
a **false** comparison. Two claims look like they conflict when they are about different
things, that reading feeds `integrate.py`, and `integrate.py` refuses the delivery. A
wrong refusal is how a gate gets bypassed.

**Overload is the expensive failure, and a registry of bare strings does not prevent it.**
Bare strings prevent splits only. **A definition is what prevents overload**, so a
definition is required at mint. The definition is also what makes a near match safe to
offer: matching on names alone, with nothing to read, is exactly how an overload happens.

A DIMENSION IS A CLAIM, SO IT CARRIES A LEVEL
---------------------------------------------
`air quality` is a level-1 dimension. `particulate concentration` is a finer one whose
`coarser` is `air quality`. That is the same mechanism `sophistication.py` runs over claims
and over conditions, and it is used here rather than re-implemented: a registry row is
handed to `sophistication.validate_statements` with its `name` as its `id`.

This resolves the fixed-list argument rather than winning it. The knowledge-base
application's fixed list of thirteen is not a rival vocabulary. It is the set of level-1
rungs. Coarse dimensions recur across projects and are stable enough for machine
extraction with no author present. The long tail hangs off them as finer children, and the
long tail is what free text is for.

**A mint is never refused for existing.** The registry accretes from use, nobody designs it
up front, and a dimension with one claim against it is still a legitimate dimension
(`docs/philosophy.md` position 9). Only a missing definition refuses.

ponytail: near-duplicate matching is `difflib` over the normalised name and over the
normalised definition. It is string similarity and nothing more. Its ceiling is that it
catches spellings and near-identical wording, not synonyms: `tooling` versus `toolchain`
reads as two dimensions and always will. True semantic matching belongs where embeddings
already exist, which is the knowledge-base application; this half deliberately stops at
what the standard library can do, with no network and no new dependency.
"""
import argparse
import difflib
import json
import os
import pathlib
import re
import sys
from datetime import date

# The level mechanism lives in one file. A registry row is a statement, so it is validated
# through the same validator claims and conditions use, never a second implementation.
import sophistication

# WHO SAID IT. The same four words the knowledge-base application's Claim Record uses,
# so a condition does not have to be re-described on the way across.
BASES = ("stated-in-source", "inferred-from-conflict", "human", "rule")

# HOW FAR IT HAS BEEN CHECKED. `boundary.py` reads this one: a formal condition on a
# claim is one whose status is `confirmed`, and nothing else is.
STATUSES = ("asserted", "proposed", "monitoring", "confirmed", "refuted")

# A condition that states no status has not been checked, so it reads as `asserted`.
# Never `confirmed`: a silent default that promotes a condition to formal is the one
# default that could not be undone by reading the file.
DEFAULT_STATUS = "asserted"

# The five words `basis` held until 29 August 2026, when it split into the pair above.
LEGACY_BASES = ("tested", "replicated", "observed", "untested", "inferred")

# THE TRANSLATION TABLE, and the only copy of it. An old basis word said two things at
# once, so reading it back out is a READING OF INTENT AND NOT A LOSSLESS CONVERSION: a
# condition written `tested` and one written `replicated` both arrive as
# `stated-in-source` + `confirmed`, and nothing downstream can tell them apart again.
# The grouping is the decision of 29 August 2026: `replicated` and `tested` are the
# strong pair and become `confirmed`; `observed` is weaker and becomes `monitoring`;
# `untested` and `inferred` were never checked at all and become `asserted` and
# `proposed`. A file on disk is never rewritten by this; it is read through it.
LEGACY = {
    "replicated": ("stated-in-source", "confirmed"),
    "tested": ("stated-in-source", "confirmed"),
    "observed": ("stated-in-source", "monitoring"),
    "untested": ("human", "asserted"),
    "inferred": ("inferred-from-conflict", "proposed"),
}

# Every word `basis` may carry, old or new. The capture CLI checks against this, so a
# habit typed a hundred times still works.
ALL_BASES = BASES + LEGACY_BASES

# Above this, two normalised names are reported as probably one dimension. Set where a
# single-character typo in a short name matches and two different words do not.
#
# THE OTHER HALF OF THE MATCHING IS PROVISIONAL, AND SO IS ITS THRESHOLD. True semantic
# matching lives in the knowledge-base application, which has embeddings and vector
# search, and its threshold sits at 0.92. **That number is provisional and is to be
# re-measured once fifty real dimensions have been minted.** Thirteen hand-written seeds
# are not a sample: they were written to be distinct, so they cannot show what the long
# tail does, and the failure that matters is a near miss in that tail. The two
# measurements that exist already disagree. An offline run saw a gap of 0.052 between the
# closest genuinely different pair and the nearest true duplicate; a live query against
# the real rows saw 0.164. A threshold chosen inside the wider gap is not safe inside the
# narrower one, and neither run says which gap fifty real dimensions produce.
NEAR = 0.85

# Above this, two definitions are reported as probably one dimension under two names.
# Lower than NEAR because a definition is a whole sentence: two sentences saying the same
# thing share far more of their characters than two words do, but they also differ in
# wording that carries no meaning, so the bar that catches a restatement sits below the bar
# that catches a typo.
NEAR_DEFINITION = 0.80

REGISTRY = "dimensions.json"

# Who minted the row. Absent means `author`, which is the convention `supports.by` already
# uses in `conflicts.py`, so the two do not have to be read differently.
MINTERS = ("author", "model")
AUTHOR = "author"

# A level is an ordinal from 1 up, and a row that states none is a level-1 rung. See
# `sophistication.py`: the ladder has no top and its rungs have no names.
DEFAULT_LEVEL = 1

# The message a mint with no definition is refused with. It is one string because it is
# the whole reason this field exists, and it must read the same from the library and from
# the command line.
NO_DEFINITION = ("a dimension needs a one-sentence definition at mint: an undefined "
                 "dimension is an overload waiting to happen, because the next author to "
                 "reach for the name has nothing to read and will use it for something "
                 "else")


def registry_path(root=None):
    """Where the registry lives: beside the source index, so one project has one.

    With no `root` this reads `sourced.STORE`, which already honours `SOURCED_ROOT`,
    `SOURCED_STORE` and `sourced.set_store()`. Imported inside the function because
    `sourced.py` imports this module, and read at call time because `set_store()` moves
    the store after import.
    """
    if root is not None:
        return pathlib.Path(root) / REGISTRY
    import sourced
    return sourced.STORE / REGISTRY


def load(root=None):
    """The registry rows, [] when the project has never recorded a dimension."""
    path = registry_path(root)
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []


def save(rows, root=None):
    """Write the registry atomically: temp file in the same directory, then replace.

    ponytail: this makes the write atomic, not the read-modify-write in `register`.
    Two captures running at the same instant can still lose one row. Ceiling is a
    single author on one machine, the same ceiling the decision ledger names; if two
    processes ever capture concurrently, take a lock file around register().
    """
    path = registry_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + f".{os.getpid()}.tmp")
    tmp.write_text(json.dumps(rows, indent=1) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def normalise(name):
    """The near-duplicate key: casefolded, punctuation flattened, plural dropped.

    Deliberately crude. It exists to catch `Air Quality`, `air-quality` and `air
    qualities` arriving as three dimensions, which is a spelling accident. It does not
    catch a genuine synonym, and it is not meant to.
    """
    text = re.sub(r"[-_]+", " ", str(name)).casefold()
    text = re.sub(r"\s+", " ", text).strip()
    return text[:-1] if len(text) > 1 and text.endswith("s") else text


def _near(a, b):
    """True when two names are probably one dimension spelt two ways."""
    na, nb = normalise(a), normalise(b)
    return na == nb or difflib.SequenceMatcher(None, na, nb).ratio() >= NEAR


class Registration(tuple):
    """What `register` answers: (status, row, why).

    A tuple so it prints and unpacks plainly, with names so a caller reads
    `result.row["definition"]` rather than counting positions. `status` is one of `new`,
    `known` or `near`. `row` is the registry row, existing or minted. `why` is None when
    there is nothing to say, and a sentence when there is: on a `near` it says what the
    name looks like and what that dimension means, and on a `known` it is the overload
    warning, raised when the definition passed differs from the one already stored.
    """
    __slots__ = ()

    def __new__(cls, status, row, why=None):
        return super().__new__(cls, (status, row, why))

    status = property(lambda self: self[0])
    row = property(lambda self: self[1])
    why = property(lambda self: self[2])


def level_of(row):
    """The row's level. A row that states none is a level-1 rung."""
    return row.get("level", DEFAULT_LEVEL)


def is_defined(row):
    """False for a row that predates the definition requirement, or was captured undefined."""
    return bool((row.get("definition") or "").strip())


def _statements(rows):
    """The registry as statements `sophistication.validate_statements` can read.

    A registry row IS a statement: `air quality` is level 1 and `particulate` is a finer
    one whose `coarser` is `air quality`. The id is the name, so a `coarser` naming an
    unknown dimension resolves to nothing and is refused there. This is why there is no
    second implementation of the level mechanism in this file.
    """
    out = []
    for row in rows:
        rec = {"id": row["name"], "level": level_of(row)}
        if row.get("coarser") is not None:
            rec["coarser"] = row["coarser"]
        out.append(rec)
    return out


def validate_rows(rows, what="dimensions"):
    """Shape check on a whole registry, or on a sidecar's `dimensions[]`. True or ValueError.

    Legacy rows pass: a row with no `definition` is an undefined row, not a refused one.
    Refusing them would break the registry that already exists, and `report()` names them
    instead.
    """
    if not isinstance(rows, list):
        raise ValueError(f"{what} must be an array")
    seen = set()
    for i, row in enumerate(rows):
        here = f"{what}[{i}]"
        if not isinstance(row, dict):
            raise ValueError(f"{here} must be an object, not {row!r}")
        name = row.get("name")
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"{here} is missing a `name`")
        key = normalise(name)
        if key in seen:
            raise ValueError(
                f"{here}: {name!r} is recorded twice, so a `coarser` naming it cannot say "
                f"which row it means")
        seen.add(key)
        if "definition" in row and not isinstance(row["definition"], str):
            raise ValueError(f"{here}: definition must be a string")
        # `level` and `coarser` are NOT checked here. They go to
        # `sophistication.validate_statements` below, which already owns the bound, the
        # resolution of a sibling and the cycle walk. A second implementation of the level
        # mechanism is exactly what this file must not grow.
        if "finer" in row:
            raise ValueError(
                f"{here}: `finer` is not stored, because it is the inverse of `coarser` and "
                f"storing both invites them to disagree; use finer_of()")
        by = row.get("mintedBy", AUTHOR)
        if by not in MINTERS:
            raise ValueError(f"{here}: mintedBy {by!r} is not one of {list(MINTERS)}")
        if row.get("mintedModel") and by == AUTHOR:
            raise ValueError(
                f"{here}: mintedModel {row['mintedModel']!r} is recorded against an author "
                f"mint; a model named there says a model minted it")
    try:
        sophistication.validate_statements(_statements(rows), what)
    except AssertionError as e:
        raise ValueError(str(e)) from None
    return True


def _norm_text(text):
    """The definition comparison key: casefolded, whitespace collapsed."""
    return re.sub(r"\s+", " ", str(text or "")).casefold().strip()


def _near_row(rows, name, definition):
    """(row, why) for the first row this looks like, or (None, None).

    Two questions, not one. The NAME may be the same word spelt differently, which is the
    split this registry has always caught. The DEFINITION may say the same thing under a
    different name, which is the split a bare-string registry never sees.
    """
    key, dkey = normalise(name), _norm_text(definition)
    for row in rows:
        ratio = difflib.SequenceMatcher(None, normalise(row["name"]), key).ratio()
        if ratio >= NEAR:
            return row, (f"{name!r} looks like {row['name']!r} (name similarity "
                         f"{ratio:.2f}), which is defined as: "
                         f"{row.get('definition') or 'nothing yet'}")
        if not dkey or not is_defined(row):
            continue
        dratio = difflib.SequenceMatcher(None, _norm_text(row["definition"]), dkey).ratio()
        if dratio >= NEAR_DEFINITION:
            return row, (f"{name!r} is defined almost exactly as {row['name']!r} "
                         f"(definition similarity {dratio:.2f}): {row['definition']}")
    return None, None


def register(name, definition=None, level=DEFAULT_LEVEL, coarser=None, root=None,
             minted_by=AUTHOR, model=None, force=False, allow_undefined=False):
    """Record a use of `name`. Returns a `Registration` of (status, row, why).

    `known`  the registry already holds this name, normalised. `uses` goes up by one. A
             `definition` passed that differs from the stored one is NOT written over the
             top, and comes back as `why`: two definitions under one name is the overload
             this whole mechanism exists to catch, and the author decides which one wins.
    `near`   the name, or the definition, is close to a row that already exists. The row
             comes back WITH its definition, so the caller can read what it would be
             joining. Nothing is minted and nothing is written. Pass `force=True` to mint
             anyway, which records `forcedPast` on the new row.
    `new`    minted.

    A mint with no definition raises ValueError. `allow_undefined=True` is the one way
    past it, and it exists for the capture path only: capturing the source is the point,
    so `sourced.py --condition` records an undefined row and warns rather than losing the
    capture. Nothing else should pass it.
    """
    name = str(name).strip()
    if not name:
        raise ValueError("a dimension needs a name")
    if minted_by not in MINTERS:
        raise ValueError(f"mintedBy {minted_by!r} is not one of {list(MINTERS)}")
    if model and minted_by == AUTHOR:
        raise ValueError(f"mintedModel {model!r} is refused on an author mint: a model "
                         f"named there says a model minted it")
    definition = (definition or "").strip()
    rows = load(root)

    key = normalise(name)
    for row in rows:
        if normalise(row["name"]) != key:
            continue
        row["uses"] = row.get("uses", 0) + 1
        why = None
        if definition and is_defined(row) and _norm_text(row["definition"]) != _norm_text(definition):
            why = (f"possible overload: {row['name']!r} is already defined as "
                   f"{row['definition']!r}, and the definition offered was "
                   f"{definition!r}. The stored definition stands. Two definitions under "
                   f"one name make a false comparison, which is the expensive failure.")
        elif definition and not is_defined(row):
            # Filling in a row that predates the requirement is not an overload.
            row["definition"] = definition
        save(rows, root)
        return Registration("known", row, why)

    if not definition and not allow_undefined:
        raise ValueError(f"{name!r}: {NO_DEFINITION}")

    match, why = _near_row(rows, name, definition)
    if match is not None and not force:
        return Registration("near", match, why)

    row = {"name": name, "definition": definition,
           "level": DEFAULT_LEVEL if level is None else level,
           "firstSeen": date.today().isoformat(), "uses": 1}
    if coarser is not None:
        row["coarser"] = str(coarser).strip()
    if minted_by != AUTHOR:
        row["mintedBy"] = minted_by
        if model:
            row["mintedModel"] = model
    if match is not None:
        row["forcedPast"] = match["name"]
    validate_rows(rows + [row])
    rows.append(row)
    save(rows, root)
    return Registration("new", row, why if match is not None else None)


def define(name, definition, level=None, coarser=None, root=None,
           minted_by=AUTHOR, model=None):
    """Set a dimension's definition, minting the row when it does not exist yet.

    This is the author saying what the name means, so it OVERWRITES. `register` refuses to
    overwrite because it is called from the capture path, where a differing definition is
    a warning and not an instruction. Returns the row.

    `level` and `coarser` default to None and NOT to the level a new row would get,
    because defining an existing dimension must not quietly move it back down the ladder.
    Only a level actually passed in changes a level already recorded. A row minted here
    gets `DEFAULT_LEVEL` like any other new row.
    """
    definition = str(definition or "").strip()
    if not definition:
        raise ValueError(f"{name!r}: {NO_DEFINITION}")
    rows = load(root)
    key = normalise(str(name).strip())
    for row in rows:
        if normalise(row["name"]) == key:
            row["definition"] = definition
            if level is not None:
                row["level"] = level
            if coarser is not None:
                row["coarser"] = str(coarser).strip()
            validate_rows(rows)
            save(rows, root)
            return row
    return register(name, definition,
                    DEFAULT_LEVEL if level is None else level,
                    coarser, root, minted_by, model, force=True).row


def finer_of(name, rows=None, root=None):
    """The names of every dimension whose `coarser` is `name`, in registry order.

    `finer` is NOT stored. It is the exact inverse of `coarser`, and a stored pair of
    inverses is a pair that can disagree, so it is computed here instead.
    """
    rows = load(root) if rows is None else rows
    key = normalise(name)
    return [r["name"] for r in rows if normalise(r.get("coarser") or "") == key]


def used_dimensions(data):
    """{normalised name: spelling} for every dimension a condition in this sidecar names.

    Both places a condition lives are read: the `holds_when` and `fails_when` regions of a
    claim, and the `conditions` an evidence row carries. A dimension-less condition and a
    condition that will not parse are skipped, because this is a lookup and not a
    validator.
    """
    out = {}

    def scan(entries):
        for entry in entries or []:
            try:
                dimension, _, _ = read_condition(entry)
            except ValueError:
                continue
            if dimension:
                out.setdefault(normalise(dimension), dimension)

    for claim in (data.get("claims") or []):
        if isinstance(claim, dict):
            scan(claim.get("holds_when"))
            scan(claim.get("fails_when"))
    for row in (data.get("evidence") or []):
        if isinstance(row, dict):
            scan(row.get("conditions"))
    return out


def for_sidecar(data, root=None):
    """The registry rows for the dimensions this sidecar actually uses, in registry order.

    A sidecar travels on its own, so a dimension defined only in a project registry means
    nothing to whoever receives the file. This is what gets written into the optional
    top-level `dimensions[]`. It is GENERATED and never authored.

    A row whose `coarser` is not itself used comes along as well, because a finer dimension
    shipped without its coarser rung names a parent the receiver cannot resolve.
    """
    rows = load(root)
    by_key = {normalise(r["name"]): r for r in rows}
    keys, taken = list(used_dimensions(data)), set()
    while keys:
        key = keys.pop(0)
        row = by_key.get(key)
        if row is None or key in taken:
            continue
        taken.add(key)
        parent = normalise(row.get("coarser") or "")
        if parent:
            keys.append(parent)
    return [r for r in rows if normalise(r["name"]) in taken]


def validate_sidecar_dimensions(data):
    """The optional top-level `dimensions[]` on a sidecar. True, or ValueError.

    Absent is fine and partial is honest: nothing here requires the block to name every
    dimension the file uses, because a sender may ship only the ones a receiver could not
    otherwise read. What IS required is that the block resolves on its own, so a `coarser`
    must name another row in the same block.
    """
    if "dimensions" not in data:
        return True
    return validate_rows(data["dimensions"], "dimensions")


def duplicates(rows):
    """[(name, name)] for every pair in the registry that is probably one dimension.

    ponytail: names only, still. A pair of rows with near-identical DEFINITIONS is caught
    at mint by `_near_row` and is not re-reported here, because by the time a row is on
    disk the author has already been shown it and decided.
    """
    names = [row["name"] for row in rows]
    return [(a, b) for i, a in enumerate(names) for b in names[i + 1:] if _near(a, b)]


def read_condition(entry):
    """(dimension, value, basis) from every condition shape. Raises ValueError otherwise.

    `basis` comes back **as written**, so a condition carrying one of the five old words
    returns that word. This is the older reader and it is kept for the callers that
    already use it. **New code should call `read_condition_full`**, which returns the
    `(basis, status)` pair and translates an old word into it.

    Shape `{dimension, value, basis}` gives all three. Shape `{condition, basis}` gives
    `(None, condition, basis)`: a dimension-less condition, which is what every condition
    written before this file was.
    """
    if not isinstance(entry, dict):
        raise ValueError(f"a condition must be an object, not {entry!r}")
    if ("dimension" in entry or "value" in entry) and "condition" in entry:
        raise ValueError(
            "a condition carries either the new `dimension`/`value` pair or the older "
            f"`condition` string, never both: {entry!r}")
    if "dimension" in entry or "value" in entry:
        dimension = (entry.get("dimension") or "").strip() if isinstance(
            entry.get("dimension"), str) else ""
        value = (entry.get("value") or "").strip() if isinstance(
            entry.get("value"), str) else ""
        if not dimension:
            raise ValueError(f"condition is missing a `dimension`: {entry!r}")
        if not value:
            raise ValueError(f"condition {dimension!r} is missing a `value`: {entry!r}")
    else:
        dimension = None
        value = (entry.get("condition") or "").strip() if isinstance(
            entry.get("condition"), str) else ""
        if not value:
            raise ValueError(
                f"a condition needs `dimension` and `value`, or the older `condition`: {entry!r}")
    basis = entry.get("basis")
    if basis not in ALL_BASES:
        raise ValueError(
            f"condition {value!r} has basis {basis!r}, not one of {list(BASES)} "
            f"or one of the older {list(LEGACY_BASES)}")
    if "status" in entry and entry["status"] not in STATUSES:
        raise ValueError(
            f"condition {value!r} has status {entry['status']!r}, not one of {list(STATUSES)}")
    return dimension, value, basis


def read_condition_full(entry):
    """(dimension, value, basis, status), always in the current two-field vocabulary.

    A condition carrying one of the five old basis words is translated through `LEGACY`,
    which is a reading of intent and not a lossless conversion. A condition carrying a
    current basis and no status reads as `DEFAULT_STATUS`. An explicit `status` always
    wins, including beside an old basis word, because the author who wrote it down knew
    more than the table does.

    This is the reader new code uses. `read_condition` stays for the callers written
    before the split.
    """
    dimension, value, basis = read_condition(entry)
    if basis in LEGACY:
        basis, status = LEGACY[basis]
    else:
        status = DEFAULT_STATUS
    return dimension, value, basis, entry.get("status", status)


def validate_condition(entry):
    """Shape check on one condition. True, or ValueError naming what was wrong."""
    read_condition(entry)
    return True


def label(entry):
    """The condition as a reader sees it: `dimension: value`, or just the value."""
    dimension, value, _ = read_condition(entry)
    return f"{dimension}: {value}" if dimension else value


def _printed(root=None):
    """What `report()` writes, as a string. Used by the self-check only."""
    import contextlib, io
    with contextlib.redirect_stdout(io.StringIO()) as buf:
        report(root)
    return buf.getvalue()


def report(root=None):
    rows = load(root)
    if not rows:
        print(f"{registry_path(root)}: no dimensions recorded yet")
        return 0
    print(f"{registry_path(root)}: {len(rows)} dimensions")
    for row in sorted(rows, key=lambda r: (-r.get("uses", 0), r["name"])):
        parent = f"   finer than {row['coarser']!r}" if row.get("coarser") else ""
        kids = finer_of(row["name"], rows)
        children = f"   finer: {', '.join(repr(k) for k in kids)}" if kids else ""
        print(f"  {row.get('uses', 0):>3}  {row['name']}   "
              f"({sophistication.level_name(level_of(row))}, first seen "
              f"{row['firstSeen']}){parent}{children}")
        if is_defined(row):
            print(f"       {row['definition']}")
        if row.get("forcedPast"):
            print(f"       minted past a near match to {row['forcedPast']!r}")
    undefined = [r for r in rows if not is_defined(r)]
    if undefined:
        print("  undefined; these predate the definition requirement and should be defined,")
        print("  because a name with nothing to read against it is an overload waiting to happen:")
        for row in undefined:
            print(f"    {row['name']!r}   sourced.py --define \"{row['name']}=…\"")
    pairs = duplicates(rows)
    if not pairs:
        print("  no probable duplicates")
        return 0
    print("  probable duplicates, one dimension spelt two ways:")
    for a, b in pairs:
        print(f"    {a!r} ~ {b!r}")
    return 0


def _self_check():
    """Seventeen cases with known answers against a temporary registry, no network.

    The threshold is all seventeen. This decides whether two claims are comparable at all,
    and it now decides it in two directions. A registry that quietly holds two names for
    one dimension makes a conflict uncomputable, which is a SPLIT, and it is silent and
    recoverable. A registry that quietly holds one name over two meanings makes a FALSE
    comparison, which is an OVERLOAD, and that reading reaches `integrate.py` and refuses
    a delivery that should have shipped. A wrong refusal is how a gate gets bypassed, so
    the definition cases are the ones with the most riding on them.
    """
    import tempfile

    AIR = "How clean the air is at the place and time of the observation."
    PM = "The mass of suspended particulate matter in the air, in parts per million."

    def case_normalise(root):
        assert normalise("Air Quality") == normalise("air-quality") == "air quality"
        assert normalise("air_qualities") == "air qualitie", normalise("air_qualities")
        assert normalise(" Tooling ") == "tooling" and normalise("toolings") == "tooling"
        assert normalise("tooling") != normalise("toolchain"), "a synonym is not a spelling"

    def case_first_seen(root):
        result = register("air quality", AIR, root=root)
        assert result.status == "new" and result.why is None, result
        rows = load(root)
        assert len(rows) == 1
        row = rows[0]
        assert row["name"] == "air quality" and row["definition"] == AIR
        assert row["uses"] == 1 and row["level"] == 1
        assert row["firstSeen"] == date.today().isoformat()
        assert "mintedBy" not in row, "an author mint says nothing, because absent is author"
        assert "finer" not in row, "finer is never stored"
        # It unpacks as a tuple as well, because that is what the old callers do.
        status, got, why = result
        assert (status, got, why) == ("new", row, None)

    def case_no_definition_refused(root):
        for bad in (None, "", "   "):
            try:
                register("humidity", bad, root=root)
            except ValueError as e:
                assert "overload waiting to happen" in str(e), e
                assert "humidity" in str(e), e
                continue
            raise AssertionError(f"a mint with definition {bad!r} must be refused")
        assert [r["name"] for r in load(root)] == [], "nothing was written"
        # The capture path is the one way past it, and it records the row as undefined.
        result = register("humidity", root=root, allow_undefined=True)
        assert result.status == "new" and not is_defined(result.row)

    def case_legacy_row_loads(root):
        # The shape the registry held before 29 August 2026: no definition, no level.
        save([{"name": "tooling", "firstSeen": "2026-08-28", "uses": 4}], root)
        rows = load(root)
        assert len(rows) == 1 and not is_defined(rows[0]), "a legacy row must still load"
        assert level_of(rows[0]) == 1, "a row that states no level is a level-1 rung"
        assert validate_rows(rows), "a legacy row is undefined, never refused"
        printed = _printed(root)
        assert "predate the definition requirement" in printed, printed
        assert "'tooling'" in printed, printed
        # A use of it still counts, and a definition supplied later fills the row in
        # rather than colliding with one: there is nothing there to collide with.
        assert register("tooling", "Which generation of tool produced the result.",
                        root=root).why is None
        assert is_defined(load(root)[0]) and load(root)[0]["uses"] == 5

    def case_exact_repeat(root):
        register("air quality", AIR, root=root)
        result = register("air quality", root=root)
        assert result.status == "known" and result.row["uses"] == 2, result
        # Normalised, so a respelling is the SAME row and not a second one.
        assert register("Air-Quality", root=root).status == "known"
        rows = load(root)
        assert len(rows) == 1 and rows[0]["uses"] == 3, rows
        assert rows[0]["name"] == "air quality", "the first spelling stands"

    def case_overload_reported(root):
        register("method", "The research method the study used.", root=root)
        other = "The manufacturing method the plant used."
        result = register("method", other, root=root)
        assert result.status == "known", result
        assert result.why and "possible overload" in result.why, result.why
        assert other in result.why and "research method" in result.why
        assert load(root)[0]["definition"] == "The research method the study used.", \
            "the stored definition must not be written over the top"
        assert load(root)[0]["uses"] == 2, "the use still counts"

    def case_near_needs_force(root):
        register("air quality", AIR, root=root)
        # Near on the NAME.
        result = register("air-qualty", "Something else entirely.", root=root)
        assert result.status == "near", result
        assert result.row["definition"] == AIR, "the caller must see what it would be joining"
        assert result.why and "air quality" in result.why and AIR in result.why
        assert len(load(root)) == 1, "a near match does not mint without force"
        # Near on the DEFINITION, under a name nothing would have matched.
        result = register("atmospheric cleanliness",
                          "How clean the air is at the place and time of observation.",
                          root=root)
        assert result.status == "near" and result.row["name"] == "air quality", result
        assert "definition similarity" in result.why, result.why
        assert len(load(root)) == 1
        # A genuinely different dimension is not near anything.
        assert register("sun angle", "How high the sun sits above the horizon.",
                        root=root).status == "new"

    def case_force_mints_and_records(root):
        register("air quality", AIR, root=root)
        result = register("air-qualty", "A deliberately separate dimension.",
                          root=root, force=True)
        assert result.status == "new", result
        assert result.row["forcedPast"] == "air quality", result.row
        assert result.why and "air quality" in result.why, "the reason is still reported"
        assert len(load(root)) == 2
        assert "minted past a near match" in _printed(root)

    def case_levels_and_coarser(root):
        register("air quality", AIR, root=root)
        register("particulate", PM, level=3, coarser="air quality", root=root)
        rows = load(root)
        assert level_of(rows[0]) == 1 and level_of(rows[1]) == 3
        assert rows[1]["coarser"] == "air quality"
        assert validate_rows(rows)
        # The check is sophistication's, not a copy of it: its message is what comes back.
        for bad in ({"name": "x", "level": 0}, {"name": "x", "level": "3"},
                    {"name": "x", "level": True}, {"name": "x", "level": 2.5}):
            try:
                validate_rows([bad])
            except ValueError as e:
                assert "whole number from 1 up" in str(e), e
                continue
            raise AssertionError(f"{bad} must be refused")
        # A coarser rung at the same depth or below is refused, by the same validator.
        try:
            validate_rows([{"name": "a", "level": 1},
                           {"name": "b", "level": 1, "coarser": "a"}])
        except ValueError as e:
            assert "coarser sibling" in str(e), e
        else:
            raise AssertionError("a coarser rung at the same level must be refused")
        # And there is no second implementation to drift: this file states no bound.
        src = pathlib.Path(__file__).read_text(encoding="utf-8")
        assert "whole number from 1 up" not in src.split("def _self_check")[0], \
            "the level bound must live in sophistication.py only"

    def case_unknown_coarser_refused(root):
        register("air quality", AIR, root=root)
        try:
            register("particulate", PM, level=3, coarser="air quailty", root=root)
        except ValueError as e:
            assert "coarser" in str(e) and "air quailty" in str(e), e
        else:
            raise AssertionError("a coarser naming an unknown dimension must be refused")
        assert [r["name"] for r in load(root)] == ["air quality"], "nothing was written"

    def case_finer_is_the_inverse(root):
        register("air quality", AIR, root=root)
        register("particulate", PM, level=3, coarser="air quality", root=root)
        register("pm2.5", "Particulate below 2.5 micrometres.", level=4,
                 coarser="particulate", root=root)
        rows = load(root)
        assert finer_of("air quality", rows) == ["particulate"]
        assert finer_of("particulate", rows) == ["pm2.5"]
        assert finer_of("pm2.5", rows) == []
        # Exactly the inverse, both ways, with no third source of truth.
        stored = {(r["coarser"], r["name"]) for r in rows if r.get("coarser")}
        computed = {(p["name"], child) for p in rows for child in finer_of(p["name"], rows)}
        assert stored == computed, (stored, computed)
        assert all("finer" not in r for r in rows), "finer is never stored"

    def case_minted_by(root):
        result = register("sun angle", "How high the sun sits above the horizon.",
                          root=root, minted_by="model", model="claude-opus-5")
        assert result.row["mintedBy"] == "model"
        assert result.row["mintedModel"] == "claude-opus-5"
        assert validate_rows(load(root))
        for kwargs in ({"minted_by": "author", "model": "claude-opus-5"},
                       {"minted_by": "nobody"}):
            try:
                register("humidity", "How much water the air holds.", root=root, **kwargs)
            except ValueError:
                continue
            raise AssertionError(f"{kwargs} must be refused")
        try:
            validate_rows([{"name": "x", "mintedModel": "claude-opus-5"}])
        except ValueError as e:
            assert "author mint" in str(e), e
        else:
            raise AssertionError("a model named on an author mint must be refused")

    def case_for_sidecar(root):
        register("air quality", AIR, root=root)
        register("particulate", PM, level=3, coarser="air quality", root=root)
        register("sun angle", "How high the sun sits above the horizon.", root=root)
        register("period", "The span of time the reading covers.", root=root)
        data = {"claims": [{"id": "c1", "holds_when": [
            {"dimension": "Air-Quality", "value": "clean", "basis": "tested"},
            {"condition": "a dimension-less condition", "basis": "tested"}]}],
            "evidence": [{"id": "e1", "conditions": [
                {"dimension": "period", "value": "2015-2026", "basis": "observed"}]}]}
        names = [r["name"] for r in for_sidecar(data, root)]
        assert names == ["air quality", "period"], names
        # A finer dimension brings its coarser rung, or the receiver cannot resolve it.
        finer = {"claims": [{"id": "c1", "holds_when": [
            {"dimension": "particulate", "value": "below 6 ppm", "basis": "tested"}]}]}
        assert [r["name"] for r in for_sidecar(finer, root)] == ["air quality", "particulate"]
        # A file naming no dimension at all carries no block.
        assert for_sidecar({"claims": [], "evidence": []}, root) == []
        # And the block it produces validates as a block.
        assert validate_sidecar_dimensions({"dimensions": for_sidecar(data, root)})

    def case_sidecar_block(root):
        assert validate_sidecar_dimensions({"claims": []}), "an absent block is fine"
        assert validate_sidecar_dimensions({"dimensions": []}), "an empty block is fine"
        good = [{"name": "air quality", "definition": AIR, "level": 1,
                 "firstSeen": "2026-08-29", "uses": 2},
                {"name": "particulate", "definition": PM, "level": 3,
                 "coarser": "air quality", "firstSeen": "2026-08-29", "uses": 1}]
        assert validate_sidecar_dimensions({"dimensions": good})
        # Partial is honest: a block naming only the coarse rung still validates.
        assert validate_sidecar_dimensions({"dimensions": good[:1]})
        for bad in ("not an array", [{"definition": AIR}], [{"name": "  "}],
                    [{"name": "a", "definition": 3}],
                    [{"name": "a", "finer": "b"}],
                    [{"name": "a"}, {"name": "A"}],
                    [{"name": "a", "coarser": "nobody"}],
                    [{"name": "a", "mintedBy": "robot"}]):
            try:
                validate_sidecar_dimensions({"dimensions": bad})
            except ValueError:
                continue
            raise AssertionError(f"a dimensions[] of {bad!r} must be refused")

    def case_shapes(root):
        assert read_condition({"dimension": "air quality", "value": "clean",
                               "basis": "observed"}) == ("air quality", "clean", "observed")
        # The shape written before this file existed still reads, as dimension-less.
        assert read_condition({"condition": "the weather is fine",
                               "basis": "tested"}) == (None, "the weather is fine", "tested")
        assert label({"dimension": "air quality", "value": "clean",
                      "basis": "observed"}) == "air quality: clean"
        assert label({"condition": "the weather is fine", "basis": "tested"}) == "the weather is fine"
        # The current pair reads as itself, and `read_condition` still answers three.
        pair = {"dimension": "air quality", "value": "clean", "basis": "human",
                "status": "confirmed"}
        assert read_condition(pair) == ("air quality", "clean", "human")
        assert read_condition_full(pair) == ("air quality", "clean", "human", "confirmed")
        # A current basis with no status has not been checked.
        assert read_condition_full({"dimension": "d", "value": "v", "basis": "rule"}) == (
            "d", "v", "rule", "asserted")

    def case_writing_the_block(root):
        # Writing the block into a sidecar validates before it replaces the file, and
        # the block it writes carries only the dimensions the file uses, plus any
        # coarser rung one of them names.
        import tempfile
        register("air quality", "how clean the air is where the observation was made",
                 root=root)
        register("particulate", "mass of suspended particulate per cubic metre",
                 level=3, coarser="air quality", root=root)
        register("unused thing", "a dimension no sidecar in this project mentions",
                 root=root)
        doc = {"sourced": "1.5",
               "artefact": {"path": "a.html"}, "disclosure": {},
               "claims": [{"id": "c1", "statement": "s",
                           "holds_when": [{"dimension": "particulate",
                                           "value": "below 6 ppm",
                                           "basis": "human", "status": "confirmed"}]}],
               "evidence": []}
        with tempfile.TemporaryDirectory() as d:
            f = pathlib.Path(d) / "a.sourced"
            f.write_text(json.dumps(doc), encoding="utf-8")
            written = write_sidecar_block(f, root)
            names = {r["name"] for r in written}
            assert names == {"particulate", "air quality"}, names
            back = json.loads(f.read_text(encoding="utf-8"))
            assert validate_sidecar_dimensions(back)
            assert all(r.get("definition") for r in back["dimensions"])

    def case_translation(root):
        # Every old word reads, and translates to a pair. The strong pair is `confirmed`,
        # `observed` is weaker, and neither of the last two has been checked at all.
        expected = {"tested": ("stated-in-source", "confirmed"),
                    "replicated": ("stated-in-source", "confirmed"),
                    "observed": ("stated-in-source", "monitoring"),
                    "untested": ("human", "asserted"),
                    "inferred": ("inferred-from-conflict", "proposed")}
        assert set(expected) == set(LEGACY_BASES), "every old word must translate"
        for old_word, pair in expected.items():
            entry = {"dimension": "air quality", "value": "clean", "basis": old_word}
            assert validate_condition(entry), old_word
            assert read_condition(entry)[2] == old_word, "the old word reads back as itself"
            assert read_condition_full(entry)[2:] == pair, old_word
        # Only the strong pair becomes formal, which is the rule that had to survive.
        formal = {w for w in LEGACY_BASES if LEGACY[w][1] == "confirmed"}
        assert formal == {"tested", "replicated"}, formal
        # An explicit status beside an old word wins over the table.
        assert read_condition_full({"dimension": "d", "value": "v", "basis": "untested",
                                    "status": "refuted"})[3] == "refuted"

    def case_refusals(root):
        bad = [({"value": "clean", "basis": "observed"}, "dimension"),
               ({"dimension": "air quality", "basis": "observed"}, "value"),
               ({"dimension": "air quality", "value": " ", "basis": "observed"}, "value"),
               ({"dimension": "air quality", "value": "clean"}, "basis"),
               ({"dimension": "air quality", "value": "clean", "basis": "guessed"}, "basis"),
               ({"dimension": "air quality", "value": "clean", "basis": "human",
                 "status": "checked"}, "status"),
               ({"dimension": "air quality", "value": "clean", "basis": "human",
                 "status": None}, "status"),
               ({"condition": "the weather is fine"}, "basis"),
               ({}, "dimension"),
               ("the weather is fine", "object")]
        for entry, word in bad:
            try:
                validate_condition(entry)
            except ValueError as e:
                assert word in str(e), f"the message must name {word}: {e}"
                continue
            raise AssertionError(f"{entry!r} must be refused")

    cases = [("the normaliser catches spellings, not synonyms", case_normalise),
             ("a first-seen dimension is minted with its definition", case_first_seen),
             ("a mint with no definition is refused", case_no_definition_refused),
             ("a legacy row with no definition still loads, and is reported", case_legacy_row_loads),
             ("an exact repeat counts a use, not a second row", case_exact_repeat),
             ("a second definition under one name is a possible overload", case_overload_reported),
             ("a near match shows its definition and does not mint", case_near_needs_force),
             ("force mints, and records what it was forced past", case_force_mints_and_records),
             ("a level and a coarser chain validate through sophistication", case_levels_and_coarser),
             ("a coarser naming an unknown dimension is refused", case_unknown_coarser_refused),
             ("finer_of is the exact inverse of coarser", case_finer_is_the_inverse),
             ("who minted the row, and a model refused on an author mint", case_minted_by),
             ("for_sidecar returns only the dimensions the file uses", case_for_sidecar),
             ("a sidecar dimensions[] block validates, or is refused", case_sidecar_block),
             ("every condition shape reads to one triple", case_shapes),
             ("an old basis word still reads, and translates to a pair", case_translation),
             ("writing the sidecar block validates before it replaces the file",
              case_writing_the_block),
             ("a missing field, or an unknown basis or status, is refused", case_refusals)]
    passed = 0
    for label_, fn in cases:
        with tempfile.TemporaryDirectory() as tmp:
            try:
                fn(tmp)
                passed += 1
                print(f"pass  {label_}")
            except AssertionError as e:
                print(f"FAIL  {label_}: {e}")
    total = len(cases)
    print(f"\ndimensions: self-check {'passed' if passed == total else 'FAILED'} "
          f"({passed} of {total} cases; the threshold is {total} of {total}, "
          f"near-duplicate above {NEAR} on the name and {NEAR_DEFINITION} on the definition)")
    return passed == total


def write_sidecar_block(path, root=None):
    """Write `dimensions[]` into a sidecar, from the registry. Returns the rows written.

    Generated, never authored. It is written last, after the claims and their conditions
    are settled, because it is a copy of what the registry already holds and a copy taken
    early goes stale.
    """
    path = pathlib.Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = for_sidecar(data, root)
    data["dimensions"] = rows
    # Validate BEFORE writing. This function edits a file in place, so a block that
    # does not resolve on its own would replace a good sidecar with a broken one, and
    # the caller would find out at the gate rather than here.
    validate_sidecar_dimensions(data)
    tmp = path.with_name(path.name + f".{os.getpid()}.tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)
    return rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="the per-project dimension registry")
    ap.add_argument("--store", default=None,
                    help="directory the registry lives in (default: the source store)")
    ap.add_argument("--sidecar", default=None, metavar="FILE.sourced",
                    help="write the definitions this sidecar's conditions use into it")
    ap.add_argument("--self-check", action="store_true")
    a = ap.parse_args()
    if a.self_check:
        sys.exit(0 if _self_check() else 1)
    if a.sidecar:
        written = write_sidecar_block(a.sidecar, a.store)
        print(f"{a.sidecar}: dimensions[] holds {len(written)} definitions")
        for row in written:
            print(f"  {row['name']}   {row.get('definition') or 'UNDEFINED'}")
        undefined = [r["name"] for r in written if not is_defined(r)]
        if undefined:
            print(f"  {len(undefined)} of them are undefined and mean nothing to a "
                  f"receiver: {', '.join(repr(n) for n in undefined)}", file=sys.stderr)
        sys.exit(0)
    sys.exit(report(a.store))
