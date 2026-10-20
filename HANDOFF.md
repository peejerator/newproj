# Handoff

Last updated: 2026-10-20 by Codex
Branch: m5.1-start-task
Task: standard
Environment: other

## Status

validating

## Completed

- AC-1: canonical start-task metadata, invocation policy, three matching pointers, and root policy copy are implemented.
- AC-2: sources, preconditions, rounds, confirmation, and handoff are implemented; E-019 allows interrupted draft resumption. Reused branches now must contain the fresh target before continuing.
- AC-3: contract format remains in handoff's Writing a task section.
- AC-4: interview guidance covers facts, decisions, rounds, finish conditions, and draft resumption, including stale and diverged task branches.
- AC-5: protocol, review, resume, handoff, prompts, and both AGENTS files agree; protocol remains 114 lines.
- AC-6: doctor checks six skills and the start-task metadata, policy, reference, and pointer.
- AC-7: E-018, E-019, and roadmap record the milestone and approved draft-resumption exception; accepted records and TASK.md remain unchanged.
- AC-8: 363 tests pass locally. Test Git configuration now disables maintenance.auto and gc.auto to prevent background repacking during Copier's local clone. Git 2.55 project-creation tests pass; CI on the new fix remains pending.

## Current working area

- `HANDOFF.md`
- `tests/conftest.py`
- `template/.agents/skills/start-task/SKILL.md`
- `template/.agents/skills/start-task/references/interview.md`

## Validation

- PASS | uv run pytest | 363 passed; AC-1, AC-3 to AC-6, AC-8; one expected Copier dirty-template warning | Linux, Python 3.13.5, Git 2.47.3, Copier 9.18.2, working tree | implementer
- PASS | PATH=<reviewer's Git 2.55 bin>:$PATH uv run pytest tests/test_new.py | 28 passed, including the previously failing tagged-template test; one expected Copier dirty-template warning; AC-8 | Linux, Git 2.55.0, working tree | implementer
- PASS | Git 2.55 trace checks using write_gitconfig in a scratch repository | commit spawns no maintenance, gc, or repack child; positive control with maintenance.auto=true spawns maintenance; AC-8 | synthetic local repository, working-tree fixture | implementer
- PASS | synthetic Git stale-target and divergence recipes | fresh target alone passes while ancestry fails; merge --ff-only repairs stale task branch; divergence refuses without changing HEAD or draft; AC-2, AC-4 | Git 2.55.0, local scratch remote, settled draft preserved | implementer
- PASS | manual acceptance-criterion inspection | AC-1 to AC-7 remain implemented; ancestry guidance follows E-019's fresh-target intent; metadata, contract format, and accepted records unchanged | working tree and base-commit diff | implementer
- PASS | newproj new demo --no-remote --template-path <repo>; newproj doctor <demo> | 20 PASS, 0 WARN, 0 FAIL; six skills and pointers pass; AC-6, AC-8 | scratch directory, synthetic Git identity, Linux, Git 2.47.3 | implementer
- PASS | git diff --check and full diff inspection | no whitespace errors or unintended changes; TASK.md, frozen spec, state copies, bootstrap, accept, accepted errata, and Review section unchanged | working tree | implementer
- PASS | uv run --no-project template/.agents/skills/resume/scripts/state.py check --neutral-dir template/.agents/skills/handoff/neutral | no violations found | repository root | implementer
- NOT RUN | CI push and pull_request events on all three operating systems | requires the user to commit and push these fixes; prior d3825a8 pull_request CI failed on Ubuntu; AC-8 remains pending | working-tree fixes | implementer
- NOT RUN | independent review of the new fixes | review requires committed work and a different agent; recorded Review below is preserved | working-tree fixes | implementer
- PASS | uv run pytest | 363 passed, one expected Copier dirty-template warning; AC-1 to AC-6, AC-8 | Linux, Git 2.47.3, commit 79266255fa81d8764040723493e5e3f331d923ed | reviewer
- PASS | git diff --check 02c79ac...HEAD | no whitespace errors | commit 79266255fa81d8764040723493e5e3f331d923ed | reviewer
- PASS | uv run --no-project template/.agents/skills/resume/scripts/state.py check --neutral-dir template/.agents/skills/handoff/neutral | no violations found | repository root | reviewer
- PASS | newproj new demo --no-remote --template-path <repo>; newproj doctor demo | 19 PASS, 1 WARN (no origin), 0 FAIL; the 6 skills and pointers pass; AC-6 | scratch directory, Linux | reviewer
- PASS | GitHub Actions CI push run 39372066605 and pull_request run 39372072714 | ubuntu-latest, macos-latest, windows-latest all succeeded; AC-8 | commit 79266255fa81d8764040723493e5e3f331d923ed | CI

## Review

Outcome: PASS
Reviewer: Claude Code/claude-opus-5-5, 2026-10-20
Reviewed at: 79266255fa81d8764040723493e5e3f331d923ed
Contract: eeb34ae4650076a2a8f148fd50de5bc594bf94d5
Working tree clean at review: yes
Baseline: base-commit diff
Artifact coverage: complete
Validation provenance: reviewer-executed

