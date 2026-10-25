# Behavioral fixture results

Results of the Phase 1 behavioral fixtures (spec 23.2): B1, B4, B5, B6, B9, B10, and B11, each run twice on the Claude Code CLI and twice on the Codex CLI. The Codex CLI stands in for the Codex VS Code extension and ChatGPT desktop app until that setup exists (docs/ERRATA.md, E-021). The harness is described in docs/DECISIONS.md, D-008.

## Method

For each run, in a fresh agent session:

1. `uv run python scripts/behavior.py setup <id> <dir>`, with `<dir>` a new directory outside any Git repository.
2. Open the tool in `<dir>`, paste `tests/fixtures/behavior/<id>/prompt.txt`, and answer only as that fixture's `notes.md` says.
3. `uv run python scripts/behavior.py check <id> <dir>`, then judge the items it lists from the transcript, as `notes.md` describes.

A run passes when `check` passes and every judged item holds. Every FAIL row cites the GitHub issue that tracks it; failures are fixed in a later milestone before M8. Exit criterion 28.1 is judged at M8.

Result column: `PASS` or `FAIL`, with the judged items stated (for example `PASS (scripted; judged: flagged)`).

## Claude Code CLI

| Fixture | Run | OS | Tool version | Model | Date | Result | Note |
|---|---|---|---|---|---|---|---|
| B1 | 1 | | | | | pending | |
| B1 | 2 | | | | | pending | |
| B4 | 1 | | | | | pending | |
| B4 | 2 | | | | | pending | |
| B5 | 1 | | | | | pending | |
| B5 | 2 | | | | | pending | |
| B6 | 1 | | | | | pending | |
| B6 | 2 | | | | | pending | |
| B9 | 1 | | | | | pending | |
| B9 | 2 | | | | | pending | |
| B10 | 1 | | | | | pending | |
| B10 | 2 | | | | | pending | |
| B11 | 1 | | | | | pending | |
| B11 | 2 | | | | | pending | |

## Codex CLI

| Fixture | Run | OS | Tool version | Model | Date | Result | Note |
|---|---|---|---|---|---|---|---|
| B1 | 1 | | | | | pending | |
| B1 | 2 | | | | | pending | |
| B4 | 1 | | | | | pending | |
| B4 | 2 | | | | | pending | |
| B5 | 1 | | | | | pending | |
| B5 | 2 | | | | | pending | |
| B6 | 1 | | | | | pending | |
| B6 | 2 | | | | | pending | |
| B9 | 1 | | | | | pending | |
| B9 | 2 | | | | | pending | |
| B10 | 1 | | | | | pending | |
| B10 | 2 | | | | | pending | |
| B11 | 1 | | | | | pending | |
| B11 | 2 | | | | | pending | |

## Pass rates

| Fixture | Claude Code CLI | Codex CLI |
|---|---|---|
| B1 | pending | pending |
| B4 | pending | pending |
| B5 | pending | pending |
| B6 | pending | pending |
| B9 | pending | pending |
| B10 | pending | pending |
| B11 | pending | pending |
