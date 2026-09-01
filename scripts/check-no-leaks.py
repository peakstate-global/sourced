#!/usr/bin/env python3
"""Pre-commit guard for a PUBLIC config repo.

Blocks a commit that introduces a hard leak (absolute home paths, personal
emails, credentials). Warns — but does not block — on mentions of the author's
own app domains, which appear deliberately in "why this rule exists" war
stories and are not secret.

Run over the staged diff:   python3 scripts/check-no-leaks.py
Run over the whole tree:    python3 scripts/check-no-leaks.py --all
Run over commit authorship: python3 scripts/check-no-leaks.py --authors <range>

The last one exists because file contents are not the only way a personal
address reaches a public repo. Two commits went out of this repo authored as a
real personal email while every sibling repo used the GitHub noreply address,
and the content guard could not see it: an author line is metadata, not a file.
"""
import re
import subprocess
import sys
from pathlib import Path

# Blocks the commit. Absolute home paths are also a portability bug, not just
# a disclosure one — they break the repo for everyone who is not the author.
HARD = [
    # A trailing `...` or `<placeholder>` is documentation, not a real path.
    (re.compile(r"/Users/(?!\.{2,}|<)[A-Za-z0-9._-]+"), "absolute home path — use $HOME or ~"),
    (re.compile(r"/home/(?!\.{2,}|<)[A-Za-z0-9._-]+"), "absolute home path — use $HOME or ~"),
    (re.compile(r"[A-Za-z0-9._%+-]+@(?:irama|peakstate|hoomans)\.[a-z.]+"), "personal email"),
    (re.compile(r"org\.irama\.[A-Za-z0-9._-]+"), "personal launchd label"),
    (re.compile(r"\bsk-[A-Za-z0-9_-]{16,}"), "possible API key"),
    (re.compile(r"\bsk-ant-[A-Za-z0-9_-]{16,}"), "Anthropic key"),
    (re.compile(r"\bghp_[A-Za-z0-9]{20,}"), "GitHub token"),
    (re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}"), "GitHub fine-grained token"),
    (re.compile(r"\bsbp_[a-f0-9]{20,}"), "Supabase token"),
    (re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}"), "Slack token"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "AWS access key"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "private key"),
    (re.compile(r"\beyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}"), "JWT"),
    # The tree is clean of these, so block rather than warn — a war story that
    # names an app is how the private inventory leaks back in one line at a time.
    # PORTED FROM irama-skills, WITH ONE DELIBERATE CHANGE: peakstate.global is the
    # brand publishing this repo, so naming it is the point rather than a leak. Any
    # private domain stays blocked: a war story that names a private app is how the
    # inventory leaks back in one line at a time.
    #
    # The list itself is NOT in this file. A guard that spells out the domains it
    # hides publishes them to everyone who reads the guard, which is the failure it
    # exists to prevent. Put one domain per line in `.leakrc` (gitignored) or in
    # LEAK_PRIVATE_DOMAINS, comma separated. With neither set the rule does not run,
    # which is correct for anyone who cloned this and has no such list.
    # Working conversation is not documentation. A public repo records the
    # decision and the reason for it; the discussion that produced the decision
    # is private material and belongs nowhere in it. Quoting a colleague's
    # in-the-moment words also makes a permanent public record of a private
    # exchange, which is not ours to publish however well meant.
    #
    # Paraphrase is the fix and it is also the better document: "the rule was
    # written down and broken three times in one artefact" says the same thing
    # as a quote, ages better, and reads as a finding rather than an exchange.
    #
    # Deliberately narrow. Quoting a SOURCE is the entire point of this
    # framework and must never be blocked, so this fires only on speech
    # attributed to a person who works on this repo.
]

def _private_domains():
    """One domain per line in .leakrc, or a comma-separated LEAK_PRIVATE_DOMAINS."""
    import os
    raw = os.environ.get("LEAK_PRIVATE_DOMAINS", "")
    rc = Path(__file__).resolve().parent.parent / ".leakrc"
    if rc.exists():
        raw += "\n" + rc.read_text()
    out = [d.strip() for line in raw.replace(",", "\n").splitlines()
           for d in [line.split("#")[0]] if d.strip()]
    return sorted(set(out))


def _team_names():
    """Surnames or given names of people who work on this repo, one per line in .leakrc
    under a `names:` prefix, or in LEAK_TEAM_NAMES. Same reason as the domains: a guard
    that spells out who it protects publishes that too."""
    import os
    raw = os.environ.get("LEAK_TEAM_NAMES", "")
    rc = Path(__file__).resolve().parent.parent / ".leakrc"
    if rc.exists():
        raw += "\n" + "\n".join(l[6:] for l in rc.read_text().splitlines()
                                 if l.strip().startswith("names:"))
    return sorted({n.strip() for line in raw.replace(",", "\n").splitlines()
                   for n in [line.split("#")[0]] if n.strip()})


