#!/usr/bin/env python3
"""SOURCED: capture a source so a claim can still be checked after it moves.

Reference rot is bigger than link rot: the URL keeps working and the content
changes underneath the citation. Zittrain, Albert & Lessig (2014) measured
more than 70% of URLs in three legal journals, and 50% in US Supreme Court
opinions, no longer producing the information originally cited.

    python3 sourced.py <url> [--tier 1|2] [--archive] [--watch REGEX] [--store DIR]
                             [--define "dimension=one sentence"] ...
                             [--condition "dimension=value:basis"] ...
    python3 sourced.py --define "air quality=How clean the air is here and now."
    python3 sourced.py --check          # re-fetch everything, report what moved
    python3 sourced.py --self-check     # runnable check, no network

    SOURCED_ROOT   where the store lives (default: current directory)
    SOURCED_STORE  path under it (default: docs/research/sources)
    --store DIR    the whole store path at once, overriding both

Exit status of a capture: 0 when the capture holds prose, 2 when it is thin. A
warning on a stream nobody reads is a warning that was not given.

Conditions are recorded in the same call, because the moment the source is in
front of you is the only moment its conditions are. `--condition` is repeatable
and optional; each one lands on the index row and counts in the project's
dimension registry (`dimensions.py`).

A dimension needs a one-sentence definition, because one name over two meanings
makes a FALSE comparison and a false conflict refuses a delivery that should
have shipped. Typing the definition on every capture is friction that gets the
feature switched off, so it is a separate repeatable flag: `--define` mints or
updates the definition once, and `--condition` then uses the definition already
known. A `--condition` naming a dimension nothing has defined WARNS and records
the row as undefined. It never fails the capture, because capturing the source
is the point and the definition can be written a minute later.

Tier 1 (default): fetch, hash the bytes, record url + sha256 + capturedAt.
                  Stores NO third-party content, so it cannot infringe anything.
Tier 2:           also writes the original bytes and a text rendering beside it.
                  Local verification only. Never redistribute, and never capture
                  a source whose terms prohibit copying.
Tier 3:           --archive as well, so somebody other than you holds a dated
                  copy. Use it for anything that might be contested: a copy you
                  hold yourself is self-attested.

ponytail: stdlib, with curl as the fallback only. A capture tool that needs a dependency tree is a
capture tool that stops working in two years, which is the failure it exists to
prevent. Text extraction is tag-stripping, not a parser: it is there so a human
can find the quote again, not to render the page.
"""
import argparse, gzip, hashlib, html, json, os, pathlib, re, subprocess, sys, zlib
import contextlib, io, tempfile
import urllib.request
from datetime import datetime, timezone

# The condition parser and the per-project dimension registry. `dimensions.py` imports
# this module lazily, inside one function, so the two can import each other.
import dimensions

# Where captures land. Defaults to the current project, overridable, and never
# assumes the layout of any one repo.
ROOT = pathlib.Path(os.environ.get("SOURCED_ROOT", pathlib.Path.cwd()))
STORE = ROOT / os.environ.get("SOURCED_STORE", "docs/research/sources")
INDEX = STORE / "index.json"

# Some sites refuse a bare urllib request with 403 and serve the same page to
# anything that looks like a browser. This is the shortest string that gets past
# them, and it is honest about being a script.
USER_AGENT = "Mozilla/5.0 (compatible; sourced/1.0; +https://github.com/irama/sourced)"


def set_store(path):
    """Point captures at another directory. Callers get the same default without
    this: it exists so a test, or a caller with its own layout, can redirect the
    store without touching the environment of the process it runs in."""
    global STORE, INDEX
    STORE = pathlib.Path(path)
    INDEX = STORE / "index.json"


def _rel(p):
    """Path recorded in the row: relative to ROOT when it sits under it, so an
    index committed to a repo stays portable, absolute when the store was moved
    somewhere else entirely."""
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)


def slug(url):
    s = re.sub(r"^https?://(www\.)?", "", url)
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return s[:90]


