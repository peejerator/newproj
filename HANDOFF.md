# Handoff

Last updated: 2026-10-19 by Codex
Branch: m5.1-start-task
Task: standard
Environment: other

## Status

in progress

## Completed

- AC-1: added canonical start-task metadata, invocation policy, three matching pointers, and root policy copy.
- AC-2: documented all three sources, preconditions, branch creation, question rounds, draft updates, confirmation, staging, and stop/go behavior.
- AC-3: contract headers, baseline, target, and end-state criterion rules stay in handoff's Writing a task section.
- AC-4: added and linked the interview reference for facts, decisions, recommendations, comprehensive rounds, and finish conditions.
- AC-5: aligned protocol, review, resume, handoff, prompts, and both AGENTS files; protocol remains 114 lines.
- AC-6: doctor checks six skills, start-task metadata/policy/reference, and its Claude pointer.
- AC-7: appended E-018 covering decisions 1 to 11 and added the M5.1 roadmap row and M6 first-use reminder.
- AC-8: render, pointer, confirmation-marker, policy, doctor failure, and healthy-project tests pass locally; reviewer recorded passing three-OS CI for 4c3aaad.

## Current working area

- `HANDOFF.md`
- `template/.agents/skills/`
- `template/.claude/skills/start-task/`
- `.agents/skills/start-task/`
- `.claude/skills/start-task/`
- `template/docs/`
- `template/AGENTS.md.jinja`
- `src/newproj/doctor.py`
- `tests/`
- `AGENTS.md`
- `docs/ERRATA.md`
- `docs/ROADMAP.md`

## Validation

- PASS | uv run pytest | 363 passed; AC-1, AC-5, AC-6, AC-8 regression coverage; one expected Copier dirty-template warning | Linux, Python 3.13.5, Copier 9.18.2 | implementer
- PASS | uv run pytest tests/test_agent_content.py tests/test_render.py | 160 passed after final skill wording changes; AC-1, AC-3, AC-4, AC-5, AC-8 | Linux | implementer
- PASS | AC-2 manual inspection | every behavior in Context decisions 2 to 9 is present in start-task/SKILL.md | working-tree skill and interview reference | implementer
- PASS | AC-3, AC-4 manual inspection | format is referenced rather than copied; interview guidance covers all four requested topics and is linked before Round 1 | working-tree skill, reference, handoff | implementer
- PASS | AC-5, AC-7 manual inspection | all named instruction surfaces agree; protocol 114 lines; E-018 records decisions 1 to 11; M5.1 sits between M5 and M6 | working-tree diff | implementer
- PASS | git diff --check | no whitespace errors; full diff inspected; TASK.md, spec, state copies, bootstrap, accept, and Review section unchanged | working tree | implementer
- PASS | uv run --no-project template/.agents/skills/resume/scripts/state.py check --neutral-dir template/.agents/skills/handoff/neutral | no violations found | repository root | implementer
- PASS | uv run --project <repo> newproj new demo --no-remote --template-path <repo>; uv run --project <repo> newproj doctor | generated demo; doctor: 19 PASS, 1 WARN, 0 FAIL; six skills present (AC-6, AC-8); warning is unauthenticated isolated gh config | scratch directory, synthetic Git identity, Linux | implementer
- FAIL | uv run python <skill-creator>/scripts/quick_validate.py template/.agents/skills/start-task | generic validator rejects disable-model-invocation, which AC-1 and E-010 require; repository metadata, policy, pointer, and render tests pass | supplementary validator compatibility limitation | implementer
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

1. Obtain the user's decision on the draft-resumption exception below. Implementation and review are already committed (4c3aaad and 9497bf6); the PR already exists.
2. After the decision, fix the draft-resumption path, clarify expected draft-state signals, add regression coverage, and append an erratum superseding the affected E-018 rules. Leave the active TASK.md and Review unchanged.
3. Run relevant validation, stage the fixes, and print commit and push commands for the user. Then check three-OS CI for the new implementation and request independent review in a different agent.

## Blockers / open questions

- User decision required: May draft resumption reuse the existing task branch without creating it again, check the target branch's freshness instead of HEAD, and retain target-branch preflight and branch creation for new or imported drafts? Recommended: yes. This amends Context decisions 3 and 4 in TASK.md; the implementer must not change that active contract. Append the accepted amendment to ERRATA.md instead of rewriting E-018.
- Review FAIL remains current. Inspection confirms the branch-preflight and branch-creation conflict in start-task/SKILL.md. The old next steps and pending-CI claims were stale; the implementation, review, and recorded CI results are already present. No implementation changes made during resume.

## Relevant decisions

- The user's decisions for this milestone are under `## Context` in `TASK.md`.
- E-018 records the new workflow and its amendments; E-007, E-008, E-010, and E-014 remain applicable.
