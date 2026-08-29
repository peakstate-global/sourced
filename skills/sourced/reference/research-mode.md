# Research mode

Read this when the work has not been done yet: `/sourced research <question>`.

The other modes run over a finished artefact. This one runs alongside the work, because on a real
run on 27 August 2026 the evidence was captured hours after the reasoning that rested on it. The
quote in the sidecar came from one retrieval and the hash beside it came from another. Nothing in
the artefact showed it, and it is not sound.

The whole mode is one idea: **the quote you keep is read out of the capture, never out of the live
page.** Everything below exists to make that the path of least effort.

---

## First. Sharpen the question

**Do this before Step 0, and before spending a single retrieval.** A contested question almost
never contains one claim. It contains several, wearing one word, and which of them you meant
decides whether the answer is yes, no, or nobody has measured it.

Four moves, in order. They take one pass and no network.

i) **Name the word doing hidden work.** Look for one word covering two mechanisms. "Decline",
   "growth", "throughput", "works", "safe", "better". Where a word carries two meanings that the
   evidence treats differently, the question has two answers and you have not yet chosen which one
   you are answering.
ii) **Split the question into separately testable propositions.** Each one has to be a thing
   evidence could bear on by itself. Three or four is usual. One is possible and is worth saying
   out loud, because a question that really does have one part is unusual.
iii) **Say what kind of claim each proposition is.** Empirical, definitional, predictive or
   normative. This matters more than it looks: **a normative proposition cannot be settled by
   retrieval.** "Should growth be subordinated to ecological limits" contains a biophysical claim
   that evidence settles, and a priority claim that it does not. Naming that early stops the run
   answering the easy half and presenting it as the whole.
iv) **State the split in one short block, then keep going.** Do not wait for approval. The user
    asked a question, not for an interview.

**Stop and ask only when the split changes what would be researched.** Two readings that need
different sources, or a reading you suspect the user did not mean, are worth one question before
fifteen retrievals go the wrong way. Anything else is friction, and the grilling rule applies: if
you can settle it by reading, reading is the answer.

**This block is not scaffolding. It is the artefact's first section**, "What is actually being
claimed", and it is the row labels of the verdict table further down. Write it once, here, and it
carries through to delivery.

Why it sits before everything: on a run on 29 August 2026 the word "throughput" turned out to be
covering several separate physical pressures with no single dial behind them. That was found by the
adversarial pass, after every retrieval was already spent, and four synthesis claims had to be
rewritten around it. The same run's sibling found its three readings at the start, and the split
became the most useful thing in the paper.

## Step 0. Check what you already hold

Before retrieving anything new, check what you already hold on this question.

This step is declared, not implemented. It runs whatever the local configuration binds it to: a
private corpus, a notes vault, a team's prior work, a search over an earlier run's captures.
**Where nothing is configured, the step degrades to nothing and the run continues.** Say in one
line which it was, so the reader knows whether prior work was consulted or was simply unavailable.

Nothing in this repo binds it, and nothing here names a knowledge base to bind it to. How any one
team runs this step is a local decision, not part of the standard (`docs/philosophy.md`, section 4).

## Step 1. Open the ledgers

Do this once, at the start, before the first retrieval.

i) Choose the artefact path now, even though the artefact does not exist yet. Everything is named
   after it: `<artefact>.claims.jsonl`, `<artefact>.decisions.jsonl`, `<artefact>.sourced`.
ii) Say in one line that the standard is on, and name that path.
iii) Confirm the store: `SOURCED_ROOT`, `SOURCED_STORE`, or `--store DIR` on each capture. Captures
    written to two different stores cannot be folded into one sidecar.

There is no state file and no session to start. The ledgers are created by the first append, which
is why turning the standard on costs one line rather than a command.

## Step 2. The loop, once per source

Run this for **every** source you read, in this order, with nothing between the retrieval and the
quote.

1. **Retrieve through capture, never with a bare fetch.**

       python3 sourced.py <url> --tier 2

   Add `--archive` when the claim might be contested, so an independent party holds a dated copy.
   Add `--condition "dimension=value:basis"`, repeatable, for each condition the source held
   under: `--condition "air quality=clean:observed"`. Record them here or not at all, because
   this is the only moment they are in front of you, and the capture prints whether each
   dimension is new, known, or a probable duplicate of one you already use. `basis` is one of
   `tested`, `replicated`, `observed`, `untested`, `inferred`. Skipping them is allowed.
   A bare fetch hashes one retrieval and leaves you to quote from another, and that is the exact
   defect this mode exists to remove. There is no case where the bare fetch is quicker: the capture
   is the fetch, plus a hash and a file.