def decoded(raw, encoding):
    """Undo a compressed transfer, so the bytes hashed are the bytes a reader sees.

    urllib does not decompress and curl does, so without this the same page
    captured on two hosts hashes differently, and the text extraction reads a
    gzip stream as navigation and calls the capture thin. Sniff the magic bytes
    as well as the header, because a server that compresses without saying so is
    common enough."""
    enc = encoding.lower().strip()
    if enc == "gzip" or raw[:2] == b"\x1f\x8b":
        try:
            return gzip.decompress(raw)
        except OSError:
            return raw
    if enc in ("deflate", "zlib"):
        for wbits in (-zlib.MAX_WBITS, zlib.MAX_WBITS):
            try:
                return zlib.decompress(raw, wbits)
            except zlib.error:
                continue
    return raw


def fetch(url):
    """Standard library first, curl second. Returns raw bytes so the hash is of
    what actually arrived.

    The capture path used to shell out to curl alone, which made the whole tool
    depend on a binary the host might not have. urllib follows redirects and is
    always there. curl stays as the fallback because it survives the handful of
    sites that hang up on urllib, so neither path being missing stops a capture."""
    try:
        with urllib.request.urlopen(
                urllib.request.Request(url, headers={"User-Agent": USER_AGENT}),
                timeout=60) as r:
            raw = decoded(r.read(), r.headers.get("Content-Encoding", ""))
        if raw:
            return raw
    except Exception:
        # Deliberately broad. Every failure mode here has the same remedy, which
        # is to try curl, and a capture tool that dies on an exception class it
        # did not anticipate is a capture tool that stops working in two years.
        pass
    try:
        r = subprocess.run(["curl", "-sL", "--max-time", "60", url], capture_output=True)
    except OSError:
        raise SystemExit(f"could not fetch {url} (no curl, and the standard library failed)")
    if r.returncode != 0 or not r.stdout:
        raise SystemExit(f"could not fetch {url} (curl exit {r.returncode})")
    return r.stdout


def to_text(raw):
    """Tag-stripped text, for finding a quote again. Not a rendering."""
    s = raw.decode("utf-8", errors="ignore")
    s = re.sub(r"<script.*?</script>|<style.*?</style>", " ", s, flags=re.S | re.I)
    s = html.unescape(re.sub(r"<[^>]+>", " ", s))
    return re.sub(r"[ \t]*\n[ \t]*", "\n", re.sub(r"[ \t]+", " ", s)).strip()


# A capture is only evidence if the words are in it. Below this many words of
# real prose, an HTML capture is almost always navigation: the page rendered its
# body in the browser and curl saw the shell. Measured across a working corpus,
# pages that yielded a quotable sentence sat at 385 and above, and the two that
# yielded nothing sat at 128 and 182.
THIN_PROSE_WORDS = 300


def prose_words(text):
    """Words that sit in sentence-length lines.

    Navigation is short lines. Prose is long ones. Counting only lines of twelve
    words or more separates a page that says something from a page that lists
    links to pages that say something, and it needs no parser to do it."""
    return sum(len(w) for w in (ln.split() for ln in text.splitlines()) if len(w) >= 12)


def text_hash(raw):
    """Hash of the normalised text, not the bytes.

    The bytes hash of a live page changes when nothing that matters changed: a
    rotating banner, a token, a timestamp. Ours flagged the case tracker as MOVED
    on the same day it was captured, and the number on it was identical. A check
    that cries wolf gets switched off, so the bytes hash and the text hash are
    both recorded and --check says which one moved."""
    if raw[:4] == b"%PDF":
        return hashlib.sha256(raw).hexdigest()
    return hashlib.sha256(to_text(raw).encode()).hexdigest()


def pdf_text(path):
    """The text of a captured PDF, via `pdftotext` when the host has it.

    A PDF with no text file cannot have a quote checked against it, so `claims.py`
    refuses every claim resting on one and the source is lost. One round-01 run lost a
    source outright this way and shipped that boundary uncited.

    No dependency is added: where `pdftotext` is absent the capture is marked thin, which
    sends the run down the retrieval ladder immediately instead of after it has written a
    quote it cannot support. An image-only PDF lands in the same place, correctly.
    """
    try:
        out = subprocess.run(["pdftotext", "-q", str(path), "-"],
                             capture_output=True, timeout=60)
    except (FileNotFoundError, subprocess.SubprocessError):
        return ""
    return out.stdout.decode("utf-8", "replace") if out.returncode == 0 else ""


def watched(raw, pattern):
    """The value you actually care about, on a page that changes constantly."""
    if not pattern:
        return None
    m = re.search(pattern, to_text(raw))
    return m.group(1) if m and m.groups() else (m.group(0) if m else None)


