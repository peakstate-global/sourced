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
iv) Run the adversarial pass **in the foreground**, over what the ledgers now say. A
    backgrounded pass in round 03 stalled on stdin at startup and returned 26 minutes
    after the run had finished, written into a directory that had already been measured.
    Run it and wait for it., and record the boundary of any claim
    that fails or holds only conditionally (`reference/boundary-record.md`). **A claim the pass
    itself writes carries the same work as the claim it replaces**: a `falsifier` and a region.
    Mark it `"origin": "adversarial"`. `integrate.py` refuses a promoted rival claim that carries
    neither, because a claim holding the position is the least externally checkable thing in the
    sidecar and the last one that should be exempt. **A conflict you
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

    **`integrate.py` now refuses a delivery whose boundaries name a dimension nobody
    defined**, so this is a gate and not a suggestion. It was a named step through rounds
    01 and 02 and ran in none of the eight runs: a step nothing refuses on is not a step.
    It lists any dimension nobody has defined. A dimension named but undefined means a
    boundary a reader cannot apply, because "holds when severity is high" only travels if
    `severity` says what it is measured with. This runs after the boundaries exist, which is
    why it is here and not at capture.
vii) Record what was actually done to each claim, and read the assurance back:

        python3 underwrite.py <artefact>.sourced

    Each claim carries `underwriting`, a list of acts with the actor on each: which tool
    checked the quote, which model challenged it, which person read it. **The assurance
    level is derived from the acts and is never asserted**, so a reader can disagree with
    it only by disputing an act.

    **Do not write `expert-reviewed` because a model decided to.** A signature nobody
    signed is worth less than an honest A1. If no person read the claim, the level says so,
    and the provenance block says so, which is the whole of the U rule made checkable.

    Whether a level is *sufficient* is a policy question and the policy belongs to whoever
    carries the risk. `--policy` takes theirs; the built-in default is deliberately thin.

viii) Re-verify before delivery: `python3 sourced.py --check`. A claim only hurts you at the moment it
   is used.
ix) Generate the provenance block from the sidecar: `/sourced statement <artefact>`.

## The shape of the paper

**The spine is fixed. The argument inside it is not.** The parts below appear in this order under
these names, because a reader who has read one of these papers should be able to navigate the next
one without learning a new layout. What varies is how many proposition sections there are, and what
they say.

An earlier version of this file said the order was "the argument's own logic, not a template to
fill in". That instinct was right about the argument and wrong about the furniture: four round-02
papers on four subjects produced the same spine in four different orders under four different
names, which helped nobody.

| # | Heading | |
|---|---|---|
| - | The question, as the title | **Required** |
| 1 | What is actually being claimed | **Required** |
| 2 | The verdict table | **Required** |
| 3...n | One section per proposition, in table order, labelled `P1`...`Pn` | **Required** |
| n+1 | What the strongest opposition did to this | Recommended |
| n+2 | The one place the evidence points the other way | Recommended |
| n+3 | The integrated position, and what it changes | **Required** |
| n+4 | Where this is going | **Required** |
| n+5 | What a person would actually have to decide | Recommended |
| n+6 | Provenance | **Required** |

A recommended part may be dropped by saying in a clause why the evidence did not produce it. A
required part may not. **Opposition always precedes the concession**: what the pass did to you is
the context for the fact you are about to concede.

**1. The title is the question, not the answer.** A reader who disagrees has to get past the title
before they can be persuaded by anything under it.

**2. What is actually being claimed.** Brought forward from `First. Sharpen the question`. Two
sub-parts, in this order, both required.

**`### Definitions`.** Not the technical terms: the *contested* ones, the words two sides of the
argument use differently. Round 02 found one in every subject it touched, and in every case the
disagreement turned out to be partly about the word.

**Say what the words mean here. Never tell the reader their usage is wrong.** The section describes
this paper's vocabulary, not the field's. A definition good enough to borrow travels on its own; an
instruction to change how somebody speaks seeds resistance in exactly the reader you most want to
persuade. So every line reads *in this paper*, and the reader is free to keep their own words.

Two subsections, in this order:

- **`#### Terms not used here`** — one line each, no properties. The term, the term this paper uses
  instead, and one sentence on why. Then the paper never discusses it again. Keep this short: it is
  a signpost, not an argument.

      **Victimhood** -> **perceived agency**
      Judges the person rather than describing something measurable, and reads as an accusation to
      anyone who was in fact wronged.

