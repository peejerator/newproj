"""`newproj doctor` (spec section 20.7, Phase 1 checks), on projects made by `newproj new`."""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

from conftest import Env, git, newproj, write_gitconfig
from newproj import doctor, state

LINE = re.compile(r"  (PASS|WARN|FAIL|INFO)  ?(.*)")


def run_doctor(path: Path, capfd: pytest.CaptureFixture[str]) -> tuple[int, str, list[tuple[str, str]]]:
    code = newproj("doctor", str(path))
    out = capfd.readouterr().out
    checks = [(m[1], m[2].strip()) for line in out.splitlines() if (m := LINE.fullmatch(line))]
    return code, out, checks


def levels(checks: list[tuple[str, str]], level: str) -> list[str]:
    return [message for found, message in checks if found == level]


def has(checks: list[tuple[str, str]], level: str, text: str) -> bool:
    return any(text in message for message in levels(checks, level))


def commit_all(project: Path, message: str = "Change", *extra: str) -> None:
    git(project, "add", "-A")
    git(project, "commit", "--quiet", "-m", message, *extra)


TASK = """# Task

Status: {status}
Tier: {tier}
Task ID: {task_id}
Base commit: {base}
Target branch: main

## Goal

Add a feature.

## Context

## Scope

## Acceptance criteria

- AC-1: It works.

## Relevant areas

## Validation

## Do not change

## Open questions
"""

HANDOFF = """# Handoff

Last updated: 2026-10-19
Branch: main
Task: Add a feature

## Status

{status}

## Completed

## Current working area

## Validation

## Review

{review}

## Exact next steps

## Blockers / open questions

## Relevant decisions
"""


def start_task(project: Path, status: str = "active", tier: str = "standard", task_id: str = "",
               base: str | None = None, handoff_status: str = "in progress", commit: bool = True) -> None:
    base = git(project, "rev-parse", "HEAD") if base is None else base
    (project / "TASK.md").write_text(TASK.format(status=status, tier=tier, task_id=task_id, base=base),
                                     encoding="utf-8", newline="\n")
    (project / "HANDOFF.md").write_text(HANDOFF.format(status=handoff_status, review="Outcome: none"),
                                        encoding="utf-8", newline="\n")
    if commit:
        commit_all(project, "Start task")


def record_review(project: Path) -> None:
    head = git(project, "rev-parse", "HEAD")
    contract = git(project, "hash-object", "TASK.md")
    review = (f"Outcome: PASS\nReviewer: tool/model, 2026-10-19\nReviewed at: {head}\nContract: {contract}\n"
              "Working tree clean at review: yes")
    (project / "HANDOFF.md").write_text(HANDOFF.format(status="complete", review=review),
                                        encoding="utf-8", newline="\n")
    commit_all(project, "Record review")


# AC-9: new, then doctor, then a lightweight change


def test_fresh_project_has_no_fail(project: Path, capfd: pytest.CaptureFixture[str]) -> None:
    code, out, checks = run_doctor(project, capfd)
    assert code == 0, out
    assert levels(checks, "FAIL") == []
    assert levels(checks, "WARN") == []
    assert has(checks, "INFO", "Template version: development render from")
    assert has(checks, "INFO", "Template update check: arrives with newproj update")
    assert has(checks, "PASS", "Default branch: main")
    assert has(checks, "INFO", "git remote set-head origin --auto")


def test_lightweight_change_keeps_no_fail(project: Path, capfd: pytest.CaptureFixture[str]) -> None:
    with (project / "README.md").open("a", encoding="utf-8", newline="\n") as stream:
        stream.write("\nBuild with make.\n")
    (project / "src").mkdir()
    (project / "src" / "main.py").write_text("print('hello')\n", encoding="utf-8", newline="\n")
    commit_all(project, "Add main.py")
    code, out, checks = run_doctor(project, capfd)
    assert code == 0, out
    assert levels(checks, "FAIL") == []


# AC-2: outside a managed project


def test_outside_project(env: Env, capfd: pytest.CaptureFixture[str]) -> None:
    code, out, checks = run_doctor(env.work, capfd)
    assert code == 0, out
    for text in ["git:", "gh:", "uv:", "Copier", "Git user.name: Test User", "Git user.email: test@example.com",
                 "gh is authenticated", "Git credential helper configured"]:
        assert has(checks, "PASS", text), text
    assert has(checks, "INFO", "not inside a managed project")
    assert not any(title.startswith("Project:") for title in out.splitlines())


