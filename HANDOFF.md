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
- PASS | uv run pytest at 219351ac2b98b6920f73351b18d89db91b373a63 | 329 passed; listed scenarios for AC-1 to AC-9 exercised | Linux, Python 3.13.5 | reviewer
- PASS | git diff --check; git diff f9ba0ca3175f80f2af05bf9c2c2f08b4eddc8d2d...HEAD --check | working tree and complete implementation diff have no whitespace errors | Linux | reviewer
- PASS | uv run newproj --help | lists new, adopt and doctor (AC-8) | Linux | reviewer
- PASS | by hand: uv --no-cache run --project <repo> --no-sync newproj new demo --no-remote --template-path <repo>; doctor inside demo before and after a README commit | 20 PASS, 0 WARN, 0 FAIL each time (AC-1, AC-3, AC-9) | Linux, scratch directory, isolated Git configuration and fake gh | reviewer
- PASS | gh pr view --json number,url,headRefOid,statusCheckRollup; gh run list --commit 219351ac2b98b6920f73351b18d89db91b373a63 --json databaseId,headSha,status,conclusion,url,name | exact-commit push run 39323098529 and PR run 39323104323 both succeed on Linux, macOS and Windows (AC-5, AC-9) | https://github.com/peejerator/newproj/actions/runs/39323098529 | reviewer
- FAIL | by hand: newproj new tagged-demo --no-remote --template-path <local tagged repository> | selects v0.0.1 and omits a file committed after that tag; finding 1 (AC-1) | Linux, isolated template source with a release tag and a later commit | reviewer
- FAIL | by hand: replace .env.* with .env.local in generated .gitignore; run doctor and git check-ignore -q --no-index .env.production | doctor reports PASS for the missing wildcard rule; .env.production is unignored; finding 2 (AC-3) | Linux, isolated generated project | reviewer
- PASS | uv run --no-project template/.agents/skills/resume/scripts/state.py check --neutral-dir template/.agents/skills/handoff/neutral | No violations found | Linux | reviewer

## Review

Outcome: FAIL
Reviewer: Codex/GPT-6, 2026-10-19
Reviewed at: 219351ac2b98b6920f73351b18d89db91b373a63
Contract: 7468b69ee92da1856e5816b1c0c91d69f1dd38f5
Working tree clean at review: yes
Baseline: base-commit diff
Artifact coverage: complete
Validation provenance: reviewer-executed

- AC-1: UNSATISFIED | Preflight, tagged cache/offline handling, local initialization, remote publication and recovery paths are covered by passing tests and inspected code. Manual creation succeeds, but --template-path selects an old release tag in a tagged development repository; see finding 1.
- AC-2: VERIFIED | Environment, identity, authentication and credential checks inspected and independently exercised by the passing isolated tests.
- AC-3: UNSATISFIED | Shared parsing, file/instruction checks, review status, repository/recovery checks and default-branch handling inspected and tested. The previous misplaced-policy finding is fixed. The secret-ignore check falsely reports the .env.* rule present when only .env.local is ignored; see finding 2.
- AC-4: VERIFIED | Check lines carry PASS, WARN, FAIL or INFO; tests confirm classification, counts and exit 1 for FAIL, otherwise 0. Invalid paths return usage-error exit 2.
- AC-5: VERIFIED | Executable template-managed hook, hooksPath and last-20-commits checks inspected. Hook/doctor agreement tests pass locally and exact-commit CI passes on Linux, macOS and Windows, including the previously failing emoji footer case.
- AC-6: VERIFIED | Added accept lines preserve safeguards and put the task-branch acceptance commit first in one && block. Render/content tests verify the single answers newline, documented Icon? rule and root push/PR instruction.
- AC-7: VERIFIED | E-016 and E-017 are append-only additions; E-017 records the standard-task baseline and Phase 1 review checks. Tests replace source URL/cache functions without another CLI hook.
- AC-8: VERIFIED | CLI help lists new, adopt and doctor; adopt exits 2. Dependency files are unchanged and the dependency assertion passes.
- AC-9: VERIFIED | All 329 tests pass locally; exact reviewed commit passes CI on all three operating systems. Tests cover the listed local/remote/preflight/diagnostic/hook/shared-parser scenarios using fake gh and local repositories. The two additional cases in Findings need regression tests.

Findings:
- 1. [P2] src/newproj/new.py:77: --template-path omits vcs_ref, allowing Copier to choose the latest release tag instead of the development files. Reproduction: initialize a local template repository, commit and tag v0.0.1, then add template/development-change.txt in a later commit. Run newproj new tagged-demo --no-remote --template-path <that repository>. It exits 0, but development-change.txt is absent and .copier-answers.yml records _commit: v0.0.1. This breaks the working-tree development command in AGENTS.md and E-002 once the source has a release tag. Explicitly select the current development source for this override and add a regression test using a tagged local repository with changes after the tag (AC-1).
- 2. [P2] src/newproj/doctor.py:426: Checking only .env.local does not establish the required .env.* ignore rule. In a fresh generated project, replace the .env.* line with .env.local, then run doctor. Reviewer reproduction: exit 0, no secret-ignore WARN, and PASS Secret-ignore rules present (.env, .env.*, !.env.example), although git check-ignore -q --no-index .env.production exits 1. Check the required wildcard rule rather than equating a single ignored filename with that rule; retain effective-behavior checks and add this regression case (AC-3).
- Both findings from the previous review at 44f0582f637f21db419570eb29cc05b49ede7307 are resolved at this HEAD. CI run 39323098529 passes on Linux, macOS and Windows: https://github.com/peejerator/newproj/actions/runs/39323098529. The older implementation/validation claims that CI still needs a push are superseded by this evidence; other sections remain unchanged as required by the review skill.
- The implementer authored the acceptance criteria for this standard task; this is weaker evidence than user-confirmed criteria. Review used a separate session and model from the recorded Claude Code/claude-opus-5-5 implementer.
- Real GitHub publication and the real tagged template repository were not exercised; remote behavior and tag selection were checked using fake gh and local bare/tagged repositories.

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
