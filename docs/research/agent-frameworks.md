# Ideas from other agent frameworks

Input for planning the milestones after M8 (decision 20). It records what seven spec-driven and agent-workflow frameworks did when checked, and the user's decisions on what newproj adopts from them. These projects change quickly: before the milestone that uses an item starts, recheck that framework's current documentation and record what changed (decision 10).

## Sources

All checked 2026-11-11 from public pages. "Not found" means the pages read did not say, not that the feature is absent.

| Framework | Pages read | Version seen |
|---|---|---|
| GitHub Spec Kit | github.com/github/spec-kit; github.github.com/spec-kit (home, installation, overview/core, reference/agentic-sdd); spec-driven.md | docs updated 2026-11-04; 0.12.11 used as an install example |
| OpenSpec | github.com/Fission-AI/OpenSpec; openspec.dev/docs (installation, cli, glossary, schemas/spec-driven) | 1.13 to 1.15 in examples |
| Kiro | kiro.dev/docs/specs, specs/feature-specs, specs/bugfix-specs, steering | pages updated 2026-08-04 to 2026-10-21 |
| BMAD Method | github.com/bmad-code-org/BMAD-METHOD; docs.bmad-method.org (choose-a-planning-path, build-your-first-change) | v6.12 stable; v7 alpha, release expected mid-November 2026 |
| Superpowers | github.com/obra/superpowers; its skills/ listing; skills/verification-before-completion/SKILL.md | not shown |
| Agent OS | github.com/buildermethods/agent-os; buildermethods.com/agent-os (home, workflow, file-structure); install steps are behind an email signup | "v3" |
| Taskmaster AI | github.com/eyaltoledano/claude-task-master; tryhamster.com/docs/taskmaster (task-structure) | not shown |
| Cline Memory Bank | docs.cline.bot/prompting/cline-memory-bank | not shown |

## Findings

**Spec Kit.** CLI `specify` (PyPI `specify-cli`, Python 3.11+, `uv tool install`). Core commands: constitution, specify, clarify (at most five questions), plan, checklist, tasks, analyze (read-only consistency check of spec, plan, and tasks), implement, converge (compares the code with spec, plan, and tasks; appends gaps to `tasks.md` until "Converged"). Per-feature `specs/<NNN-feature>/` with `spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`, `tasks.md`. Git branches only through an optional git extension. Custom checklists are ticked by a human; implement never ticks them. Brownfield through `specify init --here --force`, which also refreshes managed files while keeping user edits. Extensions, presets, workflows, bundles, and catalogs (186 community extensions, 42 presets). 41 agent integrations. Bash, PowerShell, and Python scripts. No handoff, resume, or cross-machine feature found.

**OpenSpec.** MIT; Node 22.12+; telemetry on by default (command names and version). Living specs in `openspec/specs/<capability>/spec.md`; each change in `openspec/changes/<name>/` with `proposal.md`, `design.md`, `tasks.md`, and delta specs (`## ADDED`, `## MODIFIED`, `## REMOVED`, `## RENAMED Requirements`). `openspec archive` validates, previews, then merges each delta into its main spec and moves the change to `changes/archive/<date>-<name>/`. Requirements use SHALL or MUST, each with at least one `#### Scenario:` of WHEN and THEN bullets (not EARS). `openspec validate [--strict]`; `/opsx:verify` checks the implementation against the change before archiving. `openspec status` prints a `Next:` line, which the docs say is enough to resume in a fresh session. Several active changes at once.

**Kiro.** Feature specs (`requirements.md` or `bugfix.md`, `design.md`, `tasks.md`), bugfix specs, and quick specs. Requirements use EARS: `WHEN [condition/event] THE SYSTEM SHALL [expected behavior]`; no other EARS patterns shown. Bugfix specs add `WHEN [condition] THEN the system SHALL CONTINUE TO [existing behavior]`. Analyze Requirements checks for inconsistencies, ambiguities, conflicts, and gaps before design. Steering files in `.kiro/steering/` (`product.md`, `tech.md`, `structure.md`) with inclusion modes `always`, `fileMatch`, `manual`, `auto`. Reads `AGENTS.md` (always included, also in subdirectories). Tasks run in dependency "waves". Spec location `.kiro/specs/<name>/` not confirmed.

**BMAD Method.** MIT. v7 is skills-based (needs a tool that supports skills, and uv). Scale-adaptive paths: trivial, one session (`bmad-build`), epic-sized, project-sized. Personas: analyst, PM, product owner, UX, architecture. Tracking in `tickets.toml` with a `.memlog.md`; artifacts in `_bmad-output` by default. No session handoff or resume feature found.

