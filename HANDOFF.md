# Handoff

Last updated: 2026-10-19 by Claude Code/claude-opus-5-5
Branch: m5-new-and-doctor
Task: standard
Environment: other

## Status

validating

## Completed

- AC-1: `newproj new` in `src/newproj/new.py` (preflight, render, local commit, remote, recovery commands); template source in `src/newproj/source.py` (bare cached clone, fetch only when the tag is missing).
- AC-2, AC-3, AC-4: `newproj doctor` in `src/newproj/doctor.py`, classifying results from `newproj.state`; `state.review_invalidations` split out of `review_signal` for the two-part review display, template copy synced.
- AC-5: `template/.githooks/commit-msg` (mode 100755); doctor checks `core.hooksPath`, the hook file, and the last 20 commits; erratum E-016.
- AC-6: `accept` prints one `&&` block with the commit first; answers file ends with one newline; `Icon?` rule with comment; root `AGENTS.md` push and PR rule.
- AC-7: erratum E-017. No hidden hook beyond `--template-path`: tests replace `source.TEMPLATE_URL` and `source.cache_dir` in process.
- AC-8: `--help` lists new, adopt, doctor; `adopt` exits 2; dependencies unchanged (test).
- Review findings (FAIL at 44f0582): 1. the hook runs `grep` with `LC_ALL=C`, so `[:alnum:]` is ASCII only and an emoji before "Generated with" is rejected under Git for Windows too; doctor's `ATTRIBUTION` regex is now ASCII-only (`re.ASCII`, `[^a-z0-9\n]`) to match the hook exactly. 2. `doctor.disallows_implicit_invocation` requires `allow_implicit_invocation: false` directly under the top-level `policy:` mapping; regression tests for a misplaced key, a nested key and a top-level key, plus hook/doctor agreement cases for `é` and `_` before "Generated with".
- AC-9: `tests/test_new.py`, `tests/test_doctor.py`, `tests/conftest.py`, `tests/fake_gh.py`.

## Current working area

- `src/newproj/`
- `tests/`
- `template/.githooks/`
- `template/.agents/skills/accept/SKILL.md`
- `template/.agents/skills/resume/scripts/state.py`
- `template/_includes/gitignore/macOS.gitignore`
- `template/{{_copier_conf.answers_file}}.jinja`
- `docs/ERRATA.md`
- `AGENTS.md`

## Validation

- PASS | uv run pytest | 324 passed, covers AC-1 to AC-9 | Linux (Raspberry Pi), Python 3.13, Copier 9.18.2, git 2.47.3 | implementer
- PASS | git diff --cached --check | no whitespace errors | Linux | implementer
- PASS | state.py check --neutral-dir template/.agents/skills/handoff/neutral | No violations found | Linux | implementer
- PASS | by hand: newproj new demo --no-remote --template-path <repo>, then newproj doctor, before and after a small commit | 0 FAIL, 0 WARN both times; hook rejected a Co-Authored-By line and a "Generated with" footer | Linux, isolated GIT_CONFIG_GLOBAL | implementer
- NOT RUN | CI on Linux, macOS, Windows | environment: needs the push of this branch | implementer
- PASS | uv run pytest | 324 passed; local coverage of AC-1 to AC-9 | Linux, Python 3.13.5 | reviewer
- PASS | git diff --check | no whitespace errors | Linux | reviewer
- PASS | uv run newproj --help | lists new, adopt and doctor (AC-8) | Linux | reviewer
- PASS | by hand: uv run --project <repo> --no-sync newproj new demo --no-remote --template-path <repo>; uv run --project <repo> --no-sync newproj doctor before and after a README commit | 0 FAIL, 0 WARN both times (AC-1, AC-3, AC-9) | Linux, scratch directory, isolated Git configuration and fake gh | reviewer
- FAIL | gh run view 39318449835 --log-failed | confirmed Windows CI failure at reviewed HEAD: 323 passed, 1 failed; Linux and macOS passed in the same run (AC-5, AC-9) | https://github.com/peejerator/newproj/actions/runs/39318449835 | reviewer
- FAIL | by hand: replace policy: with unrelated: in a generated bootstrap/agents/openai.yaml, then run doctor | doctor exits 0 and reports PASS for all five skills; misplaced invocation policy goes undetected (AC-3) | Linux, isolated generated project | reviewer
- PASS | uv run --no-project template/.agents/skills/resume/scripts/state.py check --neutral-dir template/.agents/skills/handoff/neutral | No violations found | Linux | reviewer
- PASS | uv run pytest, after the review fixes | 329 passed, including the new policy and attribution cases (AC-3, AC-5, AC-9) | Linux (Raspberry Pi), Python 3.13 | implementer
- PASS | git diff --check, after the review fixes | no whitespace errors | Linux | implementer
- NOT RUN | CI on Windows for the hook fix | environment: needs the push of the fix commit; the failure was Windows only and cannot be reproduced here | implementer

