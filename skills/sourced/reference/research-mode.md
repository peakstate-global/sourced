# Research mode

Read this when the work has not been done yet: `/sourced research <question>`.

The other modes run over a finished artefact. This one runs alongside the work, because on a real
run on 27 August 2026 the evidence was captured hours after the reasoning that rested on it. The
quote in the sidecar came from one retrieval and the hash beside it came from another. Nothing in
the artefact showed it, and it is not sound.

The whole mode is one idea: **the quote you keep is read out of the capture, never out of the live
page.** Everything below exists to make that the path of least effort.

---

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

i) Write the artefact. The claims are already in the ledger, so this is drafting, not recall.
ii) Create the sidecar manifest if one does not exist: `$schema`, `sourced`, `artefact`, empty
    `claims` and `evidence`, and `disclosure` (`reference/sidecar-schema.md`).
iii) Fold both ledgers:

        python3 claims.py fold <artefact>
        python3 decisions.py fold <artefact>

    Folding twice is safe. A record replaces the entry with its id rather than adding a second one.
iv) Run the adversarial pass over what the ledgers now say, and record the boundary of any claim
    that fails or holds only conditionally (`reference/boundary-record.md`).
v) **State the integrated position.** The pass returns a map: conflicts, boundaries, claims that
   hold in one region and fail in another. That is the material, not the answer. Write the view
   that holds the surviving parts together, say which conditions it depends on, and say what
   would change it. Nothing upstream does this for you: the ledgers record disagreement
   faithfully and will happily ship a stack of conditioned fragments with no position in them.
   The test is whether the position changes what a reader would do, expect or watch for. If the
   answer is the same whichever side was right, nothing has been integrated.
vi) Re-verify before delivery: `python3 sourced.py --check`. A claim only hurts you at the moment it
   is used.
vii) Generate the provenance block from the sidecar: `/sourced statement <artefact>`.

## What this mode does not do

- **It does not remember the standard is on.** Nothing polls, nothing hooks the fetch. If a
  retrieval goes around `sourced.py`, the claim resting on it is refused at append time, which is
  where it becomes visible.
- **It does not judge the claim.** It records that the quote is in the capture. Whether the quote
  supports the statement is your reading, and the statement is what a reviewer argues with.
- **It does not bind step 0 to anything.** A first-time user with no prior corpus runs this mode
  exactly as written, minus one line of output.
