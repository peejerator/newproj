"""Render the template with Copier and check the generated project."""

import configparser
import re
import shutil
import socket
from pathlib import Path

import copier
import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "template"
COPIER_YML = ROOT / "copier.yml"
SPEC = ROOT / "docs" / "spec.md"
ERRATA = ROOT / "docs" / "ERRATA.md"
SNIPPETS = TEMPLATE / "_includes" / "gitignore"
NEUTRAL = ".agents/skills/handoff/neutral"

SKILLS = ["resume", "handoff", "bootstrap", "review", "accept"]
USER_SKILLS = ["bootstrap", "review", "accept"]

# Spec section 7, adjusted by ERRATA E-011 and E-012, plus state.py (D-002).
# LICENSE is added when chosen.
LAYOUT = {
    "AGENTS.md",
    "CLAUDE.md",
    "TASK.md",
    "HANDOFF.md",
    "README.md",
    ".copier-answers.yml",
    ".env.example",
    ".gitignore",
    ".gitattributes",
    ".editorconfig",
    "docs/AGENT_PROTOCOL.md",
    "docs/PROMPTS.md",
    "docs/DECISIONS.md",
    f"{NEUTRAL}/TASK.md",
    f"{NEUTRAL}/HANDOFF.md",
    *(f".agents/skills/{name}/SKILL.md" for name in SKILLS),
    ".agents/skills/resume/scripts/state.py",
    *(f".agents/skills/{name}/agents/openai.yaml" for name in USER_SKILLS),
    *(f".claude/skills/{name}/SKILL.md" for name in SKILLS),
}

# Language answer to the .gitignore section headings it adds.
LANGUAGE_SECTIONS = {
    "python": ["# Python"],
    "js-ts": ["# Node"],
    "c-cpp": ["# C", "# C++"],
    "java": ["# Java"],
    "go": ["# Go"],
    "rust": ["# Rust"],
    "other": [],
}

RENDERS = {
    "defaults": {"project_name": "demo"},
    "all-mit": {
        "project_name": "demo-all",
        "description": "A project that uses every language.",
        "languages": list(LANGUAGE_SECTIONS),
        "license": "MIT",
        "copyright_holder": "Test Holder",
    },
    "apache": {
        "project_name": "demo-apache",
        "description": "An Apache-licensed project.",
        "languages": ["python"],
        "license": "Apache-2.0",
    },
}

AGENTS_HEADINGS = [
    "## Project",
    "## Agent protocol",
    "## Commands",
    "## Environment",
    "## Conventions",
    "## Project-specific rules",
    "## Where to find more",
]
STABLE_INSTRUCTION = "At the start of every session, read and follow `docs/AGENT_PROTOCOL.md`."
RULES = [
    "- Never commit secrets or credentials.",
    '- Never add Co-Authored-By trailers, "Generated with" footers, or other AI attribution'
    " to commits or pull requests.",
]
ENV_LINES = [".env", ".env.*", "!.env.example", "context.md"]
UPDATE_EXCLUDE = re.compile(r"\{% if _copier_operation == 'update' %\}(.+)\{% endif %\}")


def render(dest: Path, data: dict[str, object]) -> Path:
    """Render the working tree into dest, with network access blocked."""
    # A plain copy, not a Git clone, so Copier renders the working tree as it is.
    src = dest.parent / f"{dest.name}-src"
    shutil.copytree(TEMPLATE, src / "template")
    shutil.copy2(COPIER_YML, src / "copier.yml")
    with pytest.MonkeyPatch.context() as mp:
        def no_network(*args: object, **kwargs: object) -> None:
            raise AssertionError("rendering tried to use the network")

        mp.setattr(socket.socket, "connect", no_network)
        mp.setattr(socket, "create_connection", no_network)
        copier.run_copy(str(src), dest, data=data, defaults=True, quiet=True)
    return dest


@pytest.fixture(scope="module")
def projects(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Path]:
    base = tmp_path_factory.mktemp("render")
    return {name: render(base / name, data) for name, data in RENDERS.items()}


@pytest.fixture(params=list(RENDERS))
def case(request: pytest.FixtureRequest, projects: dict[str, Path]) -> tuple[dict[str, object], Path]:
    return RENDERS[request.param], projects[request.param]


def rendered_files(project: Path) -> set[str]:
    return {p.relative_to(project).as_posix() for p in project.rglob("*") if p.is_file()}