2. **If the capture exits 2, stop and climb down.** Exit status 2 means `THIN`: the fetch got the
   navigation shell and the body never arrived. The hash is real and the evidence is not there. Go
   to `reference/retrieval-ladder.md`, drop one rung, and capture again at that rung. **Do not cite
   the page.** Do not paste the quote from what you can see in the browser, because that quote did
   not come from the bytes you hashed.

3. **Read the quote out of the captured text file.** The row's `text` field names it, under the
   store's dated folder. Open that file and take the verbatim sentence from it. This is the
   mechanism, not a formality: the quote and the hash are the same retrieval only because the quote
   was read out of what the hash was taken over. A quote retyped from the live page is a different
   retrieval that happens to look the same.

4. **Append the claim as you make it.**

       python3 claims.py append <artefact> --statement "…" --url <url> --quote "…" \
           --locator "p. 12" --origin <origin-group>

   The script refuses the claim when the URL was never captured, and refuses it again when the
   quote is not in that capture's text file. A refusal is not an obstacle to route around; it is
   the check working. Fix the quote or climb the ladder.

   Add `--falsifier "…"` whenever you can already say what observation would kill the claim.
   Record it here, not at the end: a falsifier written after the pass is written to fit the claim
   that survived, and every claim that survives the pass needs one.

   A claim with no source is appended too, with `--status recalled` or `--status inferred` and no
   URL. What you could not ground has to be visible while the work happens, or it gets counted as
   sourced at the end by nobody's decision.

5. **Record which claim the source votes on, and which way.** The evidence row carries
   `supports`, and you fill it in, not the user:

       "supports": { "claim": "c1", "direction": "for",
                     "by": "model", "model": "<your model name>" }

   `direction` is `for` when the source backs the claim and `against` when it cuts against
   it. Always set `by` to `model` and always name yourself in `model`, because you proposed
   this and a person has not confirmed it yet. Decide it here, while the source is still in
   front of you, and write it onto the row as the ledger folds into the sidecar.

   **A source that bears on no claim yet simply has no `supports`.** Leave the field out.
   Guessing a claim id that does not exist is worse than leaving it out: an id that resolves
   to nothing quietly removes the row from every conflict the tools could have found.

   **You propose and you never decide.** `conflicts.py` reads opposition off this field, and
   `integrate.py` refuses on the recorded field rather than on anything inferred. So a wrong
   proposal is a visible wrong row somebody can fix, where a wrong verdict would be
   invisible. `integrate.py` flags a conflict whose two sides are both model-proposed, so the
   author knows which ones nobody has confirmed.

6. **Append the decision when the source changed what you were going to do.** Not every source is a
   decision. When one closes an option off, record it while the option is still in mind:

       python3 decisions.py append <artefact> --option A --option B --chose A \
           --reject "B: one clause" --context <evidence-id> --model … --model-version …

   See `reference/decision-ledger.md` for what a record must carry and what it must not.

## Step 3. Close the work

i) Write the artefact, to the shape in `## The shape of the paper` below. The claims are
   already in the ledger, so this is drafting, not recall.
ii) Create the sidecar manifest if one does not exist: `$schema`, `sourced`, `artefact`, empty
    `claims` and `evidence`, and `disclosure` (`reference/sidecar-schema.md`).
iii) Fold both ledgers:

        python3 claims.py fold <artefact>
        python3 decisions.py fold <artefact>

    Folding twice is safe. A record replaces the entry with its id rather than adding a second one.
iv) Run the adversarial pass over what the ledgers now say, and record the boundary of any claim
    that fails or holds only conditionally (`reference/boundary-record.md`). **A conflict you
    cannot close ships open**, with its unknown region named and a sentence in Limitations saying
    who disagrees about what: `python3 conflicts.py <file.sourced>` writes that sentence for you.
    Never close a conflict to get past the gate. An invented resolution is the failure this whole
    standard exists to prevent, and `integrate.py` passes a disclosed open conflict.
v) **State the integrated position.** The pass returns a map: conflicts, boundaries, claims that
   hold in one region and fail in another. That is the material, not the answer. Write the view
   that holds the surviving parts together, say which conditions it depends on, and say what
   would change it. Nothing upstream does this for you: the ledgers record disagreement
   faithfully and will happily ship a stack of conditioned fragments with no position in them.
   The test is whether the position changes what a reader would do, expect or watch for. If the
   answer is the same whichever side was right, nothing has been integrated.
