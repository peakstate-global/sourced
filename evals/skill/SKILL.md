---
name: sourced-eval
description: Run one round of the SOURCED eval suite — stamp the version under test, run every frozen topic through /sourced research in its own fresh thread, measure which features actually ran, score the results with two independent graders, and record the round. Use when the user says "run a round", "sourced eval", "run the evals", or invokes /sourced-eval.
---

# One eval round

**The whole value of this skill is that nothing drifts between rounds.** A round whose prompt,
rubric or topics moved is not comparable to the one before it, and a ledger of incomparable rounds
is a scrapbook. So the procedure is written down, and the four frozen files are read rather than
rewritten.

Repository layout, and which half is which:

| Where | What |
|---|---|
| `evals/` in this repo | The instrument. Public. Topics, prompt, rubric, features, `round.py` |
| `$SOURCED_EVAL_DIR` | The measurements. One folder per round, plus `LEDGER.md` |

Set `SOURCED_EVAL_DIR` to wherever the rounds are kept. Keeping them outside this repository is
the sane default: an artefact produced by a round is working material, and publishing it invites
the next round to be written towards the last one.

## Step 1. Pre-flight, and stop if it fails

    cd skills/sourced
    for m in sourced claims decisions boundary shared_claims sophistication kinds \
             dimensions conflicts integrate vocabulary skill_check; do
      python3 $m.py --self-check >/dev/null || echo "FAIL $m"; done
    python3 evals.py >/dev/null && echo "unit evals pass"
    python3 ../../evals/round.py --self-check

**A red pre-flight stops the round.** Scoring a skill whose own checkers are failing measures the
break, not the skill.

## Step 2. Commit the skill, then stamp

The stamp must describe the code that ran, so the commit comes first. `round.py new` refuses a
dirty tree, and `--allow-dirty` writes a loud line into the report rather than a quiet one.

    git status --short                                  # expect empty
    python3 evals/round.py new "$SOURCED_EVAL_DIR/rounds/round-NN"

That writes `manifest.json` with the commit hash, whether it is pushed, whether the tree was
dirty, a hash of the skill tree itself, and the four version numbers. If
`$SOURCED_EVAL_DIR/overlay.md` exists and is not empty, its text is appended to every run prompt
and the manifest records that it applied plus a hash of it. **Never report a relaxed run as a
strict one**: the hash is what lets a reader tell them apart. It also scaffolds one
directory per topic, each holding `prompt.txt` and a `bin/python3` shim that logs what the run
invokes.

**Never re-stamp an existing round.** A round is a measurement of a moment.

## Step 3. Run every topic, in parallel, in fresh threads

One `Agent` call per topic, all in one message so they run concurrently, `run_in_background: true`.
The prompt is the contents of that topic's `prompt.txt`, pasted verbatim. Add nothing.

**Three things that are easy to lose and carry the whole result:**

- **The agents are blind to the rubric.** Never paste a criterion, a weight or a past
  recommendation into a run. An agent given the marking guide writes to it, and the round then
  measures the prompt.
- **The prompt is verbatim.** Not summarised, not improved, not adjusted for a topic that seems
  to need it. If it needs a change, the change bumps `promptVersion` and applies to every future
  round.
- **A refusal is a result.** If a run stops, records that it will not proceed, or returns less
  than asked, record what it did and score it. Do not re-run it with a softer prompt.

Expect 25 to 40 minutes wall clock. Tell the user the predicted finish time in the same message
that launches them.

## Step 4. Measure coverage from disk

    for t in <topic ids>; do
      python3 evals/round.py coverage "$SOURCED_EVAL_DIR/rounds/round-NN/runs/$t"
    done

**Do not ask the agents what they used.** An agent's account of its own process is an
introspective claim, and this framework does not take those on trust. Coverage reads the artefacts
and the run log. Seven reference documents have no objective signal and are reported separately as
not instrumented, never counted as unused.

## Step 5. Score, twice, independently

One scorer per topic per grader, fresh threads, in parallel.

- **Claude**, via `Agent` on Opus.
- **Codex**, via the `codex` subagent. Probe `codex-available` first; non-zero goes to
  `adversarial-reviewer` and the report names which grader ran. A fallback is never written up as
  a cross-model pass.

Each grader receives: the artefact, its sidecar, and `rubric.md`. Each grader receives **nothing
else** — no prior round, no recommendation from last time, no coverage table. A grader who has
seen the fix grades toward it.

Record every criterion from both graders in `scores.json`, **including the disagreements, which
are never averaged.** A split score is the most informative output of the round.

Every criterion scored 0 or 1 carries a one-line triage naming what is at fault, in order: the
topic, then the rubric, then the skill.

## Step 6. Write the round up

`REPORT.md` in the round folder, in this order:

i) **Verdict.** One paragraph. What this round shows, honestly. "No movement" is an answer.
ii) **Coverage.** The table, by group. The integration group is the headline number.
iii) **Scores.** Per topic, per criterion, both graders, disagreements called out.
iv) **What changed since the last round**, from `CHANGES.md`, and whether the scores moved with it.
v) **Recommendations.** What to change in the skill, and what to change in the rubric. Keep them
   separate: a round that improved the ruler and a round that improved the skill are different
   events and the ledger has to tell them apart.

Then one line appended to `LEDGER.md`, and `python3 round.py compare` to check the trend reads
correctly. Commit the round folder wherever the measurements are kept.

## What this skill will not do

- **It will not change a frozen file to make a round work.** Topics, prompt, rubric and features
  are read-only during a round. Change them between rounds, with the version bumped.
- **It will not re-run a topic that scored badly.** The bad score is the measurement.
- **It will not report a fallback grader as a cross-model pass.**
