#!/usr/bin/env python3
"""The claims ledger: append a claim the moment it is made, fold it into the sidecar at the end.

On a real run on 27 August 2026 the evidence was captured hours after the reasoning that
rested on it, so the quote kept in the sidecar came from one retrieval and the hash beside
it came from a different one. Nobody would have noticed, and it is not sound. This script
is the mechanism that stops it happening again: a claim can only be appended by naming a
URL that has already been captured, and the quote must be present in the text file that
capture wrote. The quote and the hash therefore come from the same bytes, because the
quote is read out of the capture rather than out of the live page.

    python3 claims.py append <artefact> --statement "…" --url <url> --quote "…" \
        [--locator "p. 12"] [--slide 3] [--origin mit-2026] [--id c4]
    python3 claims.py append <artefact> --statement "…" --status inferred
    python3 claims.py fold <artefact>        ledger lines -> claims[] and evidence[]
    python3 claims.py --self-check           four cases, known answers, no network

A RECALLED or INFERRED claim carries no URL and no quote, because there is nothing to
retrieve. It still goes in the ledger, so the artefact's unsourced parts are visible while
the work happens rather than counted at the end.

ponytail: one JSON object per line, appended with open(..., "a"), no index and no locking.
The ceiling is a single author on one machine, the same as the decision ledger; if two
processes ever append at once, move to one file per process and merge at fold time.
"""
import datetime
import json
import pathlib
import re
import sys

# Reuse rather than re-derive. The sidecar naming lives in one place, and the store
# lookup is the same code that wrote the capture, so the two cannot drift apart.
from decisions import sidecar_path
import sourced
# One collapse rule, and it lives in shared_claims so nothing has to import
# claims.py to use it. Re-exported here because callers already reach for it.
from shared_claims import origins  # noqa: F401

STATUSES = ("sourced", "recalled", "inferred")


def ledger_path(artefact):
    """The ledger sits beside the artefact, so it travels with it and is obvious to find."""
    return pathlib.Path(str(artefact) + ".claims.jsonl")


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
            # Loudly, and naming the line. A ledger that quietly drops a record loses a
            # claim somebody has already published.
            raise SystemExit(f"{path}:{n} is not one JSON object per line ({e})")
    return out


# The same punctuation mark in a different codepoint. A publisher renders a curly
# quote and an author types a straight one, and refusing that match teaches people
# to switch the check off, which is the only way this script can actually fail.
TYPOGRAPHY = str.maketrans({
    "\u2018": "'", "\u2019": "'", "\u201a": "'", "\u201b": "'",
    "\u201c": '"', "\u201d": '"', "\u201e": '"', "\u2032": "'", "\u2033": '"',
    "\u2010": "-", "\u2011": "-", "\u2012": "-", "\u2013": "-", "\u2014": "-",
    "\u2015": "-", "\u2212": "-", "\u00ad": "",
})


def flatten(text):
    """Collapse whitespace and fold typographic variants, so a quote copied across a
    line break out of a rendered page still matches.

    Nothing else is normalised. A quote is verbatim by definition, so changed wording
    and changed numbers must both fail the match. Case is not folded either: a claim
    that turns on a proper noun should not match a sentence that spells it differently."""
    return re.sub(r"\s+", " ", text.translate(TYPOGRAPHY)).strip()


def captured(url):
    """The index row for a URL, or None. This is what capture wrote, not the live page."""
    for row in sourced.load_index():
        if row["url"] == url:
            return row
    return None


def quote_is_in_capture(quote, row):
    """Is this quote in the text file that capture wrote for this retrieval?

    This is the whole point of the script. Reading the quote out of the capture, rather
    than out of a re-read of the live page, is what makes the quote and the hash the same
    retrieval. Returns (ok, path_or_reason)."""
    rel = row.get("text")
    if not rel:
        return False, "the capture stored no text file; re-run sourced.py with --tier 2"
    path = pathlib.Path(rel)
    if not path.is_absolute():
        path = sourced.ROOT / rel
    if not path.is_file():
        return False, f"the captured text file is missing: {path}"
    if flatten(quote) not in flatten(path.read_text(encoding="utf-8", errors="ignore")):
        return False, f"that quote is not in {path}; quote the capture, or climb the ladder"
    return True, str(path)


