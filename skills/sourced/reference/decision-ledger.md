# The decision ledger

Read this when you are recording decisions during the work, or folding them into a sidecar.

Rejected options leave no trace in the finished artefact. Nothing else in a deliverable records
that an option was considered at all, so once the draft settles the road not taken is
unrecoverable. That is why the ledger is kept. It is not kept because a note written at the time
is more truthful than one written later: a log written as you go can be checked against what
actually happened, and a reconstructed log cannot be wrong in any way a reader can detect.

## The shape

`<artefact>.decisions.jsonl` sits beside the artefact while the work happens, one JSON object per
line, appended and never rewritten. At assembly it folds into `<artefact>.sourced` as the
top-level `decisions[]` array, whose members are the ledger's lines unchanged.

```json
{"at": "2026-08-28T01:00:00Z",
 "context": ["e1", "the ticket"],
 "options": ["stdlib", "jsonschema"],
 "chose": "stdlib",
 "rejected": [{"option": "jsonschema", "clause": "a pip install nobody runs"}],
 "model": "claude-opus-5", "modelVersion": "1m", "run": "20260828T171828",
 "narrative": {"text": "Simplest thing that holds.", "generatedAt": "2026-08-28T01:00:00Z"}}
```

`run` and `narrative` are optional; everything else is required. A record is the **state**, not
the story: what was in context, which options were enumerated, which was chosen, which were
rejected with one clause each, and which model ran. None of that needs introspection, so all of
it is checkable.

**The chosen option carries no clause.** The artefact is what it looks like. Only a rejected
option gets free text, and it gets one clause.

**`narrative` is labelled, never causal.** A justification is always generated after the choice,
because you cannot know you need to justify something until you have chosen. The key names what
it is and carries its own `generatedAt`, so a reader cannot mistake it for the reason the choice
was made.

## Keep R dumb

Do not add hypothesis, falsifier, `holds_when` or `fails_when` structure to a decision record.
That belongs in **O** and in the boundary record. Duplicating it here turns a log into a
framework, and the framework is the thing nobody fills in.

## Running it

    python3 decisions.py append <artefact> --option A --option B --chose A \
        --reject "B: needs a second dependency" --model claude-opus-5 --model-version 1m \
        --context e1 --narrative "…"
    python3 decisions.py fold <artefact>       ledger lines -> decisions[] in the sidecar
    python3 decisions.py --self-check          four cases, known answers, no network

Folding twice is safe: it replaces the array rather than extending it. Folding sets `sourced` to
`1.1`, because `decisions[]` is a 1.1 field.

## The schema version

`decisions[]` arrives in **sourced 1.1**, and it is **optional**. A sidecar without it validates,
so every `.sourced` file already on disk stays valid and an implementation that ignores the array
is not broken. `decisions.py`'s `validate()` is the shape check in this repo; the published JSON
Schema is served from the Peak State tenant's `public/sourced/v1.schema.json` and is edited there.