def archive(url):
    """Ask the Internet Archive to keep its own dated copy.

    A snapshot you hold yourself is a single-host archive with one custodian and
    no independent witness, which is the failure Zittrain et al. built Perma to
    avoid. For anything that might be contested, get somebody else to timestamp
    it too. Returns the archived URL, or None."""
    r = subprocess.run(["curl", "-sI", "--max-time", "90",
                        "https://web.archive.org/save/" + url], capture_output=True)
    head = r.stdout.decode("utf-8", "ignore")
    m = re.search(r"^(?:content-location|location):\s*(\S+)", head, re.I | re.M)
    if not m:
        return None
    loc = m.group(1)
    loc = loc if loc.startswith("http") else "https://web.archive.org" + loc
    if not snapshot_matches(loc, url):
        # The save endpoint follows redirects, so a page that redirects elsewhere comes
        # back as a snapshot of the destination. A round-05 run was handed a snapshot of a
        # different BIS page than the one it cited and spotted it by reading the URL.
        # A wrong archive URL is worse than none: it looks like independent custody of a
        # document nobody archived.
        print(f"sourced: the archive returned a snapshot of {loc}, which is not {url}. "
              f"Refused: a wrong archive URL reads as custody and is not.", file=sys.stderr)
        return None
    return loc


def snapshot_matches(snapshot, url):
    """True when a web.archive.org URL is a snapshot of this url and not of a redirect.

    The archived URL carries the original after the timestamp, so the comparison is on
    that tail. Scheme, a leading www and a trailing slash are not differences; a different
    host or path is.
    """
    def norm(u):
        u = re.sub(r"^https?://", "", (u or "").strip(), flags=re.I)
        u = re.sub(r"^www\.", "", u, flags=re.I)
        return u.rstrip("/").lower()

    tail = re.sub(r"^https?://web\.archive\.org/web/[^/]*/", "", snapshot or "", flags=re.I)
    return norm(tail) == norm(url)


def load_index():
    return json.loads(INDEX.read_text()) if INDEX.exists() else []


def save_index(rows):
    STORE.mkdir(parents=True, exist_ok=True)
    INDEX.write_text(json.dumps(rows, indent=1) + "\n")


def parse_condition(text):
    """`dimension=value:basis` -> {dimension, value, basis}. ValueError names the form.

    Strict on purpose. A condition recorded loosely at capture time is the archaeology
    this flag exists to prevent, one step later.
    """
    head, _, basis = str(text).rpartition(":")
    dimension, _, value = head.partition("=")
    dimension, value, basis = dimension.strip(), value.strip(), basis.strip()
    if not (dimension and value and basis):
        raise ValueError(
            f"--condition wants dimension=value:basis, for example "
            f"'air quality=clean:observed'; got {text!r}")
    # Both vocabularies are accepted. `basis` split into `basis` and `status` on
    # 29 August 2026, and the five older words still read and translate; refusing a
    # habit typed a hundred times would be a break with nothing gained.
    if basis not in dimensions.ALL_BASES:
        raise ValueError(f"--condition basis {basis!r} is not one of "
                         f"{list(dimensions.BASES)} or one of the older "
                         f"{list(dimensions.LEGACY_BASES)}")
    return {"dimension": dimension, "value": value, "basis": basis}


def parse_define(text):
    """`dimension=one sentence` -> (dimension, definition). ValueError names the form."""
    dimension, _, definition = str(text).partition("=")
    dimension, definition = dimension.strip(), definition.strip()
    if not (dimension and definition):
        raise ValueError(
            f"--define wants dimension=one sentence, for example "
            f"'air quality=How clean the air is at the place and time of the "
            f"observation.'; got {text!r}")
    return dimension, definition


def _immutable(path, raw):
    """A path that does not overwrite an existing capture.

    A capture is evidence: once written, every claim quoting it depends on those exact
    bytes. Re-fetching the same URL on the same day used to land on the same path and
    overwrite it, so a run that re-fetched a page which had since gone behind a wall
    destroyed the good copy it already held and had to climb to an archive rung. That
    happened in round 02 and it is a data-loss bug, not an inconvenience.

    Identical bytes reuse the path, because that is genuinely the same capture. Different
    bytes get a sibling, so both readings survive and the later one can be compared with
    the earlier.
    """
    if not path.exists():
        return path
    if path.read_bytes() == raw:
        return path
    stem, ext = path.stem, path.suffix
    for n in range(2, 100):
        alt = path.with_name(f"{stem}--{n}{ext}")
        if not alt.exists():
            print(f"sourced: {path.name} already holds different bytes; this fetch is "
                  f"{alt.name}. The first capture is untouched.", file=sys.stderr)
            return alt
        if alt.read_bytes() == raw:
            return alt
    raise RuntimeError(f"{path.name}: 99 differing captures on one day, which is a loop")


