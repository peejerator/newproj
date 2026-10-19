"""Check the agent content shipped in the template against its fixed contracts."""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "template"
PROTOCOL = TEMPLATE / "docs" / "AGENT_PROTOCOL.md"
PROMPTS = TEMPLATE / "docs" / "PROMPTS.md"
SPEC = ROOT / "docs" / "spec.md"
NEUTRAL = TEMPLATE / ".agents" / "skills" / "handoff" / "neutral"

# Agents invoke these on their own; the user invokes the others (ERRATA E-010).
MODEL_SKILLS = ["resume", "handoff"]
USER_SKILLS = ["bootstrap", "review", "accept"]
SKILLS = MODEL_SKILLS + USER_SKILLS
OPENAI_YAML = "policy:\n  allow_implicit_invocation: false\n"

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
        assert sep and re.fullmatch(r"[a-z][a-z-]*", key), f"{path}: not a simple 'key: value' line: {line!r}"
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


def canonical(name: str) -> Path:
    return TEMPLATE / ".agents" / "skills" / name / "SKILL.md"


@pytest.mark.parametrize("name", SKILLS)
def test_canonical_skill_frontmatter(name: str) -> None:
    _, fields, body = split_frontmatter(canonical(name))
    if name in USER_SKILLS:
        assert list(fields) == ["name", "description", "disable-model-invocation"]
        assert fields["disable-model-invocation"] == "true"
    else:
        assert list(fields) == ["name", "description"]
    assert fields["name"] == name
    assert fields["description"].startswith("Use ")
    assert body.strip()


@pytest.mark.parametrize("name", SKILLS)
def test_openai_yaml(name: str) -> None:
    path = TEMPLATE / ".agents" / "skills" / name / "agents" / "openai.yaml"
    if name in USER_SKILLS:
        assert read(path) == OPENAI_YAML
        assert read(ROOT / ".agents" / "skills" / name / "agents" / "openai.yaml") == OPENAI_YAML
    else:
        assert not path.parent.exists()
        assert not (ROOT / ".agents" / "skills" / name / "agents").exists()


# Pointer skill locations, and the path each body points to.
POINTERS = [
    (TEMPLATE / ".claude" / "skills", ".agents/skills"),
    (ROOT / ".agents" / "skills", "template/.agents/skills"),
    (ROOT / ".claude" / "skills", "template/.agents/skills"),
]


@pytest.mark.parametrize("name", SKILLS)
@pytest.mark.parametrize("root, target", POINTERS, ids=lambda v: v.relative_to(ROOT).as_posix() if isinstance(v, Path) else v)
def test_pointer_skill(name: str, root: Path, target: str) -> None:
    expected, _, _ = split_frontmatter(canonical(name))
    pointer, _, body = split_frontmatter(root / name / "SKILL.md")
    assert pointer == expected
    assert body == f"\nRead and follow `{target}/{name}/SKILL.md`.\n"


def test_skill_sets_match() -> None:
    for root in [TEMPLATE / ".agents" / "skills"] + [root for root, _ in POINTERS]:
        assert sorted(p.name for p in root.iterdir()) == sorted(SKILLS)


def spec_neutral_blocks() -> dict[str, str]:
    text = read(SPEC)
    section = text[text.index("### 12.8 Canonical neutral state") : text.index("## 13. `HANDOFF.md`")]
    blocks = re.findall(r"```markdown\n(.*?)```", section, re.S)
    assert len(blocks) == 2
    return {"TASK.md": blocks[0], "HANDOFF.md": blocks[1]}


@pytest.mark.parametrize("name", ["TASK.md", "HANDOFF.md"])
def test_neutral_files_match_spec(name: str) -> None:
    data = (NEUTRAL / name).read_bytes()
    assert not data.startswith(b"\xef\xbb\xbf")
    assert data.endswith(b"\n") and not data.endswith(b"\n\n")
    assert data == spec_neutral_blocks()[name].encode("utf-8")


def test_handoff_skill_defers_to_review_and_accept() -> None:
    text = read(canonical("handoff"))
    assert "Outcome: none" in text
    for moved in ["Reviewed at:", "Artifact coverage:", "Last updated: none", "Branch: none"]:
        assert moved not in text
    assert "`review` skill" in text and "`accept` skill" in text
    assert "git rev-parse HEAD" in text


def test_resume_gives_state_py_and_git_fallback() -> None:
    text = read(TEMPLATE / ".agents" / "skills" / "resume" / "SKILL.md")
    assert "uv run --no-project .agents/skills/resume/scripts/state.py" in text
    assert "py -3 .agents/skills/resume/scripts/state.py" in text
    assert "git log -1 --format=%H -- HANDOFF.md" in text


def test_prompt_adapters() -> None:
    headings = [line for line in read(PROMPTS).splitlines() if line.startswith("## ")]
    assert headings == [
        "## What to upload", "## Resume", "## Handoff", "## Bootstrap", "## Review", "## Accept",
    ]


def agent_files() -> list[Path]:
    roots = [TEMPLATE, ROOT / ".agents", ROOT / ".claude"]
    return sorted(p for root in roots for p in root.rglob("*") if p.is_file())


@pytest.mark.parametrize("path", agent_files(), ids=lambda p: p.relative_to(ROOT).as_posix())
def test_text_hygiene(path: Path) -> None:
    data = path.read_bytes()
    assert b"\r" not in data
    text = data.decode("utf-8")
    assert "—" not in text, "em dash"
    assert "–" not in text, "en dash"
    for command in PHASE_2_COMMANDS:
        assert command not in text