- **`#### Terms used here`** — the full blocks, for terms the paper actually uses. A block never
  mixes a retired term with its replacement: once the paper has moved to a better word, the block
  is about the better word. Mixing the two is what made these unreadable before.

      **Perceived agency.** [judgement-free]
      - **In this paper** — how far a person sees the outcomes in their life as following from
        what they do.
      - **Measured by** — established self-report scales.
      - **Propositions it divides** — P5, P7.

  Bullets, indented, one property per line. `Propositions it divides` names the propositions the
  distinction separates from each other, so a definition that divides nothing gets cut.

**Every defined term names its family.** Six, and each names the condition the word is in, so the
tag is a diagnosis an author can check rather than an instruction they have to derive.

| Family | The word is… | So the paper… | The line it uses |
|---|---|---|---|
| `umbrella` | a cover for several kinds of itself — take one part and you still have the thing | names the kind wherever a claim rests on one, and keeps the umbrella for the family | **Comprises** |
| `compound` | made of parts all required at once — take one away and the word says nothing | gives every part, every time | **Compounds** |
| `overloaded` | one spelling carrying two unrelated meanings | retires it, and uses a separate word for each meaning | **Means, in the debate** |
| `unmeasured` | naming something nobody has measured | says what is missing **first**, then what was measured instead, and why they are not the same | **Gap** |
| `imprecise` | vague where an exact term already exists | uses the exact one | **Exactly** |
| `judgement` | saying what *ought* to be, not what is | answers the factual half and does not dress the rest as a finding | **Not settled by evidence** |
| `specific` | one named thing that the debate discusses in general | says so, and never lets evidence about the general stand in for the specific | **Is one of** |

**`specific` is the mirror of `umbrella`**, and round 04 found it by minting a label for it: a paper
needed to say "Core Energetics is one named method, not the family", because evidence gathered on
the family was being read as evidence about the method. An umbrella term is too broad for the claim;
a specific term is narrower than the evidence offered for it. Both are a mismatch of scope and they
fail in opposite directions.

**Umbrella against compound, in one question:** *can you take one part and still have the thing?*
Calming work on its own is still somatic practice — umbrella. A likelihood on its own is not a risk
— compound. The consequence differs, which is why they are separate families: an umbrella term
stays usable bare, a compound term never is.

**A word with a measurable neighbour is not a judgement.** *Victimhood* looks like one and is not:
*perceived agency* measures the same thing without the verdict, so victimhood is set aside as
`imprecise` and the measurable term gets the block. `judgement` is only for a word with no such
neighbour — the bare *ought*, as in "growth **should** be subordinated to ecological limits".

**`### The propositions`** — the claim broken into statements evidence can bear on separately,
**enumerated and labelled `P1`…`Pn`**, each carrying its kind: empirical, definitional, predictive
or normative. A normative proposition cannot be settled by retrieval, and saying so here is what
stops a run answering the easy half and presenting it as the whole.

**Counting them is not listing them.** A round-02 paper wrote "that gives eight separately testable
propositions" and never enumerated them, which left its own verdict table unmappable.

**A proposition is a claim.** It has the same shape as any other — a statement, a verdict,
conditions, a falsifier — and the only differences are that it comes from decomposing the question
rather than from the evidence, and that other claims hang off it. So it lives in `claims[]` with
`role: "proposition"`, and the claims that answer it carry `answers: "<its id>"`. There is no
separate structure, because two homes for one truth is how they drift apart.

**3. The verdict table.** Before the argument, never after. See below.

**4. One section per proposition**, in table order, each headed with its label and closing with the
observation that would falsify it: `## P3. Core Energetics itself has no controlled evidence`.

**5. What the strongest opposition did to this.** Not "counter-arguments considered": what the
adversarial pass changed, including the claims of yours that died.

**6. The one place the evidence points the other way.** The strongest fact against your own
conclusion, conceded in its own section rather than buried in a subordinate clause.

**7. The integrated position, and what it changes.** Step 3(v), written as a section.

**8. Where this is going.** Required. Three elements, all of them:

- **The expectation.** What you expect to be true, or to be observed, that is not true or observed
  now.
- **The horizon or the trigger.** By when, or after which event. "In the next decade" counts.
  "Eventually" does not.
- **The check.** The specific observation that would show the expectation was wrong, and where a
  reader would go to look.

**An action recommendation does not satisfy this section.** "Prescribe with a stopping rule" is
advice, not a forecast, and round 02 shipped exactly that in place of a forward view on two of four
topics, where both graders caught it independently. Advice belongs in *What a person would actually
have to decide*, which already exists for it.

**A paper may say no forward view is supportable**, and some honestly cannot have one: a purely
definitional claim has nowhere to go, and forcing a prediction out of it produces a fake. Say that
in the section, with the reason. Omitting the section is not the same thing.

