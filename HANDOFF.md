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

## Review

Outcome: FAIL
Reviewer: Claude Code/claude-opus-5-5, 2026-10-19
Reviewed at: 4c3aaad5e7a0cc050a58bd691f24cfb59294dbad
Contract: eeb34ae4650076a2a8f148fd50de5bc594bf94d5
Working tree clean at review: yes
Baseline: base-commit diff
Artifact coverage: complete
Validation provenance: reviewer-executed

- AC-1: VERIFIED | canonical SKILL.md frontmatter has name, the required description, and disable-model-invocation: true; agents/openai.yaml sets policy.allow_implicit_invocation: false; the three pointers carry byte-identical frontmatter (diff, test_rendered_start_task, doctor PASS).
- AC-2: VERIFIED | start-task/SKILL.md covers all three sources with Issue:, data treatment and paste fallback; state.py and Git preconditions; never commits, pushes, or pulls; git switch -c before writing; facts first; rounds of at most 10 with no total limit, comprehensive, "yes" accepts, tier and formal-risk flags; draft after Round 1 updated each round with decisions under ## Context; explicit confirmation and the exact line; HANDOFF.md not started, both files staged, one && block; the exact stop prompt and "go" after commit. See Findings for a defect in how decisions 3 and 4 combine.
- AC-3: VERIFIED | SKILL.md defers header lines, Base commit:, Target branch:, and end-state criteria to handoff's Writing a task (E-007, E-008) without restating them; test_start_task_reuses_format_and_interview_reference asserts no contract headings.
- AC-4: VERIFIED | references/interview.md has Facts and decisions, Recommendations, Comprehensive rounds, and Finish conditions; SKILL.md step 5 says to read it before Round 1 and when answers raise new decisions.
- AC-5: VERIFIED | protocol lists start-task among user-invoked skills, 114 lines; review records user-confirmed criteria when the line is present; resume summarizes a draft and points to start-task without activating; handoff Writing a task names start-task and stays the format and escalation reference; PROMPTS.md lists start-task and adds a draft-only Start a task prompt per interview.md; both AGENTS files list start-task.
- AC-6: VERIFIED | SKILLS and USER_SKILLS include start-task; doctor checks references/interview.md; tests cover missing, malformed, policy, and pointer FAILs for start-task; generated project summary names 6 skills (reviewer run).
- AC-7: VERIFIED | E-018 appended, amending 17, E-010's list, 17.1, 17.3, 17.5, 17.6 and D22, recording decisions 1 to 11 and the confirmation line; ROADMAP has M5.1 between M5 and M6.
- AC-8: VERIFIED | tests for rendered skill, openai.yaml, pointers, frontmatter, interview.md, identical confirmation line in start-task and review, doctor FAILs, and a no-FAIL generated project; 363 passed (reviewer) and CI success on Linux, macOS, Windows for 4c3aaad.

Findings:
- Blocking: an interrupted start-task interview cannot be continued. Round step 3 creates the task branch with git switch -c after Round 1 and leaves the draft uncommitted on it, but preflight step 3 requires the user to be on the target branch with an upstream and zero ahead/behind, and stops otherwise. A later invocation on the draft therefore stops ("on another branch, or missing an upstream"), and if the user switches back to the target, git switch -c fails because the branch exists. Because resume now sends every draft to start-task and no longer activates drafts (this diff), an in-repository draft has no supported path to activation: a regression in draft handling. Decisions 3 and 4 in TASK.md combine to produce this, and the implementer did not raise the conflict under blockers. Fix needs the user's decision, for example: for Status: draft, require the current branch to be the draft's task branch (or the target, for a draft brought from a session without repository access), skip git switch -c when already on it, and check freshness of the target rather than of HEAD; record the amendment in E-018 and test or document the path.
- Minor: state.py's report labels the draft state start-task creates (draft TASK.md with neutral HANDOFF.md) as a metadata mismatch and says "an active task should not change". Preflight tells the agent to reconcile without repairing; consider stating in SKILL.md that these signals are expected for a draft.
- The acceptance criteria were user-confirmed on 2026-10-19 (Acceptance criteria confirmed by the user: line under ## Context).
- Independent review: implemented by Codex, reviewed by Claude (different model family), different session.
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
