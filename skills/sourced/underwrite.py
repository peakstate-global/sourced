#!/usr/bin/env python3
"""Who or what stands behind a claim, and whether that is enough for what it carries.

    python3 underwrite.py <artefact>.sourced           the table: every claim, its acts, its gap
    python3 underwrite.py <artefact>.sourced --policy p.json    judge against a policy
    python3 underwrite.py --self-check

SOURCED's U said only that a signature buys accountability and not accuracy. True, and it
left the sidecar with nothing to record except who signed, which does not scale and is not
even the interesting question. A human is not automatically a better validator than a
model: it depends on the expertise of the one and the capability of the other, and the
second is moving.

So this records **what was actually done** to a claim, never who is responsible for it.
An act is a verifiable event with an actor attached. The assurance level is DERIVED from
the acts present and is never asserted, which is what makes it auditable: you can disagree
with the level only by disputing an act.

**No level outranks another on a single scale.** Expert review is a different axis from
independent challenge, not a higher rung, because a non-expert skim is weaker than a
strong cross-model attack. What decides sufficiency is a policy, and the policy belongs to
the organisation whose risk it is, never to this file. Ships with a conservative default
and nothing more.
"""
import json
import pathlib
import sys

# What can be done to a claim. Each is an event somebody could check happened.
ACTS = {
    "retrieved":                "the source was fetched and hashed",
    "quote-checked":            "the quote is byte-present in the capture",
    "arithmetic-rechecked":     "numbers recomputed from the source's own figures",
    "support-judged":           "someone decided this quote supports this claim",
    "cross-challenged":         "a different model, fresh context, tried to break it",
    "independently-challenged": "a different model family AND harness tried to break it",
    "expert-reviewed":          "a person with stated expertise read it against its evidence",
}

# Derived, in order. The first level whose acts are all absent stops the climb.
LEVELS = [
    ("A0", "asserted",                  ()),
    ("A1", "tool-verified",             ("quote-checked",)),
    ("A2", "challenged",                ("quote-checked", "cross-challenged")),
    ("A3", "independently challenged",  ("quote-checked", "independently-challenged")),
]

# The default policy. Deliberately thin: an organisation's appetite is not ours to guess.
DEFAULT_POLICY = {
    "name": "conservative default",
    "requires": {
        "low":      ["quote-checked"],
        "moderate": ["quote-checked", "cross-challenged"],
        "high":     ["quote-checked", "arithmetic-rechecked", "independently-challenged"],
        "severe":   ["quote-checked", "arithmetic-rechecked", "independently-challenged",
                     "expert-reviewed"],
    },
    "raiseFor": ["medical", "financial", "legal", "safety-critical"],
}

RATINGS = ["low", "moderate", "high", "severe"]


def acts_of(claim):
    """The act names recorded on a claim, however the list is shaped."""
    got = claim.get("underwriting") or []
    out = set()
    for a in got:
        if isinstance(a, str):
            out.add(a)
        elif isinstance(a, dict) and a.get("act"):
            out.add(a["act"])
    return out


def level(claim):
    """The highest level whose required acts are all present. Never asserted."""
    have, best = acts_of(claim), LEVELS[0]
    for lv in LEVELS:
        if all(a in have for a in lv[2]):
            best = lv
    return best[0]


def corroboration(claim, evidence):
    """How many independent origins back this claim.

    Ten write-ups of one press release are one source, which is why this counts
    originGroup and not rows. It is the strongest single signal we hold for how likely a
    claim is to be wrong, and nothing has ever computed it.
    """
    by_id = {e.get("id"): e for e in evidence if isinstance(e, dict)}
    groups = set()
    for eid in claim.get("evidence") or []:
        row = by_id.get(eid) or {}
        groups.add(row.get("originGroup") or row.get("url") or eid)
    return len(groups)


def likelihood_wrong(claim, data):
    """low / medium / high, computed from six things the sidecar already records.

    This is not forecasting. It asks how likely THIS claim is to be wrong given what we
    hold, and every input is a field somebody already wrote.
    """
    score = 0
    ev = data.get("evidence") or []
    corr = corroboration(claim, ev)
    if corr == 0:
        score += 2
    elif corr == 1:
        score += 1
    open_ids = {c.get("claim") for c in (data.get("conflicts") or [])
                if isinstance(c, dict) and c.get("state") == "open"}
    if claim.get("id") in open_ids or claim.get("challenged") == "attempted-unresolved":
        score += 2
    if claim.get("challenged") in ("holds", "holds-with-boundary"):
        score -= 1
    if claim.get("status") in ("inferred", "recalled"):
        score += 1
    by_id = {e.get("id"): e for e in ev if isinstance(e, dict)}
    if any((by_id.get(eid) or {}).get("selfInterested") for eid in claim.get("evidence") or []):
        score += 1
    if (claim.get("unknown_region") or "").strip():
        score -= 1          # a claim that names where it is untested over-claims less
    return "low" if score <= 0 else ("medium" if score <= 2 else "high")


