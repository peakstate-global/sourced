# The provenance block

Read this when writing the four-label block or its References list.

The four-label provenance block, in this order, **generated from the sidecar rather than
written by hand**:

```
Attribution:  The human author, then each AI tool by product and model, what it did, and how.
Accountable:  The named person who answers for it, and nothing else.
Limitations:  What is not backed, and how far each claim is from its source.
References:   What backs it, where it lives, and how it can be checked.
```

**The test that governs every line: it must either make a limit transparent, or let the
reader go and check something.** A line that does neither is a motherhood statement and
comes out.

- *"Twelve sources, retrieved and hashed on 25 August 2026, each figure quoted with a
  locator."* — investigable. Pick one, check it, catch me.
- *"Sources verified against originals."* — neither. It asserts diligence, which is the one
  thing a reader cannot verify. **Cut it.**

**Accountable is the named person's name, and nothing else.** The default form is:

```
Accountable: Andrew Ramsden.
```

**A person is accountable for a process without reading every output of it.** That is not a
compromise or a shortcut, it is how governance and quality control already work in every
large organisation: a named person answers for the system, the sampling and the controls,
and does not personally read each thing the system produces. Accountability is for the
process. Review is for the artefact. They are different acts by possibly different people,
and collapsing them is what makes a signature meaningless. That principle lives here, in the
explanation; it no longer appears on the line itself.

- **A model never writes a review status, in either direction.** No `(Not reviewed)`, no
  `(Reviewed ...)`, and never inferred from the name being present or from the named person
  having asked for the work. The model does not know the person's review status, so any
  status it writes is an ungrounded claim about a named person.
- **Only the named person may add anything after the name**, and only their own words,
  verbatim, once they have said exactly what to add: `Accountable: Andrew Ramsden. Reviewed
  version 3, 7 September 2026.` Until they say so, the line stops at the name and the full
  stop.
- **The acts in the sidecar stay the record of who did what.** The sidecar, not the
  provenance line, is where a review act is logged (`underwriting`), because it is checkable
  there and the line only ever reports a person's own words back to them.

There is no `Verified:` label. Verification is a property of the references and belongs
inside that line, stated as a checkable fact. **Limitations is as short as the truth allows.**
It is never padded to look diligent: a Limitations line that exists to prove the author
looked is a motherhood statement of a different colour. If nothing material was omitted,
write `None material.` and move on.

**Limitations is a list of limits on the evidence, not a list of the author's own reasoning.**
Four rules, each
from a real miss on 2026-08-27:

- **Our own thinking never appears in Limitations. Not even to label it.** No "this is
  my framework", "my estimate", "my arithmetic", "a prediction", "our own framing".
  Naming our thinking as a limitation puts it beneath the thinking we cite, and our
  thinking is the value of the piece. Label it INFERRED in the sidecar and say nothing
  here. Restating the rule did not make it hold. The `kind` field did, by giving our own
  contribution a place of its own.
- **A claim's own `kind` decides where it is disclosed.** A stance and a piece of lived
  experience owe no evidence by design, so `position` and `story` claims are disclosed as
  INFERRED in the sidecar and do not appear in Limitations. That is not an omission, it is the
  right label: naming a stance as a limit on the evidence files it under the wrong question.
- **The decision test, per sentence: would a reader decide differently knowing this?** If
  not, cut it. A source not retrieved; a primary read through a secondary; a figure quoted
  from a write-up; a survey whose base is small. One sentence each. Nothing else qualifies
  — not where our working files live, not what we did not publish, not how the piece was
  made. The stretching came from an older rule saying Limitations must never be empty, which
  turned an honest "none material" into a hunt for something to confess. That rule is gone.
- **A source you could not fetch is "unavailable at the time of retrieval".** Nothing about
  navigation shells, 403s or curl. Then, in the delivery message, **list every URL that was
  blocked** so the user can try to source it by hand.
