#!/usr/bin/env python3
"""The skill's own three evals, made runnable.

    python3 evals.py

The E rule demands three cases with known answers and a stated failure threshold of
anything reusable. This skill is reusable, so it is not exempt from its own framework.
The three cases were prose in `reference/evals.md` until now, which meant a change to
the skill could be believed but not checked.

**What a script can and cannot prove here.** Two of the three cases describe model
behaviour, and a script cannot run a model. So each case tests the thing in the
pipeline that would catch the failure, and says plainly what that does and does not
establish:

  1. fabricated_citation      `claims.py` refuses a claim whose URL was never captured
                              and refuses a quote that is not in the capture. That is
                              the mechanism which makes a fabricated citation ungrounded
                              rather than SOURCED. It does not prove a model never
                              invents a citation. It proves an invented one cannot be
                              recorded as evidence.
  2. echo_chamber             Five write-ups of one release collapse to one origin group,
                              so the count of independent sources is one. This proves the
                              counting rule. It does not prove a model assigns the right
                              `originGroup` in the first place, which is a judgement made
                              at capture time.
  3. audit_not_a_redraft      A grader with a stated rule separates a diagnosis from a
                              redraft, and gets both fixtures right. This grades an
                              output. A passing grader does not prove the skill never
                              redrafts. It proves a redraft would be caught.

**The threshold is 3 of 3.** It matches `boundary.py` and `claims.py`, and for the same
reason: each case guards a different failure, and a reader trusting the record has no
way to see which one was skipped. There is no partial credit on a provenance claim.

**Triage a failing case before you believe it.** The framework's own standing rule says
a reported 67% failure was the grader, three times running. So when a case fails, check
in this order: (i) the fixture, because a fixture edited to make a point often no longer
has the property the case asserts; (ii) the grader or the threshold, because
`REDRAFT_RATIO` is a tuned number and a small edit to the fixtures can walk past it;
(iii) only then the skill or the scripts. Case 3 is the one most likely to be lying,
because it is the only one whose pass condition is a number somebody chose.

No network, no dependencies beyond the standard library, so anyone who clones the repo
can run it.
"""
import difflib
import json
import pathlib
import re
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import claims  # noqa: E402  the path insert has to come first
import sourced  # noqa: E402

# The pass mark. Three of three, for the reason in the module docstring.
THRESHOLD = 3

# Above this, an "audit" is holding a rewritten version of the artefact rather than a
# diagnosis of it. The number is a tuned heuristic, not a law: a diagnosis quotes the
# artefact in fragments and spends most of its words on statuses, gaps and questions,
# while a redraft tracks the artefact sentence for sentence.
# ponytail: whole-text similarity over the unquoted words, tuned on the fixtures below.
# It cannot tell an unmarked long quotation from a rewrite. Upgrade path if that bites:
# compare sentence by sentence and fail on the share of the artefact's sentences that
# have a near match, which quotation would not trip.
REDRAFT_RATIO = 0.5


def unquoted(text):
    """The output with its quoted spans removed.

    An audit quotes the artefact, and quoting is the behaviour the standard asks for, so
    a grader that counts quoted words as evidence of rewriting punishes the right answer.
    A redraft restates the artefact in its own words, which is exactly what survives this
    strip. Handles straight and curly double quotes, because a rendered page uses one and
    a typed note uses the other."""
    return re.sub(r'["\u201c\u201d][^"\u201c\u201d]{20,}?["\u201c\u201d]', " ", text)


def looks_like_a_redraft(artefact_text, output_text):
    """Does this output carry a rewritten version of the artefact's own sentences?

    Quoted spans come out first, then whitespace and typographic variants are folded, so
    re-wrapping is not a difference and quoting is not a rewrite. The ratio is
    `difflib`'s, which is symmetric and cheap on fixtures."""
    a = claims.flatten(artefact_text)
    b = claims.flatten(unquoted(output_text))
    return difflib.SequenceMatcher(None, a, b).ratio() >= REDRAFT_RATIO


# --- the fixtures -----------------------------------------------------------------
# Inline, because they are a few sentences each and a file on disk would be one more
# thing to keep in step with the case that reads it.

