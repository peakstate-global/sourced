# The eval suite

**Can this framework push a polarised question to an integrated answer?** That is the only thing
this suite measures, and it measures it by running the skill for real rather than by asking it.

The **E** rule requires anything reusable to ship with test cases, known answers and a failure
threshold. `skills/sourced/evals.py` does that at the unit level, without a network, and it proves
the mechanisms work. It cannot tell you whether the skill produces good work, because a script
cannot run a model on a hard question. This suite is the other half.

## How a round works

Four frozen claims, four fresh sub-agent threads, each running `/sourced research` blind to the
rubric. Then coverage is generated from what is on disk, two graders score independently, and the
round is recorded against the exact version of the skill that produced it.

    python3 evals/round.py new <round-dir>       stamp the manifest, scaffold the runs
    python3 evals/round.py coverage <run-dir>    which features actually ran
    python3 evals/round.py compare <rounds-dir>  the trend
    python3 evals/round.py --self-check          seven cases, known answers, no network

The procedure is in `evals/skill/`, so a round runs the same way every time.

## The four files that must not drift

| File | Why it is frozen |
|---|---|
| `topics.json` | A reworded question breaks every comparison in the ledger. A changed claim gets a new id; nothing is ever edited or retired. |
| `run-prompt.md` | Byte-identical every round. A drifting prompt measures the prompt. |
| `rubric.md` | Frozen **before** any skill edit, so the commit order shows the criteria were not written to flatter the skill. |
| `features.json` | Coverage is only meaningful against a fixed list. |

## Two design choices worth arguing with

**Coverage is generated, never reported.** Nothing asks the agent which features it used. An
agent's account of its own process is an introspective claim, which is the one kind of claim this
framework refuses to take on trust. `round.py coverage` reads the artefacts on disk and the tool
calls in the transcript, and prefers the disk where they disagree.

**Graders disagree in public.** Two models score independently and their disagreements are
recorded per criterion rather than averaged. A split score is the most informative thing a round
produces: either the criterion is ambiguous or one grader can see something the other cannot.

## What this does not show

It does not show that SOURCED improves real work, only that a run under it reaches a certain
standard on four questions we chose. Four cases is a start, not a suite. The topics are ours, the
rubric is ours, and one of the two graders shares a model family with the runs it scores.

The rounds themselves are not published here. This repository holds the instrument; the
measurements are private working material.

## Triage before belief

Any criterion scored 0 or 1 gets a one-line triage naming what is at fault, in order: the topic,
then the rubric, then the skill. This suite's predecessor reported a 67 per cent failure rate on
its first day and every one of those failures was in the measuring instrument.
