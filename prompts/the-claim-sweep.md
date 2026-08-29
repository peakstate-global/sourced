# The Claim Sweep

Finds the claims in a document that would be embarrassing to be wrong about, and labels each one by
where it actually came from. Run it on one document. It changes nothing and fetches nothing.

**Paste your document under the line, then this prompt above it.**

---

You are auditing a document for claim provenance. Do not rewrite it, do not improve it, and do not
comment on its quality. Provenance and quality are different questions and conflating them turns a
governance conversation into a taste argument.

Find the **load-bearing claims**. A claim is load-bearing when the document's argument changes if it
is wrong: numbers, findings, causal statements, regulatory assertions, and anything a reader would
repeat. Ignore rhetorical questions, restatements of a claim you have already listed, and the
author's descriptions of their own process.

For each one, output a row with:

1. **The claim**, restated in one sentence, present tense, source-neutral. If it needs an "and" to
   hold two facts, it is two claims. Split it.
2. **The label**, exactly one of:
   - `sourced` — the document names a specific source you could open, with enough locator to find
     the passage.
   - `recalled` — asserted with no source, or with a source too vague to open. Legitimate, and it
     must be labelled.
   - `inferred` — the author's own conclusion drawn from other claims. Also legitimate, also
     labelled.
3. **Distance from primary**, where it applies: "cited through a news article, not the study",
   "quotes a preprint, not the published version", "trade reporting of a report".
4. **What would have to be true** for the claim to be false. If you cannot name an observation that
   would falsify it, say so: an unfalsifiable claim must never be presented as a finding.

Then, separately:

- **Origin groups.** Group the sources. Ten write-ups of one press release are ONE source. Say how
  many independent origins actually support the document, not how many citations it carries.
- **Self-interest.** Name any source that benefits from its own claim being believed: a vendor
  sizing its own market, a company reporting its own adoption, a professional body reporting a
  shortage in its own profession.
- **The verdict**, one of:
  - `defensible` — every load-bearing claim is either sourced with a locator, or labelled as
    something other than a finding.
  - `thin` — it survives a friendly room and not a hostile one. List which claims to fix first.
  - `not safe to send` — in its current form. Say what the shortest path to defensible is.

End with the single most likely place this document is wrong, and why you think so.

---

## What it refuses to do

It cannot tell you whether a claim is **true**. It tells you whether you can show where it came
from. Those are different questions, and conflating them is how "verified" becomes a word that means
nothing.

It also cannot see what is not in the document. A claim with a confident-looking citation attached
to a source that does not support it will pass this sweep. That is what the Source Check is for.