def capture(url, tier, note, watch=None, archive_it=False, conditions=()):
    """Capture a source, and the conditions it held under while they are still in front
    of you. Conditions are optional and skipping them is the default: the reading is what
    the capture is for. Each one is validated, counted in the project's dimension
    registry, and stored on the index row."""
    recorded = []
    for entry in conditions:
        dimensions.validate_condition(entry)
        # STORE, not the module default: this module is `__main__` when run as a
        # script, so `dimensions` importing it by name would get a second copy whose
        # store is still the default and write the registry somewhere else.
        # STORE is the ROOT here, and it is passed by keyword: the second positional
        # argument is now the definition. `allow_undefined` is what keeps a capture from
        # failing over a dimension nobody has defined yet, and `force` is what keeps it
        # from stopping on a near match. Both are reported below rather than swallowed.
        recorded.append((entry, dimensions.register(entry["dimension"], root=STORE,
                                                    force=True, allow_undefined=True)))
    raw = fetch(url)
    digest = hashlib.sha256(raw).hexdigest()
    now = datetime.now(timezone.utc)
    is_pdf = raw[:4] == b"%PDF"
    prose = None if is_pdf else prose_words(to_text(raw))
    row = {"url": url, "sha256": digest, "textSha256": text_hash(raw), "bytes": len(raw),
           "capturedAt": now.isoformat(timespec="seconds"),
           "tier": tier, "custodian": "self", "note": note or ""}
    if prose is not None:
        row["proseWords"] = prose
        if prose < THIN_PROSE_WORDS:
            row["thin"] = True
    if watch:
        row["watch"] = watch
        row["watchValue"] = watched(raw, watch)
    if recorded:
        row["conditions"] = [entry for entry, _ in recorded]
    if archive_it:
        row["archiveUrl"] = archive(url)
        row["custodian"] = "self+third-party" if row["archiveUrl"] else "self"

    if tier >= 2:
        day = STORE / now.strftime("%Y-%m-%d")
        day.mkdir(parents=True, exist_ok=True)
        ext = ".pdf" if is_pdf else ".html"
        base = day / slug(url)
        snap = _immutable(base.with_suffix(ext), raw)
        snap.write_bytes(raw)
        row["snapshot"] = _rel(snap)
        if ext == ".html":
            snap.with_suffix(".txt").write_text(to_text(raw))
            row["text"] = _rel(snap.with_suffix(".txt"))
        else:
            text = pdf_text(snap)
            if text.strip():
                snap.with_suffix(".txt").write_text(text)
                row["text"] = _rel(snap.with_suffix(".txt"))
                row["proseWords"] = prose = prose_words(text)
                if prose < THIN_PROSE_WORDS:
                    row["thin"] = True
            else:
                # No text means no quote can ever be checked against this capture.
                # Say so now, at the rung where it can still be climbed.
                row["thin"] = True
                row["note"] = (row.get("note") or "") + \
                    " no extractable text: image-only PDF, or pdftotext is not installed"

    rows = [r for r in load_index() if r["url"] != url] + [row]
    save_index(rows)
    print(f"{digest[:16]}  tier {tier}  {len(raw):>9,} bytes  {url}")
    for entry, result in recorded:
        said = "new dimension" if result.status == "new" else "known dimension"
        print(f"                 condition: {entry['dimension']} = {entry['value']} "
              f"({entry['basis']}), {said}")
        if result.why:
            print(f"                 {result.why}", file=sys.stderr)
        if not dimensions.is_defined(result.row):
            print(f"                 UNDEFINED: nothing says what "
                  f"{entry['dimension']!r} means. One name over two meanings makes a "
                  f"false comparison, and a false conflict refuses a delivery. Run:",
                  file=sys.stderr)
            print(f"                   python3 sourced.py --define "
                  f"\"{entry['dimension']}=…\"", file=sys.stderr)
    if row.get("watchValue"):
        print(f"                 watching: {row['watchValue']}")
    if row.get("archiveUrl"):
        print(f"                 archived: {row['archiveUrl']}")
    if tier >= 2:
        print(f"                 -> {row['snapshot']}")
    if row.get("thin"):
        print(f"                 THIN: only {prose} words of prose in {len(raw):,} bytes.",
              file=sys.stderr)
        print("                 The hash is real and the evidence may not be. Sites that render",
              file=sys.stderr)
        print("                 their body in the browser return navigation to curl. Open the",
              file=sys.stderr)
        print("                 text file and confirm your quote is in it before citing this.",
              file=sys.stderr)
    return row


