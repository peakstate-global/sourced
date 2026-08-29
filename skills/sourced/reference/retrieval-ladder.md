# The retrieval ladder

Read this when a source is paywalled, dead, moved, or reachable only through somebody else's
write-up.

Until 28 August 2026 this was improvised differently on every run, so two claims in the same
artefact could be held to different standards without anyone noticing. The ladder fixes the order
and fixes what gets recorded at each rung.

Climb down one rung at a time, and only after the rung above has actually failed. **Capture what
you read, never what you wish you had read.** Run every retrieval through
`python3 sourced.py <url> --tier 2` at the rung you landed on, so the hash and the quote come from
the same bytes.

**A thin capture is not evidence.** Below 300 prose words `sourced.py` warns `THIN` and exits 2,
because the fetch almost always saw a navigation shell. The hash is real and the evidence is not
there. Open the captured `.txt`, confirm your quote is in it, and drop one rung if it is not.
Never cite the page from what the browser shows you.

**Dropping a rung is a fact the reader needs**, not an internal detail. Record the rung in the
evidence record, and say it in Limitations whenever the drop changes what the claim can support.

---

## Rung 1. The publisher

The source itself, at the publisher's own address: the journal, the regulator, the statistical
agency, the company's own filing. This is the only rung where the bytes you hash are the bytes the
author published.

Record: the URL, the retrieval date, the verbatim sentence, the locator, both hashes.

Drop when: the page is paywalled, gone, or returns a navigation shell that trips the thin-capture
check.

## Rung 2. A metadata API

Crossref, DOI resolution, a publisher or repository API, a registry endpoint. These answer for the
bibliographic facts, and often for an abstract, when the full text will not open.

Record: the DOI or identifier, which API answered, the fields it returned, and plainly that **the
full text was not read**. A claim about a study's findings cannot rest on its abstract alone; a
claim about who wrote it, when, and where it appeared, can.

Drop when: no identifier resolves, or the claim needs the body of the text.

## Rung 3. An archive

The Internet Archive's Wayback Machine, Perma.cc, or the publisher's own archive. A third party
holds the copy, which is why an archived page is worth more than a snapshot you took yourself: a
snapshot you hold is self-attested and proves only what you say you saw.

Record: the archive URL, the snapshot date, the original URL, and that the live page did not
answer. The snapshot date is load-bearing, because an archived page can be years away from the
figure being discussed.

Drop when: no archive holds it, or every snapshot predates the claim.

## Rung 4. Quoting through a secondary

Read the write-up, quote the write-up, and say so. This is a real rung, not a failure: much
reporting of primary research is only ever available this way.

Record: the secondary you actually read, with its own quote and locator; the primary as that
secondary describes it; the **distance from primary**, which is 1 for a source read through one
write-up and higher when the write-up is itself quoting another; and that the primary was not
read. Where several write-ups trace to one release, collapse them to one `originGroup` before
counting sources.

Below rung 4 there is no rung. A claim you cannot reach at all is **RECALLED** or it comes out.
Never present the ladder's bottom as though it were its top.
