#!/usr/bin/env python3
"""One eval round: stamp it, measure what the skill actually used, compare it to the last one.

    python3 round.py new <round-dir>                 stamp the manifest, scaffold the runs
    python3 round.py coverage <run-dir>              which features ran, generated not asserted
    python3 round.py verify <rounds-dir>             refuse a round whose files moved after scoring
    python3 round.py compare <rounds-dir>            the trend across rounds
    python3 round.py --self-check                    seven cases, known answers, no network

**Why the stamp happens before the run.** The thing under test is a working tree, and a working
tree changes. A commit hash taken afterwards describes something other than what ran, especially
in the session where the round's own findings are being fixed. So `new` runs first, refuses a
dirty tree unless told otherwise, and records a tree hash that stays true even when git does not.

**Why coverage is generated rather than reported.** An agent's account of its own process is an
introspective claim, which is the one kind of claim this framework refuses to take on trust. So
nothing here asks the agent what it used. It reads the artefacts left on disk and the tool calls
in the transcript, and where the two disagree it prefers the disk.
"""

import hashlib
import json
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
SKILL = HERE.parent / "skills" / "sourced"


def git(repo, *args):
    """One git call, or None when the command fails. A missing repo is a recordable state."""
    try:
        out = subprocess.run(["git", "-C", str(repo), *args],
                             capture_output=True, text=True, timeout=30)
        return out.stdout.strip() if out.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def tree_hash(root):
    """sha256 over the sorted per-file hashes of a directory.

    The only version field that is true when the tree is dirty. Two rounds with the same tree
    hash ran identical code, whatever the commit hash says.
    """
    h = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*")
                       if p.is_file() and "__pycache__" not in p.parts):
        h.update(str(path.relative_to(root)).encode())
        h.update(hashlib.sha256(path.read_bytes()).digest())
    return h.hexdigest()


def front_matter_version(path, key):
    m = re.search(rf"^{key}:\s*(\S+)", path.read_text(), re.M)
    return m.group(1) if m else None


def overlay(round_dir):
    """The operator's overlay: a file that relaxes or adds a constraint for these runs.

    Its TEXT stays with the measurements. Its HASH goes in the manifest, because a round
    that quietly relaxed a rule and a round that did not must not read the same, and a
    reader checking a result has to be able to tell which one they are holding.
    """
    for p in (round_dir / "overlay.md", round_dir.parent.parent / "overlay.md"):
        if p.exists() and p.read_text().strip():
            text = p.read_text()
            return text, hashlib.sha256(text.encode()).hexdigest()[:16]
    return "", None


def _arms():
    f = HERE / "arms.json"
    return json.loads(f.read_text()) if f.exists() else {}


def _arms_hash():
    f = HERE / "arms.json"
    return hashlib.sha256(f.read_bytes()).hexdigest()[:16] if f.exists() else None


def manifest(round_dir, allow_dirty=False):
    repo = SKILL.parent.parent
    sha = git(repo, "rev-parse", "HEAD")
    dirty = bool(git(repo, "status", "--porcelain", "skills/sourced", "evals"))
    if dirty and not allow_dirty:
        sys.exit("refusing to stamp a dirty tree. Commit first, or pass --allow-dirty.")
    pushed = bool(sha and git(repo, "branch", "-r", "--contains", sha))
    topics = json.loads((HERE / "topics.json").read_text())
    return {
        "round": round_dir.name,
        "date": (git(repo, "log", "-1", "--format=%cI") or "unknown"),
        "skillSha": sha,
        "skillDirty": dirty,
        "skillPushed": pushed,
        "skillTreeHash": tree_hash(SKILL),
        "promptVersion": front_matter_version(HERE / "run-prompt.md", "promptVersion"),
        "rubricVersion": front_matter_version(HERE / "rubric.md", "rubricVersion"),
        "topicsVersion": topics["topicsVersion"],
        "featuresVersion": json.loads((HERE / "features.json").read_text())["featuresVersion"],
        "overlayApplied": bool(overlay(round_dir)[1]),
        "overlayHash": overlay(round_dir)[1],
        # The control arms are frozen the way the prompt is, and hashed so that "the arms
        # did not move" is checkable rather than asserted. SKILL.md promised this stamp
        # and nothing implemented it, so prompts, models or settings could differ across
        # rounds while the manifest looked identical.
        "armsVersion": _arms().get("armsVersion"),
        "armsHash": _arms_hash(),
        "topics": [t["id"] for t in topics["topics"]],
    }


