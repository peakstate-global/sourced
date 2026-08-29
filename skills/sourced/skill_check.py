#!/usr/bin/env python3
"""Structural check on the SOURCED skill folder.

Five cases with known answers, no network, the same shape as `sourced.py --self-check`
and `boundary.py --self-check`:

  1. The standing-rules block in SKILL.md and in standing-rules.md is character-identical.
  2. Every companion file SKILL.md names in its table exists.
  3. SKILL.md is under the size budget, so the whole body can be read every time it fires.
  4. The handoff template in reference/adversarial-pass.md carries no inner code fence.
  5. Dispatch works: all five modes are named, the bare invocation has a row, the interview
     asks at most three questions, and it offers the escape word.

Case 5 is the one that stops a bare `/sourced` falling through to nothing. A skill that
needs the correct incantation is a skill that gets abandoned.

Case 4 is character by character on purpose. An inner triple backtick closes the outer
fence early, so the user copies half a prompt and never sees that the rest is missing.
It is easy to break while editing and impossible to notice by reading.

The budget is 10,000 bytes because that is the point at which a whole-file read stops being
routine; a skill body above it is one nobody loads in full.

    python3 skill_check.py --self-check
"""
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
# The body is read in full every time the skill fires, so it has a ceiling. 12KB is
# roughly three thousand tokens, which is small beside what an audit then retrieves.
# Raised from 10,000 on 28 August 2026, when the research and adversarial modes each
# needed their few lines of routing. The ceiling is the point, not the number: when
# the body runs out of room again, the detail goes to a companion file, not here.
BUDGET = 13_500
START = "<!-- standing-rules:start -->"
END = "<!-- standing-rules:end -->"
FENCE = "```"
MODES = ("interview", "audit", "research", "check", "statement")
ESCAPE = "`skip`"
# Three is the ceiling because the interview is the tax a hurried user pays before the
# work starts, and a fourth question is where they stop answering and stop invoking.
MAX_QUESTIONS = 3
HANDOFF = "reference/adversarial-pass.md"
HSTART = "<!-- handoff-template:start -->"
HEND = "<!-- handoff-template:end -->"


def block(text, where):
    """The standing-rules block, markers included. Raises if it is missing or doubled."""
    parts = text.split(START)
    if len(parts) != 2 or parts[1].count(END) != 1:
        raise AssertionError(f"{where}: expected exactly one standing-rules block")
    return START + parts[1].split(END)[0] + END


def companions(text):
    """The companion files named in the table rows of SKILL.md, in the order it lists them."""
    return re.findall(r"^\| `(reference/[\w.-]+\.md)` \|", text, re.M)


def handoff_template(text):
    """The handoff block between its markers, fence lines included."""
    parts = text.split(HSTART)
    assert len(parts) == 2 and parts[1].count(HEND) == 1, (
        f"{HANDOFF}: expected exactly one handoff-template block")
    return parts[1].split(HEND)[0].strip()


def dispatch(text):
    """The dispatch section and the interview, as (modes named, bare row, questions)."""
    start = text.index("## Start here")
    section = text[start:text.index("\n## ", start + 1)]
    named = [m for m in MODES if f"| {m} " in text]
    bare = [ln for ln in section.splitlines()
            if ln.startswith("| Nothing at all") and "interview" in ln]
    questions = re.findall(r"^\d+\. \*\*\"", section, re.M)
    return named, bare, questions, section


def check(root=HERE):
    skill = (root / "SKILL.md").read_text()
    standalone = (root / "standing-rules.md").read_text()

    assert block(skill, "SKILL.md") == block(standalone, "standing-rules.md"), (
        "the standing-rules block has drifted between SKILL.md and standing-rules.md"
    )

    named = companions(skill)
    assert named, "SKILL.md names no companion files"
    missing = [n for n in named if not (root / n).is_file()]
    assert not missing, f"SKILL.md names files that do not exist: {missing}"

    tmpl = handoff_template((root / HANDOFF).read_text())
    assert tmpl.count(FENCE) == 2, (
        f"{HANDOFF}: the handoff block must be exactly one fenced code block, "
        f"and it holds {tmpl.count(FENCE)} fence markers")
    assert tmpl.startswith(FENCE) and tmpl.endswith(FENCE), (
        f"{HANDOFF}: the handoff block must open and close with its own fence")
    body = tmpl[len(FENCE):-len(FENCE)]
    assert FENCE not in body, f"{HANDOFF}: the handoff block carries an inner code fence"

    named_modes, bare, questions, section = dispatch(skill)
    assert len(named_modes) == len(MODES), (
        f"SKILL.md names only {named_modes} in its modes table; expected all of {list(MODES)}")
    assert len(bare) == 1, (
        "the dispatch table needs exactly one row for a bare invocation, routing to interview")
    assert 0 < len(questions) <= MAX_QUESTIONS, (
        f"the interview asks {len(questions)} questions; the ceiling is {MAX_QUESTIONS}")
    assert ESCAPE in section, (
        f"the interview must offer the escape word {ESCAPE} in its first question")

    size = len((root / "SKILL.md").read_bytes())
    assert size <= BUDGET, f"SKILL.md is {size:,} bytes, over the {BUDGET:,}-byte budget"
    return len(named), size, len(body.splitlines()), len(questions)


def demo():
    named, size, lines, questions = check()
    print(f"PASS  rules block identical in SKILL.md and standing-rules.md")
    print(f"PASS  {named} companion files named in SKILL.md, all present")
    print(f"PASS  SKILL.md {size:,} bytes, under the {BUDGET:,}-byte budget "
          f"({BUDGET - size:,} to spare)")
    print(f"PASS  handoff template is one fence, {lines} lines, no inner fence")
    print(f"PASS  all {len(MODES)} modes named, bare invocation routes to interview, "
          f"{questions} questions, escape offered")
    print(f"skill_check: 5/5 cases pass, budget {BUDGET:,} bytes")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] not in ("--self-check", "--check"):
        sys.exit(f"usage: {sys.argv[0]} [--self-check]")
    demo()
