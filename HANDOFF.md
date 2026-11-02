# Handoff

Last updated: 2026-11-02
Branch: m8-dogfooding-exit
Task: standard

## Status

not started

## Completed

## Current working area

## Validation

## Review

Outcome: none

## Exact next steps

1. Set `"cleanupPeriodDays": 365` in Claude Code user settings on macOS and Windows (user; already set on the Linux machine).
2. Adopt ohm-manager with `newproj adopt --template-path <this repository>` on this branch, run its `bootstrap` skill, and record the result in `docs/research/dogfooding.md` (AC-2).
3. Create Project B with `newproj new` and check it with `newproj doctor` on macOS and Windows (AC-3).
4. Run recovery tests 24.1, 24.3, and 24.2 on real tasks and record each (AC-4).

## Blockers / open questions

## Relevant decisions

- User decisions and facts: `TASK.md` `## Context`.