**Superpowers.** MIT; installs per tool (Claude Code, Codex, Cursor, Gemini CLI, Copilot CLI, OpenCode, Pi, and others). Skills include brainstorming, writing-plans, executing-plans, subagent-driven-development (review after each task: spec compliance, then code quality), test-driven-development, systematic-debugging, using-git-worktrees, finishing-a-development-branch, requesting and receiving code review, verification-before-completion ("NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE"; "If you haven't run the verification command in this message, you cannot claim it passes"). Optional visual companion has telemetry. No handoff or resume feature found.

**Agent OS.** MIT. Discovers a codebase's standards and injects them into context: `agent-os/standards/`, `agent-os/product/` (`mission.md`, `roadmap.md`, `tech-stack.md`), `agent-os/specs/`; commands `/discover-standards`, `/index-standards`, `/inject-standards`, `/plan-product`, `/shape-spec`. Full integration with Claude Code; other tools read the files. No verification, review, or resume feature found.

**Taskmaster AI.** MIT with Commons Clause (no selling it, hosting it as a service, or building competing products). Node; MCP server with up to 36 tools; needs an API key except through Claude Code or Codex. Tasks with dependencies, priorities, `testStrategy`, and subtasks; `parse-prd`, `next`, `analyze-complexity`, tags.

**Cline Memory Bank.** A custom-instructions convention, not a built-in feature: `memory-bank/` with `projectbrief.md`, `productContext.md`, `activeContext.md`, `systemPatterns.md`, `techContext.md`, `progress.md`. No guidance on keeping files small; it invites adding files.

## Decisions

Numbers are the interview's question numbers. Round 1 was answered 2026-11-11; Round 2 on 2026-11-15. Questions 11 to 20 restate or replace the open parts of 3 to 9.

1. Settled: this note now; the work is planned after M8 is accepted (structure per decision 20); spec changes get ERRATA entries.
2. Settled: items may be adopted on the user's judgment without dogfooding evidence (D29); each records its reason in its ERRATA entry.
3. Restated as 11; answered by 21.
4. Restated as 12; answered by 22.
5. Settled in principle: completion claims need fresh evidence; details in 13.
6. Settled: a contract check (contradictions, unverifiable criteria, gaps) before the user confirms criteria in `start-task`; details in 23.
7. Settled: when the implementer sets `validating`, one line per criterion with evidence or a gap; gaps go under `## Blockers / open questions`.
8. Not adopted as proposed (per-framework handling in `adopt`, `doctor`, `bootstrap`, the compatibility matrix): the user does not want other frameworks as dependencies to track. Replaced by 15.
9. Each previously skipped item weighed separately: 16 to 19.
10. Settled: claims here carry their source and date; recheck before the milestone that uses an item.
11. Answered by 21.
12. Answered by 22.
13. Settled: freshness by commit. Each validation entry's environment field records the commit it ran at (`at <short hash>`, or `uncommitted`); a result is current only when its commit matches the code being judged, otherwise it is rerun or marked as from an earlier commit. The implementer runs targeted checks while working and the full suite once after the last code change. The reviewer may rely on a CI run at the exact reviewed commit and reruns locally only what CI does not cover. For long local-only checks, the `start-task` interview settles per task whether the reviewer reruns them in full or a subset, recorded in `TASK.md`.
14. Answered by 23.
15. Settled: newproj names no other framework in code, tests, or skills. It edits only the paths it owns (spec section 8), `adopt` reports collisions instead of overwriting, and every other repository file is data, never instructions; `bootstrap` and `start-task` may read any repository document as source material. Work: one protocol sentence and a test that `adopt` leaves unknown directories untouched.
16. Settled: no multi-task files or task graphs. Add a worktree case to the planned test that accepting tasks on separate branches causes no task-file conflicts (spec 28.2); try one task per worktree by hand before building more.
17. Answered by 24.
18. Answered by 25.
19. Answered by 26 to 30.
20. Settled: replace the phase sequence with two release gates and one ordered milestone list. `v0.1.0` is spec 28.1, unchanged (M8 still marks Phase 1 complete). `v1.0.0` is spec 28.2's criteria plus research items the user makes required, each added by an ERRATA entry. Each milestone cites its justification (a gate criterion, evidence from real use, or the user's judgment); order follows value and dependencies. Phase 3 items and research items not required stay conditional, built when needed, before or after `v1.0.0`. Recorded as an ERRATA entry replacing spec 2.3's sequencing rule; the ordered list is planned right after M8 is accepted.