- AC-1: VERIFIED | canonical SKILL.md frontmatter has name: start-task, the required description, and disable-model-invocation: true; agents/openai.yaml sets policy.allow_implicit_invocation: false; the three pointers carry identical frontmatter (render test, doctor PASS in a generated project).
- AC-2: VERIFIED | SKILL.md covers the three sources with Issue:, data treatment and the paste fallback; state.py and Git preconditions; never commits, pushes, or pulls; git switch -c before writing, with E-019's reuse of an interrupted draft's task branch; facts first; rounds of at most 10 with no total limit, comprehensive, "yes" accepts, tier and formal-risk flags; draft after Round 1, updated each round, decisions under ## Context; explicit confirmation and the exact line; HANDOFF.md not started, both files staged, one && block; the exact stop prompt and "go" after commit. 7926625 adds the ancestry check (git merge-base --is-ancestor <target> HEAD, then git merge --ff-only, never reset or rebase) for a reused task branch, resolving the prior non-blocking finding.
- AC-3: VERIFIED | SKILL.md defers header lines, Base commit:, Target branch:, and end-state criteria to handoff's Writing a task (E-007, E-008) without restating them; test asserts no contract headings.
- AC-4: VERIFIED | references/interview.md has Facts and decisions, Recommendations, Comprehensive rounds, Draft resumption cases (now including the stale task branch case), and Finish conditions; SKILL.md says when to read it.
- AC-5: VERIFIED | protocol lists start-task among user-invoked skills (114 lines); review records user-confirmed criteria; resume summarizes a draft and points to start-task without activating; handoff Writing a task names start-task and remains the format and escalation reference; PROMPTS.md lists start-task with a draft-only Start a task prompt; both AGENTS files list start-task.
- AC-6: VERIFIED | SKILLS and USER_SKILLS include start-task, plus a references/interview.md check; tests cover missing, malformed, policy, and pointer FAILs; reviewer-generated project shows 0 FAIL and "the 6 skills, and their pointers".
- AC-7: VERIFIED | E-018 records decisions 1 to 11, the confirmation line, and the amendments to 17, E-010, 17.1, 17.3, 17.5, 17.6 and D22; E-019 is appended for the user-approved exception; ROADMAP has M5.1 between M5 and M6; accepted entries unchanged.
- AC-8: VERIFIED | the listed tests exist; 363 pass locally (reviewer); CI push run 39372066605 and pull_request run 39372072714 on 79266255fa81d8764040723493e5e3f331d923ed both passed on ubuntu, macos, and windows.

Findings:
- None blocking. The prior blocking finding (Git 2.54+ background maintenance racing Copier's local clone in tests) is fixed in tests/conftest.py write_gitconfig with maintenance.auto=false and gc.auto=0, which every isolate()-based test, including the identity=False rewrites in test_new.py and test_doctor.py, inherits through GIT_CONFIG_GLOBAL. The fix has a comment but no regression test; the reviewer could not reproduce the race locally (Git 2.47.3), so the evidence that it is fixed is the root-cause analysis plus green CI on both events, not a demonstrated before/after.
- Non-blocking, outside M5.1 scope and still open: real use of newproj new --template-path right after a commit on Git 2.54+ can hit the same race; recorded under Blockers for a later task.
- Non-blocking: in the reviewer's generated project, doctor also reported "WARN The default branch does not resolve", expected for --no-remote (no origin); the implementer's 0 WARN run differs only in environment. Not an M5.1 change.
- The acceptance criteria were user-confirmed on 2026-10-19 (Acceptance criteria confirmed by the user: line under ## Context).
- Independent review: implemented by Codex, reviewed by Claude (different model family), in a different session. Earlier reviews of this task were also by claude-opus-5-5, in other sessions.

## Exact next steps

1. User commits the staged fixes and pushes: `git commit -m "Fix test clone race and draft branch freshness" && git push`. The PR already exists.
2. Check both push and pull_request CI events on that commit; tests must pass on Linux, macOS, and Windows.
3. User invokes review in a different agent against the committed fixes. Keep TASK.md active and the existing Review unchanged until that review.

## Blockers / open questions

- No unanswered user question. E-019 records the user's approved draft-resumption exception to TASK.md Context decisions 3 and 4.
- The recorded FAIL covers d3825a8. Its blocking fixture race and nonblocking branch-ancestry finding are addressed in the working tree; CI and independent review of these fixes remain pending.
- Deferred outside M5.1 scope: real use of --template-path immediately after a commit can encounter the same Copier local-clone/background-repack race on Git 2.54+. This fix changes test isolation only; consider clone transport or retry behavior in a later task.
- The generic skill-creator validator rejects disable-model-invocation required by AC-1 and E-010; this previously recorded supplementary limitation is nonblocking. Repository metadata, policy, pointer, and render tests pass.

## Relevant decisions

- User-confirmed milestone decisions are under Context in TASK.md.
- E-019 supersedes E-018's conflicting branch rules; E-007, E-008, E-010, and E-014 remain applicable.