## Review

Outcome: FAIL
Reviewer: Codex/GPT-6, 2026-10-19
Reviewed at: 44f0582f637f21db419570eb29cc05b49ede7307
Contract: 7468b69ee92da1856e5816b1c0c91d69f1dd38f5
Working tree clean at review: yes
Baseline: base-commit diff
Artifact coverage: complete
Validation provenance: reviewer-executed

- AC-1: VERIFIED | Complete preflight, cache/tag selection, rendering, Git initialization and remote/recovery paths inspected; local tests exercise local tagged repositories, fake gh and local bare remotes; manual creation succeeds. Real GitHub publication was not exercised.
- AC-2: VERIFIED | Environment, Git identity, authentication and credential checks inspected and independently tested with isolated inputs.
- AC-3: UNSATISFIED | Project checks and shared parsers otherwise covered, but a misplaced invocation policy is accepted as healthy; see finding 2.
- AC-4: VERIFIED | Report classifies checks and returns 1 on FAIL, 0 otherwise; classification and exit-code tests pass. Invalid input paths return 2 as a usage error.
- AC-5: UNSATISFIED | Hook, hooksPath and history checks exist and pass locally, but Windows accepts an attribution footer; see finding 1.
- AC-6: VERIFIED | Added lines preserve acceptance safeguards, put the task-branch commit first in one && block, fix the answers newline, add the documented Icon? rule and add the root push/PR rule; content/render tests pass.
- AC-7: VERIFIED | E-016 and E-017 are append-only additions; E-017 records baseline/review behavior and the absence of another hidden test hook.
- AC-8: VERIFIED | CLI help and adopt exit 2 checked by tests; only Copier remains a runtime dependency, and no dependency files changed.
- AC-9: UNSATISFIED | All 324 tests pass locally; exact-HEAD CI passes Linux/macOS but fails Windows. Local repository fixtures and shared-parser spies are present. The malformed-policy regression also needs test coverage.

Findings:
- 1. [P1] template/.githooks/commit-msg:6: Windows accepts a message whose footer is an emoji followed by "Generated with [Some Tool](https://example.com)". Exact-HEAD CI fails tests/test_doctor.py:636 because git commit returns 0 instead of rejecting it (323 passed, 1 failed). This bypasses the attribution rule on a supported platform and blocks AC-5 and AC-9. Make footer detection work under Git for Windows and rerun all three CI jobs. Evidence: https://github.com/peejerator/newproj/actions/runs/39318449835/job/118285943936.
- 2. [P2] src/newproj/doctor.py:245: The regex accepts any indented allow_implicit_invocation: false line, without requiring the policy mapping. In a generated .agents/skills/bootstrap/agents/openai.yaml, replace policy: with unrelated: and leave the indented setting unchanged. Reviewer reproduction: skill_problems returns [], doctor exits 0, and the protocol/skills check reports PASS. The file no longer expresses the E-010 policy, so this is a false health report for a user-invoked skill. Validate the policy mapping and add a misplaced-key regression test (AC-3).
- The implementer authored the acceptance criteria for this standard task; this is weaker evidence than user-confirmed criteria. Review used a separate session and model from the recorded Claude Code/claude-opus-5-5 implementer.
- Earlier implementer entries and next steps remain unchanged per the review skill. Their claim that CI still needs a push is superseded by the exact-HEAD CI evidence above.

## Exact next steps

1. The user commits the review fixes and pushes; the PR already exists.
2. Check CI on all three operating systems, especially `test_hook_and_doctor_agree` on Windows.
3. Record the CI result here with `CI` provenance, set Status to `complete`, then the user runs the `review` skill in a different agent.

## Blockers / open questions

- None. The user confirmed these implementation choices on 2026-10-19:
  - `new` rewrites `_src_path` in `.copier-answers.yml` from the cache path to the template URL, so the file names no local path and works on every machine (not done for `--template-path`, per E-002).
  - When stdin is not a terminal, `new` uses the template's default answers and says so.
  - Missing `gh` or `uv`, unauthenticated `gh`, and no credential setup are WARN; missing `git` and Git identity are FAIL.
  - Recovery signals are INFO, except a stale `HANDOFF.md`, which is WARN (spec 20.7 examples).
- Unverified here: behavior on macOS and Windows (until CI runs), real `gh` against GitHub, and rendering from the real tagged repository, which has no `v0.1.0` tag yet (only local tagged repositories are tested).

## Relevant decisions

- D-001
- D-002
- E-002
- E-007
- E-011
- E-016
- E-017
