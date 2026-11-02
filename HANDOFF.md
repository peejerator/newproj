# Handoff

Last updated: 2026-11-02
Branch: m7.1-fixture-fixes
Task: standard

## Status

not started

## Completed

## Current working area

## Validation

## Review

Outcome: none

## Exact next steps

1. Add the B6 rule (AC-1) and the B10 rule (AC-2) to `template/docs/AGENT_PROTOCOL.md`, and the content tests (AC-3). Run `uv run pytest`.
2. Add the M7.1 row to `docs/ROADMAP.md` (AC-6).
3. Stage the work and print the commit commands for the user. Fixture reruns use the committed wording.
4. Set up the B6 reruns (Claude Code and Codex) and the B10 reruns (Codex) for the user, run `check`, judge the transcripts, and record the results (AC-4, AC-5).

## Blockers / open questions

## Relevant decisions

- Not rerunning B1, B4, B5, B9, and B11 is a recorded limitation (TASK.md Context).
