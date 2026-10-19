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
- Review findings (FAIL at 219351a): 1. `--template-path` passes `vcs_ref="HEAD"`, so a local Git repository with release tags renders its working tree, uncommitted changes included, instead of the latest tag (E-002); regression test with a tagged local repository plus a committed and an uncommitted change after the tag. 2. doctor's `.env.*` check probes `.env.local`, `.env.production` and `.env.newproj-doctor-probe`, so a single listed name no longer passes as the wildcard rule; regression tests replace `.env.*` with `.env.local`, and with `.env.local` plus `.env.production`.
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
- PASS | uv run pytest at 219351ac2b98b6920f73351b18d89db91b373a63 | 329 passed; listed scenarios for AC-1 to AC-9 exercised | Linux, Python 3.13.5 | reviewer
- PASS | git diff --check; git diff f9ba0ca3175f80f2af05bf9c2c2f08b4eddc8d2d...HEAD --check | working tree and complete implementation diff have no whitespace errors | Linux | reviewer
- PASS | uv run newproj --help | lists new, adopt and doctor (AC-8) | Linux | reviewer
- PASS | by hand: uv --no-cache run --project <repo> --no-sync newproj new demo --no-remote --template-path <repo>; doctor inside demo before and after a README commit | 20 PASS, 0 WARN, 0 FAIL each time (AC-1, AC-3, AC-9) | Linux, scratch directory, isolated Git configuration and fake gh | reviewer
- PASS | gh pr view --json number,url,headRefOid,statusCheckRollup; gh run list --commit 219351ac2b98b6920f73351b18d89db91b373a63 --json databaseId,headSha,status,conclusion,url,name | exact-commit push run 39323098529 and PR run 39323104323 both succeed on Linux, macOS and Windows (AC-5, AC-9) | https://github.com/peejerator/newproj/actions/runs/39323098529 | reviewer
- FAIL | by hand: newproj new tagged-demo --no-remote --template-path <local tagged repository> | selects v0.0.1 and omits a file committed after that tag; finding 1 (AC-1) | Linux, isolated template source with a release tag and a later commit | reviewer
- FAIL | by hand: replace .env.* with .env.local in generated .gitignore; run doctor and git check-ignore -q --no-index .env.production | doctor reports PASS for the missing wildcard rule; .env.production is unignored; finding 2 (AC-3) | Linux, isolated generated project | reviewer
- PASS | uv run --no-project template/.agents/skills/resume/scripts/state.py check --neutral-dir template/.agents/skills/handoff/neutral | No violations found | Linux | reviewer
- PASS | uv run pytest, after the second review fixes | 332 passed; the three new regression tests fail without the fixes (AC-1, AC-3, AC-9) | Linux (Raspberry Pi), Python 3.13 | implementer
- PASS | git diff --check; state.py check --neutral-dir template/.agents/skills/handoff/neutral | no whitespace errors; No violations found | Linux | implementer
- PASS | by hand: newproj new demo --no-remote --template-path <repo>, doctor before and after a README commit, then .env.* replaced with .env.local | 0 FAIL, 0 WARN both times; then WARN listing .env.* | Linux, isolated GIT_CONFIG_GLOBAL | implementer
- NOT RUN | CI on Linux, macOS, Windows for the second review fixes | environment: needs the push of the fix commit | implementer
- PASS | uv run pytest | 332 passed, one expected DirtyLocalWarning; covers AC-1 to AC-9 at cd98dd8c69886774d7dda4d8689bf7f209256dfb | Linux, Python 3.13.5 | reviewer
- PASS | git diff --check; git diff f9ba0ca3175f80f2af05bf9c2c2f08b4eddc8d2d...HEAD --check | no whitespace errors in the working tree or full milestone diff | Linux | reviewer
- PASS | uv --no-cache run --no-sync newproj --help | lists new, adopt and doctor (AC-8) | Linux | reviewer
- PASS | by hand: uv --no-cache run --project <repo> --no-sync newproj new demo --no-remote --template-path <repo>; doctor before and after a README commit; replace .env.* with .env.local and rerun doctor | 20 PASS, 0 WARN, 0 FAIL before and after the commit; missing wildcard produces WARN (AC-1, AC-3, AC-9) | Linux, scratch directory, isolated Git configuration and fake gh | reviewer
- PASS | gh pr view --json number,url,headRefOid,statusCheckRollup | exact reviewed commit cd98dd8c69886774d7dda4d8689bf7f209256dfb passes Linux, macOS and Windows in push and PR runs (AC-5, AC-9) | https://github.com/peejerator/newproj/actions/runs/39326152238 and https://github.com/peejerator/newproj/actions/runs/39326158866 | CI
- PASS | uv --no-cache run --no-project template/.agents/skills/resume/scripts/state.py check --neutral-dir template/.agents/skills/handoff/neutral | No violations found | Linux | reviewer