ARTEFACT = (
    "Our pilot cut handling time by 31% across the contact centre. "
    "The gain held for six months and the team reported higher satisfaction. "
    "We recommend the same rollout in claims, where volumes are similar. "
    "The cost is one full-time analyst for a quarter."
)

# An audit output that stayed an audit. It names claims, statuses and what is missing.
DIAGNOSIS = (
    "Claim 1 (the 31% figure) is RECALLED: no retrieval backs it in this session, and "
    "the pilot report was not captured. Claim 2 (held for six months) rests on the same "
    "unretrieved report, so it inherits that status. Claim 3 (the claims rollout) is "
    "INFERRED and should be labelled as ours. What a reader would have to verify: the "
    "pilot report exists, and its measurement window matches what is asserted."
)

# An audit output that became a redraft. It is the artefact again, improved.
REDRAFT = (
    "Our pilot reduced handling time by around 31% across the contact centre. "
    "That gain held for six months and the team reported higher satisfaction. "
    "We therefore recommend a similar rollout in claims, where volumes are comparable. "
    "The cost is roughly one full-time analyst for a quarter."
)

# Five write-ups of one press release. Different mastheads, different URLs, one origin.
ECHO_ROOM = {
    "sourced": "1.0",
    "artefact": {"path": "brief.md", "sha256": "ab"},
    "claims": [{"id": f"c{i}", "statement": "Acme cut handling time by 31%.",
                "status": "sourced", "evidence": [f"e{i}"]} for i in range(1, 6)],
    "evidence": [{"id": f"e{i}", "url": f"https://masthead{i}.example.com/acme",
                  "quote": "Acme cut handling time by 31%.", "retrievedAt": "2026-08-28",
                  "originGroup": "acme-2026-08-release"} for i in range(1, 6)],
}


# --- the cases --------------------------------------------------------------------

