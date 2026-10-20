# Handoff

Last updated: 2026-10-19 by Codex
Branch: m5.1-start-task
Task: standard
Environment: other

## Status

validating

## Completed

- AC-1: added canonical start-task metadata, invocation policy, three matching pointers, and root policy copy.
- AC-2: documented sources, preconditions, rounds, confirmation, and handoff; user-approved E-019 now reuses an interrupted draft's task branch and checks the target's freshness. Expected draft-state warnings are explained.
- AC-3: contract headers, baseline, target, and end-state criterion rules stay in handoff's Writing a task section.
- AC-4: linked interview guidance covers facts, decisions, recommendations, comprehensive rounds, finish conditions, and five branch/draft scenarios.
- AC-5: aligned protocol, review, resume, handoff, prompts, and both AGENTS files; protocol remains 114 lines.
- AC-6: doctor checks six skills, start-task metadata/policy/reference, and its Claude pointer.
- AC-7: E-018 and roadmap cover the milestone; appended E-019 records the user's approved draft-resumption exception without changing TASK.md or accepted errata.
- AC-8: 363 tests pass after the fix; existing three-OS CI covers 4c3aaad only. CI and independent review of this fix are pending.

## Current working area

- `HANDOFF.md`
- `template/.agents/skills/start-task/SKILL.md`
- `template/.agents/skills/start-task/references/interview.md`
- `docs/ERRATA.md`

## Validation

- PASS | uv run pytest | 363 passed after draft-resumption fix; AC-1, AC-3 to AC-6, AC-8; one expected Copier dirty-template warning | Linux, Python 3.13.5, Copier 9.18.2 | implementer
- PASS | AC-2, AC-3, AC-4, AC-5, AC-7 manual inspection | E-019 exception implemented; existing decisions and confirmation preserved; format still referenced; branch scenarios documented; other instruction surfaces unchanged | working-tree skill, reference, erratum | implementer
- PASS | isolated Git recipe checks and state.py check | five documented Git/draft-state scenarios exercised with synthetic local remotes: new task, interrupted draft without upstream, imported draft, identifiable task branch after switching, stale target; draft check passes with expected report signals; interview routing inspected manually | Linux, temporary fixtures | implementer
- PASS | git diff --check | no whitespace errors; full diff inspected; TASK.md, spec, state copies, bootstrap, accept, and Review section unchanged | working tree | implementer
- PASS | uv run --no-project template/.agents/skills/resume/scripts/state.py check --neutral-dir template/.agents/skills/handoff/neutral | no violations found | repository root | implementer
- FAIL | .venv/bin/python <skill-creator>/scripts/quick_validate.py template/.agents/skills/start-task | unchanged generic-validator limitation: rejects disable-model-invocation required by AC-1 and E-010; repository metadata, policy, pointer, and render tests pass | supplementary check, Linux | implementer
- NOT RUN | CI and independent review of the draft-resumption fix | user must commit and push these changes before new CI and committed-work review | working-tree changes only | implementer
- PASS | uv run pytest | 363 passed, one expected Copier dirty-template warning; AC-1, AC-3 to AC-6, AC-8 | Linux, Python 3.13.5, commit 4c3aaad | reviewer
- PASS | git diff --check 02c79ac...HEAD | no whitespace errors | commit 4c3aaad | reviewer
- PASS | uv run --no-project template/.agents/skills/resume/scripts/state.py check --neutral-dir template/.agents/skills/handoff/neutral | no violations found | repository root, commit 4c3aaad | reviewer
- PASS | newproj new demo --no-remote --template-path <repo>; newproj doctor | 19 PASS, 1 WARN (default branch unresolved without a remote), 0 FAIL; "the 6 skills, and their pointers" PASS; AC-6, AC-8 | scratch directory, synthetic Git identity, Linux | reviewer
- PASS | state.py check on a generated project with a draft TASK.md (empty Task ID, Base commit, Target branch) and neutral HANDOFF.md | no violations found; the report flags the pair as a metadata mismatch | scratch project, Linux | reviewer
- PASS | CI push run 39352232732 and pull_request run 39352237929 | Tests on ubuntu-latest, macos-latest, windows-latest all success; AC-8 | commit 4c3aaad5e7a0cc050a58bd691f24cfb59294dbad | CI
- PASS | uv run pytest | 363 passed, one expected Copier dirty-template warning; AC-1, AC-3 to AC-6, AC-8 | Linux, Python 3.13.5, commit d3825a8 | reviewer
- PASS | git diff --check 02c79ac...HEAD | no whitespace errors; no em or en dashes in added lines; ERRATA diff since 4c3aaad is append only | commit d3825a8 | reviewer
- PASS | uv run --no-project template/.agents/skills/resume/scripts/state.py check --neutral-dir template/.agents/skills/handoff/neutral | no violations found | repository root, commit d3825a8 | reviewer
- PASS | newproj new demo --no-remote --template-path <repo>; newproj doctor | 20 PASS, 0 WARN, 0 FAIL, 4 INFO; "the 6 skills, and their pointers" PASS; rendered interview.md has Draft resumption cases; AC-6, AC-8 | scratch directory, synthetic Git identity, Linux, commit d3825a8 | reviewer
- PASS | synthetic Git recipe for the stale-target resumption path | target freshness check passes after the user pulls main and returns to the task branch, but the task branch does not contain main's new tip; see Review findings | scratch repositories, Linux, commit d3825a8 | reviewer
- PASS | CI push run 39363083402 | Tests on ubuntu-latest, macos-latest, windows-latest all success; AC-8 | commit d3825a8c39665997bc7768836b26cf38f6e8b06b | CI
- FAIL | CI pull_request run 39363087923, attempts 1 and 2 | macOS and Windows success; ubuntu-latest failed both attempts in tests/test_new.py::test_template_path_renders_working_tree_of_tagged_repository: git clone "failed to copy file to .../.git/objects/<xx>/<loose object>: No such file or directory" (1 failed, 362 passed); AC-8 | commit d3825a8c39665997bc7768836b26cf38f6e8b06b, git 2.55.0, ubuntu-24.04 image 20261012.334.1 | CI
- FAIL | Git 2.55.0 built from source; commit in a copy of d3825a8's template, then local git clone after a 0 to 30 ms delay | 2/93 clones failed with the CI error under default config, 0/93 with maintenance.auto=false; GIT_TRACE2 shows the commit spawning detached git maintenance run --auto, then git repack -d, leaving 0 loose objects; AC-8 | Linux, scratch repositories | reviewer
- PASS | object shard count for the test's template repository at each M5.1 commit | objects/17 holds 2 objects (trees 172097b..., 17904c7...) at d3825a8 and 0 at 02c79ac, 4549236, 4c3aaad, 9497bf6, b6a9a40 | git 2.47.3, scratch repositories | reviewer