_names = _team_names()
if _names:
    # Working conversation is not documentation. A repo records the decision and the
    # reason for it; the discussion that produced the decision is private material.
    # Deliberately narrow: quoting a SOURCE is the whole point of this framework and
    # must never be blocked, so this fires only on speech attributed to the team.
    _quote = "[" + chr(34) + chr(0x201C) + chr(0x2018) + "']"
    _verb = r"(?::\s*|\bsaid\b|\basked\b|\bwrote\b|\bput it\b|\bcomplained\b)"
    _who = "|".join(re.escape(n) for n in _names)
    HARD.append((
        re.compile(r"\b(?:" + _who + r")\b[^\n" + chr(34) + r"]{0,60}?"
                   + _verb + r"[^\n]{0,20}" + _quote),
        "quoted working conversation — paraphrase the substance instead"))


_domains = _private_domains()
if _domains:
    HARD.append((
        re.compile(r"\b(?:[a-z0-9-]+\.)?(?:%s)\b" % "|".join(re.escape(d) for d in _domains),
                   re.I),
        "private app domain — describe it generically instead"))


# Reported for eyeballing, never blocks.
SOFT = re.compile(r"(?!)")  # nothing soft-flagged at present

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv"}


def staged_files():
    out = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        capture_output=True, text=True, check=True,
    ).stdout
    return [f for f in out.splitlines() if f.strip()]


def all_files():
    out = subprocess.run(["git", "ls-files"], capture_output=True, text=True, check=True).stdout
    return [f for f in out.splitlines() if f.strip()]


# The email pattern, reused for authorship. Kept as a lookup into HARD rather
# than a second copy, because two copies of a guard rule drift and the drift is
# silent.
EMAIL_RULE = next(p for p, label in HARD if label == "personal email")


def check_authors(rev_range) -> int:
    """Refuse a push carrying a commit authored from a personal address.

    Git hands a pre-push hook the range it is about to send. Everything in that
    range gets its author and committer lines read; a noreply address passes,
    a real one does not."""
    try:
        out = subprocess.run(
            ["git", "log", "--format=%H%x1f%an <%ae>%x1f%cn <%ce>", rev_range],
            capture_output=True, text=True, check=True).stdout
    except subprocess.CalledProcessError:
        return 0                      # nothing to compare against, nothing to check
    bad = []
    for line in out.splitlines():
        if not line.strip():
            continue
        sha, author, committer = line.split("\x1f")
        for role, ident in (("author", author), ("committer", committer)):
            for hit in EMAIL_RULE.findall(ident):
                bad.append((sha[:9], role, hit))
    if bad:
        print("\nBLOCKED — a commit in this push is signed with a personal address.")
        for sha, role, hit in bad:
            print(f"  {sha}  {role}: {hit}")
        print("\nThis is a public repo, and an author line is as visible as a file.")
        print("Set the identity, then rewrite the commits that carry it:")
        print("  git config --local user.email <id>+<user>@users.noreply.github.com")
        print("  git rebase -i --exec 'git commit --amend --no-edit --reset-author' <base>")
        print("\nOverride once (you are sure it is safe): git push --no-verify")
        return 1
    return 0


# ── Portability rules ────────────────────────────────────────────────────────
# A skill that only works in one folder on one machine is broken for everyone
# else, and the failure is silent: the path simply is not there. All three of
# these caught a real defect in this repo before they were written down.
PORTABILITY = [
    (re.compile(r"[~$](?:HOME)?/\.claude/skills/"),
     "hardcoded skill path — address <skill-dir>, resolved from where the skill loaded"),
]

CODE_SPAN = re.compile(r"`[^`]*`")
MD_LINK = re.compile(r"\[[^\]]*\]\((?!https?:|mailto:|#|<)([^)\s]+)\)")


def check_portability(name, path, text, hits):
    """Three checks a leak guard cannot express as one line pattern."""
    parts = set(path.parts)

    # 1. A skill must not name its own install location.
    if "skills" in parts:
        for lineno, line in enumerate(text.splitlines(), 1):
            for pattern, label in PORTABILITY:
                for hit in pattern.findall(line):
                    hits.append((name, lineno, label, hit))

    # 2. A relative markdown link must point at something that exists. Ten dead
    #    links shipped in this repo pointing at a docs/ directory it never had.
    if path.suffix == ".md":
        fenced = False
        for lineno, line in enumerate(text.splitlines(), 1):
            # Code shows what a link should LOOK like; it is not a link. Skip
            # fenced and indented blocks. This trades a little coverage — a real
            # link indented four spaces under a list item goes unchecked — for no
            # false positives, because a guard that cries wolf gets switched off.
            if line.lstrip().startswith("```"):
                fenced = not fenced
                continue
            if fenced or line.startswith("    ") or line.startswith("\t"):
                continue
            # A link inside a code span is documentation OF link syntax, not a
            # link. So is anything carrying a <placeholder>, or a site-root path
            # that is served rather than stored.
            for target in MD_LINK.findall(CODE_SPAN.sub("", line)):
                rel = target.split("#", 1)[0]
                if not rel or rel.startswith("/") or "<" in target or ">" in target:
                    continue
                if not (path.parent / rel).exists():
                    hits.append((name, lineno, "dead relative link", target))