def cmd_new(round_dir, allow_dirty=False):
    round_dir = pathlib.Path(round_dir)
    if (round_dir / "manifest.json").exists():
        sys.exit(f"{round_dir}/manifest.json exists. A round is a measurement of a moment "
                 f"and is never re-stamped.")
    man = manifest(round_dir, allow_dirty)
    topics = {t["id"]: t for t in json.loads((HERE / "topics.json").read_text())["topics"]}
    body = (HERE / "run-prompt.md").read_text().split("```")[1]
    extra, _ = overlay(round_dir)
    if extra:
        body += "\n\nOPERATOR OVERLAY, in force for this run:\n\n" + extra.strip() + "\n"
    for tid in man["topics"]:
        run = round_dir / "runs" / tid
        (run / "store").mkdir(parents=True, exist_ok=True)
        write_shim(run)
        (run / "prompt.txt").write_text(
            body.replace("{{CLAIM}}", topics[tid]["claim"]).replace("{{RUNDIR}}", str(run.resolve()))
        )
    round_dir.joinpath("manifest.json").write_text(json.dumps(man, indent=2) + "\n")
    print(json.dumps(man, indent=2))
    return man


SHIM = """#!/bin/sh
# Logs every python3 command this run makes, then runs it. The point is that
# coverage is measured rather than reported: an agent's account of its own
# process is exactly the introspective claim this framework will not take on
# trust. Put this directory first on PATH and the log writes itself.
echo "$@" >> "{log}"
exec {real} "$@"
"""


def write_shim(run):
    """A python3 on PATH that records its own argv. Eight lines, and it is the whole
    instrument for script invocations."""
    b = run / "bin"
    b.mkdir(exist_ok=True)
    shim = b / "python3"
    shim.write_text(SHIM.format(log=(run / "runlog.txt").resolve(),
                                real=subprocess.run(["which", "python3"], capture_output=True,
                                                    text=True).stdout.strip() or "/usr/bin/python3"))
    shim.chmod(0o755)


# --- coverage ---------------------------------------------------------------