## Review

Outcome: FAIL
Reviewer: Claude Code/claude-opus-5-5, 2026-10-19
Reviewed at: d3825a8c39665997bc7768836b26cf38f6e8b06b
Contract: eeb34ae4650076a2a8f148fd50de5bc594bf94d5
Working tree clean at review: yes
Baseline: base-commit diff
Artifact coverage: complete
Validation provenance: reviewer-executed

- AC-1: VERIFIED | canonical SKILL.md frontmatter has name, the required description, and disable-model-invocation: true; agents/openai.yaml sets policy.allow_implicit_invocation: false; the three pointers carry identical frontmatter (render tests, doctor PASS in a generated project).
- AC-2: VERIFIED | SKILL.md covers the three sources with Issue:, data treatment and the paste fallback; state.py and Git preconditions; never commits, pushes, or pulls; git switch -c before writing for new and imported drafts, and reuse of the recorded task branch for an interrupted draft (E-019, user-approved); facts first; rounds of at most 10 with no total limit, comprehensive, "yes" accepts, tier and formal-risk flags; draft after Round 1, updated each round, decisions and task branch under ## Context; explicit confirmation and the exact line; HANDOFF.md not started, both files staged, one && block; the exact stop prompt and "go" after commit. The prior blocking finding is resolved.
- AC-3: VERIFIED | SKILL.md defers header lines, Base commit:, Target branch:, and end-state criteria to handoff's Writing a task (E-007, E-008) without restating them; test asserts no contract headings.
- AC-4: VERIFIED | references/interview.md has Facts and decisions, Recommendations, Comprehensive rounds, Draft resumption cases, and Finish conditions; SKILL.md step 5 says when to read it, and preflight step 3 cites the resumption cases.
- AC-5: VERIFIED | protocol lists start-task among user-invoked skills and stays at 114 lines; review records user-confirmed criteria; resume summarizes a draft and points to start-task without activating; handoff Writing a task names start-task and remains the format and escalation reference; PROMPTS.md lists start-task with a draft-only Start a task prompt; both AGENTS files list start-task.
- AC-6: VERIFIED | SKILLS and USER_SKILLS include start-task; tests cover missing, malformed, policy, and pointer FAILs; generated project shows 0 FAIL and names 6 skills (reviewer run).
- AC-7: VERIFIED | E-018 appended with decisions 1 to 11, the confirmation line, and amendments to 17, E-010, 17.1, 17.3, 17.5, 17.6 and D22; E-019 appended for the user-approved draft-resumption exception without altering E-018; ROADMAP has M5.1 between M5 and M6.
- AC-8: UNSATISFIED | the tests listed exist and 363 pass locally (reviewer), and CI push run 39363083402 passed on all three systems, but CI pull_request run 39363087923 failed on ubuntu-latest in both attempts. The cause is a race between Git 2.54+ background auto-maintenance and Copier's local clone; d3825a8's template content makes it trigger on every test commit (see Findings). Passing CI on all three operating systems is not reliably met.

