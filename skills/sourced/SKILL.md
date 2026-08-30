---
name: sourced
description: Audit a document, deck, brief or report for claim provenance and emit a .sourced sidecar; re-verify a sidecar's evidence and report what moved; or generate the four-label provenance block from it. Use when the user says "run SOURCED on this", "audit this for claims", "check my sources are still live", "write the provenance block", or invokes /sourced. Also the pre-delivery gate for anything that will be published, presented or relied on.
---

# SOURCED

Seven checks on any artefact containing model output. **S**ourced, **O**pposed, **U**nderwritten,
**R**ecorded, **C**onstrained, **E**valuated, **D**isclosed.

**The seven rules travel inside this skill**, below, so invoking it applies them with nothing
pasted from elsewhere. They also ship as `standing-rules.md`, for when nothing has been invoked.
The rules are the cheap half. **This skill is the expensive half**: it retrieves, hashes and
writes files, so it is invoked deliberately.

## Start here: what followed the verb

Take the **first** row true of the invocation. Never ask the user which mode needs a network or
a script; that is this table's job.

| What followed `/sourced` | Mode | Go to |
|---|---|---|
| Nothing at all | interview | The three questions below |
| A mode word: `audit`, `research`, `check`, `statement`, `tldr` | that mode | That mode's section |
| A path to a file that exists | audit | "Audit", below |
| A question whose output is published or relied on | research | `reference/research-mode.md` |
| A question, or a sentence describing work not done yet | short form | `reference/short-form.md` |
| Anything else | ask one question | "An artefact to audit, or work you are about to do?" |

**If the invocation already names a file or a mode word, run it and ask nothing.** The user has
answered the interview by typing it, and a second question is friction.

**A bare question gets the short form, and never nothing.** Research mode is what a question
**escalates to**, not what it starts as. Take it when the user named an artefact, when the output
goes to someone else, when the decision is hard to reverse, or when they typed `research`.

### The interview

Three questions, **asked one at a time**, each one waiting for its answer. Say the escape in the
first question, so the user knows the interview is optional.

1. **"What are you making?"** Add: *"Say `skip` and I will audit whatever file you point me at."*
   Picks the stage: work not started yet is research, a finished file is audit.
2. **"Who relies on it?"** Picks the ceiling: only you means stop at the audit; a client, an
   audience or a regulator means the statement ships with it.
3. **"What would it cost if a claim were wrong?"** Picks the care: nothing much means audit alone;
   money, a decision or a reputation means run check before it goes out.

On `skip`, or on silence, go straight to audit and say so in one line.

**When the answers conflict, the state of the artefact wins**, because an artefact that does not
exist yet cannot be audited. Route on question 1; questions 2 and 3 decide how far past that mode
to go.

<!-- standing-rules:start -->
## The seven standing rules

They apply to research, analysis, claims-based writing, briefs, decks, and anything that will be
published, presented or relied on. They do not apply to mechanical coding, refactors, config or
tooling, because the scope line is what stops this becoming ceremony on a one-line fix.

- **S**ourced — every load-bearing claim names a source **retrieved this session**, with the
  verbatim sentence and its locator. From memory is **RECALLED**; your own conclusion is
  **INFERRED**; both are legitimate and both must be labelled. Ten write-ups of one press release
  are one source: collapse origin before counting. Say plainly what could not be grounded.
- **O**pposed & Integrated — argue the strongest case against a conclusion before presenting it,
  then build the surviving position, not just the objections. Name the move that
  resolved each: **Conditional** (each holds in a stated region), **Reframe** (both share a hidden
  assumption — **name it**, or it is not a reframe), **Redirect** (the observation is sound, the
  conclusion is not), **Hold** (nothing settles it — name what would, ship open). Splitting the
  difference is a last resort. The requirement is a **fresh thread, explicitly adversarial**, because an
  instance not holding the draft has no commitment to defend it. A different model is an upgrade,
  not the mechanism: it catches shared priors. Record which grade ran and never report a lower
  grade as a higher one. For every claim that stands, state what would make it false.
