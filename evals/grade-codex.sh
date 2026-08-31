#!/usr/bin/env bash
# The second grader, called directly rather than through a subagent.
#
# The eval's whole value is that a second, DIFFERENT model marks the work. Until round
# 06 that second opinion came back through the `codex` subagent, whose wrapper is itself
# a Claude model instructed to forward to the Codex CLI. So a sheet could return whether
# or not Codex ran, and the only evidence of which model reasoned was the sheet's own
# claim about itself. Round 05 returned one sheet self-identified as "haiku" and I could
# not tell what had happened.
#
# The framework this eval measures holds that an agent's account of its own process is an
# introspective claim and is never taken on trust. This script applies that to the
# instrument: the model string is recorded from the CLI, not from the model.
#
#   ./grade-codex.sh <run-dir> <rubric> <out-dir>
#
# Writes <out-dir>/<topic>.codex.json      the sheet
#        <out-dir>/<topic>.codex.meta.json provenance: command, version, exit code, at
set -uo pipefail

RUN_DIR="${1:?usage: grade-codex.sh <run-dir> <rubric> <out-dir>}"
RUBRIC="${2:?}"
OUT="${3:?}"
TOPIC="$(basename "$RUN_DIR")"
mkdir -p "$OUT"

CLI="codex-auto"; command -v "$CLI" >/dev/null 2>&1 || CLI="codex"
VERSION="$("$CLI" --version 2>&1 | head -1)"

# --version names the EXECUTABLE, not the model that reasons. codex-auto also picks an
# account profile per call by live quota, so two runs can carry identical metadata and
# different backends. Pin the model explicitly and record what was pinned, or the second
# grader's identity is still an assumption wearing a version string.
MODEL="${SOURCED_GRADER_MODEL:-gpt-5.6-sol}"

read -r -d '' PROMPT <<EOF || true
Grade one research artefact against a fixed rubric.

  Artefact: $RUN_DIR/artefact.md
  Working record (may not exist): $RUN_DIR/artefact.md.sourced
  Rubric:   $RUBRIC

Read the artefact and the rubric. Read the working record if it exists.

For the G1 and G1b gates you may also:
  - read any captured source texts under $RUN_DIR/store, if that directory exists;
  - AND, where a citation has no capture, FETCH THE LIVE SOURCE and check it.

Fetching live sources is expected, not exceptional: a paper produced without a capture
store is held to the same standard with more work on your side. Before recording a G1
fail, name the file or URL you checked and the string you searched for.

Read nothing else.

Do not read any other round, any other run, or any note about what the skill was meant
to improve.

Score all NINE criteria C1 to C9 (0 to 3) and both gates G1 and G2 (pass or fail).
Every criterion scored 0 or 1 gets a one-line triage naming what is at fault, in the
rubric's order: the topic, then the rubric, then the skill. C8 requires the count of
in-scope claims, how many carry a falsifier, and one falsifier quoted with a note on
whether you could go and check it. C6 requires you to say whether any row confuses an
untested region with a contested one.

Return strict JSON and nothing else:
{"topic":"$TOPIC","C1":{"score":2,"why":"one line"}, ... ,"C9":{...},
 "G1":{"pass":true,"why":"one line"},"G2":{"pass":true,"why":"one line"},
 "triage":{},"note":"at most two lines"}

Do NOT include a "grader" field. The harness records which model ran.
EOF

STARTED="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
RAW="$("$CLI" exec --skip-git-repo-check --model "$MODEL" "$PROMPT" 2>&1)"
CODE=$?
FINISHED="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

printf '%s\n' "$RAW" > "$OUT/$TOPIC.codex.raw"
# The sheet is the last JSON object in the output.
python3 - "$OUT/$TOPIC.codex.raw" "$OUT/$TOPIC.codex.json" <<'PY'
import json, re, sys
raw = open(sys.argv[1], encoding="utf-8", errors="replace").read()
blocks = re.findall(r"\{(?:[^{}]|\{[^{}]*\})*\}", raw, re.S)
CRITERIA = [f"C{i}" for i in range(1, 10)]
GATES = ["G1", "G1b", "G2"]


def complete(d):
    """A sheet, or something that merely looks like one.

    The first version accepted any object with any key starting with C, so a truncated
    reply carrying only C1 — or an unrelated object with a key like CLI — was written out
    and marked parsed.
    """
    if not isinstance(d, dict):
        return False
    for c in CRITERIA:
        v = d.get(c)
        if not isinstance(v, dict) or v.get("score") not in (0, 1, 2, 3):
            return False
    for g in GATES:
        v = d.get(g)
        if not isinstance(v, dict) or not isinstance(v.get("pass"), bool):
            return False
    return True


for b in reversed(blocks):
    try:
        d = json.loads(b)
    except ValueError:
        continue
    if complete(d):
        open(sys.argv[2], "w").write(json.dumps(d, indent=2) + "\n")
        raise SystemExit(0)
raise SystemExit("no complete sheet in the CLI output: need C1-C9 with integer scores "
                 "0-3 and G1, G1b, G2 with boolean pass")
PY
PARSED=$?

python3 - "$OUT/$TOPIC.codex.meta.json" <<PY
import json, sys
json.dump({
    "topic": "$TOPIC",
    "cli": "$CLI",
    "cliVersion": """$VERSION""".strip(),
    "modelPinned": "$MODEL",
    "exitCode": $CODE,
    "sheetParsed": $PARSED == 0,
    "startedAt": "$STARTED",
    "finishedAt": "$FINISHED",
    "note": ("cliVersion is the executable, recorded by the harness. modelPinned is what "
             "--model asked for. Neither is a claim the grading model made about itself, and "
             "neither proves what ran server-side: it is the strongest evidence available "
             "short of the provider attesting it."),
}, open(sys.argv[1], "w"), indent=2)
PY

echo "$TOPIC: cli exit $CODE, sheet parsed $([ $PARSED -eq 0 ] && echo yes || echo NO), $VERSION, model $MODEL"

# A clean CLI exit with no parseable sheet is a failed grading, and the old script
# returned 0 for it. Nothing downstream could then tell a graded topic from an ungraded
# one, or fall back.
if [ $CODE -ne 0 ]; then exit $CODE; fi
if [ $PARSED -ne 0 ]; then
  echo "grade-codex: the CLI exited 0 but produced no usable sheet for $TOPIC" >&2
  exit 3
fi
exit 0
