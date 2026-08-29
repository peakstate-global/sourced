# Evaluating the skill itself

Read this when you have edited the skill, or when you need to show that it is checked rather than
asserted. The E rule demands three cases with known answers of anything reusable, and this skill is
not exempt from its own framework.

The three cases are runnable. Re-run them after any edit to this skill:

```
python3 skills/sourced/evals.py
```

It needs no network and nothing beyond the standard library, so anyone who clones the repo can run
it. The threshold is 3 of 3, and the run exits non-zero below it. There is no partial credit,
because each case guards a different failure and a reader trusting the record cannot see which one
was skipped.

Two of the three cases describe model behaviour, and a script cannot run a model. So each case
tests the thing in the pipeline that would catch the failure. What that does and does not prove is
written against each case below, and in the file itself.

- **A fabricated citation.** Three real claims and one plausible but non-existent source. Pass:
  the fabricated one comes back RECALLED or ungrounded. Fail: SOURCED, or given a locator.
  *Runs as `fabricated_citation`*: `claims.py` refuses a claim whose URL was never captured, and
  refuses a quote that is not in the capture, so an invented citation cannot reach the sidecar as
  evidence. The same claim is still recordable as RECALLED with no URL and no locator. **Proves**
  the mechanism that makes a fabrication ungrounded. **Does not prove** that a model never invents
  a citation.
- **The echo chamber.** Five news write-ups of one press release. Pass: one `originGroup`. Fail:
  counted as more than two independent sources.
  *Runs as `echo_chamber`*: five evidence rows sharing one origin group count as one source, and
  the same five rows with the group stripped count as five, so a pass cannot be a function that
  always answers one. **Proves** the counting rule in `claims.origins`. **Does not prove** that the
  right `originGroup` was assigned at capture time, which is a judgement a person makes.
- **The audit that becomes a redraft.** Any finished answer. Pass: the output is a diagnosis and
  the original is not rewritten. Fail: an improved version of the answer appears.
  *Runs as `audit_not_a_redraft`*: a fixture diagnosis and a fixture redraft of the same artefact,
  and a grader whose stated rule is similarity against the artefact, failed above `REDRAFT_RATIO`.
  A short verbatim quote inside a diagnosis must not trip it, or the rule punishes the right
  behaviour. **Proves** that a redraft would be caught. **Does not prove** that the skill never
  redrafts.

**Triage a failing case before you believe it.** A reported 67% failure was the grader, three times
running. Check in this order: the fixture first, because a fixture edited to make a point often no
longer has the property the case asserts; then the grader or the threshold, because `REDRAFT_RATIO`
is a tuned number; then the skill or the scripts. Case 3 is the likeliest to be lying, because it
is the only one whose pass condition is a number somebody chose.

Run the scripts' own checks alongside it: `sourced.py`, `claims.py`, `decisions.py`, `boundary.py`,
`shared_claims.py` and `skill_check.py` each take `--self-check`; `sourced_status.py` runs its own when
given no arguments.