## Review

Outcome: PASS
Reviewer: Codex/GPT-6, 2026-10-19
Reviewed at: cd98dd8c69886774d7dda4d8689bf7f209256dfb
Contract: 7468b69ee92da1856e5816b1c0c91d69f1dd38f5
Working tree clean at review: yes
Baseline: base-commit diff
Artifact coverage: complete
Validation provenance: reviewer-executed

- AC-1: VERIFIED | Complete creation/source/tool code inspected; passing tests exercise preflight failures, tagged cache/fetch/offline behavior, local initialization, fake-gh publication, origin/HEAD and recovery commands. Manual creation succeeds. The tagged-local-source regression now confirms both committed and uncommitted development files render through --template-path. Copier tasks are skipped.
- AC-2: VERIFIED | Environment, Git identity, authentication and credential checks inspected and independently exercised by isolated tests, including missing-tool and missing-configuration cases.
- AC-3: VERIFIED | Complete doctor/shared-module integration inspected and tested: files, protocol/skills/pointers, imports, task format/baselines, neutral state, review status, conflicts/operations, budgets, ignores, recovery and default branch. Misplaced invocation policies fail. Replacing .env.* with one or two explicit filenames triggers WARN in tests; .env.local replacement independently confirmed by hand.
- AC-4: VERIFIED | Check lines use PASS, WARN, FAIL or INFO. Tests verify classification/counts and exit 1 for FAIL, otherwise 0; an invalid path returns usage-error exit 2.
- AC-5: VERIFIED | Executable template-managed hook, hooksPath and last-20-commits checks inspected. Attribution rejection and normal-message acceptance pass locally and in exact-commit CI on Linux, macOS and Windows, including the emoji footer case.
- AC-6: VERIFIED | Added accept lines retain the override, merge-failure, no-rebase and review-invalidation safeguards while placing the task-branch acceptance commit first in one && block. Content/render tests verify the single answers newline, documented Icon? rule and root push/PR instruction.
- AC-7: VERIFIED | E-016 and E-017 are append-only additions. E-017 records E-007 baselines and Phase 1 review display. Tests replace the source URL and cache function in process; no additional hidden CLI hook is introduced.
- AC-8: VERIFIED | Help lists new, adopt and doctor; adopt exits 2 in the console-script test. Dependency files are unchanged and the dependency assertion passes.
- AC-9: VERIFIED | All 332 tests pass independently on Linux, and exact-commit CI passes on Linux, macOS and Windows. Tests cover the specified creation, lightweight commit, remote/recovery, preflight, diagnostic, hook and shared-parser scenarios using fake gh and local repositories. Three regression cases cover the second review's findings.

Findings:
- No blocking findings. Both findings from the review at 219351ac2b98b6920f73351b18d89db91b373a63 are resolved, with regression coverage; the earlier Windows attribution and misplaced-policy findings remain resolved.
- The implementer authored the acceptance criteria for this standard task; this is weaker evidence than user-confirmed criteria. This review used a separate session and model from the recorded Claude Code/claude-opus-5-5 implementer.
- Exact-commit CI runs 39326152238 and 39326158866 pass on all three operating systems. Older claims elsewhere in this handoff that CI or a push is still needed are superseded by this evidence; those sections are preserved as required by the review skill.
- Real GitHub publication and the real released-template source were not exercised. Remote behavior and tag selection were verified with fake gh and local bare/tagged repositories, as required by the task.

## Exact next steps

1. The user commits the second review fixes and pushes; the PR already exists.
2. Check CI on all three operating systems for the fix commit and record it here with `CI` provenance.
3. Set Status to `complete`, then the user runs the `review` skill in a different agent.

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
