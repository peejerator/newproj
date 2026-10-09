"""Check the agent content shipped in the template against its fixed contracts."""

from pathlib import Path

import pytest

TEMPLATE = Path(__file__).resolve().parent.parent / "template"
PROTOCOL = TEMPLATE / "docs" / "AGENT_PROTOCOL.md"
PROMPTS = TEMPLATE / "docs" / "PROMPTS.md"
SKILLS = ["resume", "handoff", "bootstrap"]

PROTOCOL_HEADINGS = [
    "## Session start",
    "## Workflow tiers",
    "## Reconciliation",
    "## Task rules",
    "## During work",
    "## Definition of done",
    "## Trust boundaries and authority",
    "## Session end and switching",
    "## Durable documents",
]

# Commands that do not exist in Phase 1 (spec sections 20.4 to 20.6).
PHASE_2_COMMANDS = ["newproj activate", "newproj checkpoint", "newproj bundle"]


def read(path: Path) -> str:
    return path.read_bytes().decode("utf-8")


def split_frontmatter(path: Path) -> tuple[str, dict[str, str], str]:
    """Return the raw frontmatter block, its keys and values, and the body."""
    text = read(path)
    assert text.startswith("---\n"), f"{path} does not start with frontmatter"
    end = text.index("\n---\n", 4)
    block = text[: end + len("\n---\n")]
    fields: dict[str, str] = {}
    for line in text[4:end].split("\n"):
        key, sep, value = line.partition(": ")
        assert sep and key.isidentifier(), f"{path}: not a simple 'key: value' line: {line!r}"
        assert key not in fields, f"{path}: duplicate key {key!r}"
        # Keep values valid as YAML plain scalars on one line.
        assert value and value[0] not in "'\"[]{}>|*&!%@`#,?:-", f"{path}: {key} needs quoting"
        assert ": " not in value and " #" not in value, f"{path}: {key} needs quoting"
        fields[key] = value
    return block, fields, text[len(block) :]


def test_protocol_line_limit() -> None:
    assert len(read(PROTOCOL).splitlines()) <= 120


def test_protocol_headings() -> None:
    headings = [line for line in read(PROTOCOL).splitlines() if line.startswith("## ")]
    assert headings == PROTOCOL_HEADINGS


def test_protocol_states_handoff_invariants() -> None:
    text = read(PROTOCOL)
    for value in [
        "## Status", "## Completed", "## Current working area", "## Validation",
        "## Review", "## Exact next steps", "## Blockers / open questions",
        "## Relevant decisions",
        "`none`, `not started`, `in progress`, `blocked`, `validating`, `complete`",
        "`implementer`, `reviewer`, or `CI`",
        "`PASS`, `FAIL`, `INCONCLUSIVE`, `none`",
        "never by the agent that implemented the work",
    ]:
        assert value in text


@pytest.mark.parametrize("name", SKILLS)
def test_canonical_skill_frontmatter(name: str) -> None:
    _, fields, body = split_frontmatter(TEMPLATE / ".agents" / "skills" / name / "SKILL.md")
    assert list(fields) == ["name", "description"]
    assert fields["name"] == name
    assert fields["description"].startswith("Use ")
    assert body.strip()


@pytest.mark.parametrize("name", SKILLS)
def test_claude_pointer_skill(name: str) -> None:
    canonical, _, _ = split_frontmatter(TEMPLATE / ".agents" / "skills" / name / "SKILL.md")
    pointer, _, body = split_frontmatter(TEMPLATE / ".claude" / "skills" / name / "SKILL.md")
    assert pointer == canonical
    assert body == f"\nRead and follow `.agents/skills/{name}/SKILL.md`.\n"


def test_skill_sets_match() -> None:
    for root in [TEMPLATE / ".agents" / "skills", TEMPLATE / ".claude" / "skills"]:
        assert sorted(p.name for p in root.iterdir()) == sorted(SKILLS)


def test_resume_gives_state_py_and_git_fallback() -> None:
    text = read(TEMPLATE / ".agents" / "skills" / "resume" / "SKILL.md")
    assert "uv run --no-project .agents/skills/resume/scripts/state.py" in text
    assert "py -3 .agents/skills/resume/scripts/state.py" in text
    assert "git log -1 --format=%H -- HANDOFF.md" in text


def test_prompt_adapters() -> None:
    headings = [line for line in read(PROMPTS).splitlines() if line.startswith("## ")]
    assert headings == ["## What to upload", "## Resume", "## Handoff", "## Bootstrap"]


def template_files() -> list[Path]:
    return sorted(p for p in TEMPLATE.rglob("*") if p.is_file())


@pytest.mark.parametrize("path", template_files(), ids=lambda p: p.relative_to(TEMPLATE).as_posix())
def test_template_text_hygiene(path: Path) -> None:
    data = path.read_bytes()
    assert b"\r" not in data
    text = data.decode("utf-8")
    assert "—" not in text, "em dash"
    assert "–" not in text, "en dash"
    for command in PHASE_2_COMMANDS:
        assert command not in text