def check_shell(files, hits):
    """3. shellcheck every shell script. `bash -n` proves syntax, not correctness:
    it passed a quoting bug that word-split any path containing a space."""
    import shutil
    if not shutil.which("shellcheck"):
        return
    # A .sh extension is not a promise: this repo has a .sh file that is Python
    # and another that is zsh, neither of which shellcheck can parse. Trust the
    # shebang, so an unparseable *bash* file is still reported.
    scripts = []
    for f in files:
        if not f.endswith(".sh"):
            continue
        try:
            first = Path(f).read_text(errors="ignore").split("\n", 1)[0]
        except OSError:
            continue
        if re.search(r"\b(bash|sh|dash|ksh)\b", first):
            scripts.append(f)
    if not scripts:
        return
    out = subprocess.run(
        ["shellcheck", "--severity=warning", "--exclude=SC1090", "--format=gcc", *scripts],
        capture_output=True, text=True).stdout
    for line in out.splitlines():
        bits = line.split(":", 4)
        if len(bits) >= 5 and "warning" in bits[3] or len(bits) >= 5 and "error" in bits[3]:
            hits.append((bits[0], bits[1], "shellcheck" + bits[3], bits[4].strip()))


def selftest() -> int:
    """Three rules, three known answers. Both false positives these rules shipped
    with — a link inside a code span, and a format example in a code block — are
    cases here, because that is how they came back."""
    import tempfile
    ok = True
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "skills").mkdir()
        (root / "skills" / "real.md").write_text("see [it](real.md)\n")
        md = root / "skills" / "SKILL.md"
        md.write_text(
            "python3 ~/.claude/skills/x/y.py\n"          # 1 hardcoded install path
            "[live](real.md)\n"                          # 2 fine, target exists
            "[dead](nope.md)\n"                          # 3 dead link
            "`[shown](example.md)`\n"                    # 4 code span, not a link
            "```\n[fenced](example.md)\n```\n"          # 5 fenced, not a link
            "    [indented](example.md)\n"               # 6 indented, not a link
            "[site](/served/path)\n"                     # 7 site-root, not a file
            "[ph](<placeholder>.md)\n")                  # 8 placeholder
        hits = []
        check_portability("SKILL.md", md, md.read_text(), hits)
        labels = sorted(h[2] for h in hits)
        want = ["dead relative link",
                "hardcoded skill path — address <skill-dir>, resolved from where the skill loaded"]
        if labels != want:
            print(f"selftest FAIL: expected {want}, got {labels}")
            ok = False
    print("selftest passed" if ok else "selftest FAILED")
    return 0 if ok else 1


def main() -> int:
    if "--selftest" in sys.argv:
        return selftest()
    if "--authors" in sys.argv:
        i = sys.argv.index("--authors")
        rng = sys.argv[i + 1] if len(sys.argv) > i + 1 else "@{push}..HEAD"
        return check_authors(rng)

    files = all_files() if "--all" in sys.argv else staged_files()
    if not files:
        return 0

    hard_hits, soft_hits = [], []
    for name in files:
        path = Path(name)
        if not path.is_file() or SKIP_DIRS & set(path.parts):
            continue
        if path.name == "check-no-leaks.py":  # this file names the patterns
            continue
        try:
            text = path.read_text(errors="ignore")
        except OSError:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for pattern, label in HARD:
                for hit in pattern.findall(line):
                    hard_hits.append((name, lineno, label, hit))
            for hit in SOFT.findall(line):
                soft_hits.append((name, lineno, hit))
        check_portability(name, path, text, hard_hits)

    check_shell(files, hard_hits)

    if soft_hits:
        print(f"note: {len(soft_hits)} mention(s) of your own app domains (allowed):")
        for name, lineno, hit in soft_hits[:10]:
            print(f"  {name}:{lineno}  {hit}")
        if len(soft_hits) > 10:
            print(f"  … and {len(soft_hits) - 10} more")

    if hard_hits:
        print("\nBLOCKED — this is a public repo. Fix these before committing:")
        for name, lineno, label, hit in hard_hits:
            print(f"  {name}:{lineno}  {label}: {hit}")
        print("\nOverride once (you are sure it is safe): git commit --no-verify")
        return 1

    print(f"leak check clean — {len(files)} file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