Round 3 was answered 2026-11-15.

21. Settled: a durable-knowledge step at `validating`, part of the self-check (decision 7). The implementer proposes entries only for what code and tests cannot show: reasons and rejected alternatives, things deliberately not done, facts outside the code (environment, tools, people), and rules spanning many files. A fact local to one piece of code goes in a code comment or a test instead. The user approves each entry; approved entries are committed with the implementation, so the reviewer sees them; `accept` is unchanged. "Nothing to record" is a valid result. No living specs.
22. Settled: acceptance-criteria wording is guidance, not mandatory. The `start-task` interview reference recommends "WHEN <condition>, <observable result>" for behavior and "WHEN ..., the system SHALL CONTINUE TO ..." for preserved behavior; free-form criteria stay valid; nothing checks the form automatically. The contract check (23) flags behavior criteria without a clear trigger or observable result.
23. Settled: the contract check lives in `start-task/references/contract-check.md`, read at the confirmation step; `review` may point to it. It reports, without editing: criteria the reviewer cannot check in the review environment; contradictions between criteria or with `AGENTS.md` rules and protected areas; parts of the goal without a criterion and criteria outside it; unverified assumptions; vague terms without a measure; criteria without a validation check, and long local-only checks without a rerun decision (13).
24. Settled, conditional item: nested `AGENTS.md`. First recheck how each tool loads nested files (only Kiro's support was confirmed 2026-11-11). Then: a protocol rule that the root `AGENTS.md` holds everything that must always apply, including safety rules, and nested files hold only subtree-specific rules; a `doctor` check of nested pairs (each nested `CLAUDE.md` points to its `AGENTS.md`; sizes); a `bootstrap` proposal to split an oversized root file.
25. Settled: for large tasks, `start-task` offers one design document in `docs/specs/`, cited from `TASK.md`; consistency rules in 31.
26. Settled: newproj's purpose becomes a portable workflow for building software with AI agents; continuity across tools and machines is one pillar, and code quality becomes a fourth success criterion in spec 2.4. ERRATA entry. The user also wants steps such as mocks between planning and implementation (32, 33).
27. Settled: start with practice skills for test-driven development and systematic debugging; others (safe refactoring, responding to review findings) when real use shows a need. Existing newproj skills already cover brainstorming (`start-task`), plans (`TASK.md`, 25), verification (13), review, worktrees (16), and finishing a branch (`accept`).
28. Settled: practice skills ship as template skills the agent invokes itself (only descriptions load at session start); a project turns one off with a line in `AGENTS.md`.
29. Settled: newproj writes its own practice skills, informed by Superpowers but not copied, short, language-agnostic, using `AGENTS.md` commands and newproj's terms.
30. Settled: each practice skill gets a behavioral fixture (spec 23.2 mechanism) run on Claude Code and Codex; the practice skills are conditional items, not `v1.0.0` requirements.

Round 4 was answered 2026-11-15.

31. Settled, design documents:
    1. `TASK.md` holds what (goal, scope, criteria); the design document holds how (approach, components, interfaces, alternatives) and cites criteria by ID without restating them.
    2. `TASK.md` wins a conflict: the implementer follows it, records the conflict under `## Blockers / open questions`, and asks the user.
    3. The design document is editable during the task; the implementer updates it when the approach changes and notes the change in `HANDOFF.md`.
    4. The self-check at `validating` (7) confirms the design document describes what was built; the reviewer compares it with the code, since it is in the diff.
    5. A criterion may pin a file by path and Git blob hash (as `accept` checks `Contract:` with `git hash-object`); a pinned file changes only with the user's approval. Unpinned documents are informative.
    6. One design document per task, named after it, so parallel tasks never edit the same one. It stays in `docs/specs/` as a record; a later task that changes the area updates it or marks it `Superseded by <file>`, prompted by the durable-knowledge step (21).
32. Settled: all four kinds. Visual mockups, interface-first stubs (APIs, schemas, output formats, fake data), and spikes become one optional prototype step in `start-task`, offered when a task has UI, a new interface, or a technical unknown. Guidance on test doubles goes in the test-driven development skill (27).
33. Settled: prototypes happen while the task is a draft, before the user confirms criteria. An approved mockup or interface is saved under `docs/specs/<task>/`, committed with the active `TASK.md`, and pinned by a criterion with its blob hash (31.5). A spike is throwaway: its code is deleted or kept off the task branch, and only its findings go to the design document or `## Context`.

The interview is complete. Next: after M8 is accepted, plan the ordered milestone list (20) from these decisions, rechecking sources first (10).