def read(path: Path) -> str:
    return path.read_bytes().decode("utf-8")


def copier_config() -> dict[str, object]:
    return yaml.safe_load(read(COPIER_YML))


# AC-1


def test_layout(case: tuple[dict[str, object], Path]) -> None:
    data, project = case
    expected = set(LAYOUT)
    if data.get("license", "none") != "none":
        expected.add("LICENSE")
    files = rendered_files(project)
    assert files == expected
    assert not any("delegate" in f for f in files)


# AC-2


def test_neutral_files_rendered(case: tuple[dict[str, object], Path]) -> None:
    _, project = case
    for name in ["TASK.md", "HANDOFF.md"]:
        assert (project / name).read_bytes() == (project / NEUTRAL / name).read_bytes()
        assert (project / name).read_bytes() == (TEMPLATE / NEUTRAL / name).read_bytes()


def test_neutral_text_has_one_home() -> None:
    texts = {name: read(TEMPLATE / NEUTRAL / name) for name in ["TASK.md", "HANDOFF.md"]}
    for path in TEMPLATE.rglob("*"):
        if not path.is_file() or path.parent == TEMPLATE / NEUTRAL:
            continue
        content = read(path)
        for name, text in texts.items():
            assert text not in content, f"{path} duplicates neutral {name}"
    for name in texts:
        assert not (TEMPLATE / name).exists()
        assert f"{NEUTRAL}/{name}" in read(TEMPLATE / f"{name}.jinja")


# AC-3


def test_agents_md(case: tuple[dict[str, object], Path]) -> None:
    data, project = case
    text = read(project / "AGENTS.md")
    lines = text.splitlines()
    assert len(lines) <= 150
    assert [line for line in lines if line.startswith("## ")] == AGENTS_HEADINGS
    assert lines[0] == f"# {data['project_name']}"
    assert f"`{data['project_name']}`" in text
    if data.get("description"):
        assert data["description"] in lines
    else:
        assert "TODO: describe the project in one paragraph." in lines
    assert STABLE_INSTRUCTION in lines
    for command in ["Build", "Test", "Run", "Lint and format"]:
        assert any(line.startswith(f"- {command}: TODO") for line in lines), command
    for rule in RULES:
        assert rule in lines


# AC-4


def test_claude_md(case: tuple[dict[str, object], Path]) -> None:
    _, project = case
    assert read(project / "CLAUDE.md") == "@AGENTS.md\n@docs/AGENT_PROTOCOL.md\n"


# AC-5


def test_decisions_md(case: tuple[dict[str, object], Path]) -> None:
    _, project = case
    text = read(project / "docs" / "DECISIONS.md")
    assert text.startswith("# Decisions\n\n<!--\n")
    assert text.endswith("-->\n")
    for word in ["Proposed", "Accepted", "Superseded", "### Supersedes"]:
        assert word in text
    assert not re.search(r"^## ", text, re.MULTILINE), "contains an entry"


# AC-6


def test_gitattributes(case: tuple[dict[str, object], Path]) -> None:
    _, project = case
    lines = read(project / ".gitattributes").splitlines()
    assert "* text=auto eol=lf" in lines
    for ext in ["png", "jpg", "gif", "ico", "pdf", "zip", "gz"]:
        assert f"*.{ext} binary" in lines


def test_editorconfig(case: tuple[dict[str, object], Path]) -> None:
    _, project = case
    config = configparser.ConfigParser()
    config.read_string(read(project / ".editorconfig").replace("root = true\n", "", 1))
    every = config["*"]
    assert every["charset"] == "utf-8"
    assert every["end_of_line"] == "lf"
    assert every["insert_final_newline"] == "true"
    assert every["trim_trailing_whitespace"] == "true"
    assert every["indent_style"] == "space"
    assert every["indent_size"] == "4"
    assert config["*.md"]["trim_trailing_whitespace"] == "false"
    assert config["*.{json,yml,yaml,toml,js,ts}"]["indent_size"] == "2"


def test_gitignore(case: tuple[dict[str, object], Path]) -> None:
    data, project = case
    lines = read(project / ".gitignore").splitlines()
    for heading in ["# macOS", "# Windows", "# VS Code"]:
        assert heading in lines
    # The environment rules come last, together, so no language rule overrides them.
    assert lines[-len(ENV_LINES) :] == ENV_LINES
    selected = data.get("languages", [])
    for language, headings in LANGUAGE_SECTIONS.items():
        for heading in headings:
            assert (heading in lines) == (language in selected), heading


