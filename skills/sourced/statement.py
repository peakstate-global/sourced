#!/usr/bin/env python3
"""Statement mode: generate the four-label provenance block from a sidecar.

    statement.py <file.sourced> --agent "Claude Opus 5.5 (claude-opus-5-5)" --agent "Claude Code 2.x" \
        [--author NAME] [--accountable NAME] [--sidecar-url URL] [--write]
    statement.py --self-check

Every line follows reference/provenance-block.md:
- Attribution names the author, the fidelity line (each --agent, model, harness and tools, with a
  version each), and the adversarial grade sentence from reference/adversarial-pass.md when the
  grade belongs there (fresh thread, either model).
- Accountable is the named person, and nothing else. A model never writes a review status on
  this line, in either direction. Only the named person may add their own words, verbatim, and
  only after they have said exactly what to add.
- Limitations holds limits on the evidence only: a weak or missing adversarial pass, sources
  with no third-party archive, rows missing a quote or locator, self-interested sources,
  self-reported figures, and the open-conflict lines from conflicts.py. Otherwise "None material."
- References counts distinct origins (shared_claims.origins), says what is checkable only when it
  is true, lists each row's `reference` (a full APA 7 entry, retrieved this session) in
  alphabetical order, and ends with the sidecar link.
A row with no `reference` is refused: a bare URL is not a reference, and an entry is never
written from memory. --write stores the block in `disclosure`, keeping the file's permissions.
"""
import argparse, json, os, re, shutil, sys, tempfile, unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared_claims import origins  # noqa: E402

ATTRIBUTION_GRADES = {
    "cross-model-fresh-thread": "The adversarial pass ran in a fresh thread on a different model ({model}) on {at}, and raised {raised} challenges.",
    "same-model-fresh-thread": "The adversarial pass ran in a fresh thread on the same model ({model}) on {at}, and raised {raised} challenges. A fresh thread has no commitment to the draft, so it does not catch a belief this model already holds.",
}
LIMITATION_GRADES = {
    "same-thread-self-challenge": "The adversarial pass was a self-challenge in the same thread, on {at}, and raised {raised} challenges. It is the weakest of the three grades, because the instance challenging the draft is the instance that wrote it.",
    "not-performed": "No adversarial pass was performed on this artefact.",
}


class Refused(Exception):
    pass


def _origin(e):
    return e.get("originGroup") or "url:" + str(e.get("url") or e.get("id", ""))


def _sort_key(entry):
    """APA order by first element, with accents folded rather than dropped (Öztürk sorts under O)."""
    folded = "".join(ch for ch in unicodedata.normalize("NFKD", entry) if not unicodedata.combining(ch))
    return "".join(ch for ch in folded.casefold() if ch.isalnum())


