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
    python3 claims.py append <artefact> --statement "…" --falsifier "what would kill it"
    python3 claims.py set <artefact> --id c2 --role proposition
    python3 claims.py set <artefact> --from fields.json      bulk, idempotent
                                        [--quote-gloss "what a non-prose quote means"]
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


def is_prose(quote):
    """True when a quote reads as a sentence rather than as stripped markup.

    Round 03 recorded `"quote": "8 8 0"` against a claim about how many trials exist. It
    was the Count, RetMax and RetStart of a PubMed search response with the tags removed:
    genuinely present in the capture, so the check passed it, and unreadable to anybody.
    A quote below half letters is structured data wearing a quotation's clothes, and it
    needs a sentence saying what it means.
    """
    text = (quote or "").strip()
    if len(text) < 12:
        return False
    letters = sum(ch.isalpha() or ch.isspace() for ch in text)
    return letters / len(text) >= 0.6


def record(artefact, statement, status="sourced", url="", quote="", locator="", origin="",
           slide=None, claim_id="", at=None, falsifier="", quote_gloss=""):
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
    if quote and not is_prose(quote) and not quote_gloss.strip():
        raise ValueError(
            f"the quote {quote.strip()[:40]!r} is not prose, so a reader cannot tell what it "
            f"says. Pass --quote-gloss with one plain sentence naming what the fragment means "
            f"(reference/research-mode.md, Evidence).")
    if falsifier.strip():
        # What would kill this claim, recorded while the evidence is still in front of
        # you. Written here rather than gathered at the end, because a falsifier invented
        # after the fact is written to fit the claim that survived.
        claim["falsifier"] = falsifier.strip()
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
        # An id identifies a QUOTE, not a source. The 1.8 rule is one evidence row per
        # quote, several rows sharing a url, because a source cited for three claims said
        # three different things and a reader needs all three. Keying the id on the url
        # alone gave two quotes one id and `fold` then dropped the second silently: one
        # round-04 run folded 10 rows for 20 quotes and had to rebuild by hand.
        prior_rows = [r["evidence"] for r in existing if r.get("evidence")]
        for prior in prior_rows:
            if prior["url"] == url and prior.get("quote") == quote:
                eid = prior["id"]     # genuinely the same evidence, recorded twice
                break
        else:
            eid = f"e{len({r['id'] for r in prior_rows}) + 1}"
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
    """Update by id, append what is new, keep the order. Folding twice is then safe.

    The ledger owns the fields it writes and nothing else. Everything the adversarial
    pass later puts on a claim in the sidecar, the boundary regions, `challenged`,
    `kind`, `level`, `replaced_by`, `unknown_region`, survives a re-fold, because this
    updates the entry rather than replacing it.

    That is not a nicety. A fold that replaced the whole entry destroyed the O layer
    every time it ran, and two separate runs on 29 August 2026 each wrote their own
    idempotent re-apply script to put it all back. Two runs inventing the same tool is
    the toolchain naming its own gap.
    """
    out = list(current)
    # Skip the entries that carry no id. A hand-written sidecar can hold two of them,
    # and keying both on None would make the second overwrite the first.
    by_id = {item["id"]: i for i, item in enumerate(out) if item.get("id")}
    for item in incoming:
        if item["id"] in by_id:
            at = by_id[item["id"]]
            out[at] = {**out[at], **item}
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


def set_fields(artefact, updates):
    """Write fields onto claims already in the sidecar, in bulk, idempotently.

    The gap this closes has been visible for three rounds. Round 01 saw two runs write
    their own re-apply scripts, round 03 two more, round 04 eight across three runs, and
    every one of them existed because a field the skill had just gained had no way in.
    A run that writes tooling is telling you the toolchain is missing a verb.

    `updates` maps a claim id to a dict of fields. Only the named fields change; nothing
    is removed, and re-running with the same input is a no-op. This is deliberately NOT a
    general JSON patch: it edits `claims[]` by id and refuses an id it cannot find, because
    the failure mode worth preventing is a typo silently creating a claim nobody wrote.
    """
    path = pathlib.Path(str(artefact) + ".sourced")
    doc = json.loads(path.read_text(encoding="utf-8"))
    by_id = {c.get("id"): c for c in doc.get("claims") or [] if isinstance(c, dict)}
    missing = [cid for cid in updates if cid not in by_id]
    if missing:
        raise ValueError(f"no such claim: {', '.join(sorted(missing))}. "
                         f"Known ids: {', '.join(sorted(by_id)[:12])}"
                         f"{' ...' if len(by_id) > 12 else ''}")
    touched = 0
    for cid, fields in updates.items():
        claim = by_id[cid]
        for k, v in fields.items():
            if claim.get(k) != v:
                claim[k] = v
                touched += 1
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return len(updates), touched