Findings:
- Blocking (AC-8): tests/test_new.py::test_template_path_renders_working_tree_of_tagged_repository fails intermittently on Git 2.54 and later, and failed both pull_request attempts on ubuntu-latest (git 2.55.0). Root cause, reproduced with Git 2.55.0 built from source:
  - Since Git 2.54 the default maintenance strategy is "geometric". After git commit, `git maintenance run --auto --detach` runs the geometric-repack task when the estimated loose-object count exceeds 256 (default threshold 100, rounded up to 256). The estimate is 256 times the number of loose objects in objects/17/ (builtin/gc.c too_many_loose_objects; odb/source-loose.c), so 2 objects in that one shard are enough.
  - Blob and tree hashes depend only on content. At d3825a8 the test's template repository has 2 trees in objects/17 (172097b..., the template/.agents tree, and 17904c7...); at every earlier M5.1 commit it has 0. Every commit the test fixture makes therefore starts a background `git repack -d`, which deletes all loose objects once they are packed.
  - Copier clones a local template with `git clone --no-checkout <path>`, which hardlinks or copies objects/ file by file. If the background repack deletes a loose object between the directory listing and the copy, clone dies with exactly the CI error. Local reproduction: 2/93 clones failed under default config, 0/93 with maintenance.auto=false. Whether the race hits depends on timing, which is why push run 39363083402 passed and local runs pass.
  - This milestone's diff did not introduce the race (the test and the clone path are from M5), but it is what turns the trigger on, so CI on the PR is red and AGENTS.md requires CI to pass before merging.
  - Suggested fix, in scope under tests/: add `[maintenance]` `auto = false` (and `[gc]` `auto = 0` for older Git) to write_gitconfig in tests/conftest.py, which every test's Git and Copier inherit through GIT_CONFIG_GLOBAL. Better still, add a regression test or comment so the suite never depends on object-hash luck. Then rerun three-OS CI on both the push and pull_request events.
- Non-blocking, outside M5.1 scope: the same race can affect real use of `newproj new --template-path <repo>` (E-002) right after a commit in that repository on Git 2.54 or later, because Copier's local clone and the background repack overlap. The window is milliseconds; consider recording it for a later milestone (for example, cloning with --no-local or retrying).
- Non-blocking: on the stale-target resumption path, preflight checks the target against its upstream but not that the task branch contains the target. Following interview.md's case (update main, return to m6-adopt), the task branch still points at the old main tip, so the activation-time Base commit is stale while the freshness check passes (reproduced with synthetic repositories). Suggested follow-up: for a reused task branch, also require git merge-base --is-ancestor <target> HEAD and, if it fails, tell the user to run git merge --ff-only <target> on the task branch (it has no commits yet).
- The prior review's blocking finding (interrupted draft cannot be continued) is resolved by E-019 and the SKILL.md preflight; its minor finding (expected state.py draft warnings) is addressed in SKILL.md preflight step 1 and interview.md.
- The acceptance criteria were user-confirmed on 2026-10-19 (Acceptance criteria confirmed by the user: line under ## Context).
- Independent review: implemented by Codex, reviewed by Claude (different model family), different session. The previous review was also by claude-opus-5-5, in another session. A first version of this review recorded PASS while treating the Ubuntu failure as flaky; the user's rerun failed again, and the root-cause investigation above replaced it.
- The implementer's FAIL entry for the generic skill-creator validator reflects that tool's rejection of disable-model-invocation, which AC-1 and E-010 require; not a defect.

## Exact next steps

1. User commits the staged fix and pushes: `git commit -m "Fix start-task draft resumption" && git push`. The PR already exists.
2. Check three-OS CI on that implementation commit; prior CI covers 4c3aaad only.
3. User invokes review in a different agent against the committed fix. Leave TASK.md active and Review unchanged until then.

## Blockers / open questions

- No unanswered user question. On 2026-10-19 the user approved reusing the existing draft branch, checking target freshness, and retaining branch creation for new/imported drafts; E-019 records the exception to TASK.md Context decisions 3 and 4.
- The recorded FAIL is historical after these skill changes. Its blocking and minor findings are addressed by the implementer; a new independent review and three-OS CI remain pending. The generic skill validator's required-metadata incompatibility remains supplementary and nonblocking.

## Relevant decisions

- The user's decisions for this milestone are under `## Context` in `TASK.md`.
- E-019 supersedes E-018's conflicting branch rules; E-007, E-008, E-010, and E-014 remain applicable.