def record(artefact, statement, status="sourced", url="", quote="", locator="", origin="",
           slide=None, claim_id="", at=None):
    """Build one ledger line: the claim, and the evidence it rests on.

    The claim object is exactly the sidecar's `claims[]` member, so folding can put it in
    unchanged. The evidence object is exactly the sidecar's `evidence[]` member, built
    from the index row that capture wrote rather than from anything typed here."""
    at = at or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if status not in STATUSES:
        raise ValueError(f"status must be one of {STATUSES}, not {status!r}")
    if not statement.strip():
        raise ValueError("a claim needs a statement")

    existing = read_ledger(artefact)
    claim_id = claim_id or f"c{len(existing) + 1}"
    claim = {"id": claim_id, "statement": statement, "status": status}
    if slide is not None:
        claim["locator"] = {"slide": slide}
    claim["evidence"] = []
    evidence = None

    if status == "sourced":
        if not url or not quote:
            raise ValueError("a SOURCED claim needs the URL it was retrieved from and the "
                             "verbatim quote; label it recalled or inferred if it has neither")
        row = captured(url)
        if row is None:
            raise ValueError(f"{url} has not been captured; run "
                             f"python3 sourced.py {url} --tier 2 first, then quote the capture")
        ok, why = quote_is_in_capture(quote, row)
        if not ok:
            raise ValueError(why)
        # One evidence row per source. A source cited by three claims is one source, and
        # counting it three times is the exact miscount `originGroup` exists to prevent.
        for prior in existing:
            if prior.get("evidence") and prior["evidence"]["url"] == url:
                eid = prior["evidence"]["id"]
                break
        else:
            eid = f"e{len({r['evidence']['url'] for r in existing if r.get('evidence')}) + 1}"
        evidence = {"id": eid, "url": url, "quote": quote,
                    "retrievedAt": row["capturedAt"][:10],
                    "sha256": row["sha256"], "textSha256": row.get("textSha256", ""),
                    "custodian": row.get("custodian", "self")}
        if locator:
            evidence["locator"] = locator
        if origin:
            evidence["originGroup"] = origin
        if row.get("archiveUrl"):
            evidence["archiveUrl"] = row["archiveUrl"]
        if row.get("thin"):
            # The hash is real and the evidence may not be. The quote was found, so the
            # capture is not empty, but a thin page is usually navigation and the reader
            # should be told which rung this claim actually stands on.
            evidence["thinCapture"] = True
        claim["evidence"] = [eid]
    return {"at": at, "claim": claim, "evidence": evidence}


def append(artefact, rec):
    """Append one record. Append mode only, so an earlier line cannot be rewritten."""
    line = json.dumps(rec, sort_keys=True)
    assert "\n" not in line, "a record must be one line"
    path = ledger_path(artefact)
    with path.open("a", encoding="utf-8") as fh:
        # Heal a missing final newline before writing. A run killed mid-write leaves the
        # last line unterminated, and appending to that fuses two records into one line
        # that no longer parses.
        if fh.tell() and path.read_bytes()[-1:] != b"\n":
            fh.write("\n")
        fh.write(line + "\n")
    return path


def _merge(current, incoming):
    """Replace by id, append what is new, keep the order. Folding twice is then safe."""
    out = list(current)
    # Skip the entries that carry no id. A hand-written sidecar can hold two of them,
    # and keying both on None would make the second overwrite the first.
    by_id = {item["id"]: i for i, item in enumerate(out) if item.get("id")}
    for item in incoming:
        if item["id"] in by_id:
            out[by_id[item["id"]]] = item
        else:
            by_id[item["id"]] = len(out)
            out.append(item)
    return out


