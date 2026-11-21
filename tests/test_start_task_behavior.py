"""Local-only start-task fixtures and driver, without agent credentials or network."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import Env, git
from test_behavior import behavior, copy, projects  # shared prepared projects fixture

_spec = importlib.util.spec_from_file_location("start_task_behavior", behavior.ROOT / "scripts/start_task_behavior.py")
assert _spec and _spec.loader
driver = importlib.util.module_from_spec(_spec)
sys.path.insert(0, str(behavior.ROOT / "scripts"))
try:
    _spec.loader.exec_module(driver)
finally:
    sys.path.pop(0)

CONFIRM = "Yes, I explicitly confirm these final acceptance criteria."
OUTPUT = ("No remotes configured; skipping fetch and upstream freshness checks.\n"
          'git commit -m "Start --min-length"\n'
          "Implement the active task in TASK.md and verify its acceptance criteria.")


def passing(project: Path) -> None:
    manifest = json.loads(behavior.manifest_path(project).read_text(encoding="utf-8"))
    setup = behavior.fixture_module("B13", "setup")
    task = setup.DRAFT.replace("Status: draft", "Status: active")
    task = task.replace("Base commit:\n", f"Base commit: {manifest['head']}\n")
    task = task.replace("Target branch:\n", "Target branch: main\n")
    task = task.replace("## Context\n", "## Context\n\nAcceptance criteria confirmed by the user: 2026-11-21\n")
    if git(project, "branch", "--show-current") == "main":
        git(project, "switch", "-c", "add-min-length")
    (project / "TASK.md").write_text(task, encoding="utf-8")
    handoff = (behavior.ROOT / "template/.agents/skills/handoff/neutral/HANDOFF.md").read_text(encoding="utf-8")
    handoff = handoff.replace("Last updated: none", "Last updated: 2026-11-21 by test")
    handoff = handoff.replace("Branch: none", "Branch: add-min-length")
    handoff = handoff.replace("Task: none", "Task: standard").replace("## Status\n\nnone", "## Status\n\nnot started")
    (project / "HANDOFF.md").write_text(handoff, encoding="utf-8")
    git(project, "add", "TASK.md", "HANDOFF.md")
    artifact = behavior.manifest_path(project).parent / "transcript.json"
    artifact.write_text(json.dumps({"turns": [{"prompt": CONFIRM, "assistant": OUTPUT}], "error": None}),
                        encoding="utf-8")


@pytest.mark.parametrize("fixture", behavior.START_TASK_FIXTURE_IDS)
def test_local_start_task_passes(projects: dict[str, Path], fixture: str, env: Env, tmp_path: Path) -> None:
    project = copy(projects, fixture, tmp_path)
    assert git(project, "remote") == ""
    assert git(project, "branch", "--show-current") == ("main" if fixture == "B12" else "add-min-length")
    assert ("Status: draft" in (project / "TASK.md").read_text(encoding="utf-8")) == (fixture == "B13")
    passing(project)
    verdict, lines = behavior.check(fixture, project)
    assert verdict == "PASS", "\n".join(lines)
    assert "JUDGE" not in "\n".join(lines)


@pytest.mark.parametrize("explanation", [
    "No remotes are configured, so I'm skipping the fetch and upstream freshness checks.",
    "**Remotes:** none are configured, so I'm skipping the fetch and upstream checks.",
    "No remotes are configured, so I skipped the fetch and upstream freshness checks.",
])
def test_skip_explanation_accepts_equivalent_wording(projects: dict[str, Path], env: Env,
                                                   tmp_path: Path, explanation: str) -> None:
    project = copy(projects, "B12", tmp_path)
    passing(project)
    path = behavior.manifest_path(project).parent / "transcript.json"
    transcript = json.loads(path.read_text(encoding="utf-8"))
    transcript["turns"][0]["assistant"] = OUTPUT.replace(
        "No remotes configured; skipping fetch and upstream freshness checks.",
        explanation)
    path.write_text(json.dumps(transcript), encoding="utf-8")
    verdict, lines = behavior.check("B12", project)
    assert verdict == "PASS", "\n".join(lines)


@pytest.mark.parametrize("fault, expected", [
    ("unstaged", "must be staged"),
    ("extra", "only TASK.md and HANDOFF.md"),
    ("commit", "agent committed"),
    ("hidden_commit", "agent committed"),
    ("remote", "must remain local-only"),
    ("skip", "skip explanation missing"),
    ("push", "push or PR command printed"),
    ("pr", "push or PR command printed"),
    ("commit_output", "commit command missing"),
    ("confirmation", "confirmation was not sent"),
    ("transcript", "invalid agent transcript"),
    ("runner_error", "agent runner failed"),
    ("state", "state.py check reports violations"),
    ("target", "activated task missing"),
])
@pytest.mark.parametrize("fixture", behavior.START_TASK_FIXTURE_IDS)
def test_local_start_task_detects_failure(projects: dict[str, Path], fixture: str, fault: str,
                                         expected: str, env: Env, tmp_path: Path) -> None:
    project = copy(projects, fixture, tmp_path)
    passing(project)
    path = behavior.manifest_path(project).parent / "transcript.json"
    transcript = json.loads(path.read_text(encoding="utf-8"))
    if fault == "unstaged":
        git(project, "reset", "--", "HANDOFF.md")
    elif fault == "extra":
        (project / "implementation.py").write_text("# unexpected\n", encoding="utf-8")
        git(project, "add", "implementation.py")
    elif fault in {"commit", "hidden_commit"}:
        baseline = git(project, "rev-parse", "HEAD")
        git(project, "commit", "--quiet", "-m", "Unexpected activation commit")
        if fault == "hidden_commit":
            git(project, "reset", "--soft", baseline)
    elif fault == "remote":
        git(project, "remote", "add", "offline", "https://example.invalid/project.git")
    elif fault == "skip":
        transcript["turns"][0]["assistant"] = OUTPUT.split("\n", 1)[1]
    elif fault in {"push", "pr"}:
        command = "git -C . push origin main" if fault == "push" else "gh pr create --base main"
        transcript["turns"].insert(0, {"prompt": "initial", "assistant": command})
    elif fault == "commit_output":
        transcript["turns"][0]["assistant"] = OUTPUT.replace('git commit -m "Start --min-length"', "")
    elif fault == "confirmation":
        transcript["turns"][0]["prompt"] = "yes"
    elif fault == "runner_error":
        transcript["error"] = "agent timed out"
    elif fault == "state":
        (project / "HANDOFF.md").write_text("# invalid\n", encoding="utf-8")
        git(project, "add", "HANDOFF.md")
    elif fault == "target":
        task = project / "TASK.md"
        task.write_text(task.read_text(encoding="utf-8").replace("Target branch: main", "Target branch: wrong"),
                        encoding="utf-8")
        git(project, "add", "TASK.md")
    if fault == "transcript":
        path.unlink()
    else:
        path.write_text(json.dumps(transcript), encoding="utf-8")
    verdict, lines = behavior.check(fixture, project)
    assert verdict == "FAIL"
    assert expected in "\n".join(lines)


def events(text: str) -> str:
    return "\n".join(json.dumps(event) for event in [
        {"type": "assistant", "message": {"content": [{"type": "text", "text": text}]}},
        {"type": "result", "is_error": False},
    ])


def test_driver_replies_only_to_interview_prompts() -> None:
    assert driver.next_reply("Round 1\n1. Use standard tier? Recommended: yes.") == \
        "Yes, I accept the recommendations for this round."
    assert driver.next_reply("AC-1: tests pass.\nConfirm these criteria?") == CONFIRM
    with pytest.raises(driver.behavior.HarnessError):
        driver.next_reply("May I implement now?")
    # A round mentioning future confirmation is still only approval of recommendations.
    assert driver.next_reply("Round 1\n1. AC-1: tests pass. Confirm this recommendation?") != CONFIRM


def test_driver_enables_project_skill_without_permission_bypass() -> None:
    command = driver.agent_command("claude", "test-session", False)
    assert command[command.index("--setting-sources") + 1] == "project"
    assert "Skill" in command[command.index("--tools") + 1].split(",")
    assert "Skill(start-task)" in command
    assert command[command.index("--permission-mode") + 1] == "acceptEdits"
    assert "--dangerously-skip-permissions" not in command


def test_driver_reads_assistant_text_without_tool_contents() -> None:
    raw = json.dumps({"type": "assistant", "message": {"content": [
        {"type": "text", "text": "skip explanation"},
        {"type": "tool_use", "name": "Bash", "input": {"command": "cat SKILL.md"}},
    ]}}) + "\n" + json.dumps({"type": "user", "message": {"content": "git push from skill text"}})
    raw += "\n" + events("final answer")
    assert driver.assistant_text(raw) == "skip explanation\nfinal answer"


@pytest.mark.parametrize("raw", ["{}", "not json", events("text").replace('false', 'true'),
                                  events("text").replace('"is_error": false', '"permission_denials": ["Bash"]')])
def test_driver_rejects_incomplete_or_failed_output(raw: str) -> None:
    with pytest.raises((ValueError, driver.behavior.HarnessError)):
        driver.assistant_text(raw)


@pytest.mark.parametrize("failure", [None, "timeout", "exit", "unexpected", "early_activation"])
def test_driver_one_command_runs_both_fixtures_without_real_agent(env: Env, tmp_path: Path,
                                                                failure: str | None,
                                                                capsys: pytest.CaptureFixture[str]) -> None:
    real_run = subprocess.run
    calls: list[list[str]] = []

    def fake_run(args: list[str], **kwargs):
        if args[0] != "fixture-claude":
            return real_run(args, **kwargs)
        if args[1:] == ["--version"]:
            return subprocess.CompletedProcess(args, 0, "fixture-agent\n", "")
        calls.append(args)
        prompt = kwargs["input"]
        if failure == "timeout":
            raise subprocess.TimeoutExpired(args, 1)
        if failure == "exit":
            return subprocess.CompletedProcess(args, 1, "", "missing login")
        if failure == "unexpected":
            text = "Please implement now."
        elif failure == "early_activation" or prompt == CONFIRM:
            passing(Path(kwargs["cwd"]))
            text = OUTPUT
        elif prompt.startswith("Yes,"):
            text = "AC-1: --min-length filters words. Confirm these final criteria?"
        else:
            text = "Round 1\n1. Use standard tier and add-min-length? Recommended: yes."
        return subprocess.CompletedProcess(args, 0, events(text), "")

    env.monkeypatch.setattr(subprocess, "run", fake_run)
    output = tmp_path / "agent-output"
    assert driver.main([str(output), "--claude", "fixture-claude"]) == (0 if failure is None else 1)
    text = capsys.readouterr().out
    assert f"start-task: {'PASS' if failure is None else 'FAIL'}" in text
    for fixture in ("b12", "b13"):
        assert (output / ".behavior" / fixture / "transcript.json").exists()
    assert "--session-id" in calls[0]
    if failure is None:
        assert len(calls) == 6
        assert "--resume" in calls[1]
        assert calls[0][calls[0].index("--session-id") + 1] != calls[3][calls[3].index("--session-id") + 1]


def test_driver_refuses_existing_directory(env: Env, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert driver.main([str(tmp_path)]) == 1
    assert "new output directory" in capsys.readouterr().err