**9. What a person would actually have to decide.** Routes different readers to different actions,
which is what makes a paper usable rather than admirable.

Then the provenance block, under its own `## Provenance` heading, unchanged otherwise.

### The verdict table

**Generate it, do not write it:**

    python3 boundary.py table <artefact>.sourced

It reads the ledger, so the table cannot drift from it. A row you disagree with is a boundary
recorded wrongly, and the fix is `boundary.py`, not the sentence.

**Four columns.**

| Proposition | Verdict | Conditions | Evidence and reasoning |
|---|---|---|---|
| P1 — the dollar's real exchange rate will be lower in 10 to 15 years | Holds narrowly | Holds on the real trade-weighted rate. Fails as a statement about the dollar's institutional position. | Rate near a series high on a large external deficit. |
| P1.1 — the fall is already running | Falsified | Unconditional | The rate rose over the four years to 2026. |

- **Column one restates the proposition**, beside its label. Not the claim's wording, not a
  paragraph — the proposition's own sentence, which is the best-written line in the paper and is
  wasted anywhere else. A reader must never have to scroll back to learn what `P1` was.
- **Column two is the verdict word alone**, from the closed list below. Nothing else in the cell.
- **Column three is the conditions, or the word `Unconditional`.** It is not a second place to
  explain the verdict. A claim with no boundary has no conditions, and saying `Unconditional` is
  clearer than silence, which reads as an omission.
- **Column four is the evidence and the reasoning**, in a few words.

**Sub-rows carry the nuance.** A claim that needs its own verdict is grouped under its proposition
as `P2.1`, `P2.2`, in `P` order. Set `answers: "<proposition id>"` on the claim to place it.

**Push the conditionality downwards.** A proposition whose verdict is `Holds narrowly` or
`Contested` is carrying a disagreement that has not been resolved into anything a reader can use.
Decompose it until each leaf is as close to `Unconditional` as the evidence allows:

    P1   The sky is blue          Holds narrowly   Depends on the weather
    P1.1 The sky is blue          Holds            Fine weather
    P1.2 The sky is grey          Holds            Stormy weather

The parent carries the nuance and the leaves carry clean verdicts, so the reader watches a
disagreement resolve into two things that are both true. **`integrate.py` asks for children on any
narrow or contested proposition**, and a paper that genuinely cannot split one says why.

**Conditions is a written sentence, not a field dump.** Give each boundary a `reads_as`. The
generator prints it when present and falls back to concatenating `holds_when`, `fails_when` and
`unknown_region` when it is not, which is what round 02 shipped and it read like this:

    fails when inferential step: body psychotherapy had no benefit whatsoever;
    control group activity: body psychotherapy versus no intervention

Machine-readable and reader-hostile. The conditions stay as they are, because `dimensions.py` needs
them; `reads_as` is what a person reads. `boundary.py table` warns for every row that took the
fallback.

**The verdict word comes from this list and nowhere else.**

| Verdict | Means | Carried in the sidecar by |
|---|---|---|
| `Holds` | Supported by retrieved evidence, within a stated region | `holds_when` |
| `Holds narrowly` | Survives only in a named region, and fails outside it | `holds_when` and `fails_when` |
| `Falsified` | The evidence contradicts it | `fails_when` and `replaced_by` |
| `Unevaluated` | Nobody has measured it, which is not the same as false | `unknown_region` |
| `Contested` | Sources disagree and the conflict is open | an open `conflicts` record |

**How this lines up with the adversarial pass's four moves.** The moves resolve a *finding* during
the pass; the verdicts describe a *claim* in the paper. They are different objects and neither
replaces the other, but they meet in one place:

| Move (`reference/adversarial-pass.md`) | Usually produces the verdict |
|---|---|
| Conditional — each side holds in a nameable region | `Holds narrowly` |
| Reframe — a named shared assumption dropped | `Holds`, on a re-stated claim |
| Redirect — the observation stands, the conclusion does not | `Falsified`, with `replaced_by` |
| Hold — nothing available settles it | `Contested` |

**`Hold` and `Contested` are the same situation seen from two sides**, and a paper should never
carry one without the other. `Unevaluated` is a different thing again: nobody disagrees, nobody has
measured it.

Do not invent a sixth verdict. "Promising but thin" and "not established, not refuted" belong in
`Conditions`, which is free text and exists for exactly that.

**Every verdict is derivable from fields the sidecar already holds.** A row whose verdict you cannot
trace to one of those fields means the boundary was never recorded, and the fix is `boundary.py`,
not a better adjective.