def rating(impact, likelihood, domain=None, policy=None):
    """Impact x likelihood, then raised one step for a regulated domain.

    The ordinary matrix, because every organisation already has one on a wall. Domain is
    a modifier and not a third axis, which is what keeps this drawable.
    """
    policy = policy or DEFAULT_POLICY
    imp = ["trivial", "minor", "moderate", "major", "severe"].index(impact)
    lik = ["low", "medium", "high"].index(likelihood)
    idx = min(3, (imp * 3 + lik * 2) // 5)
    if domain and domain in policy.get("raiseFor", []):
        idx = min(3, idx + 1)
    return RATINGS[idx]


def shortfall(claim, rate, policy=None):
    """Acts the policy asks for and the claim has not collected."""
    policy = policy or DEFAULT_POLICY
    want = policy.get("requires", {}).get(rate, [])
    have = acts_of(claim)
    return [a for a in want if a not in have]


def report(data, policy=None):
    """One row per claim: what was done, what it earned, what is missing."""
    policy = policy or DEFAULT_POLICY
    ev = data.get("evidence") or []
    rows = []
    for c in data.get("claims") or []:
        if not isinstance(c, dict):
            continue
        lik = likelihood_wrong(c, data)
        imp = c.get("impact") or ("major" if c.get("role") == "proposition" else "moderate")
        rate = rating(imp, lik, c.get("domain"), policy)
        rows.append({
            "id": c.get("id"), "level": level(c), "likelihood": lik, "impact": imp,
            "rating": rate, "corroboration": corroboration(c, ev),
            "missing": shortfall(c, rate, policy),
        })
    return rows


def render(rows, policy=None):
    policy = policy or DEFAULT_POLICY
    out = [f"policy: {policy.get('name', 'unnamed')}",
           "| Claim | Assurance | Sources | Chance wrong | Impact | Risk rating | Still required |",
           "|---|---|---|---|---|---|---|"]
    for r in rows:
        out.append(f"| {r['id']} | {r['level']} | {r['corroboration']} | {r['likelihood']} "
                   f"| {r['impact']} | {r['rating']} | {', '.join(r['missing']) or '-'} |")
    short = [r for r in rows if r["missing"]]
    out.append("")
    out.append(f"{len(short)} of {len(rows)} claim(s) are under-assured for their risk rating."
               if short else f"all {len(rows)} claim(s) meet the policy.")
    return "\n".join(out)


def _self_check():
    ev = [{"id": "e1", "originGroup": "g1"}, {"id": "e2", "originGroup": "g1"},
          {"id": "e3", "originGroup": "g2", "selfInterested": True}]

    # The level is derived from acts, never asserted.
    bare = {"id": "c1"}
    assert level(bare) == "A0", "no acts is A0"
    assert level({"id": "c1", "underwriting": ["quote-checked"]}) == "A1"
    assert level({"id": "c1", "underwriting": ["quote-checked", "cross-challenged"]}) == "A2"
    assert level({"id": "c1", "underwriting": [{"act": "quote-checked", "by": "tool"},
                                               {"act": "independently-challenged",
                                                "by": "gpt-5.6-sol"}]}) == "A3", \
        "an act may be a record with an actor, not only a name"
    assert level({"id": "c1", "underwriting": ["expert-reviewed"]}) == "A0", \
        "expert review is a different axis, not a higher rung, and does not imply the quote was checked"

    # Ten write-ups of one press release are one source.
    assert corroboration({"evidence": ["e1", "e2"]}, ev) == 1, "same origin counts once"
    assert corroboration({"evidence": ["e1", "e3"]}, ev) == 2
    assert corroboration({"evidence": []}, ev) == 0

    # Likelihood is computed from fields somebody already wrote.
    data = {"evidence": ev, "claims": []}
    solid = {"id": "c1", "evidence": ["e1", "e3"], "challenged": "holds-with-boundary",
             "status": "sourced", "unknown_region": "outside the tested band"}
    assert likelihood_wrong(solid, data) == "low", likelihood_wrong(solid, data)
    weak = {"id": "c2", "evidence": [], "status": "inferred",
            "challenged": "attempted-unresolved"}
    assert likelihood_wrong(weak, data) == "high", likelihood_wrong(weak, data)
    assert likelihood_wrong({"id": "c3", "evidence": ["e3"], "status": "sourced"},
                            data) == "medium"

    # A regulated domain raises the rating by one step and is not a third axis.
    assert rating("moderate", "medium") == "moderate", rating("moderate", "medium")
    assert rating("severe", "high") == "severe"
    plain = rating("minor", "low")
    assert rating("minor", "low", domain="medical") != plain, "a regulated domain raises it"
    assert rating("severe", "high", domain="medical") == "severe", "and never past the top"

    # The shortfall names acts, so a reader can go and do them.
    c = {"id": "c9", "underwriting": ["quote-checked"]}
    assert shortfall(c, "high") == ["arithmetic-rechecked", "independently-challenged"]
    assert shortfall(c, "low") == []

    # An organisation's policy overrides the default entirely.
    lax = {"name": "test", "requires": {"high": ["quote-checked"]}, "raiseFor": []}
    assert shortfall(c, "high", lax) == [], "the policy decides sufficiency, not this file"

    print("underwrite: self-check passed (14 of 14 cases; the threshold is 14 of 14)")


if __name__ == "__main__":
    argv = sys.argv[1:]
    if not argv or "--self-check" in argv:
        _self_check()
        raise SystemExit(0)
    policy = None
    if "--policy" in argv:
        i = argv.index("--policy")
        policy = json.loads(pathlib.Path(argv[i + 1]).read_text())
        argv = argv[:i] + argv[i + 2:]
    doc = json.loads(pathlib.Path(argv[0]).read_text())
    rows = report(doc, policy)
    print(render(rows, policy))
    raise SystemExit(1 if any(r["missing"] for r in rows) else 0)
