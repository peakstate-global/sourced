# The Four Lines

Generates the provenance block that ships with the finished thing. It is generated from what the
first two prompts found, never written by hand, or it drifts within two revisions.

**Give it the output of the Claim Sweep, and the Source Checks you ran.**

---

Write a four-label provenance block for this document, from the audit results below.

> [paste the Claim Sweep output and any Source Check results]

The block is exactly four labels, in this order, in a fixed shape:

```
Attribution:  Who authored it, and that AI tools assisted, in one sentence.
Accountable:  The named person who answers for it.
Limitations:  What is not backed, and how far each claim is from its source.
References:   What backs it, where it lives, and how it can be checked.
```

**The test that governs every line: it must either make a limit transparent, or let the reader go
and check something.** A line that does neither is a motherhood statement. Cut it.

- *"Twelve sources, retrieved and hashed on 25 August 2026, each figure quoted with a locator."*
  Investigable. Pick one, check the locator, catch me.
- *"Sources verified against originals."* Neither. It asserts diligence, which is the one thing a
  reader cannot verify. Cut it.

Rules:

- **There is no `Verified:` label.** Verification is a property of the references and belongs inside
  that line, stated as a checkable fact.
- **Limitations is never empty.** If nothing is limited, the document has not been examined closely
  enough. Name what could not be grounded, and how far each remaining claim sits from its source.
- **Never imply that a human review makes the output correct.** A signature buys accountability, not
  accuracy. Where a decision needs a person, say which decision and what they would have to verify.
- **Accountable is a person, not a team and not a system.** Accountability means being able to be
  asked what you checked, and a process cannot be asked.

Output the block and nothing else.
