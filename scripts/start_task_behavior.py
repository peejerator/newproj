"""Run B12/B13 locally with Claude Code; never invoked by pytest or CI.

    uv run python scripts/start_task_behavior.py <new-directory>

Requires an installed, authenticated `claude`. Uses only synthetic projects.
Manifests, raw JSONL events, and normalized transcripts live outside the projects.
The test driver answers numbered recommendation rounds and then explicitly
confirms criteria shown by the agent. It never supplies a completed contract.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

import behavior

CONFIRM = "Yes, I explicitly confirm these final acceptance criteria."
FINISH = "Implement the active task in TASK.md and verify its acceptance criteria."


def next_reply(text: str) -> str:
    """Fail closed on unexpected questions; never authorize implementation."""
    if re.search(r"\bRound\s+\d+\b", text, re.I) and re.search(r"^\s*\d+[.)]", text, re.M):
        return "Yes, I accept the recommendations for this round."
    if re.search(r"AC-\d+", text) and re.search(r"confirm|approv", text, re.I):
        return CONFIRM
    raise behavior.HarnessError("agent did not present a numbered round or criteria for confirmation")


def assistant_text(raw: str) -> str:
    """Include all assistant text, excluding tool inputs and tool-result file contents."""
    texts = []
    finished = False
    for line in raw.splitlines():
        event = json.loads(line)
        if event.get("type") == "assistant":
            texts.extend(block["text"] for block in event["message"]["content"]
                         if block.get("type") == "text")
        if event.get("type") == "result":
            finished = True
            if event.get("is_error") or event.get("permission_denials"):
                raise behavior.HarnessError("agent returned an error or a tool permission denial; inspect JSONL")
    if not finished or not texts:
        raise behavior.HarnessError("agent output lacks a completed result or assistant text")
    return "\n".join(texts)


def agent_command(executable: str, session: str, resume: bool) -> list[str]:
    return [executable, "-p", "--output-format", "stream-json", "--verbose",
            "--resume" if resume else "--session-id", session,
            "--setting-sources", "project", "--settings", '{"disableAllHooks":true}',
            "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
            "--tools", "Read,Glob,Grep,Edit,Write,Bash,Skill", "--permission-mode", "acceptEdits",
            "--append-system-prompt", "Use Read, Glob and Grep for file inspection. The Bash allowlist "
            "covers simple git, Python, uv state and echo commands only; avoid shell loops and substitutions.",
            "--allowedTools", "Read", "Glob", "Grep", "Edit", "Write", "Skill(start-task)", "Bash(git *)",
            "Bash(python3 *)", "Bash(python *)", "Bash(uv run --no-project *)", "Bash(echo *)"]


def run_fixture(fixture: str, root: Path, template: Path, executable: str,
                version: str, timeout: int) -> bool:
    project = root / fixture.lower()
    behavior.setup(fixture, project, template)
    artifact_dir = behavior.manifest_path(project).parent
    prompt = (behavior.FIXTURES / fixture / "prompt.txt").read_text(encoding="utf-8")
    session = str(uuid.uuid4())
    transcript: dict = {"agent_version": version, "session": session, "turns": [], "error": None}
    try:
        for index in range(5):
            print(f"{fixture}: agent turn {index + 1}", flush=True)
            process = subprocess.run(agent_command(executable, session, index > 0), cwd=project,
                                     input=prompt, capture_output=True, text=True, encoding="utf-8",
                                     errors="replace", timeout=timeout, env=behavior.git_env(), check=False)
            (artifact_dir / f"turn-{index + 1}.jsonl").write_text(process.stdout, encoding="utf-8")
            (artifact_dir / f"turn-{index + 1}.stderr.txt").write_text(process.stderr, encoding="utf-8")
            if process.returncode:
                raise behavior.HarnessError(f"agent exited {process.returncode}; inspect turn-{index + 1} artifacts")
            text = assistant_text(process.stdout)
            transcript["turns"].append({"prompt": prompt, "assistant": text})
            # Check activation separately: a quoted stop prompt alone does not finish the run.
            if re.search(r"^Status: active$", (project / "TASK.md").read_text(encoding="utf-8"), re.M):
                if prompt != CONFIRM or FINISH not in text:
                    raise behavior.HarnessError("agent activated without this turn's explicit confirmation or stop prompt")
                break
            prompt = next_reply(text)
        else:
            raise behavior.HarnessError("agent did not finish within five turns")
    except (behavior.HarnessError, OSError, ValueError, KeyError, subprocess.TimeoutExpired) as error:
        transcript["error"] = str(error)
    (artifact_dir / "transcript.json").write_text(json.dumps(transcript, indent=2) + "\n", encoding="utf-8")
    verdict, lines = behavior.check(fixture, project)
    print("\n".join(lines), flush=True)
    print(f"Artifacts: {artifact_dir}", flush=True)
    return verdict == "PASS"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dir", type=Path, help="new output directory outside any Git repository")
    parser.add_argument("--claude", default="claude", help="Claude Code executable")
    parser.add_argument("--timeout", type=int, default=300, help="maximum seconds per agent turn")
    args = parser.parse_args(argv)
    root = args.dir.resolve()
    try:
        if args.timeout <= 0:
            raise behavior.HarnessError("timeout must be positive")
        if root.exists() or behavior.inside_git_repository(root):
            raise behavior.HarnessError("choose a new output directory outside any Git repository")
        version = subprocess.run([args.claude, "--version"], capture_output=True, text=True,
                                 encoding="utf-8", check=True, timeout=15).stdout.strip()
        root.mkdir(parents=True)
        # A plain working-tree copy includes uncommitted skill fixes and avoids Copier's Git clone.
        template = root / "template-source"
        shutil.copytree(behavior.ROOT / "template", template / "template")
        shutil.copy2(behavior.ROOT / "copier.yml", template / "copier.yml")
        print(f"Agent: {version}", flush=True)
        passed = [run_fixture(f, root, template, args.claude, version, args.timeout)
                  for f in behavior.START_TASK_FIXTURE_IDS]
    except (behavior.HarnessError, OSError, subprocess.SubprocessError) as error:
        print(f"start-task: FAIL: {error}", file=sys.stderr)
        return 1
    print(f"start-task: {'PASS' if all(passed) else 'FAIL'}", flush=True)
    return 0 if all(passed) else 1


if __name__ == "__main__":
    sys.exit(main())
