---
promptVersion: 2
frozen: 2026-08-29
---

# The run prompt

**Every research agent in every round receives this, byte-identical, with only `{{CLAIM}}` and
`{{RUNDIR}}` substituted.** If the prompt drifts, the rounds are not comparable and the ledger is a
scrapbook. A change bumps `promptVersion` and the ledger marks the round where the ruler moved.

**The agent is blind to the rubric.** Hand an agent the scoring criteria and it writes to them,
which measures the prompt rather than the skill. Nothing below names a criterion.

---

## Prompt body

```
Run /sourced research on the claim below. Before anything else, run these two lines, which
put the run's own bin first on PATH and point captures at the run's store:

  export PATH="{{RUNDIR}}/bin:$PATH"
  export SOURCED_STORE="{{RUNDIR}}/store"

Work in {{RUNDIR}}.

The claim:

  {{CLAIM}}

This claim is deliberately contentious. Your job is not to pick a side and not to be even-handed
about it. Produce the most defensible integrated position you can reach, and write it to
{{RUNDIR}}/artefact.md with its sidecar.

Two settings apply to this run and are recorded in the round manifest:

1. An operator overlay may apply, relaxing or adding a constraint for this run. Where one is
   present it is appended below this line, and the manifest records that it applied along with a
   hash of it. Where none is present, every rule in the skill applies as written.

2. Run step 0 before touching the open web: check whatever prior corpus this host binds, and say
   in one line what it held and what it did not. A thin corpus is a finding, not a failure, and a
   host that binds nothing says so in that line and continues.

Everything else about /sourced applies as written. Use the skill as it is. Do not invent process.

Return at most 12 lines: the path to the artefact, the number of sources captured, how many claims
were sourced, recalled and inferred, and anything the skill refused to let you do.
```

---

## The overlay, and why its contents are not in this file

A harness that switches a rule off and does not say so is measuring something other than what it
claims to. A public harness that prints the switched-off rule in its own README is also handing a
sentence to anyone who reads it out of context, and a sentence out of context is what a stranger
quotes.

So the two halves are split. **That an overlay applied, and a hash of it, are recorded in every
round manifest**, which is what makes a round reproducible and stops a relaxed run being reported
as a strict one. **What the overlay says is the operator's**, and it lives with the measurements
rather than with the instrument.

Every rule in the skill stays on in ordinary use. Under test, a rule that stops a run before it
reaches a conclusion leaves nothing to score, and the round then measures the refusal rather than
the reasoning. An operator may relax such a rule for a run. The output of a relaxed run is
laboratory material, not a deliverable, whatever it concludes.

Put the overlay at `$SOURCED_EVAL_DIR/overlay.md`. If the file is absent, nothing is relaxed.