def build(d, agents, author, accountable, sidecar_link):
    if not agents:
        raise Refused("the fidelity line needs at least one --agent (model, harness or tool, with a version)")
    ev = [e for e in d.get("evidence") or [] if isinstance(e, dict)]
    # Only cited rows count: an evidence row no claim uses is not something the artefact rests on.
    cited = {i for c in d.get("claims") or [] for i in (c.get("evidence") or [])}
    if cited:
        ev = [e for e in ev if e.get("id") in cited or e.get("supports")]
    missing = sorted({e.get("url") or e.get("id", "?") for e in ev if not (e.get("reference") or "").strip()})
    if missing:
        raise Refused("these rows have no `reference` (full APA 7 entry): " + ", ".join(missing))
    op = d.get("opposed") or {"grade": "not-performed"}
    if op.get("grade") not in ATTRIBUTION_GRADES and op.get("grade") not in LIMITATION_GRADES:
        raise Refused(f"unknown adversarial grade {op.get('grade')!r}; run decisions.py validate")
    fill = {"model": op.get("model", "model not recorded"), "at": str(op.get("at", ""))[:10],
            "raised": op.get("raised", 0)}

    attr = f"Written by {author}. Produced with " + "; ".join(agents) + "."
    if op.get("grade") in ATTRIBUTION_GRADES:
        attr += " " + ATTRIBUTION_GRADES[op["grade"]].format(**fill)

    lim = []
    if op.get("grade") in LIMITATION_GRADES:
        lim.append(LIMITATION_GRADES[op["grade"]].format(**fill))
    srcs = origins(d) if ev else set()
    archived = {_origin(e) for e in ev if (e.get("archiveUrl") or "").strip()}
    if srcs - archived:
        lim.append(f"{len(srcs - archived)} of {len(srcs)} sources have no third-party archived copy.")
    gaps = [e for e in ev if not ((e.get("quote") or "").strip() and str(e.get("locator") or "").strip())]
    if gaps:
        lim.append(f"{len(gaps)} of {len(ev)} evidence rows carry no quote or no locator.")
    undated = [e for e in ev if not e.get("retrievedAt")]
    if undated:
        lim.append(f"{len(undated)} of {len(ev)} evidence rows have no recorded retrieval date.")
    nd = sorted({_origin(e) for e in ev if "(n.d.)" in e["reference"]})
    if nd:
        lim.append(f"{len(nd)} of {len(srcs)} sources carry no publication date (n.d.).")
    si = sorted({_origin(e) for e in ev if e.get("selfInterested")})
    if si:
        lim.append("Sources with an interest in their own finding: " + ", ".join(si) + ".")
    sr = sorted({_origin(e) for e in ev if any(c.get("value") == "self-report" for c in e.get("conditions") or [])})
    if sr:
        lim.append("Figures self-reported rather than measured: " + ", ".join(sr) + ".")
    try:
        import conflicts
        lim += conflicts.disclosure_lines(d)
    except ImportError:
        pass

    if ev:
        dates = sorted({str(e.get("retrievedAt", ""))[:10] for e in ev if e.get("retrievedAt")})
        lead = f"{len(srcs)} source{'' if len(srcs) == 1 else 's'}, retrieved on {', '.join(dates) or 'unrecorded dates'}"
        if undated:
            lead += f" ({len(undated)} rows undated)"
        lead += ", each quote with its locator." if not gaps else "."
        entries = sorted({e["reference"].strip() for e in ev}, key=_sort_key)
        refs = lead + "\n" + "\n".join(entries)
    else:
        refs = "No external sources."
    refs += f"\n[SOURCED sidecar]({sidecar_link})"
    return {"attribution": attr, "accountable": f"{accountable}.",
            "limitations": " ".join(lim) if lim else "None material.", "references": refs}


def render(block):
    return "\n".join(f"{k.capitalize()}: {v}" for k, v in block.items())