def check():
    """Re-fetch everything and report what moved. The point of a hash is that
    'has this changed?' costs one second instead of a re-reading."""
    rows, moved = load_index(), 0
    for r in rows:
        try:
            raw = fetch(r["url"])
        except SystemExit:
            print(f"DEAD      {r['url']}  (captured {r['capturedAt'][:10]})")
            moved += 1
            continue
        same_bytes = hashlib.sha256(raw).hexdigest() == r["sha256"]
        same_text = text_hash(raw) == r.get("textSha256")
        now_watch = watched(raw, r.get("watch"))
        if r.get("watch") and now_watch != r.get("watchValue"):
            moved += 1
            print(f"VALUE     {r['url']}\n          {r.get('watchValue')} -> {now_watch}")
        elif same_text:
            note = "" if same_bytes else "  (bytes differ, text identical)"
            print(f"unchanged {r['url']}{note}")
        else:
            moved += 1
            print(f"MOVED     {r['url']}\n          text changed since {r['capturedAt'][:10]}")
    print(f"\n{moved} of {len(rows)} sources changed materially since capture")
    return moved


def demo():
    """Three cases with known answers, no network. The threshold is all three: a
    capture that passes two of them is a capture that writes a row a reader will
    trust, and there is no partial credit on evidence."""
    # Case 1: a hash notices what a reader would not. One byte moves the bytes
    # hash; a comment that changes nothing readable must not move the text hash,
    # because a check that cries wolf gets switched off.
    a, b = b"the sky is blue", b"the sky is blue."
    assert hashlib.sha256(a).hexdigest() != hashlib.sha256(b).hexdigest()
    assert slug("https://www.example.com/a/b?c=1") == "example-com-a-b-c-1"
    assert "quote here" in to_text(b"<p>quote <b>here</b></p><script>x</script>")
    assert "x" not in to_text(b"<p>quote <b>here</b></p><script>x</script>")
    a2, b2 = b"<p>hi</p><!--t=1-->", b"<p>hi</p><!--t=2-->"
    assert hashlib.sha256(a2).hexdigest() != hashlib.sha256(b2).hexdigest()
    assert text_hash(a2) == text_hash(b2)
    assert watched(b"<p>( 1959 cases identified so far)</p>", r"\(\s*([\d,]+) cases") == "1959"
    # A compressed transfer must hash the same as an uncompressed one, whether the
    # server declared the encoding or not, or the same page captured on a host with
    # curl and a host without it produces two different hashes for one document.
    page = b"<p>the quick brown fox jumps over the lazy dog</p>"
    assert decoded(gzip.compress(page), "gzip") == page
    assert decoded(gzip.compress(page), "") == page, "sniff the magic bytes too"
    assert decoded(zlib.compress(page)[2:-4], "deflate") == page
    assert decoded(page, "") == page and decoded(page, "identity") == page

    # Case 2: navigation is not evidence. Many short lines count zero prose words,
    # sentence-length lines count above the threshold, and the threshold is 300.
    nav = "\n".join(["Docs", "Blog", "Pricing", "Spans", "Metrics", "Logs"] * 40)
    assert prose_words(nav) == 0
    body = ("Application tracing records the complete lifecycle of a request as it flows "
            "through your system, capturing every operation along the way.\n") * 20
    assert prose_words(body) > THIN_PROSE_WORDS

    # Case 3: end to end over file://, so the standard library fetch, the row that
    # lands on disk and the thin flag are all exercised without a network.
    keep_store, keep_index = STORE, INDEX
    try:
        with tempfile.TemporaryDirectory() as d:
            d = pathlib.Path(d)
            set_store(d / "store")
            thin_page = d / "thin.html"
            thin_page.write_bytes(b"<html><body><a>Docs</a><a>Blog</a></body></html>")
            fat_page = d / "fat.html"
            fat_page.write_bytes(("<html><body><p>" + body + "</p></body></html>").encode())
            # the capture prints its own report; quiet here so the pass line is
            # the only thing this check says
            with contextlib.redirect_stdout(io.StringIO()), \
                    contextlib.redirect_stderr(io.StringIO()):
                thin = capture(thin_page.as_uri(), 2, "self-check")
                fat = capture(fat_page.as_uri(), 1, "self-check")
            assert thin["thin"] is True and thin["proseWords"] == 0
            assert "thin" not in fat and fat["proseWords"] > THIN_PROSE_WORDS
            rows = load_index()
            assert len(rows) == 2, rows
            row = [r for r in rows if r["url"] == thin["url"]][0]
            # every field a later check reads must survive the round trip to disk
            assert row["sha256"] == hashlib.sha256(thin_page.read_bytes()).hexdigest()
            assert row["textSha256"] == text_hash(thin_page.read_bytes())
            assert row["proseWords"] == 0 and row["thin"] is True
            assert (ROOT / row["snapshot"]).exists(), "tier 2 must leave the bytes on disk"
            # Conditions ride along with the capture. Skipping them is the default, so
            # the two rows above carry no `conditions` key at all and stay valid.
            assert "conditions" not in row
            with contextlib.redirect_stdout(io.StringIO()), \
                    contextlib.redirect_stderr(io.StringIO()):
                withcond = capture(fat_page.as_uri(), 1, "self-check", conditions=[
                    {"dimension": "air quality", "value": "clean", "basis": "observed"}])
            assert withcond["conditions"][0]["dimension"] == "air quality"
            saved = [r for r in load_index() if r["url"] == withcond["url"]][0]
            assert saved["conditions"] == withcond["conditions"], "conditions survive the disk"
            assert [x["name"] for x in dimensions.load(STORE)] == ["air quality"], \
                "the dimension is registered in the store the capture wrote to"
            # and the flag parses to exactly that shape, or refuses with the form named
            assert parse_condition("air quality=clean:observed") == withcond["conditions"][0]
            # A value carrying its own separators: the split takes the first `=` and
            # the last `:`, so a time window survives intact.
            assert parse_condition("time window=14:00 to 18:00:tested") == {
                "dimension": "time window", "value": "14:00 to 18:00", "basis": "tested"}
            assert parse_condition("query=a=b:inferred") == {
                "dimension": "query", "value": "a=b", "basis": "inferred"}
            for bad in ("air quality=clean", "air quality:observed", "=clean:observed",
                        "air quality=clean:guessed"):
                try:
                    parse_condition(bad)
                except ValueError:
                    continue
                raise AssertionError(f"--condition {bad!r} must be refused")

            # Case 4: both basis vocabularies. `basis` split into `basis` and `status`
            # on 29 August 2026, and the flag takes either word, so a habit typed a
            # hundred times still works and a new capture can say who said it.
            for word in dimensions.ALL_BASES:
                assert parse_condition(f"air quality=clean:{word}")["basis"] == word
            assert parse_condition("air quality=clean:human") == {
                "dimension": "air quality", "value": "clean", "basis": "human"}
            # and the refusal names both vocabularies, so the message is followable
            try:
                parse_condition("air quality=clean:confirmed")
            except ValueError as e:
                assert "human" in str(e) and "tested" in str(e), e
            else:
                raise AssertionError("a status word is not a basis word")

            # Case 5: the definition flag, and the warning that replaces a refusal.
            # A dimension needs a definition, because one name over two meanings makes a
            # false comparison. But refusing the capture over it would lose the source,
            # so the capture above recorded `air quality` UNDEFINED and warned on stderr.
            reg = [r for r in dimensions.load(STORE) if r["name"] == "air quality"][0]
            assert not dimensions.is_defined(reg), "a captured dimension starts undefined"
            with contextlib.redirect_stdout(io.StringIO()), \
                    contextlib.redirect_stderr(io.StringIO()) as err:
                capture(fat_page.as_uri(), 1, "self-check", conditions=[
                    {"dimension": "air quality", "value": "clean", "basis": "observed"}])
            said = err.getvalue()
            assert "UNDEFINED" in said and "air quality" in said and "--define" in said, said
            # --define parses to a pair, mints the row, and fills the undefined one in.
            assert parse_define("air quality=How clean the air is here and now.") == (
                "air quality", "How clean the air is here and now.")
            assert parse_define("period=The span of time = the reading covers.") == (
                "period", "The span of time = the reading covers.")
            for bad in ("air quality", "=a sentence", "air quality=", "  "):
                try:
                    parse_define(bad)
                except ValueError as e:
                    assert "dimension=one sentence" in str(e), e
                    continue
                raise AssertionError(f"--define {bad!r} must be refused")
            dimensions.define("air quality", "How clean the air is here and now.",
                              root=STORE)
            reg = [r for r in dimensions.load(STORE) if r["name"] == "air quality"][0]
            assert dimensions.is_defined(reg) and reg["uses"] >= 2, reg
            # and a capture after the definition says nothing about it
            with contextlib.redirect_stdout(io.StringIO()), \
                    contextlib.redirect_stderr(io.StringIO()) as err:
                capture(fat_page.as_uri(), 1, "self-check", conditions=[
                    {"dimension": "air quality", "value": "clean", "basis": "observed"}])
            assert "UNDEFINED" not in err.getvalue(), err.getvalue()
    finally:
        set_store(keep_store)
        assert INDEX == keep_index

    # A capture is never overwritten by a later, different fetch of the same URL.
    with tempfile.TemporaryDirectory() as d:
        f = pathlib.Path(d) / "page.html"
        f.write_bytes(b"first")
        assert _immutable(f, b"first") == f, "identical bytes reuse the path"
        with contextlib.redirect_stderr(io.StringIO()):
            alt = _immutable(f, b"second")
        assert alt != f and alt.name == "page--2.html", alt
        alt.write_bytes(b"second")
        assert f.read_bytes() == b"first", "the first capture survives a later fetch"
        assert _immutable(f, b"second") == alt, "the same later bytes find their own file"

    print(f"sourced: self-check passed (6 of 6 cases; the threshold is 6 of 6, "
          f"thin below {THIN_PROSE_WORDS} prose words)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("url", nargs="?")
    ap.add_argument("--tier", type=int, default=1, choices=[1, 2])
    ap.add_argument("--note", default="")
    ap.add_argument("--watch", default=None,
                    help="regex whose group(1) is the value you care about, for live pages")
    ap.add_argument("--define", action="append", default=[], metavar="DIM=SENTENCE",
                    help="what a dimension means, in one sentence; repeatable, and "
                         "usable on its own without a url, for example "
                         "'air quality=How clean the air is here and now.'")
    ap.add_argument("--condition", action="append", default=[], metavar="DIM=VALUE:BASIS",
                    help="a condition this source held under, recorded as you read it; "
                         "repeatable, for example 'air quality=clean:observed'")
    ap.add_argument("--archive", action="store_true",
                    help="also ask the Internet Archive to keep a dated copy")
    ap.add_argument("--store", default=None,
                    help="directory the store lives in (default: $SOURCED_ROOT/$SOURCED_STORE)")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--self-check", action="store_true")
    a = ap.parse_args()
    if a.store:
        set_store(a.store)
    if a.self_check:
        demo()
        raise SystemExit(0)
    # Definitions land before anything else, so one command can define a dimension and
    # then capture a source under it. With no url this is the whole run, which is how a
    # dimension gets defined before the source that needs it turns up.
    for text in a.define:
        try:
            name, definition = parse_define(text)
        except ValueError as e:
            ap.error(str(e))
        row = dimensions.define(name, definition, root=STORE)
        print(f"defined  {row['name']}: {row['definition']}")
    if a.check:
        sys.exit(0 if check() == 0 else 1)
    elif a.url:
        try:
            conds = [parse_condition(c) for c in a.condition]
        except ValueError as e:
            ap.error(str(e))
        row = capture(a.url, a.tier, a.note, a.watch, a.archive, conds)
        # A thin capture exits 2, not 0. The warning above used to be the only
        # signal, and a truncated command swallowed it: the run reported success
        # while the evidence held nothing quotable.
        sys.exit(2 if row.get("thin") else 0)
    elif not a.define:
        ap.error("give a url, or --define, or --check, or --self-check")