def _sidecar(run):
    for p in run.glob("*.sourced"):
        try:
            return json.loads(p.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def _claim_fields(sidecar):
    fields = set()
    for c in sidecar.get("claims", []) or []:
        fields.update(k for k, v in c.items() if v not in (None, [], {}, ""))
    return fields


def detect(feature, run, transcript):
    """True when there is evidence on disk or in the transcript that this feature ran."""
    how = feature["detect"]
    if how == "store_rows":
        return any(f.is_file() for f in (run / "store").rglob("*"))
    if how.startswith("file:"):
        p = run / how.split(":", 1)[1]
        return p.exists() and p.stat().st_size > 0
    if how.startswith("sidecar_key:"):
        key = how.split(":", 1)[1]
        return bool(_sidecar(run).get(key))
    if how.startswith("claim_field:"):
        return how.split(":", 1)[1] in _claim_fields(_sidecar(run))
    if how.startswith("claim_any_field:"):
        # A feature whose output is fields ON claims, any one of which proves it ran.
        # boundary.py writes holds_when/fails_when/replaced_by/unknown_region per claim
        # and never a top-level key, which is what round 01 detected against and missed.
        wanted = set(how.split(":", 1)[1].split("|"))
        return bool(wanted & _claim_fields(_sidecar(run)))
    if how.startswith("evidence_any_field:"):
        # Same idea as claim_any_field, one level down: a field written on an
        # evidence row rather than on a claim.
        wanted = set(how.split(":", 1)[1].split("|"))
        rows = _sidecar(run).get("evidence") or []
        return any(wanted & set(r) for r in rows if isinstance(r, dict))
    if how == "sidecar_fn:multi_quote":
        # A source cited more than once, which is the practice change round 04 asks
        # for: one evidence row per quote, sharing the URL. Twelve runs across three
        # rounds produced exactly zero, so this starts at the floor.
        rows = [r for r in (_sidecar(run).get("evidence") or []) if isinstance(r, dict)]
        urls = [r.get("url") for r in rows if r.get("url")]
        return len(urls) > len(set(urls))
    if how.startswith("artefact_re:"):
        # Evidence in the delivered artefact itself, not in the ledgers.
        art = run / "artefact.md"
        if not art.exists():
            return False
        return re.search(how.split(":", 1)[1], art.read_text(errors="replace"),
                         re.M | re.I) is not None
    if how == "read":
        return feature["note"] in transcript
    if how.startswith("invocation"):
        needle = how.split(":", 1)[1] if ":" in how else feature["id"].split()[0]
        return needle in transcript
    return False


def _dir_hash(run):
    """sha256 over the run's artefacts and ledgers, sorted, excluding what we write.

    The store is included: a capture is evidence and a changed capture changes what a
    quote was checked against.
    """
    h = hashlib.sha256()
    skip = {"coverage.json", "runlog.txt"}
    for f in sorted(p for p in run.rglob("*") if p.is_file()):
        if f.name in skip or "/bin/" in str(f):
            continue
        h.update(str(f.relative_to(run)).encode())
        h.update(f.read_bytes())
    return h.hexdigest()[:16]


def cmd_verify(rounds_dir):
    """Refuse a round whose files moved after coverage was taken."""
    bad = 0
    for cov in sorted(pathlib.Path(rounds_dir).glob("*/runs/*/coverage.json")):
        rec = json.loads(cov.read_text())
        want = rec.get("runHash")
        if not want:
            print(f"  no runHash  {cov.parent}  (measured before hashing existed)")
            continue
        got = _dir_hash(cov.parent)
        if got != want:
            print(f"  CHANGED     {cov.parent}\n    scored at {want}, now {got}")
            bad += 1
        else:
            print(f"  ok          {cov.parent}")
    print(("all runs match what was scored" if not bad
           else f"{bad} run(s) changed after scoring — the round is no longer what it measured"))
    return 1 if bad else 0


def cmd_coverage(run_dir):
    run = pathlib.Path(run_dir)
    # The run log is the objective record: the shim wrote it, not the agent.
    parts = [(run / n).read_text(errors="replace")
             for n in ("runlog.txt", "transcript.txt") if (run / n).exists()]
    transcript = "\n".join(parts)
    feats = json.loads((HERE / "features.json").read_text())["features"]
    rows = [{"id": f["id"], "group": f["group"],
             "used": None if f["detect"] == "not_instrumented" else detect(f, run, transcript)}
            for f in feats]
    scored = [r for r in rows if r["used"] is not None]
    groups = {}
    for r in scored:
        g = groups.setdefault(r["group"], [0, 0])
        g[1] += 1
        g[0] += r["used"]
    out = {
        "run": run.name,
        "runlog": (run / "runlog.txt").exists(),
        "notInstrumented": [r["id"] for r in rows if r["used"] is None],
        "overall": f"{sum(r['used'] for r in scored)}/{len(scored)}",
        "byGroup": {k: f"{v[0]}/{v[1]}" for k, v in sorted(groups.items())},
        "features": rows,
    }
    # A hash of the run's own files, taken at the moment coverage is measured. Round 03
    # had a stalled subagent write into a run directory 26 minutes after the round was
    # scored and committed; it was harmless, and nothing would have caught it if it had
    # not been. `verify` re-reads this and refuses a round whose files moved after scoring.
    out["runHash"] = _dir_hash(run)
    (run / "coverage.json").write_text(json.dumps(out, indent=2) + "\n")
    if not transcript:
        print("NOTE: no runlog.txt. Invocation detections read false, which may mean the shim "
              "was not on PATH rather than that the feature went unused.")
    print(f"{run.name}: {out['overall']}  " +
          "  ".join(f"{k} {v}" for k, v in out["byGroup"].items()))
    return out


def cmd_compare(rounds_dir):
    rows = []
    for rd in sorted(pathlib.Path(rounds_dir).iterdir()):
        man = rd / "manifest.json"
        if not man.is_dir() and man.exists():
            m = json.loads(man.read_text())
            covs = [json.loads(c.read_text()) for c in rd.glob("runs/*/coverage.json")]
            used = sum(int(c["overall"].split("/")[0]) for c in covs)
            tot = sum(int(c["overall"].split("/")[1]) for c in covs)
            scores = rd / "scores.json"
            mean = json.loads(scores.read_text()).get("weightedMean") if scores.exists() else None
            rows.append((m["round"], (m.get("skillSha") or "?")[:8],
                         m["skillTreeHash"][:8], f"p{m['promptVersion']}/r{m['rubricVersion']}",
                         f"{used}/{tot}" if tot else "-", mean if mean is not None else "-"))
    print(f"{'round':<10}{'sha':<10}{'tree':<10}{'ruler':<12}{'coverage':<12}{'mean'}")
    for r in rows:
        print(f"{r[0]:<10}{r[1]:<10}{r[2]:<10}{r[3]:<12}{r[4]:<12}{r[5]}")
    return rows


# --- self-check -------------------------------------------------------------

def self_check():
    import tempfile
    ok = []
    with tempfile.TemporaryDirectory() as d:
        run = pathlib.Path(d) / "T-x"
        (run / "store" / "2026-08-29").mkdir(parents=True)
        t = ""
        # 1. an empty run uses nothing but the store it was given
        assert detect({"detect": "file:artefact.md.claims.jsonl", "id": "c", "note": ""}, run, t) is False
        ok.append("empty run detects no claims ledger")
        # 2. an empty store directory is not evidence of a capture
        assert detect({"detect": "store_rows", "id": "s", "note": ""}, run, t) is False
        ok.append("an empty store is not a capture")
        (run / "store" / "2026-08-29" / "a.txt").write_text("x")
        assert detect({"detect": "store_rows", "id": "s", "note": ""}, run, t) is True
        ok.append("a captured file is a capture")
        # 3. an empty ledger file is not a used feature
        (run / "artefact.md.claims.jsonl").write_text("")
        assert detect({"detect": "file:artefact.md.claims.jsonl", "id": "c", "note": ""}, run, t) is False
        (run / "artefact.md.claims.jsonl").write_text('{"id":"c1"}\n')
        assert detect({"detect": "file:artefact.md.claims.jsonl", "id": "c", "note": ""}, run, t) is True
        ok.append("an empty ledger counts as unused, a written one as used")
        # 4. a sidecar key present but empty is not use
        (run / "artefact.md.sourced").write_text(json.dumps({"conflicts": [], "claims": [{"level": 2}]}))
        assert detect({"detect": "sidecar_key:conflicts", "id": "x", "note": ""}, run, t) is False
        ok.append("an empty conflicts list is not an opened conflict")
        # 5. a claim field is read off the claims, not the top level
        assert detect({"detect": "claim_field:level", "id": "x", "note": ""}, run, t) is True
        assert detect({"detect": "claim_field:kind", "id": "x", "note": ""}, run, t) is False
        ok.append("claim fields are read per claim")
        # 6. an absent or empty overlay is not an applied overlay
        assert overlay(pathlib.Path(d))[1] is None
        (pathlib.Path(d) / "overlay.md").write_text("   \n")
        assert overlay(pathlib.Path(d))[1] is None
        (pathlib.Path(d) / "overlay.md").write_text("relax one rule for this run")
        assert overlay(pathlib.Path(d))[1] is not None
        ok.append("an empty overlay file is not an applied overlay")
        # 7. tree hash is stable and content-sensitive
        h1 = tree_hash(run)
        (run / "artefact.md").write_text("new")
        assert tree_hash(run) != h1 and tree_hash(run) == tree_hash(run)
        ok.append("tree hash is stable and changes with content")
    for line in ok:
        print("ok:", line)
    print(f"{len(ok)}/{len(ok)} pass")
    return len(ok) == 8


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "--self-check":
        sys.exit(0 if self_check() else 1)
    cmd, rest = args[0], [a for a in args[1:] if not a.startswith("--")]
    if cmd == "new":
        cmd_new(rest[0], allow_dirty="--allow-dirty" in args)
    elif cmd == "coverage":
        cmd_coverage(rest[0])
    elif cmd == "compare":
        cmd_compare(rest[0])
    elif cmd == "verify":
        sys.exit(cmd_verify(rest[0]))
    else:
        sys.exit(__doc__)