def test_gitignore_snippets_are_vendored() -> None:
    names = {"Python", "Node", "C", "C++", "Java", "Go", "Rust", "macOS", "Windows", "VisualStudioCode"}
    assert {p.stem for p in SNIPPETS.glob("*.gitignore")} == names
    source = re.compile(r"# Vendored from https://github\.com/github/gitignore/blob/[0-9a-f]{40}/\S+\.gitignore")
    for path in SNIPPETS.glob("*.gitignore"):
        assert source.fullmatch(read(path).splitlines()[0]), path


def test_env_example(case: tuple[dict[str, object], Path]) -> None:
    _, project = case
    lines = read(project / ".env.example").splitlines()
    assert lines and all(line.startswith("#") for line in lines)


def test_readme(case: tuple[dict[str, object], Path]) -> None:
    data, project = case
    text = read(project / "README.md")
    assert text.startswith(f"# {data['project_name']}\n")
    if data.get("description"):
        assert data["description"] in text.splitlines()
    assert "AGENTS.md" in text
    assert "\n\n\n" not in text


# AC-7


def test_license(case: tuple[dict[str, object], Path]) -> None:
    data, project = case
    license_file = project / "LICENSE"
    answers = yaml.safe_load(read(project / ".copier-answers.yml"))
    choice = data.get("license", "none")
    if choice == "none":
        assert not license_file.exists()
    elif choice == "MIT":
        lines = read(license_file).splitlines()
        assert lines[0] == "MIT License"
        assert lines[2] == f"Copyright (c) {data['copyright_holder']}"
        assert "Permission is hereby granted, free of charge, to any person obtaining a copy" in lines
    else:
        text = read(license_file)
        assert text == read(TEMPLATE / "_includes" / "licenses" / "Apache-2.0.txt")
        assert text.splitlines()[1].strip() == "Apache License"
        assert "Version 2.0, January 2004" in text
        assert "END OF TERMS AND CONDITIONS" in text
    assert ("copyright_holder" in answers) == (choice == "MIT")


def test_copyright_holder_question() -> None:
    question = copier_config()["copyright_holder"]
    assert question["type"] == "str"
    assert question["when"] == "{{ license == 'MIT' }}"
    assert "default" not in question
    assert "## E-015:" in read(ERRATA)


@pytest.mark.parametrize("holder", ["", "   "])
def test_copyright_holder_required(holder: str, tmp_path: Path) -> None:
    data = {"project_name": "demo", "license": "MIT", "copyright_holder": holder}
    with pytest.raises(ValueError, match="must not be empty"):
        render(tmp_path / "out", data)


# AC-8


def spec_project_owned() -> set[str]:
    """Project-owned concrete paths from the ownership table in spec section 8."""
    text = read(SPEC)
    section = text[text.index("## 8. File Ownership") : text.index("## 9. `AGENTS.md`")]
    paths = set()
    for match in re.finditer(r"^\| `([^`]+)` \| ([^|]+) \|", section, re.MULTILINE):
        path, ownership = match[1], match[2].strip()
        if ownership.startswith("Project") and "*" not in path:
            paths.add(path)
    return paths


def test_project_owned_lists(projects: dict[str, Path]) -> None:
    config = copier_config()
    rendered = rendered_files(projects["all-mit"])
    owned = sorted(spec_project_owned() & rendered)
    assert "AGENTS.md" in owned and ".env.example" in owned and "LICENSE" in owned
    assert sorted(config["_skip_if_exists"]) == owned
    conditional = [m[1] for entry in config["_exclude"] if (m := UPDATE_EXCLUDE.fullmatch(entry))]
    assert sorted(conditional) == owned


# AC-9


def test_rendered_text_hygiene(case: tuple[dict[str, object], Path]) -> None:
    _, project = case
    for name in sorted(rendered_files(project)):
        data = (project / name).read_bytes()
        assert not data.startswith(b"\xef\xbb\xbf"), f"{name}: byte-order mark"
        text = data.decode("utf-8")
        assert "\r" not in text, f"{name}: CR"
        assert text.endswith("\n"), f"{name}: no final newline"
        assert "—" not in text, f"{name}: em dash"
        assert "–" not in text, f"{name}: en dash"