- **U**nderwritten — never imply a human review makes output correct. A signature buys
  accountability, not accuracy. Where a decision needs a person, say which decision and what they
  would have to verify.
- **R**ecorded — keep the decision log as you go, and log the **state** rather than the story:
  what was retrieved and in context, which options were enumerated, which was chosen, which were
  rejected with one clause each, and which model and version ran. None of that needs
  introspection, so all of it is checkable. A justification is still written, because humans read
  it, and it is labelled as narrative generated at that time, never as cause.
- **C**onstrained — no number without its source, no claims about a named individual, no legal,
  financial or medical conclusions. If a task needs one, stop and say so.
- **E**valuated — anything reusable ships with three test cases, known answers, and a failure
  threshold. Triage a failing eval before believing it: a reported 67% failure was the
  grader, three times running.
- **D**isclosed — a deliverable ships with the four-label provenance block: **Attribution,
  Accountable, Limitations, References**. Attribution carries a fidelity line: model, harness,
  tools, and a version for each, in C2PA's `softwareAgent` shape. No short-form exemption. Every line must either make a limit transparent or let
  the reader go and check something. No `Verified:` label, ever. Limitations passes the decision
  test per sentence: would a reader decide differently knowing this? If not, cut it. A source not
  retrieved, a primary read through a secondary, a small survey base, one sentence each. Never
  padded; `None material.` and `No external sources.` are each complete lines.
  Our own frameworks, estimates, arithmetic and judgement never appear there, not
  even to label them: INFERRED in the sidecar is the whole disclosure. An unfetchable source is "unavailable at the time of retrieval", with the blocked
  URLs listed in the delivery message. References are full APA 7th entries, one per source, in
  alphabetical order by first element, never prose shorthand and never written from memory.
<!-- standing-rules:end -->

## Companion files

Open one when its line is true; never preload them.

| File | Read this when |
|---|---|
| `reference/sidecar-schema.md` | You are writing, extending or validating a `.sourced` file |
| `reference/adversarial-pass.md` | You are running O, or writing the line that says which grade ran |
| `reference/boundary-record.md` | A claim has failed, or holds only conditionally, and needs its boundary |
| `reference/retrieval-ladder.md` | A source is paywalled, dead, moved, or reachable only second-hand |
| `reference/research-mode.md` | The work is not done yet, and you are researching it now |
| `reference/short-form.md` | A question arrived and nobody asked for a paper |
| `reference/provenance-block.md` | You are writing the four-label block or its References list |
| `reference/decision-ledger.md` | You are recording decisions as you work, or folding them in |
| `reference/evals.md` | You have edited this skill and need to re-run its known-answer cases |

## The five modes

| Mode | Invoked by | What it does | Cost |
|---|---|---|---|
| interview | `/sourced` | Ask the three questions above, then route | A minute. Nothing is fetched |
| audit | `/sourced <file>` | Mark each load-bearing claim SOURCED / RECALLED / INFERRED, hash what retrieves, write `<file>.sourced` | Real. It retrieves |
| research | `/sourced research <q>` | Turn the standard on for the work itself: capture each source as it is read | Real. It retrieves |
| check | `/sourced check <file>` | Re-verify the sidecar's evidence and report what moved | Small. It re-reads |
| statement | `/sourced statement <file>` | Generate the four-label block from the sidecar | Seconds. It reads the sidecar |

**Research mode is the behavioural change; the rest is presentation.** Read
`reference/research-mode.md` before the first retrieval. Claims and decisions accrue as they are
made, then fold into the sidecar. `claims.py` refuses a quote absent from the capture, so the
quote and the hash are one retrieval.

## Audit

**Extract the load-bearing claims, not every sentence.** A claim is load-bearing when the
artefact's argument changes if it is wrong: numbers, findings, causal statements, regulatory
assertions, anything a reader would repeat. Mark each SOURCED, RECALLED or INFERRED.

