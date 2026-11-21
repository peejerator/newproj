# Handoff

Last updated: 2026-11-21
Branch: fix-46-remote-name
Task: standard

## Status

not started

## Completed

## Current working area

## Validation

## Review

Outcome: none

## Exact next steps

1. Implement AC-1 to AC-3 in `src/newproj/state.py`, `doctor.py`, and `adopt.py`; run `uv run python scripts/sync_state.py`.
2. Update the `handoff`, `start-task`, and `accept` skills (AC-4, AC-5) and append E-027 (AC-6).
3. Add the tests for AC-7 and run `uv run pytest`.

## Blockers / open questions

## Relevant decisions

- Remote selection rule and printed push commands: `TASK.md`, `## Context`, decisions 2 and 3.
- E-025 (resolution item 2 is superseded by the planned E-027).