- **Link the sidecar. Always, published or not.** The References line ends with a link to
  the sidecar, because a paper a reader cannot get from to its own evidence has given up the
  thing that makes it different from an opinion. Published: link where it is served,
  `[SOURCED sidecar](/sourced/<slug>.sourced.json)`. For a Kilipress tenant that means the
  sidecar lives in `public/sourced/`, not beside the post. **Unpublished, on disk: link the
  relative path**, `[SOURCED sidecar](artefact.md.sourced)`.
  The old rule made this conditional on publication, so of four round-02 papers that lived
  on disk, three named the sidecar as bare text and one did not mention it at all.
  A piece with no external sources says exactly that: `No external sources.` is a complete
  Limitations line, and so is `None material.`

**The distinction.** A limit on the evidence stays; a limit on our own thinking belongs in the
sidecar instead.

| A limit on the **evidence** | "read through a secondary, not the original" | keep |
| A limit on **our own thinking** | "no evidence this framework improves anything" | cut |

The first tells a reader how far to trust a source. The second answers a different question and
answers it in the wrong place: how far to trust our reasoning is what INFERRED says, in the
sidecar, where a reader can see which claims it applies to.

**Open conflicts write their own Limitations lines.** Do not compose them by hand:

    python3 conflicts.py <file.sourced>          every conflict, open ones last

`conflicts.disclosure_lines(data)` returns one sentence per open conflict, naming both
sources, the claim, the dimensions they differ on and the unknown region. Paste those
straight into Limitations. They are a limit on the **evidence**, which is exactly what
that label carries. An open conflict that does not appear in Limitations is the failure
`integrate.py` refuses, so generating the line and running the gate are two halves of one
step.

**The gate.** `python3 integrate.py <file.sourced>` runs before any statement ships. It refuses
a delivery that hides a disagreement, which is the O rule failing the way a written-down rule
fails: agreed, and quietly not done.
Three things refuse it, and each one is a disagreement the reader never gets to see.

| An open conflict in `conflicts[]` | the sidecar records it and the delivery says nothing | refuse |
| Evidence rows that disagree with no conflict record and no boundary | the disagreement is in the evidence and nothing acknowledges it | refuse |
| `fails_when` with no `replaced_by` | a refutation with no replacement leaves the reader holding the belief it refuted | refuse |
| Evidence whose period ends before the subject's period begins | the study finished before the thing it is cited about began | flag |

The flag prints and the exit code stays 0. Staleness is read off periods written by hand, so it
is a soft signal, and a gate that fails on a soft signal is a gate that gets switched off.

### References are APA 7th, always

**Every source in the References line is a full APA 7th edition entry.** Prose shorthand
is not a reference — the reader cannot retrieve the source from it, which fails the
investigable test the label exists to pass.

Shape: the prose sentence that makes the set checkable (count, retrieval dates, that
each figure carries a locator), then the entries as a list, one per source, hanging
indent where the medium supports it, **in alphabetical order by the first element of each
entry** (author surname; title when there is no author), as APA 7th requires. Prose first,
entries after — never entries fused into a sentence.

- ✗ `Zittrain, Albert & Lessig (2014), Harvard Law Review 127.`
- ✓ `Zittrain, J., Albert, K., & Lessig, L. (2014). Perma: Scoping and addressing the
  problem of link and reference rot in legal citations. Legal Information Management,
  14(2), 88–99. https://doi.org/10.1017/S1472669614000255`

Include author surname and initials, year, full title, container with volume, issue and
page range where they exist, publisher where there is one, and a DOI or URL. Add a
retrieval date only where the content is designed to change (a live database, a wiki).

**Never write an entry from memory.** Every element comes from the source retrieved this
session. Missing element → use the APA rule for it (`(n.d.)`, title in the author
position) and say so in Limitations. Do not invent a volume or a page range.

## Generating the block

    python3 statement.py <file.sourced> --agent "<model and version>" --agent "<harness and version>" --write

It applies every rule above: the grade sentence lands in Attribution or Limitations by grade,
Accountable is the name alone, source counts collapse by origin, the diligence sentence
appears only when every row has a quote and a locator, and References ends with the sidecar link.
It refuses a sidecar whose cited rows lack a `reference` (schema 1.11), and it refuses to run
without at least one `--agent`, because the fidelity line is mandatory.
