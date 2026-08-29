#!/usr/bin/env python3
"""The sidecar's claim status is DERIVED, not stored. Decided 26 August 2026 (Q3).

The old format stored one of `sourced`, `recalled`, `inferred` on each claim. That
field was fusing two independent things:

    - does anything back this claim   -> is `evidence[]` empty
    - how far is the wording from the source -> `fidelity`

Fusing them is the same mistake the claim store's own separation exists to prevent,
one layer down, and it made one real case inexpressible: a claim that is the writer's own inference
AND rests on retrieved evidence. That is a synthesis, and the A4 deck contains one.

So the sidecar now stores the two real fields and computes the word, exactly as
Publish's 0-4 ladder is kept as a projection rather than a stored field.

    python3 sourced_status.py            # self-check, no network
    python3 sourced_status.py <file.sourced> ...   # verify stored status matches

`fidelity` uses the claim store's vocabulary unchanged, so a sidecar converts without a
lookup table:

    quotation   the statement is the source's own words
    paraphrase  a restatement of what the source said
    inference   a conclusion the writer drew, which the source did not state

ponytail: a dict, not a rules engine. Four cases, and they are the whole domain.
"""
import json
import sys

FIDELITIES = ("quotation", "paraphrase", "inference")

# (has_evidence, is_inference) -> the word shown to a reader.
_STATUS = {
    (True, False): "sourced",
    (True, True): "sourced-inference",
    (False, False): "recalled",
    (False, True): "inferred",
}


def retrieved(entries):
    """The evidence entries that were actually fetched.

    A row with an id, a URL and nothing else is a POINTER, not evidence: no quote,
    no retrieval date, no hash. Counting it as backing is how a claim nobody
    checked comes to read as sourced, which is the exact failure this file exists
    to prevent. Found on 26 August 2026, when migrating the brochure sidecar
    silently upgraded three unretrieved claims from `recalled` to `sourced`.
    """
    return [e for e in entries if isinstance(e, dict) and e.get("retrievedAt")]


def derive_status(evidence, fidelity):
    """The displayed status of one claim, from the two fields that actually vary.

    `sourced-inference` is the cell the old three-value field could not reach: the
    writer's own conclusion, resting on evidence that was retrieved and hashed. It
    must not read as `sourced`, because the reader would take the conclusion for a
    finding, and it must not read as `inferred`, because that hides real backing.
    """
    if fidelity not in FIDELITIES:
        raise ValueError(f"fidelity must be one of {FIDELITIES}, got {fidelity!r}")
    return _STATUS[(bool(evidence), fidelity == "inference")]


def check_file(path):
    """Verify a sidecar's stored status is what the rule derives. Returns problems."""
    doc = json.load(open(path))
    by_id = {e["id"]: e for e in doc.get("evidence", [])}
    problems = []
    for claim in doc["claims"]:
        backing = retrieved(by_id.get(eid) for eid in claim.get("evidence", []))
        want = derive_status(backing, claim["fidelity"])
        if claim.get("status") != want:
            problems.append(f"{path} {claim['id']}: stored {claim.get('status')!r}, derived {want!r}")
    return problems


def demo():
    assert derive_status(["e1"], "paraphrase") == "sourced"
    assert derive_status([], "paraphrase") == "recalled"
    assert derive_status([], "quotation") == "recalled", "no evidence is recalled however exact the words"
    assert derive_status([], "inference") == "inferred"
    # The case the old format could not express, and the reason for this file.
    assert derive_status(["e3"], "inference") == "sourced-inference"
    # A pointer is not evidence. Only entries carrying a retrieval date count.
    real = {"id": "e1", "retrievedAt": "2026-08-26"}
    pointer = {"id": "e2"}
    assert retrieved([real, pointer, None]) == [real]
    assert derive_status(retrieved([pointer]), "paraphrase") == "recalled", \
        "an unretrieved pointer must never make a claim read as sourced"
    assert derive_status(retrieved([real]), "paraphrase") == "sourced"
    try:
        derive_status([], "sourced")  # the OLD value, in the NEW field
    except ValueError:
        pass
    else:
        raise AssertionError("a stale status value must not pass as a fidelity")
    print("sourced_status: self-check passed")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        demo()
    else:
        found = [p for f in sys.argv[1:] for p in check_file(f)]
        print("\n".join(found) if found else f"{len(sys.argv) - 1} sidecar(s): status matches the rule")
        sys.exit(1 if found else 0)