### Evidence: what a source is allowed to contribute

**One source, as many quotes as it earns.** A source cited for more than one claim gets **one
evidence row per quote**, all sharing the `url`, the `sha256` and the `originGroup`, because they
are the same capture read twice. Nothing ever stopped this and no run has done it: twelve papers
across three rounds produced zero sources quoted twice, so every source contributed its single
strongest sentence and nothing else it said was recorded.

**Capture what cuts against you.** Where a cited source says something that undermines the claim it
is cited for, that sentence is captured as its own row with `supports.direction: "against"` or
`"mixed"`. This is the only mechanical defence against cherry-picking the standard has: a reader
cannot see what a source said that we left out, so the run has to put it in. It also feeds
`conflicts.detect()`, which reads directions and conditions and is currently near-blind because
almost nothing carries them.

**A quote is a sentence, not a fragment of markup.** Where the useful evidence is a number inside
structured data — a search count, a table cell, a JSON field — the quote is still the bytes from
the capture, and the row carries **`quoteGloss`**: one plain sentence saying what the fragment
means. Round 03 shipped `"quote": "8 8 0"` against a claim about how many trials exist. The 8 is
genuinely in the capture, so the gate passed it, and no reader could tell which of the three
numbers was the count. `claims.py` asks for a gloss when a quote is mostly not letters.

**Custody: somebody other than you holds a copy.** Every cited capture is run with `--archive`, so
the row carries an `archiveUrl` and `custodian: self+third-party`. Without it the hash proves only
that the quote matches *our own file*, and an auditor asking whether the page really said that on
the day has nothing to check. Rounds 01 to 03 wrote **zero** archive URLs across 48 cited rows,
which is the largest single hole in the standard as it stands.

Where the archive service refuses or is down, say so on the row and in Limitations. A source that
could not be archived is a disclosed limit, not a blocked run — but a paper where *nothing* was
archived means nobody tried, and `integrate.py` refuses that.

**A claim says where it appears in the paper.** `claims[].locator` carries the section or heading
the claim is argued in. Without it the sidecar audits the ledger and not the artefact, and a
sentence that drifts away from the claim behind it is invisible. Rounds 01 to 03 wrote zero.

### Plain English, and where the jargon is allowed to live

**The paper and the sidecar have different readers.** The paper is read by somebody deciding
something. The sidecar is read by an auditor or a machine. Forcing one register on both makes the
paper opaque or the sidecar imprecise, so they get different rules.

**In the paper:**

- Write ASD-STE100 Simplified Technical English: one idea per sentence, active voice, present
  tense, one word for one meaning.
- **Every term of art is either in Definitions or glossed in the sentence that first uses it.** No
  exceptions, and the gloss is plain even where the term is not. Round 03 shipped "no trial made it
  an endpoint" inside a definitions block whose whole purpose was stopping jargon from hiding a
  distinction; "no trial asked about it" says the same thing.
- **If a sentence needs a following clause starting "which means", the sentence before it was too
  technical.** Rewrite it rather than explaining it.

**In the sidecar:** the technical vocabulary stays, and the sidecar carries its own `definitions`
registry giving the technical sense of every term the paper defines plainly. The two are checkable
against each other, which is the point.

## What this mode does not do

- **It does not remember the standard is on.** Nothing polls, nothing hooks the fetch. If a
  retrieval goes around `sourced.py`, the claim resting on it is refused at append time, which is
  where it becomes visible.
- **It does not judge the claim.** It records that the quote is in the capture. Whether the quote
  supports the statement is your reading, and the statement is what a reviewer argues with.
- **It does not bind step 0 to anything.** A first-time user with no prior corpus runs this mode
  exactly as written, minus one line of output.

## Retrieve and project in separate passes

**Close the sources before asking what follows.** Retrieval and projection compete for the same
attention, and retrieval always wins, because it produces visible artefacts and the other does not.
A session that grounds and extrapolates in one pass reliably ships all grounding and no
extrapolation, and the gap is invisible in the output: the piece reads as thorough rather than as
timid.

So run two passes with a hard break between them.

- **Pass one, retrieve.** Capture, quote, hash, record. Nothing is concluded here beyond what a
  source says.
- **Pass two, project.** Working from the *summarised* findings rather than the captures, ask what
  the retrieved rates imply, where the mechanism carries and where it breaks, and what the argument
  is now committed to. Anything load-bearing that comes out of this pass is marked `predictive` and
  carries its resolution.

The measured failure this prevents: an artefact whose central argument is that something is
changing, carrying twenty claims and no forecast, because every unit of session attention was spent
proving what had already happened.