def _cli(argv):
    if argv and argv[0] == "set":
        # python3 claims.py set <artefact> --from fields.json
        #   {"c1": {"role": "proposition"}, "c2": {"answers": "c1", "impact": "major"}}
        # or one claim inline:
        # python3 claims.py set <artefact> --id c2 --answers c1 --impact major
        artefact, rest = argv[1], argv[2:]
        if "--from" in rest:
            updates = json.loads(pathlib.Path(rest[rest.index("--from") + 1]).read_text())
        else:
            cid, fields = None, {}
            while rest:
                flag, rest = rest[0], rest[1:]
                val, rest = (rest[0], rest[1:]) if rest else ("", [])
                key = flag.lstrip("-").replace("-", "_")
                if key == "id":
                    cid = val
                else:
                    fields[key] = val
            if not cid:
                raise SystemExit("claims.py set: --id is required without --from")
            updates = {cid: fields}
        claims_touched, fields_touched = set_fields(artefact, updates)
        print(f"claims.py: {fields_touched} field(s) set on {claims_touched} claim(s)")
        return
    if not argv or argv[0] not in ("append", "fold") or len(argv) < 2:
        raise SystemExit(__doc__.strip().splitlines()[0])
    mode, artefact, rest = argv[0], argv[1], argv[2:]
    kw = {"statement": "", "status": "sourced", "url": "", "quote": "", "locator": "",
          "origin": "", "slide": None, "claim_id": "", "falsifier": "", "quote_gloss": ""}
    flags = {"--statement": "statement", "--status": "status", "--url": "url",
             "--quote": "quote", "--locator": "locator", "--origin": "origin",
             "--slide": "slide", "--id": "claim_id", "--store": "store",
             "--falsifier": "falsifier", "--quote-gloss": "quote_gloss"}
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
    # Two quotes from one source get two ids; the same quote twice gets one.
    import tempfile as _tf, os as _os
    with _tf.TemporaryDirectory() as _d:
        art = pathlib.Path(_d) / "a.md"
        art.write_text("x")
        rows = [{"evidence": {"id": "e1", "url": "https://x", "quote": "first"}},
                {"evidence": {"id": "e2", "url": "https://y", "quote": "other"}}]
        seen = {r["evidence"]["id"] for r in rows}
        assert f"e{len(seen) + 1}" == "e3", "ids count evidence rows, not distinct urls"
        same_url = [r["evidence"] for r in rows if r["evidence"]["url"] == "https://x"]
        assert same_url and same_url[0]["quote"] != "second", \
            "a second quote from the same url must not match the first row"

    # A quote that is stripped markup needs a sentence saying what it means.
    assert is_prose("Mixed model regression showed significant intervention effects.")
    assert not is_prose("8 8 0"), "a run of numbers is not a quotation"
    assert not is_prose('{"count": 8, "retmax": 8}'), "structured data is not a quotation"
    assert is_prose("The dollar was on one side of 89% of all FX trades in April 2025.")

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

        # Case 4: one source, two different quotes, two evidence rows. This reverses the
        # rule that stood until 1.8, where an id was keyed on the url and a second quote
        # from a source silently inherited the first row's id, so `fold` dropped it. A
        # source cited for three claims said three things and a reader needs all three.
        # Origin collapse still happens, at originGroup, which is where it belongs.
        r3 = record(art, "The cohort was large.", url="https://example.com/a",
                    quote="across the cohort", at="2026-08-28T03:00:00Z")
        append(art, r3)
        assert r3["evidence"]["id"] != r1["evidence"]["id"], \
            "a different quote from one source is a different evidence row"
        assert r3["evidence"]["url"] == r1["evidence"]["url"], "and it keeps the url"
        assert fold(art) == (3, 2), "two quotes fold to two rows"

        # The same quote recorded twice is genuinely one row, and reuses the id.
        r4 = record(art, "Restated for a second claim.", url="https://example.com/a",
                    quote="across the cohort", at="2026-08-28T04:00:00Z")
        append(art, r4)
        assert r4["evidence"]["id"] == r3["evidence"]["id"], "same url and quote is one row"
        assert fold(art) == (4, 2), "and it adds no third source"

    # Case 5: a re-fold must not destroy what the adversarial pass wrote. The ledger owns
    # the fields it writes; every other field on the claim survives.
    passed_o = {"id": "c1", "statement": "old", "status": "sourced",
                "challenged": "holds-with-boundary", "kind": "empirical",
                "holds_when": [{"dimension": "d", "value": "v", "basis": "observed"}],
                "unknown_region": "dusk"}
    refolded = _merge([passed_o], [{"id": "c1", "statement": "new", "status": "sourced",
                                    "evidence": ["e1"]}])[0]
    assert refolded["statement"] == "new" and refolded["evidence"] == ["e1"], refolded
    for field in ("challenged", "kind", "holds_when", "unknown_region"):
        assert field in refolded, f"a re-fold destroyed {field}"
    assert _merge([], [{"id": "c2"}]) == [{"id": "c2"}], "a new claim still appends"

    print("claims: self-check passed (5 of 5 cases; the threshold is 5 of 5; "
          "a quote absent from the capture is refused)")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("--self-check", "--check"):
        _self_check()
    else:
        sys.exit(_cli(sys.argv[1:]))
