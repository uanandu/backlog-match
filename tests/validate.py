#!/usr/bin/env python3
"""Static checks for the backlog-match plugin. Standard library only.

Run from anywhere:  python3 tests/validate.py
Exits non-zero if any check fails. These catch the mistakes that are easy to
make when editing the skills by hand (drifting versions, broken step
references, allow rules Claude Code silently ignores, stale tool names). They
do not run the skills; behavior is covered by tests/evals.json.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
errors = []


def fail(msg):
    errors.append(msg)


def frontmatter(text):
    parts = text.split("---", 2)
    return (parts[1], parts[2]) if len(parts) == 3 else ("", text)


def mcp_rule_anchored(rule):
    """True if an MCP allow rule names a literal server (glob-free) first."""
    return bool(re.fullmatch(r"mcp__[^*_][^*]*?(__.*)?", rule)) and "*" not in rule.split("__")[1]


def check_manifests():
    plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
    market = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
    entry = next((p for p in market.get("plugins", []) if p.get("name") == plugin["name"]), None)
    if entry is None:
        fail(f"marketplace.json has no plugin entry named {plugin['name']!r}")
        return
    for key in ("version", "description"):
        if plugin.get(key) != entry.get(key):
            fail(f"plugin.json and marketplace.json disagree on {key!r}")
    if "email" in market.get("owner", {}):
        fail("marketplace.json publishes an owner email; remove it")


def check_skill(skill_dir):
    name = skill_dir.name
    text = (skill_dir / "SKILL.md").read_text()
    fm, body = frontmatter(text)

    if not re.search(rf"^name: {re.escape(name)}$", fm, re.M):
        fail(f"{name}: frontmatter name must equal the directory name")
    m = re.search(r"^description: >-\n((?:  .*\n)+)", fm, re.M)
    if not m:
        fail(f"{name}: missing folded description")
    else:
        desc = " ".join(line.strip() for line in m.group(1).splitlines())
        if len(desc) > 1024:
            fail(f"{name}: description is {len(desc)} chars (limit 1024)")
    if not re.search(r'^  version: "\d+\.\d+\.\d+"$', fm, re.M):
        fail(f"{name}: metadata.version missing or not quoted semver")
    if "generatedBy" in fm:
        fail(f"{name}: stale generatedBy field")

    # Allow rules Claude Code ignores: MCP globs are only honored after a
    # literal mcp__<server>__ prefix, so a bare mcp__* pre-approves nothing.
    tools = re.findall(r"^  - (.+)$", fm.split("allowed-tools:", 1)[-1], re.M) if "allowed-tools:" in fm else []
    for t in tools:
        t = t.strip()
        if t == "*" or (t.startswith("mcp__") and not mcp_rule_anchored(t)):
            fail(f"{name}: allow rule {t!r} is unanchored and will be ignored")
    if any(t.startswith("Bash(gh") for t in tools):
        fail(f"{name}: gh is deliberately not used")

    # Every "step N" reference must point at a real top-level step.
    steps = {int(n) for n in re.findall(r"^(\d+)\. ", body, re.M)}
    for ref in re.findall(r"\bsteps? (\d+)", body):
        if int(ref) not in steps:
            fail(f"{name}: reference to step {ref}, but steps are {sorted(steps)}")
    if steps and steps != set(range(1, max(steps) + 1)):
        fail(f"{name}: top-level steps are not consecutive: {sorted(steps)}")

    for stale in ("getTransitionsForJiraIssue", "addCommentToJiraIssue"):
        if stale in text:
            fail(f"{name}: stale Jira tool name {stale}")
    if re.search(r"\bgh (pr|api|repo)\b", text):
        fail(f"{name}: mentions the gh CLI")


def check_repo():
    readme = (ROOT / "README.md").read_text()
    for d in sorted((ROOT / "skills").iterdir()):
        if d.is_dir() and d.name not in readme:
            fail(f"README.md never mentions skill {d.name!r}")
    gi = (ROOT / ".gitignore").read_text()
    for pattern in ("*.local.md", ".claude/settings.local.json"):
        if pattern not in gi:
            fail(f".gitignore is missing {pattern!r}")
    try:
        tracked = subprocess.run(
            ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
        ).stdout.split()
    except (OSError, subprocess.CalledProcessError):
        return  # not a git checkout (e.g. a source tarball)
    for f in tracked:
        if f.endswith(".local.md") or f.endswith("settings.local.json"):
            fail(f"private file is tracked: {f}")


def check_evals():
    path = ROOT / "tests/evals.json"
    data = json.loads(path.read_text())
    skills = {d.name for d in (ROOT / "skills").iterdir() if d.is_dir()}
    for case in data.get("cases", []):
        if case.get("skill") not in skills | {None}:
            fail(f"evals.json: unknown skill {case.get('skill')!r} in {case.get('id')}")
        if not case.get("id") or not case.get("prompt"):
            fail(f"evals.json: case needs id and prompt: {case}")
        if "should_trigger" not in case or not case.get("expect"):
            fail(f"evals.json: case {case.get('id')} needs should_trigger and expect")


def main():
    check_manifests()
    for d in sorted((ROOT / "skills").iterdir()):
        if (d / "SKILL.md").exists():
            check_skill(d)
    check_repo()
    check_evals()
    if errors:
        print(f"{len(errors)} problem(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("ok: manifests, skills, repo hygiene and evals all consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
