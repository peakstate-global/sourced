# The provenance block

The settled contract. A decision made while reviewing a workshop deck. It governs
any tool or skill that produces a document, brief, deck, report or research
artefact.

---

## The decision

Every deliverable that contains model output ships with a **provenance block**:
four labels, in this order, in a fixed shape.

```
Attribution:  Who authored it, and that AI tools assisted, in one sentence,
              followed by the technical fidelity line.
Accountable:  The named person who answers for it.
Limitations:  What is not backed, and how far each claim is from its source.
References:   What backs it, where it lives, and how it can be checked.
```

### The technical fidelity line

Attribution names the pipeline, not the fact of a machine: **model identifiers, the harness or
framework, the skills or tools invoked, and a version for each.** Where a component has no
version, say so rather than dropping the component.

Use C2PA's `softwareAgent` name-and-version shape per component, and IPTC `digitalSourceType`
terms when the artefact is media. Confirmed against C2PA specification 2.3 and the IPTC
vocabulary on 30 August 2026. Same vocabulary as tooling that already exists, so the block stays
machine-readable without a new dialect.

**Why this grain.** Disclosure exists so a reader can assess the work. A model and a version tell
them something they can check. "AI was involved" tells them only which prior to apply, and it
stops predicting anything the moment the underlying systems get good. It is never a badge, and
never staged so that it pre-empts a reader's judgement.

**No exemption for short form.** A rule with an exemption is a rule people route around.

## The test that governs what goes in it

**Every line must either make a limit transparent, or let the reader go and
check something.** A line that does neither is a motherhood statement and comes
out.

| Line | Function |
|---|---|
| Attribution | integrity |
| Accountable | investigable |
| Limitations | integrity |
| References | investigable |

Worked example of the test:

- `Twelve sources, retrieved and hashed on 25 August 2026, each figure quoted
  with a locator.` — investigable. Pick a figure, check the locator, catch me.
- `Sources verified against originals.` — neither. It asserts diligence, which
  is the one thing a reader cannot verify. **Cut.**

This is why there is no `Verified:` label. Verification is a property of the
references, so it belongs inside the References line, stated as a checkable
fact.

## What was rejected, and why

- **`Verified:` as its own label** — became a statement about how carefully we
  worked. Folded into References as a checkable fact instead.
- **`Out of scope:` as the label for limitations** — the wrong label produced
  the wrong content. "Out of scope" invites facts about the *project* ("this
  session has never been run"); "Limitations" forces facts about the *claims*
  ("read through a citation, not the original"). Reader value is entirely in
  the second kind.
- **A separate AI-attribution line** — demoted to a clause inside Attribution.
  A generic disclosure is enough: *"AI tools assisted research and drafting; all
  outputs verified."* The exact model and division of labour is not what the
  reader needs. What they need is who stands behind it.

## Why the block exists at all

Not compliance. Nothing in APRA's April 2026 letter, the National AI Centre's
six essential practices, Privacy Act APP 1.7–1.8 or the NIST GenAI Profile
requires a limitations statement on a deliverable. APP 1.7–1.8 is a
privacy-policy obligation about automated decisions, and it is discharged by the
entity, not by a line on a document.

The block exists because **every other line tells the reader what is backed.**
Without Limitations, a reader reasonably assumes everything in the document has
the same evidential status as the parts carrying references. That inference is
the harm the block prevents, and it is the only line that bounds how far the
artefact can be relied on.

A statement with no admitted gap reads as marketing. Limitations is what makes
the other three believable.

## The position behind it

None of these problems are new. A machine did not invent one of them. It made
every one of them faster, cheaper and harder to see, at a volume nobody reads.
Human work has always needed this block; AI made the absence of it expensive.

The policy conversation about disclosing AI is largely an overreaction to a new
tool. A ghost-writer never got a credit line either. The one thing that does
survive the comparison: **a ghost-writer can be asked what they checked, and a
model cannot** — which is why the disclosure is about scope, not credit.

## What this means for a skill

Any skill that emits a document, brief, report or deck should:

1. Emit the four-label block, in this order, in a fixed shape — mono or plain
   text, labelled, not styled as prose.
2. Run the test on every line before emitting it. Drop anything that neither
   makes a limit transparent nor lets the reader check something.
3. Fill Limitations honestly, and never leave it empty. If nothing is
   limited, the artefact has not been examined closely enough.
4. State distance from source. "Read through a citation, not the original" is
   a limitation and belongs in the block.
5. Never claim verification it did not perform.

The definition-of-done line that came out of the same session:

> No deliverable containing model output ships without a provenance block: who
> authored it and with what, who is accountable, what its limitations are, and
> where the references live.

## Related

The strength model for an individual claim is separate from this block and
already exists: the the claim-tier editor claim-tier spectrum (tier 0 unanalysed, 1 evidence
sought and none found, 2 single source, 3 multi-source corroborated, 4 boundary
recorded, meaning the claim carries a record of where it holds and where it
fails, plus position and story as their own species of sentence). Use that for grading a claim; use this block for the artefact.