def fold(artefact):
    """Fold the ledger into the sidecar's claims[] and evidence[], the members unchanged.

    Folding twice is safe: a record replaces the entry with its id rather than being
    appended again, so a re-run after two more appends is still correct."""
    side = sidecar_path(artefact)
    if not side.is_file():
        raise SystemExit(f"no sidecar at {side}; write the manifest before folding")
    data = json.loads(side.read_text(encoding="utf-8"))
    ledger = read_ledger(artefact)
    data["claims"] = _merge(data.get("claims", []), [r["claim"] for r in ledger])
    data["evidence"] = _merge(data.get("evidence", []),
                              [r["evidence"] for r in ledger if r.get("evidence")])
    # Write to a temporary file and rename. The sidecar is the deliverable, and a fold
    # interrupted halfway through a truncating write leaves nothing to ship.
    tmp = side.with_suffix(side.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(side)
    return len(data["claims"]), len(data["evidence"])


def _cli(argv):
    if not argv or argv[0] not in ("append", "fold") or len(argv) < 2:
        raise SystemExit(__doc__.strip().splitlines()[0])
    mode, artefact, rest = argv[0], argv[1], argv[2:]
    kw = {"statement": "", "status": "sourced", "url": "", "quote": "", "locator": "",
          "origin": "", "slide": None, "claim_id": ""}
    flags = {"--statement": "statement", "--status": "status", "--url": "url",
             "--quote": "quote", "--locator": "locator", "--origin": "origin",
             "--slide": "slide", "--id": "claim_id", "--store": "store"}
    while rest:
        flag, rest = rest[0], rest[1:]
        val, rest = (rest[0], rest[1:]) if rest else ("", [])
        if flag not in flags:
            raise SystemExit(f"unknown flag {flag}")
        if flag == "--store":
            sourced.set_store(val)
        elif flag == "--slide":
            kw["slide"] = int(val)
        else:
            kw[flags[flag]] = val
    if mode == "fold":
        claims, evidence = fold(artefact)
        print(f"folded {claims} claims and {evidence} evidence rows into {sidecar_path(artefact)}")
        return 0
    try:
        rec = record(artefact, **kw)
    except ValueError as e:
        raise SystemExit(f"refused: {e}")
    append(artefact, rec)
    ev = rec["evidence"]
    print(f"{rec['claim']['id']}  {rec['claim']['status']}  {rec['claim']['statement'][:60]}")
    if ev:
        print(f"      {ev['id']}  {ev['url']}  quote verified against the capture")
        if ev.get("thinCapture"):
            print("      THIN capture: say which rung of the ladder this claim stands on.",
                  file=sys.stderr)
    return 0


def _self_check():
    """Four cases with known answers, no network. The threshold is all four, because a
    claim recorded against a quote that is not in the capture is the exact failure this
    script exists to prevent, and it would be invisible in the finished sidecar."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        store = tmp / "sources"
        (store / "2026-08-28").mkdir(parents=True)
        text = store / "2026-08-28" / "example-com-a.txt"
        text.write_text("Accuracy fell from 82.3%\nto 45.5% across the cohort.\n")
        sourced.set_store(store)
        sourced.save_index([{"url": "https://example.com/a", "sha256": "aa", "textSha256": "bb",
                             "capturedAt": "2026-08-28T01:00:00+00:00", "tier": 2,
                             "custodian": "self", "text": str(text)}])
        art = tmp / "report.md"
        art.write_text("# report\n")

        # Case 1: two appends accrue two lines, and the FIRST line is byte-identical
        # afterwards. Accrual is the criterion; a rewrite would mean reconstruction.
        r1 = record(art, "Accuracy fell from 82.3% to 45.5%.", url="https://example.com/a",
                    quote="Accuracy fell from 82.3% to 45.5% across the cohort.",
                    locator="p. 4", origin="rsna", at="2026-08-28T01:00:00Z")
        append(art, r1)
        first = ledger_path(art).read_bytes()
        r2 = record(art, "The drop is large enough to change triage.", status="inferred",
                    at="2026-08-28T02:00:00Z")
        append(art, r2)
        after = ledger_path(art).read_bytes()
        assert after.count(b"\n") == 2, "two appends, two lines"
        assert after.startswith(first), "the first line was rewritten by the second append"
        assert read_ledger(art) == [r1, r2], "the ledger does not read back what was written"
        # The quote spans a line break in the capture and still matches, because a quote
        # copied out of prose is re-wrapped and that is not a difference in the words.
        assert r1["evidence"]["sha256"] == "aa", "the hash comes from the capture, not from here"
        assert r2["evidence"] is None, "an INFERRED claim rests on no evidence"

        # Case 2: folding puts the claims in claims[] unchanged, and twice is safe.
        base = {"sourced": "1.0", "artefact": {"path": "report.md", "sha256": "ab"},
                "claims": [], "evidence": [], "disclosure": {"attribution": "…"}}
        sidecar_path(art).write_text(json.dumps(base))
        assert fold(art) == (2, 1)
        folded = json.loads(sidecar_path(art).read_text())
        assert folded["claims"] == [r1["claim"], r2["claim"]], "claims[] must be the ledger's claims"
        assert folded["evidence"] == [r1["evidence"]], "evidence[] must be the ledger's evidence"
        assert fold(art) == (2, 1), "folding twice must not duplicate a claim"

        # Case 3: a quote that is not in the captured text file is refused. This is the
        # same-retrieval criterion, made checkable.
        for bad, why in (
                (lambda: record(art, "x", url="https://example.com/a",
                                quote="Accuracy fell from 82% to 45%."),
                 "a quote that is not in the capture must be refused"),
                (lambda: record(art, "x", url="https://example.com/never-captured",
                                quote="Accuracy fell from 82.3% to 45.5% across the cohort."),
                 "a claim on an uncaptured URL must be refused"),
                (lambda: record(art, "x", url="https://example.com/a", quote=""),
                 "a SOURCED claim with no quote must be refused"),
                (lambda: record(art, "x", status="guessed"),
                 "an unknown status must be refused")):
            try:
                bad()
            except ValueError:
                pass
            else:
                raise AssertionError(why)

        # A curly quote in the capture and a straight one in the claim are the same
        # punctuation mark, and refusing that match teaches people to switch the check off.
        assert flatten("don\u2019t \u201cstop\u201d \u2014 here") == flatten('don\'t "stop" - here')

        # Case 4: one source cited twice is one evidence row, because ten citations of one
        # retrieval are still one source.
        r3 = record(art, "The cohort was large.", url="https://example.com/a",
                    quote="across the cohort", at="2026-08-28T03:00:00Z")
        append(art, r3)
        assert r3["evidence"]["id"] == r1["evidence"]["id"], "one source, one evidence id"
        assert fold(art) == (3, 1), "a second claim on one source adds no second source"

    print("claims: self-check passed (4 of 4 cases; the threshold is 4 of 4; "
          "a quote absent from the capture is refused)")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("--self-check", "--check"):
        _self_check()
    else:
        sys.exit(_cli(sys.argv[1:]))
