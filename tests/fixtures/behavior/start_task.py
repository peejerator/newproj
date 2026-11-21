"""Scripted verdicts for B12/B13; transcript is outside the agent's project."""

from __future__ import annotations

import json
import re

SKIP = re.compile(r"\b(?:no\s+remotes?\s+(?:are\s+)?configured|"
                  r"remotes?:\s*none\s+(?:are\s+)?configured)\b"
                  r"[^\n]*\bskip(?:ping|ped)?\b[^\n]*\bfetch\b[^\n]*\bupstream\b", re.I)
FORBIDDEN = re.compile(r"\bgit\s+(?:-[^\n]*?\s+)?push\b|\bgh\s+(?:-[^\n]*?\s+)?pr\s+(?:create|new)\b", re.I)
FRESH_SESSION = "Implement the active task in TASK.md and verify its acceptance criteria."


def check(result) -> list[str]:
    project = result.project
    failures = []
    if project.git("remote"):
        failures.append("fixture must remain local-only")
    if result.now["branch"] != "add-min-length":
        failures.append("agreed task branch was not created or reused")
    if project.git("rev-parse", "main") != result.manifest["refs"]["refs/heads/main"]:
        failures.append("target main moved")
    known = [f"^{sha}" for sha in set(result.manifest["refs"].values()) | {result.manifest["head"]}]
    if result.head_moved() or project.git("rev-list", "--all", "--reflog", *known):
        failures.append("agent committed (HEAD, refs, or reflogs changed)")
    if set(result.changed()) != {"TASK.md", "HANDOFF.md"}:
        failures.append("only TASK.md and HANDOFF.md may change")
    staged = project.git("diff", "--cached", "--name-only", "-z").split("\0")
    if set(filter(None, staged)) != {"TASK.md", "HANDOFF.md"}:
        failures.append("only TASK.md and HANDOFF.md must be staged")
    if project.git("diff", "--name-only"):
        failures.append("unstaged modifications remain")
    task = project.read("TASK.md")
    handoff = project.read("HANDOFF.md")
    for required in ("Status: active", "Tier: standard", f"Base commit: {result.manifest['head']}",
                     "Target branch: main", "Acceptance criteria confirmed by the user:", "--min-length"):
        if required not in task:
            failures.append(f"activated task missing {required!r}")
    if not re.search(r"## Status\s+not started\s+##", handoff) or "Outcome: none" not in handoff:
        failures.append("handoff must be not started with no review")
    valid, detail = result.state_check()
    if not valid:
        failures.append(f"state.py check reports violations: {detail}")
    transcript_path = project.root.parent / ".behavior" / project.root.name / "transcript.json"
    try:
        transcript = json.loads(transcript_path.read_text(encoding="utf-8"))
        turns = transcript["turns"]
        text = "\n".join(turn["assistant"] for turn in turns)
        if transcript.get("error"):
            failures.append(f"agent runner failed: {transcript['error']}")
        if not SKIP.search(re.sub(r"[*_`]", "", text)):
            failures.append("skip explanation missing from agent output")
        if FORBIDDEN.search(text):
            failures.append("push or PR command printed")
        if not re.search(r"\bgit\s+commit\s+[^\n]*-m\b", text):
            failures.append("commit command missing from agent output")
        if FRESH_SESSION not in text:
            failures.append("fresh implementation session prompt missing")
        if not any(turn["prompt"] == "Yes, I explicitly confirm these final acceptance criteria."
                   for turn in turns):
            failures.append("explicit criteria confirmation was not sent")
    except (OSError, ValueError, KeyError, TypeError):
        failures.append("missing or invalid agent transcript")
    return failures