Then run `sourced.py <url> --tier 2` on anything SOURCED, starting at the top of
`reference/retrieval-ladder.md` and recording the rung you land on. Add `--archive` for anything
contested: a snapshot you hold proves only what you say you saw.

**A thin capture is not evidence.** `sourced.py` exits 2 on `THIN`; climb the ladder rather than
cite the page.

Where a claim fails or holds only conditionally, record the boundary:
`reference/boundary-record.md`, plus

    python3 boundary.py <file.sourced>     the boundary card, per claim carrying one

## Check

    python3 sourced.py --check

Re-fetches every captured source and reports `unchanged`, `MOVED`, `VALUE` or `DEAD`. It compares
the **text** hash, not the bytes hash, because a check that cries wolf gets switched off. Run it
**before a delivery**: a claim only hurts you when it is used.

## Statement

The four-label block, **generated from the sidecar rather than written by hand**. Every line
must either make a limit transparent, or let the reader check something. Run `integrate.py`
over the sidecar before the block ships. The rules each label obeys, and the
misses they came from, are in `reference/provenance-block.md`.

## The tools

Open one when its line is true. **Most of these hold O, not S.** Capturing sources is the
visible half of the work and the easy half to stop at; the rest is where an argument becomes
a position somebody can use.

| Run this | When |
|---|---|
| `conflicts.py` | Two sources disagree. It opens the conflict, and closes it into a boundary or ships it open |
| `boundary.py` | A claim failed, or holds only in some region. Records where it holds, where it fails, what is true instead |
| `dimensions.py` | A source held under conditions worth naming. Builds the registry those conditions accrete into |
| `sophistication.py` | Two statements are the same claim at different depths, and should be siblings rather than rivals |
| `kinds.py` | A claim is a stance or a piece of lived experience, not an empirical claim |
| `integrate.py` | Before any statement ships. Refuses a delivery that hides a disagreement |
| `shared_claims.py` | This claim also appears in another artefact. Do they still agree? |

## The adversarial pass

**O always runs in some grade, and the disclosure says which one.** Take the best grade this host
offers: `cross-model-fresh-thread`, `same-model-fresh-thread`, or `same-thread-self-challenge`.
Where no fresh thread can be spawned, emit the handoff block from `reference/adversarial-pass.md`
so the user can run it by hand. **Never report a lower grade as a higher one**, and where nothing
ran, record `not-performed` and disclose it. The grade lands in the optional `opposed` object on
the sidecar (sourced 1.2), and `decisions.py validate()` refuses an unknown grade.

**Ask the pass for a map, never for a verdict.** Whichever grade runs, in a sub-agent or by hand,
the instruction is the same: for every disagreement, name the conditions each side held under and
say where each is right. Never ask which claim survived, which is stronger, or which to keep. What
comes back is conflict and boundary records, in the shapes `reference/adversarial-pass.md` sets
out, so the sidecar absorbs them directly.

## The gate before a statement ships

    python3 integrate.py <file.sourced>    refuse a delivery that hides a disagreement

`integrate.py` holds O: a conflict recorded in the sidecar and absent from the delivery is a
disagreement the reader never gets to see. What it refuses, and why, is in
`reference/provenance-block.md`.

D needs no gate. A claim's `kind` decides where it is disclosed: `position` and `story` are
evidence-exempt, disclosed as INFERRED in the sidecar, so they never reach Limitations.

## What this skill will not do

- **It will not claim verification it did not perform.** A source that could not be retrieved is
  a limitation, never a silence.
- **It will not judge whether the work is any good.** Provenance and quality are different
  questions, and conflating them makes governance a matter of taste.
- **It will not retro-audit a back catalogue unasked.** That needs its own scoping.

## Evaluating the skill

`python3 evals.py`, three cases with known answers. Re-run after any edit, with every script's
own `--self-check`.