def write(side, d):
    fd, tmp = tempfile.mkstemp(dir=side.parent, suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
    shutil.copymode(side, tmp)  # mkstemp makes 0600; a served sidecar must stay readable
    os.replace(tmp, side)


def self_check():
    row = lambda **k: {"url": "https://a.example", "retrievedAt": "2026-10-06", "quote": "q", "locator": "p. 1",
                       "reference": "Zed, A. (2026). Z. https://a.example", **k}
    a = ["Claude Opus 5.5 (claude-opus-5-5)", "Claude Code 2.1"]
    # 1 fresh-thread grade lands in Attribution with its exact sentence, and two write-ups of one origin count once
    d = {"opposed": {"grade": "same-model-fresh-thread", "model": "m", "at": "2026-10-06T00:00Z", "raised": 4},
         "evidence": [row(originGroup="o", archiveUrl="x"), row(url="https://b.example", originGroup="o", archiveUrl="y",
                      reference="Alpha, B. (2026). A. https://b.example")]}
    b = build(d, a, "A. Author", "A. Author", "f.md.sourced")
    assert "fresh thread on the same model (m)" in b["attribution"] and "Claude Code 2.1" in b["attribution"]
    assert b["references"].startswith("1 source,") and "each quote with its locator" in b["references"]
    assert b["references"].index("Alpha") < b["references"].index("Zed") and b["references"].endswith("(f.md.sourced)")
    assert b["limitations"] == "None material." and b["accountable"] == "A. Author."
    # 2 a missing or self-challenge pass goes to Limitations, never Attribution
    assert "No adversarial pass" in build({"evidence": [row(archiveUrl="x")]}, a, "x", "x", "s")["limitations"]
    b2 = build({"opposed": {"grade": "same-thread-self-challenge", "at": "2026-10-06", "raised": 1},
                "evidence": [row(archiveUrl="x")]}, a, "x", "x", "s")
    assert "weakest of the three grades" in b2["limitations"] and "adversarial" not in b2["attribution"]
    # 3 gaps are disclosed and the diligence sentence is withheld
    b3 = build({"evidence": [row(locator="", selfInterested=True, originGroup="v",
                                 conditions=[{"value": "self-report"}])]}, a, "x", "x", "s")
    assert "1 of 1 evidence rows carry no quote" in b3["limitations"] and "each quote" not in b3["references"]
    assert "1 of 1 sources have no third-party archived copy" in b3["limitations"] and "v" in b3["limitations"]
    # 4 refusals: no fidelity line, and a row with no APA reference
    for bad in (lambda: build({"evidence": []}, [], "x", "x", "s"),
                lambda: build({"evidence": [row(reference="")]}, a, "x", "x", "s")):
        try:
            bad(); raise AssertionError("should refuse")
        except Refused:
            pass
    # 5 no sources at all
    assert build({"evidence": []}, a, "x", "x", "s")["references"].startswith("No external sources.")
    # 7 unknown grade refused; undated, n.d. and uncited rows handled; accented names sort by base letter
    try:
        build({"opposed": {"grade": "typo"}, "evidence": [row(archiveUrl="x")]}, a, "x", "x", "s"); raise AssertionError
    except Refused:
        pass
    b7 = build({"claims": [{"id": "c1", "evidence": ["e1", "e2"]}],
                "evidence": [row(id="e1", archiveUrl="x", reference="Öztürk, A. (n.d.). T. https://a.example"),
                             row(id="e2", url="https://c.example", retrievedAt="", archiveUrl="x", reference="Pym, B. (2026). P."),
                             row(id="e9", url="https://u.example", reference="")]}, a, "x", "x", "s")
    assert b7["references"].index("Öztürk") < b7["references"].index("Pym") and "u.example" not in b7["references"]
    assert "no recorded retrieval date" in b7["limitations"] and "(n.d.)" in b7["limitations"]
    # 6 --write keeps the file mode
    with tempfile.TemporaryDirectory() as t:
        p = Path(t) / "f.sourced"; p.write_text("{}"); os.chmod(p, 0o644); write(p, {"a": 1})
        assert oct(p.stat().st_mode & 0o777) == "0o644"
    print("statement: self-check passed (7 of 7 cases; the threshold is 7 of 7)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("sidecar", nargs="?")
    ap.add_argument("--agent", action="append", default=[])
    ap.add_argument("--author", default="Andrew Ramsden")
    ap.add_argument("--accountable")
    ap.add_argument("--sidecar-url", help="where the sidecar is served; default is its relative file name")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--self-check", action="store_true")
    a = ap.parse_args()
    if a.self_check:
        self_check(); sys.exit(0)
    if not a.sidecar:
        sys.exit(__doc__)
    side = Path(a.sidecar); d = json.loads(side.read_text(encoding="utf-8"))
    try:
        block = build(d, a.agent, a.author, a.accountable or a.author, a.sidecar_url or side.name)
    except Refused as e:
        sys.exit(f"statement: refused, {e}")
    print(render(block))
    if a.write:
        d["disclosure"] = block
        write(side, d)
