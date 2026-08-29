# The one-pass audit

One prompt that runs everything that can run without fetching: labels every claim by where it came
from, argues back at the load-bearing ones, collapses sources into independent origins, gives a
verdict, and drafts the four-line provenance block. Where a claim cannot be trusted without opening
its source, it says so — that list is your homework, in order. Run it on one document.

If you want the pieces separately, they are `the-claim-sweep.md`, `the-source-check.md` (the only
one that fetches) and `the-four-lines.md` in this directory.

**Paste your document under the line, then this prompt above it.**

---

You are auditing a document I am about to send. Do not rewrite it, do not improve it, and do not
comment on its quality.

First, find every load-bearing claim — numbers, findings, causal statements, regulatory assertions,
and anything a reader would repeat. Restate each in one sentence and label it with exactly one of:
**sourced** (the document names a source I could open, with a locator), **recalled** (asserted from
memory, with no source or one too vague to open), or **inferred** (a conclusion the author drew).
Note where a claim cites a write-up rather than the original, or a preprint rather than the
published version.

Second, argue back. For the three claims the argument most depends on, make the strongest case that
each one is wrong, and state what would have to be true for it to be false.

Third, group the sources into origins — ten write-ups of one press release are one source — and say
how many independent origins actually support this document. Name any source that benefits from its
own claim being believed.

Fourth, give a verdict: **defensible**, **thin**, or **not safe to send**, and the single most
likely place this document is wrong.

Last, draft a four-line provenance block from what you found, not from how careful the author felt.
Attribution: who authored it, and that AI tools assisted, in one sentence. Accountable: the named
person who answers for it. Limitations: what is not backed, and how far each claim sits from its
source — never empty. References: what backs it, where it lives, and how a reader can check it.
Every line must either make a limit transparent or let the reader go and check something; cut any
line that does neither.

Do not fetch anything. Where a claim cannot be trusted without opening its source, say so — that
list, in order, is the author's homework.
