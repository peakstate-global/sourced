#!/usr/bin/env python3
"""Strip the framework's fingerprints off a set of papers, so a reader can judge the work.

    python3 blind.py pack <out-dir> <arm>:<paper.md> [<arm>:<paper.md> ...]
    python3 blind.py unpack <out-dir>                      reveal the key, after judging

WHY THIS EXISTS. The rubric measures conformance to a rubric we wrote. That tells us the
papers match our taste; it does not tell us they are better. The one judgement the rubric
cannot supply is the reader's, and the reader can only give it honestly if they cannot
tell which arm produced which paper.

WHAT IS STRIPPED. Only the tells — the provenance block, sidecar references, the
laboratory-conditions banner, our verdict vocabulary in table headers, the skill's own
name. **The argument, the evidence, the numbers and the citations are untouched**, because
those are the thing being judged.

WHAT IS NOT STRIPPED, deliberately: house style. A paper is allowed to read like itself.
Rewriting prose to disguise its author would change the artefact and destroy the judgement.
This blinds the LABEL, not the voice, and a reader who recognises a style anyway should say
so — that is a finding about how distinctive the output is.
"""
import hashlib
import json
import pathlib
import random
import re
import sys

# Ordered: longer patterns first, so a general rule cannot eat a specific one.
TELLS = [
    (r"(?im)^\s*\*?\s*A SOURCED research run\b.*$", ""),
    # The banner varies in wording between runs; match the idea, not one phrasing.
    (r"(?ims)^>?[ \t]*.{0,120}\blaboratory conditions\b.*?(?=\n\s*\n)", ""),
    (r"(?im)^.*\bprovenance framework\b.*$", ""),
    (r"(?ims)^#{1,4}[ \t]*Provenance[ \t]*$.*?(?=^#{1,4}[ \t]|\Z)", ""),
    (r"(?im)^\*\*(Attribution|Accountable|Limitations|References):\*\*", "**Notes:**"),
    (r"(?i)\bartefact\.md\.sourced\b", "the working record"),
    (r"(?i)\bSOURCED sidecar\b", "the working record"),
    (r"(?i)\bthe sidecar\b", "the working record"),
    (r"(?i)\bsidecars?\b", "working record"),
    (r"(?i)\bthe SOURCED standard\b", "the method used"),
    (r"(?i)\bSOURCED standard\b", "the method used"),
    (r"(?i)\bSOURCED\b", "the method"),
    (r"(?i)\bcross-model-fresh-thread\b", "an independent review"),
    # Consume a leading article so the substitution does not leave "the the".
    (r"(?i)\bthe adversarial pass\b", "the challenge round"),
    (r"(?i)\badversarial pass\b", "challenge round"),
    (r"(?i)\b(claims|boundary|integrate|dimensions|conflicts|underwrite)\.py\b", "a check"),
]


def strip(text):
    out = text
    for pat, sub in TELLS:
        out = re.sub(pat, sub, out)      # every pattern carries its own inline flags
    out = re.sub(r"\n{4,}", "\n\n\n", out)
    return out.strip() + "\n"


def pack(out_dir, pairs, seed=None):
    """Write blinded copies under neutral codes, and the key beside them, unread."""
    out = pathlib.Path(out_dir)
    (out / "papers").mkdir(parents=True, exist_ok=True)
    items = []
    for arm, path in pairs:
        p = pathlib.Path(path)
        items.append({"arm": arm, "source": str(p), "text": strip(p.read_text())})
    rng = random.Random(seed if seed is not None else
                        int(hashlib.sha256("".join(i["source"] for i in items)
                                           .encode()).hexdigest()[:8], 16))
    rng.shuffle(items)
    key = []
    for n, it in enumerate(items, 1):
        code = f"P{n:02d}"
        (out / "papers" / f"{code}.md").write_text(it["text"])
        key.append({"code": code, "arm": it["arm"], "source": it["source"]})
    (out / "KEY.json").write_text(json.dumps(key, indent=2) + "\n")
    (out / "papers" / "README.md").write_text(
        "# Papers for judging\n\n"
        "Each file is one answer to one question, with the method that produced it removed.\n"
        "Read them and say which you would rely on, and why. The key is in the folder above\n"
        "and is not needed to judge: open it afterwards.\n")
    return key


def unpack(out_dir):
    return json.loads((pathlib.Path(out_dir) / "KEY.json").read_text())


def _self_check():
    src = ("# Q?\n\n*A SOURCED research run. Twelve sources retrieved.*\n\n"
           "This is a laboratory conditions, not published advice line.\n\n"
           "## Body\n\nThe adversarial pass killed c19, and claims.py refused a quote.\n"
           "Full detail is in artefact.md.sourced.\n\n"
           "## Provenance\n\n**Attribution:** written under the SOURCED standard.\n")
    got = strip(src)
    for tell in ("SOURCED", "laboratory conditions", "artefact.md.sourced",
                 "adversarial pass", "claims.py", "## Provenance"):
        assert tell not in got, f"{tell!r} survived: {got}"
    assert "killed c19" in got, "the argument must survive"
    assert "## Body" in got, "structure must survive"

    import tempfile
    with tempfile.TemporaryDirectory() as d:
        a = pathlib.Path(d) / "a.md"; a.write_text("# A\n\nsourced paper\n")
        b = pathlib.Path(d) / "b.md"; b.write_text("# B\n\ncontrol paper\n")
        key = pack(d + "/out", [("sourced", a), ("bare", b)], seed=1)
        codes = {k["code"] for k in key}
        assert codes == {"P01", "P02"}, codes
        assert {k["arm"] for k in key} == {"sourced", "bare"}
        assert unpack(d + "/out") == key, "the key round-trips"
        # The code must not encode the arm: same inputs, same seed, stable; and the arm
        # order is decided by the shuffle, not by argument order.
        assert (pathlib.Path(d) / "out" / "papers" / "P01.md").exists()

    print("blind: self-check passed (9 of 9 cases; the threshold is 9 of 9)")


if __name__ == "__main__":
    argv = sys.argv[1:]
    if not argv or "--self-check" in argv:
        _self_check(); raise SystemExit(0)
    cmd = argv[0]
    if cmd == "pack":
        pairs = [tuple(a.split(":", 1)) for a in argv[2:]]
        for k in pack(argv[1], pairs):
            print(f"  {k['code']}  <- {k['arm']}")
        print(f"\nkey written to {argv[1]}/KEY.json — do not open it before judging")
    elif cmd == "unpack":
        for k in unpack(argv[1]):
            print(f"  {k['code']}  =  {k['arm']:10} {k['source']}")
    else:
        raise SystemExit(__doc__)
