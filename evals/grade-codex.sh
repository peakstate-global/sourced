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

read -r -d '' PROMPT <<EOF || true
Grade one research artefact against a fixed rubric. Read only these three files:

  Artefact: $RUN_DIR/artefact.md
  Sidecar:  $RUN_DIR/artefact.md.sourced
  Rubric:   $RUBRIC

For the G1 gate you may also read the captured source texts under $RUN_DIR/store.
Before recording a G1 fail, name the file you searched and the string you searched for.

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
RAW="$("$CLI" exec --skip-git-repo-check "$PROMPT" 2>&1)"
CODE=$?
FINISHED="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

printf '%s\n' "$RAW" > "$OUT/$TOPIC.codex.raw"
# The sheet is the last JSON object in the output.
python3 - "$OUT/$TOPIC.codex.raw" "$OUT/$TOPIC.codex.json" <<'PY'
import json, re, sys
raw = open(sys.argv[1], encoding="utf-8", errors="replace").read()
blocks = re.findall(r"\{(?:[^{}]|\{[^{}]*\})*\}", raw, re.S)
for b in reversed(blocks):
    try:
        d = json.loads(b)
    except ValueError:
        continue
    if any(k.startswith("C") for k in d):
        open(sys.argv[2], "w").write(json.dumps(d, indent=2) + "\n")
        raise SystemExit(0)
raise SystemExit("no sheet found in the CLI output")
PY
PARSED=$?

python3 - "$OUT/$TOPIC.codex.meta.json" <<PY
import json, sys
json.dump({
    "topic": "$TOPIC",
    "cli": "$CLI",
    "cliVersion": """$VERSION""".strip(),
    "exitCode": $CODE,
    "sheetParsed": $PARSED == 0,
    "startedAt": "$STARTED",
    "finishedAt": "$FINISHED",
    "note": ("The model string is the CLI's own --version output, recorded by the harness. "
             "It is not a claim the grading model made about itself."),
}, open(sys.argv[1], "w"), indent=2)
PY

echo "$TOPIC: exit $CODE, $VERSION"
exit $CODE