vi) Write the dimension definitions the boundaries use into the sidecar:

        python3 dimensions.py --sidecar <artefact>.sourced

    It lists any dimension nobody has defined. A dimension named but undefined means a
    boundary a reader cannot apply, because "holds when severity is high" only travels if
    `severity` says what it is measured with. This runs after the boundaries exist, which is
    why it is here and not at capture.
vii) Re-verify before delivery: `python3 sourced.py --check`. A claim only hurts you at the moment it
   is used.
viii) Generate the provenance block from the sidecar: `/sourced statement <artefact>`.

## The shape of the paper

Eight parts. **Four are required**, and a paper missing one of those is not finished. Four are
recommended, and a paper may drop one by saying in a clause why the evidence did not produce it.
The order is the argument's own logic, not a template to fill in.

1. **The title is the question, not the answer.** Required. A reader who disagrees has to get past
   the title before they can be persuaded by anything under it.
2. **What is actually being claimed.** Required. The block you already wrote in `First. Sharpen the
   question`, brought forward.
3. **The verdict table.** Required, and it goes **before** the argument, not after. One row per
   proposition, so the reader knows where they stand before being asked to follow anything.
4. **One section per proposition**, in table order, each closing with the observation that would
   falsify it. Required.
5. **What the strongest opposition did to this.** Recommended. Not "counter-arguments considered":
   what the adversarial pass changed, including the claims of yours that died.
6. **The one place the evidence points the other way.** Recommended. The strongest fact against
   your own conclusion, conceded in its own section rather than buried in a subordinate clause.
7. **The integrated position, and what it changes.** Required. Step 3(v), written as a section.
8. **What a person would actually have to decide.** Recommended. Routes different readers to
   different actions, which is what makes a paper usable rather than admirable.

Then the provenance block, unchanged.

### The verdict table

**Generate it, do not write it:**

    python3 boundary.py table <artefact>.sourced

It reads every claim carrying a boundary, plus every claim under an open conflict, and prints the
markdown. Paste it in. A row you disagree with is a boundary recorded wrongly, and the fix is
`boundary.py`, not the sentence.

Give each claim a short `reading` and that is what the first column shows. Without one the whole
statement goes in the cell, and a paragraph in a table cell is the sign that the question was never
split.

Three columns at minimum: the proposition, the verdict, and the region it holds or fails in. A
fourth column for the evidence in a few words earns its place on most subjects.

| Reading of the claim | Verdict | Where |
|---|---|---|
| Share of official reserve stocks | Holds | Fell slowly over 14 years, and continues |
| Share of transaction flows | Falsified | Rose over the same period |
| Exchange value | Holds narrowly | Direction supported, the rate is not |

**The verdict word comes from this list and nowhere else.** One word, one meaning, so that two
papers can be read side by side and a verdict means the same thing in both.

| Verdict | Means | Carried in the sidecar by |
|---|---|---|
| `Holds` | Supported by retrieved evidence, within a stated region | `holds_when` |
| `Holds narrowly` | Survives only in a named region, and fails outside it | `holds_when` and `fails_when` |
| `Falsified` | The evidence contradicts it | `fails_when` and `replaced_by` |
| `Unevaluated` | Nobody has measured it, which is not the same as false | `unknown_region` |
| `Contested` | Sources disagree and the conflict is open | an open `conflicts` record |

Do not invent a sixth. "Promising but thin", "not established, not refuted" and "attempted
unresolved" all say something real, and all of them belong in the `Where` column, which is free
text and exists for exactly that.

**Every verdict is derivable from fields the sidecar already holds**, which is the point: the table
is a reading of the ledger, not a second opinion about it. A row whose verdict you cannot trace to
one of those fields means the boundary was never recorded, and the fix is `boundary.py`, not a
better adjective.

## What this mode does not do

- **It does not remember the standard is on.** Nothing polls, nothing hooks the fetch. If a
  retrieval goes around `sourced.py`, the claim resting on it is refused at append time, which is
  where it becomes visible.
- **It does not judge the claim.** It records that the quote is in the capture. Whether the quote
  supports the statement is your reading, and the statement is what a reviewer argues with.
- **It does not bind step 0 to anything.** A first-time user with no prior corpus runs this mode
  exactly as written, minus one line of output.
