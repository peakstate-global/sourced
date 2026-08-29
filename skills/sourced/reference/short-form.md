# Short form

Read this when a question arrived inside other work and nobody asked for a paper.

Most questions do not want twenty minutes and four files. They arrive mid-task, the answer is
wanted in the next minute, and the person will act on it inside something they were already doing.
**The short form is the default for a bare question**, and research mode is what a question
escalates to, not what it starts as.

The one thing this mode exists to prevent: the gap between an unlabelled opinion and a full
research pass. Left unbridged, almost every question takes the unlabelled route, and the standard
applies to none of them.

## The card

Five parts. Four are required. This is the paper's shape with four of its eight parts collapsed,
so the two forms teach one structure and a card escalates into a paper without redoing the
thinking.

i) **Bottom line.** Required. One sentence, the integrated position. Not a summary of the debate,
   and not "it depends".
ii) **Where it holds and where it fails.** Required. Two to four rows: the reading, the verdict
    from the closed list in `research-mode.md`, and why in a few words. This is the verdict table
    with the region column folded into the last column. Sharpen the question first
    (`research-mode.md`, `First. Sharpen the question`): the propositions are the rows.
iii) **Provenance, inline.** Required. One line of counts, not prose: how many claims are SOURCED
     and from where, how many RECALLED, how many INFERRED, **and what was not done.** "No
     adversarial pass" is a complete disclosure and costs four words. So is "no captures kept".
iv) **What would change it.** Required. One observation, specific enough that a reader could go
    and check it.
v) **Escalation.** Recommended. One line naming what a full pass would add and roughly what it
   costs, so the reader decides whether to spend rather than having the decision made for them.

**Two things survive the compression and everything else may go.** The labels, because an
unlabelled quick take is indistinguishable from an opinion, and the S rule exists precisely for the
cheap end of the range. And the falsifier, because it is the cheapest available signal that the
answer is not being defended. Drop the mechanism, the references, the four-label block, the
regions. A card without SOURCED / RECALLED / INFERRED counts is not a SOURCED output and must not
be presented as one.

## Capture anyway

**Retrieve through `sourced.py`, exactly as research mode does.** The capture is the fetch plus a
hash and a file, so it is not the slower path, and quoting off the live page is the one defect this
whole standard exists to remove. A cheap mode is cheap because it writes no ledger and no sidecar,
not because it skips the capture.

What the short form does **not** do: open `claims.jsonl` or `decisions.jsonl`, fold a sidecar, run
the adversarial pass, or generate a provenance block. Those are what make research mode cost twenty
minutes, and they are what the card is trading away.

Where no store is configured and capture is genuinely unavailable, say `no captures kept` in the
provenance line and carry on. A stated limit is a finding. A silent one is the failure.

## The three tiers

| Tier | Cost | Retrievals | Writes | Use when |
|---|---|---|---|---|
| Recalled answer | Seconds | 0 | Nothing | Orientation, and the whole answer is marked RECALLED |
| The card | 2 to 3 minutes | 2 to 5 | Captures only | A real question inside other work, and a reversible decision |
| Research mode | 20 to 30 minutes | 15 to 30 | Ledgers, sidecar, paper | It will be published, presented, relied on, or is expensive to get wrong |

**A recalled answer is legitimate and is not this mode's enemy.** What is not legitimate is a
recalled answer that reads like a retrieved one. If the whole answer comes from memory, say so in
the first clause and stop there.

## Worked example

> **Bottom line.** "The dollar declines" is three claims in one word, and over the last fourteen
> years they moved in opposite directions, so the sentence is true, false or unmeasured depending
> on which one was meant.
>
> | Reading | Verdict | Why |
> |---|---|---|
> | Share of official reserves | Holds | Fell slowly, about 57% now |
> | Share of transaction flows | Falsified | Rose, 88.4% to 89.2% |
> | Exchange value | Holds narrowly | Direction yes, "slowly" unsupported |
>
> **Provenance.** 3 SOURCED (IMF COFER, BIS Triennial, Federal Reserve, captured today), 1
> INFERRED (the extrapolation band), 0 RECALLED. No adversarial pass.
>
> **Would change it.** The 2028 BIS Triennial showing the dollar below 85% of turnover.
>
> **Escalation.** A full pass adds the cross-model challenge, the transmission channels and a
> checkable sidecar: about twenty minutes and fifteen retrievals.