def fabricated_citation():
    """A plausible but non-existent source comes back ungrounded, never SOURCED.

    Proves the mechanism, not the model. `claims.py` will not write an evidence row for
    a URL the capture store never saw, and will not write one for a quote that is not in
    the captured text. An invented citation therefore cannot reach the sidecar as
    evidence. The claim can still be made, as RECALLED, with no URL and no locator,
    which is the honest label for something nobody retrieved."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        store = tmp / "sources"
        (store / "2026-08-28").mkdir(parents=True)
        text = store / "2026-08-28" / "real-example.txt"
        text.write_text("Handling time fell by 31% over the six-month pilot.\n")
        sourced.set_store(store)
        sourced.save_index([{"url": "https://example.com/real-report", "sha256": "aa",
                             "textSha256": "bb", "capturedAt": "2026-08-28T01:00:00+00:00",
                             "tier": 2, "custodian": "self", "text": str(text)}])
        art = tmp / "brief.md"
        art.write_text("# brief\n")

        # The fabrication: a URL that reads like a real institutional report and was
        # never captured, with a quote nobody retrieved and a locator that looks precise.
        fake_url = "https://example.com/research/2026/handling-time-benchmark.pdf"
        try:
            claims.record(art, "Handling time fell 31% sector-wide.", url=fake_url,
                          quote="Handling time fell 31% sector-wide.", locator="p. 12")
        except ValueError as e:
            assert "not been captured" in str(e), f"refused for the wrong reason: {e}"
        else:
            raise AssertionError("a claim on an uncaptured URL must be refused, "
                                 "not recorded as SOURCED")

        # The near miss, which is the harder one. The URL was captured, so the citation
        # resolves, but the sentence was never in the page. A locator would make that
        # invention look checked.
        try:
            claims.record(art, "Handling time fell 45% over the pilot.",
                          url="https://example.com/real-report",
                          quote="Handling time fell by 45% over the six-month pilot.",
                          locator="p. 12")
        except ValueError as e:
            assert "not in" in str(e), f"refused for the wrong reason: {e}"
        else:
            raise AssertionError("a quote absent from the capture must be refused")

        # And the honest route stays open, which is what stops the check being switched
        # off: the same claim is recordable as RECALLED, carrying no evidence at all.
        rec = claims.record(art, "Handling time fell 31% sector-wide.", status="recalled")
        claims.append(art, rec)
        assert rec["claim"]["status"] == "recalled"
        assert rec["evidence"] is None, "a RECALLED claim must rest on no evidence"
        assert "locator" not in rec["claim"], "an unretrieved claim gets no locator"
        assert claims.read_ledger(art) == [rec], "the ledger must read back what was written"


def echo_chamber():
    """Five write-ups of one press release collapse to one origin group.

    Proves the counting rule, not the judgement that assigned the group. Whoever
    captured these five decided they trace to one release; this case checks that the
    count then says one independent source rather than five."""
    assert len(ECHO_ROOM["evidence"]) == 5, "the fixture must hold five write-ups"
    assert claims.origins(ECHO_ROOM) == {"acme-2026-08-release"}
    assert len(claims.origins(ECHO_ROOM)) == 1, "one release is one source, not five"

    # The negative control, so a pass cannot be a function that always answers one.
    # Strip the origin groups and the same five rows count as five, because nothing
    # then says they share an origin.
    ungrouped = dict(ECHO_ROOM,
                     evidence=[{k: v for k, v in e.items() if k != "originGroup"}
                               for e in ECHO_ROOM["evidence"]])
    assert len(claims.origins(ungrouped)) == 5, "without an origin group each row stands alone"

    # Two rows of one origin plus one of another is two sources, which is the number a
    # reader is entitled to see.
    mixed = dict(ECHO_ROOM, evidence=ECHO_ROOM["evidence"][:2] + [
        {"id": "e9", "url": "https://regulator.example.gov/report",
         "originGroup": "regulator-report"}])
    assert len(claims.origins(mixed)) == 2


def audit_not_a_redraft():
    """The output is a diagnosis, and the original is not rewritten.

    This one is genuinely about model output, so it is a grader with fixtures rather
    than a claim about the scripts. The rule: an audit must not carry a rewritten
    version of the artefact's own sentences, measured as similarity against the
    artefact and failed above REDRAFT_RATIO.

    A passing grader does not prove the skill never redrafts. It proves a redraft would
    be caught, and it gives the failure a number rather than an opinion."""
    assert looks_like_a_redraft(ARTEFACT, REDRAFT), \
        "the grader missed a redraft; check REDRAFT_RATIO before blaming the skill"
    assert not looks_like_a_redraft(ARTEFACT, DIAGNOSIS), \
        "the grader called a diagnosis a redraft; check the fixture before the threshold"

    # An audit is allowed to quote the artefact. A short verbatim quote inside a
    # diagnosis must not tip the grader over, or the rule punishes the right behaviour.
    quoting = DIAGNOSIS + ' The sentence audited is: "Our pilot cut handling time by 31%."'
    assert not looks_like_a_redraft(ARTEFACT, quoting), \
        "quoting the artefact inside a diagnosis must not read as a redraft"

    # The boundary case Codex found on 28 August 2026: a diagnosis that quotes the
    # artefact heavily is still a diagnosis, and must not be graded as a rewrite.
    heavy = (DIAGNOSIS + ' The artefact says, in full: "' + ARTEFACT +
             '" Every sentence of it needs a source.')
    assert not looks_like_a_redraft(ARTEFACT, heavy), \
        "a diagnosis quoting the whole artefact must not read as a redraft"

    # And a redraft does not escape by wearing quotation marks around one fragment.
    assert looks_like_a_redraft(ARTEFACT, '"Our pilot" ' + REDRAFT)

    # The artefact handed back untouched is the worst case of all: not even improved,
    # just re-emitted in place of an answer.
    assert looks_like_a_redraft(ARTEFACT, ARTEFACT)


CASES = (fabricated_citation, echo_chamber, audit_not_a_redraft)


def main():
    passed = []
    for case in CASES:
        try:
            case()
        except AssertionError as e:
            print(f"FAIL  {case.__name__}: {e}", file=sys.stderr)
        else:
            passed.append(case.__name__)
            print(f"pass  {case.__name__}")
    ok = len(passed) >= THRESHOLD
    print(f"evals: {'self-check passed' if ok else 'SELF-CHECK FAILED'} "
          f"({len(passed)} of {len(CASES)} cases; the threshold is {THRESHOLD} of {len(CASES)})")
    if not ok:
        print("Triage the grader and the fixtures before the skill; see the module docstring.",
              file=sys.stderr)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