def test_environment_problems(env: Env, capfd: pytest.CaptureFixture[str]) -> None:
    write_gitconfig(env.gitconfig, identity=False)
    git(env.work, "config", "--global", "--unset", "credential.helper")
    env.gh_mode("unauthenticated")
    code, out, checks = run_doctor(env.work, capfd)
    assert code == 1
    assert has(checks, "FAIL", "Git user.name is not set")
    assert has(checks, "FAIL", "Git user.email is not set")
    assert has(checks, "WARN", "gh is not authenticated")
    assert has(checks, "WARN", "No Git credential setup found")
    assert "gh auth setup-git" in out


def test_ssh_key_counts_as_credentials(env: Env, capfd: pytest.CaptureFixture[str]) -> None:
    git(env.work, "config", "--global", "--unset", "credential.helper")
    ssh = Path.home() / ".ssh"
    ssh.mkdir()
    (ssh / "id_ed25519.pub").write_text("ssh-ed25519 AAAA test\n", encoding="utf-8")
    _, _, checks = run_doctor(env.work, capfd)
    assert has(checks, "PASS", "SSH keys found")


def test_missing_tools(env: Env, monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setenv("PATH", str(env.tmp / "empty"))
    code, _, checks = run_doctor(env.work, capfd)
    assert code == 1
    assert has(checks, "FAIL", "git is not available")
    assert has(checks, "WARN", "gh is not available")
    assert has(checks, "WARN", "uv is not available")


# AC-3: template version


def test_template_version_from_url(project: Path, capfd: pytest.CaptureFixture[str]) -> None:
    answers = project / ".copier-answers.yml"
    text = re.sub(r"_src_path: .*", "_src_path: https://github.com/peejerator/newproj.git",
                  answers.read_text(encoding="utf-8"))
    answers.write_text(text.replace("_src_path:", "_commit: v0.1.0\n_src_path:"), encoding="utf-8", newline="\n")
    _, _, checks = run_doctor(project, capfd)
    assert has(checks, "INFO", "Template version: v0.1.0 (from https://github.com/peejerator/newproj.git)")


def test_subdirectory_finds_project(project: Path, capfd: pytest.CaptureFixture[str]) -> None:
    code, out, _ = run_doctor(project / "docs", capfd)
    assert code == 0
    assert f"Project: {project.resolve()}" in out


# AC-3: project-owned files


@pytest.mark.parametrize("name", doctor.REQUIRED)
def test_required_file_missing(name: str, project: Path, capfd: pytest.CaptureFixture[str]) -> None:
    (project / name).unlink()
    code, out, checks = run_doctor(project, capfd)
    assert code == 1
    assert has(checks, "FAIL", f"Required project-owned file missing: {name}")
    assert f"git checkout HEAD -- {name}" in out


def test_required_file_deleted_in_history(project: Path, capfd: pytest.CaptureFixture[str]) -> None:
    git(project, "rm", "--quiet", "docs/DECISIONS.md")
    git(project, "commit", "--quiet", "-m", "Remove decisions")
    deleted = git(project, "rev-parse", "--short=7", "HEAD")
    _, out, _ = run_doctor(project, capfd)
    assert re.search(rf"git checkout {deleted}\w*\^ -- docs/DECISIONS\.md", out)


@pytest.mark.parametrize("name", ["CLAUDE.md", "README.md", ".env.example"])
def test_optional_file_missing(name: str, project: Path, capfd: pytest.CaptureFixture[str]) -> None:
    (project / name).unlink()
    code, _, checks = run_doctor(project, capfd)
    assert code == 0
    assert has(checks, "WARN", f"Optional project-owned file missing: {name}")


def test_license_expected_only_when_chosen(project: Path, capfd: pytest.CaptureFixture[str]) -> None:
    _, _, checks = run_doctor(project, capfd)
    assert not has(checks, "WARN", "LICENSE")
    answers = project / ".copier-answers.yml"
    answers.write_text(answers.read_text(encoding="utf-8").replace("license: none", "license: MIT"),
                       encoding="utf-8", newline="\n")
    _, _, checks = run_doctor(project, capfd)
    assert has(checks, "WARN", "Optional project-owned file missing: LICENSE")


# AC-3: protocol and skills


def test_protocol_missing(project: Path, capfd: pytest.CaptureFixture[str]) -> None:
    (project / "docs" / "AGENT_PROTOCOL.md").unlink()
    code, _, checks = run_doctor(project, capfd)
    assert code == 1
    assert has(checks, "FAIL", "docs/AGENT_PROTOCOL.md is missing")


@pytest.mark.parametrize("name", doctor.SKILLS)
def test_skill_missing(name: str, project: Path, capfd: pytest.CaptureFixture[str]) -> None:
    shutil.rmtree(project / ".agents" / "skills" / name)
    code, out, checks = run_doctor(project, capfd)
    assert code == 1
    assert has(checks, "FAIL", f"Malformed or incomplete skill: {name}")
    assert f".agents/skills/{name}/SKILL.md is missing" in out


@pytest.mark.parametrize("edit, expected", [
    (lambda t: t.replace("---\n", "", 1), "has no well-formed frontmatter"),
    (lambda t: t.replace("name: review", "name: other"), "expected 'review'"),
    (lambda t: re.sub(r"description: .*", "description:", t, count=1), "has no description"),
    (lambda t: t.replace("disable-model-invocation: true\n", ""), "lacks disable-model-invocation: true"),
])
def test_skill_malformed(edit: object, expected: str, project: Path, capfd: pytest.CaptureFixture[str]) -> None:
    path = project / ".agents" / "skills" / "review" / "SKILL.md"
    path.write_text(edit(path.read_text(encoding="utf-8")), encoding="utf-8", newline="\n")  # type: ignore[operator]
    code, out, checks = run_doctor(project, capfd)
    assert code == 1
    assert has(checks, "FAIL", "Malformed or incomplete skill: review")
    assert expected in out


@pytest.mark.parametrize("path, expected", [
    ("accept/agents/openai.yaml", "accept/agents/openai.yaml is missing"),
    ("handoff/neutral/TASK.md", "handoff/neutral/TASK.md is missing"),
    ("resume/scripts/state.py", "resume/scripts/state.py is missing"),
])
def test_skill_file_missing(path: str, expected: str, project: Path, capfd: pytest.CaptureFixture[str]) -> None:
    (project / ".agents" / "skills" / path).unlink()
    code, out, _ = run_doctor(project, capfd)
    assert code == 1
    assert expected in out


@pytest.mark.parametrize("policy", [
    "policy:\n  allow_implicit_invocation: true\n",
    "unrelated:\n  allow_implicit_invocation: false\n",
    "policy:\n  other:\n    allow_implicit_invocation: false\n",
    "allow_implicit_invocation: false\n",
])
def test_openai_yaml_policy(policy: str, project: Path, capfd: pytest.CaptureFixture[str]) -> None:
    path = project / ".agents" / "skills" / "bootstrap" / "agents" / "openai.yaml"
    path.write_text(policy, encoding="utf-8", newline="\n")
    code, out, _ = run_doctor(project, capfd)
    assert code == 1
    assert "lacks allow_implicit_invocation: false" in out


@pytest.mark.parametrize("edit, expected", [
    (None, "is missing"),
    (lambda t: t.replace("description:", "description: changed"), "frontmatter differs"),
    (lambda t: t.replace(".agents/skills/handoff/SKILL.md", "elsewhere.md"), "does not point to"),
])
def test_broken_pointer(edit: object, expected: str, project: Path, capfd: pytest.CaptureFixture[str]) -> None:
    path = project / ".claude" / "skills" / "handoff" / "SKILL.md"
    if edit is None:
        path.unlink()
    else:
        path.write_text(edit(path.read_text(encoding="utf-8")), encoding="utf-8", newline="\n")  # type: ignore[operator]
    code, out, checks = run_doctor(project, capfd)
    assert code == 1
    assert has(checks, "FAIL", "Broken Claude pointer: handoff")
    assert expected in out


# AC-3: AGENTS.md and CLAUDE.md


def test_agents_md_protocol_line(project: Path, capfd: pytest.CaptureFixture[str]) -> None:
    path = project / "AGENTS.md"
    path.write_text(path.read_text(encoding="utf-8").replace(doctor.PROTOCOL_LINE + "\n", ""),
                    encoding="utf-8", newline="\n")
    code, out, checks = run_doctor(project, capfd)
    assert code == 1
    assert has(checks, "FAIL", "AGENTS.md does not reference the protocol")
    assert f"        {doctor.PROTOCOL_LINE}\n" in out


@pytest.mark.parametrize("line", doctor.CLAUDE_IMPORTS)
def test_claude_md_import(line: str, project: Path, capfd: pytest.CaptureFixture[str]) -> None:
    path = project / "CLAUDE.md"
    path.write_text(path.read_text(encoding="utf-8").replace(line + "\n", ""), encoding="utf-8", newline="\n")
    code, out, checks = run_doctor(project, capfd)
    assert code == 1
    assert has(checks, "FAIL", f"CLAUDE.md does not import {line[1:]}")
    assert f"        {line}\n" in out


# AC-3: task files


def test_task_format_problem(project: Path, capfd: pytest.CaptureFixture[str]) -> None:
    start_task(project)
    path = project / "HANDOFF.md"
    path.write_text(path.read_text(encoding="utf-8").replace("## Completed", "## Done"),
                    encoding="utf-8", newline="\n")
    code, out, checks = run_doctor(project, capfd)
    assert code == 1
    assert has(checks, "FAIL", "break their format rules")
    assert "HANDOFF.md:" in out and "unexpected heading '## Done'" in out


def test_invalid_status(project: Path, capfd: pytest.CaptureFixture[str]) -> None:
    start_task(project, status="started")
    code, out, _ = run_doctor(project, capfd)
    assert code == 1
    assert "invalid Status: 'started'" in out


def test_neutral_not_byte_identical(project: Path, capfd: pytest.CaptureFixture[str]) -> None:
    path = project / "TASK.md"
    path.write_text(path.read_text(encoding="utf-8") + "\nextra\n", encoding="utf-8", newline="\n")
    code, out, checks = run_doctor(project, capfd)
    assert code == 0
    assert has(checks, "WARN", "TASK.md is neutral but not byte-identical to its neutral copy")
    assert "+extra" in out and "--- .agents/skills/handoff/neutral/TASK.md" in out


def test_neutral_with_header_values(project: Path, capfd: pytest.CaptureFixture[str]) -> None:
    path = project / "TASK.md"
    path.write_text(path.read_text(encoding="utf-8").replace("Tier:", "Tier: standard"),
                    encoding="utf-8", newline="\n")
    code, _, checks = run_doctor(project, capfd)
    assert code == 0
    assert has(checks, "WARN", "Status: none but non-empty header values: Tier")


@pytest.mark.parametrize("status", ["draft", "active"])
def test_tier_required(status: str, project: Path, capfd: pytest.CaptureFixture[str]) -> None:
    start_task(project, status=status, tier="")
    code, _, checks = run_doctor(project, capfd)
    assert code == 1
    assert has(checks, "FAIL", f"TASK.md has Status: {status} but Tier: (empty)")


def test_active_standard_task_passes(project: Path, capfd: pytest.CaptureFixture[str]) -> None:
    start_task(project)
    code, out, checks = run_doctor(project, capfd)
    assert code == 0, out
    assert levels(checks, "WARN") == []
    assert has(checks, "INFO", "Recovery signals (state.py)")
    assert "Base commit resolves and is an ancestor of HEAD" in out


def test_base_commit_missing(project: Path, capfd: pytest.CaptureFixture[str]) -> None:
    start_task(project, base="")
    code, out, _ = run_doctor(project, capfd)
    assert code == 1
    assert "an active task needs a Base commit (ERRATA E-007)" in out


def test_base_commit_unresolvable(project: Path, capfd: pytest.CaptureFixture[str]) -> None:
    start_task(project, base="0123456789abcdef0123456789abcdef01234567")
    code, out, _ = run_doctor(project, capfd)
    assert code == 1
    assert "does not resolve to a commit" in out


def test_standard_task_id(project: Path, capfd: pytest.CaptureFixture[str]) -> None:
    start_task(project, task_id="T-1")
    code, _, checks = run_doctor(project, capfd)
    assert code == 0
    assert has(checks, "WARN", "An active standard task has a Task ID")


def test_formal_task_deferred(project: Path, capfd: pytest.CaptureFixture[str]) -> None:
    start_task(project, tier="formal")
    _, _, checks = run_doctor(project, capfd)
    assert has(checks, "INFO", "Formal-task checks arrive in Phase 2")


@pytest.mark.parametrize("neutral", ["TASK.md", "HANDOFF.md"])
def test_partial_neutral(neutral: str, project: Path, capfd: pytest.CaptureFixture[str]) -> None:
    start_task(project, handoff_status="none" if neutral == "HANDOFF.md" else "in progress")
    if neutral == "TASK.md":
        shutil.copyfile(project / ".agents/skills/handoff/neutral/TASK.md", project / "TASK.md")
    _, _, checks = run_doctor(project, capfd)
    other = "HANDOFF.md" if neutral == "TASK.md" else "TASK.md"
    assert has(checks, "WARN", f"{neutral} is neutral but {other} is not")


def test_stale_handoff(project: Path, capfd: pytest.CaptureFixture[str]) -> None:
    start_task(project)
    (project / "feature.py").write_text("x = 1\n", encoding="utf-8")
    commit_all(project, "Add feature")
    _, _, checks = run_doctor(project, capfd)
    assert has(checks, "WARN", "HANDOFF.md is stale: 1 commit since the last handoff")


def test_recovery_signals_only_while_active(project: Path, capfd: pytest.CaptureFixture[str]) -> None:
    _, _, checks = run_doctor(project, capfd)
    assert not has(checks, "INFO", "Recovery signals")
    start_task(project, status="draft")
    _, _, checks = run_doctor(project, capfd)
    assert not has(checks, "INFO", "Recovery signals")


# AC-3: review


def test_review_outcome_missing(project: Path, capfd: pytest.CaptureFixture[str]) -> None:
    start_task(project)
    path = project / "HANDOFF.md"
    path.write_text(path.read_text(encoding="utf-8").replace("Outcome: none", ""), encoding="utf-8", newline="\n")
    code, out, checks = run_doctor(project, capfd)
    assert code == 1
    assert "'## Review' has no 'Outcome:' line" in out
    assert not has(checks, "PASS", "## Review has an Outcome: line")


def test_review_none(project: Path, capfd: pytest.CaptureFixture[str]) -> None:
    start_task(project)
    _, _, checks = run_doctor(project, capfd)
    assert ("INFO", "Review: none") in checks
    assert ("INFO", "Current review: none") in checks


def test_review_current_pass(project: Path, capfd: pytest.CaptureFixture[str]) -> None:
    start_task(project)
    record_review(project)
    _, _, checks = run_doctor(project, capfd)
    short = git(project, "rev-parse", "HEAD~1")[:7]
    assert ("INFO", f"Review: PASS (current) at {short}, 2026-10-19") in checks
    assert ("INFO", "Current review: PASS") in checks


def test_review_historical(project: Path, capfd: pytest.CaptureFixture[str]) -> None:
    start_task(project)
    record_review(project)
    (project / "feature.py").write_text("x = 2\n", encoding="utf-8")
    _, out, checks = run_doctor(project, capfd)
    assert has(checks, "INFO", "Review: PASS (historical) at")
    assert "invalidated by: 1 uncommitted change outside HANDOFF.md" in out
    assert ("INFO", "Current review: none") in checks
    lines = out.splitlines()
    first = next(i for i, line in enumerate(lines) if "Review: PASS (historical)" in line)
    assert "invalidated by:" in lines[first + 1] and "Current review: none" in lines[first + 2]


# AC-3: repository state


def make_conflict(project: Path) -> None:
    git(project, "switch", "--quiet", "-c", "other")
    (project / "README.md").write_text("other\n", encoding="utf-8")
    commit_all(project, "Other")
    git(project, "switch", "--quiet", "main")
    (project / "README.md").write_text("main\n", encoding="utf-8")
    commit_all(project, "Main")
    git(project, "merge", "--quiet", "other", check=False)


def test_merge_conflict(project: Path, capfd: pytest.CaptureFixture[str]) -> None:
    make_conflict(project)
    code, out, checks = run_doctor(project, capfd)
    assert code == 1
    assert has(checks, "FAIL", "Unmerged paths")
    assert has(checks, "FAIL", "Unresolved conflict markers")
    assert has(checks, "WARN", "A merge is in progress")
    assert "README.md:1:<<<<<<< HEAD" in out


def test_conflict_markers_committed(project: Path, capfd: pytest.CaptureFixture[str]) -> None:
    (project / "notes.md").write_text("a\n<<<<<<< HEAD\nb\n=======\nc\n>>>>>>> other\n", encoding="utf-8")
    code, _, checks = run_doctor(project, capfd)
    assert code == 1
    assert has(checks, "FAIL", "Unresolved conflict markers")
    assert not has(checks, "FAIL", "Unmerged paths")


def test_setext_heading_is_not_a_marker(project: Path, capfd: pytest.CaptureFixture[str]) -> None:
    (project / "notes.md").write_text("Title\n=======\n", encoding="utf-8")
    code, _, _ = run_doctor(project, capfd)
    assert code == 0


def test_rebase_in_progress(project: Path, capfd: pytest.CaptureFixture[str]) -> None:
    make_conflict(project)
    git(project, "merge", "--abort")
    git(project, "switch", "--quiet", "other")
    git(project, "rebase", "--quiet", "main", check=False)
    _, _, checks = run_doctor(project, capfd)
    assert has(checks, "WARN", "A rebase is in progress")


# AC-3: size budgets and ignore rules


def test_size_budgets(project: Path, capfd: pytest.CaptureFixture[str]) -> None:
    for name in ["AGENTS.md", "docs/AGENT_PROTOCOL.md"]:
        with (project / name).open("a", encoding="utf-8", newline="\n") as stream:
            stream.write("line\n" * 200)
    code, _, checks = run_doctor(project, capfd)
    assert code == 0
    assert has(checks, "WARN", "AGENTS.md has")
    assert has(checks, "WARN", "docs/AGENT_PROTOCOL.md has")


@pytest.mark.parametrize("rule", [".env", ".env.*", "!.env.example"])
def test_ignore_rules(rule: str, project: Path, capfd: pytest.CaptureFixture[str]) -> None:
    path = project / ".gitignore"
    lines = path.read_text(encoding="utf-8").splitlines()
    lines.remove(rule)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    code, out, checks = run_doctor(project, capfd)
    assert code == 0
    assert has(checks, "WARN", "Secret-ignore rules missing")
    assert f"        {rule}\n" in out


# AC-3: default branch


def test_default_branch_unresolved(project: Path, capfd: pytest.CaptureFixture[str]) -> None:
    git(project, "branch", "--quiet", "-m", "main", "work")
    git(project, "config", "--global", "--unset", "init.defaultBranch")
    _, out, checks = run_doctor(project, capfd)
    assert has(checks, "WARN", "The default branch does not resolve")
    assert "git remote set-head origin --auto" in out


def test_default_branch_with_remote(env: Env, capfd: pytest.CaptureFixture[str]) -> None:
    assert newproj("new", "demo", "--template-path", str(env.template)) == 0
    capfd.readouterr()
    _, _, checks = run_doctor(env.work / "demo", capfd)
    assert has(checks, "PASS", "Default branch: main (step 1: refs/remotes/origin/HEAD)")
    assert not has(checks, "INFO", "set-head")


# AC-5: attribution


def test_hooks_path_not_set(project: Path, capfd: pytest.CaptureFixture[str]) -> None:
    git(project, "config", "--unset", "core.hooksPath")
    code, out, checks = run_doctor(project, capfd)
    assert code == 0
    assert has(checks, "WARN", "core.hooksPath is not set")
    assert "git config core.hooksPath .githooks" in out


def test_hook_missing(project: Path, capfd: pytest.CaptureFixture[str]) -> None:
    (project / ".githooks" / "commit-msg").unlink()
    _, out, checks = run_doctor(project, capfd)
    assert has(checks, "WARN", ".githooks/commit-msg is missing")
    assert "git checkout HEAD -- .githooks/commit-msg" in out


def test_attribution_in_history(project: Path, capfd: pytest.CaptureFixture[str]) -> None:
    (project / "a.txt").write_text("a\n", encoding="utf-8")
    commit_all(project, "Add a", "-m", "Co-Authored-By: Bot <bot@example.com>", "--no-verify")
    short = git(project, "rev-parse", "--short", "HEAD")
    code, out, checks = run_doctor(project, capfd)
    assert code == 0
    assert has(checks, "WARN", "AI attribution in the last 20 commits")
    assert f"{short}: Co-Authored-By:" in out


def test_attribution_beyond_last_20_commits(project: Path, capfd: pytest.CaptureFixture[str]) -> None:
    git(project, "commit", "--quiet", "--allow-empty", "--no-verify", "-m", "Old", "-m", "Co-authored-by: x")
    for number in range(20):
        git(project, "commit", "--quiet", "--allow-empty", "-m", f"Commit {number}")
    _, _, checks = run_doctor(project, capfd)
    assert has(checks, "PASS", "No AI attribution in the last 20 commits")


ATTRIBUTED = [
    "Co-Authored-By: Bot <bot@example.com>",
    "co-authored-by: bot",
    "  Co-authored-by: bot",
    "\U0001F916 Generated with [Some Tool](https://example.com)",
    "Generated with Some Tool",
    "\u00e9 Generated with Some Tool",
    "_generated with care",
]
CLEAN = [
    "Fix the parser",
    "Explain why co-authored-by: lines are rejected",
    "Code generated with care",
    "# Co-Authored-By: a Git comment line",
]


@pytest.mark.parametrize("line", ATTRIBUTED + CLEAN)
def test_hook_and_doctor_agree(line: str, project: Path) -> None:
    rejected = line in ATTRIBUTED
    (project / "a.txt").write_text(line + "\n", encoding="utf-8")
    git(project, "add", "a.txt")
    message = project.parent / "message.txt"
    message.write_text(f"Change\n\n{line}\n", encoding="utf-8", newline="\n")
    result = subprocess.run(["git", "commit", "--quiet", "--cleanup=verbatim", "-F", str(message)],
                            cwd=project, capture_output=True, text=True, check=False)
    assert (result.returncode != 0) == rejected, result.stderr
    if rejected:
        assert "commit-msg: remove the AI attribution line" in result.stderr
    stripped = "\n".join(l for l in f"Change\n\n{line}\n".splitlines() if not l.startswith("#"))
    assert bool(doctor.ATTRIBUTION.search(stripped)) == rejected


# AC-4: classification and exit code


def test_every_line_is_classified(project: Path, capfd: pytest.CaptureFixture[str]) -> None:
    (project / "AGENTS.md").unlink()
    code, out, checks = run_doctor(project, capfd)
    assert code == 1
    check_lines = [line for line in out.splitlines() if line.startswith("  ") and not line.startswith("        ")]
    assert len(check_lines) == len(checks) > 10
    summary = out.strip().splitlines()[-1]
    counts = {level: len(levels(checks, level)) for level in doctor.LEVELS}
    assert summary == ", ".join(f"{counts[level]} {level}" for level in doctor.LEVELS)


def test_doctor_path_must_exist(env: Env, capfd: pytest.CaptureFixture[str]) -> None:
    assert newproj("doctor", str(env.tmp / "missing")) == 2


# AC-9: doctor uses the shared module


def test_doctor_uses_shared_module(project: Path, monkeypatch: pytest.MonkeyPatch,
                                   capfd: pytest.CaptureFixture[str]) -> None:
    start_task(project)
    record_review(project)
    called = set()
    for name in ["parse_task", "parse_handoff", "check", "review_invalidations", "history_signals",
                 "metadata_signals", "resolve_default_branch", "in_progress"]:
        original = getattr(state, name)

        def spy(*args: object, _name: str = name, _original: object = original, **kwargs: object) -> object:
            called.add(_name)
            return _original(*args, **kwargs)  # type: ignore[operator]

        monkeypatch.setattr(state, name, spy)
    run_doctor(project, capfd)
    assert called == {"parse_task", "parse_handoff", "check", "review_invalidations", "history_signals",
                      "metadata_signals", "resolve_default_branch", "in_progress"}
    source = Path(doctor.__file__).read_text(encoding="utf-8")
    for constant in ["## Status", "## Acceptance criteria", "refs/remotes/origin/HEAD", "ls-remote"]:
        assert constant not in source
