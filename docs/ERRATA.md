# Errata to the specification

`docs/spec.md` (revision 10) is frozen. Changes found during implementation are recorded here instead of editing it, and folded into the next spec revision at the end of the phase. Append only.

Each entry names the spec sections it changes, the problem, and the resolution.

An erratum must cite an observed failure (what was run, what happened, and what was expected, from a real session, test, or CI run) or an outright contradiction in the spec. Hypothetical improvements wait for the next spec revision. Issues labeled `trial-finding` meet this bar.

## E-001: Open decisions resolved, and Copier minimum verified

Date: 2026-10-09
Sections: 19.2, 27

Resolutions of the decisions section 27 left open:

| Decision | Resolution |
|---|---|
| GitHub owner | `peejerator` |
| Template repository name | `newproj` |
| Template repository visibility | public |
| Default license for generated projects | none |
| Minimum Copier version | 9.18.2 |

Verification of section 19.2 on Copier 9.18.2, using `_skip_if_exists` together with an `_exclude` entry conditional on `_copier_operation == 'update'`:

- a project-owned file edited in the project was left untouched by `copier update`;
- a project-owned file deleted in the project was not recreated by `copier update`;
- a template-managed file was updated;
- control: with `_skip_if_exists` alone, the deleted file was recreated, confirming the conditional exclusion is necessary;
- adoption (`copier copy` into an existing repository) preserved an existing `AGENTS.md` and added missing files.

Additional finding: setting `_exclude` replaces Copier's default exclusions, so `copier.yml` restates them (`copier.yml`, `copier.yaml`, `~*`, `*.py[co]`, `__pycache__`, `.git`, `.DS_Store`, `.svn`). Verified that `.DS_Store` and `__pycache__` in `template/` are not rendered.

## E-002: Development-only template source

Date: 2026-10-09
Sections: 20 (introduction)

Problem: section 20 says each CLI version renders the template at its own release tag. During development no tags exist, and tests need to render the working tree.

Resolution: `newproj new` and `newproj adopt` accept a hidden `--template-path <dir>` option that renders from a local directory instead of the tagged remote. It is omitted from `--help`, used only by tests and development, and never documented as normal usage. Projects rendered this way record the local path in `.copier-answers.yml`, so `newproj doctor` reports them as development renders.

## E-003: Precedence of instructions

Date: 2026-10-19
Sections: 11 (introduction), 11.7

Observed failure: in the ohm-manager trial, project rules and protocol defaults conflicted and each agent invented its own precedence. ohm-manager's `AGENTS.md` forbids commits without explicit authorization and says work happens on `main`, while the protocol says acceptance includes a commit and a machine switch commits to a non-default branch. Codex wrote its own override rule into `HANDOFF.md` (`57c4c27`). Issues #7 and #8.

Resolution: the protocol states the order: the user's current instruction, then `AGENTS.md`, then the protocol's defaults. The trust and authority table (11.7) is a floor that `AGENTS.md` may tighten but never loosen.

## E-004: Only the user resolves questions addressed to the user

Date: 2026-10-19
Sections: 11.4, 17.1

Observed failure: Claude Code recorded a question for the user in ohm-manager's `HANDOFF.md` (`4cbe014`). The next implementer, Codex, closed it on its own without asking. Separately, Codex and then Claude Code, each given only `resume`, reconciled correctly and went straight into the next part of the work without reporting, while `HANDOFF.md` held an open question for the user (the session that produced `cd10b8c`). Issues #9 and #10.

Resolution: agents settle facts themselves and record the evidence, but never resolve a question addressed to the user; it stays open until the user answers. `resume` still continues on the normal path without confirmation (17.1), except that it reports the reconciled state and stops when `## Blockers / open questions` contains a question addressed to the user.

## E-005: Commit order when the user makes every commit

Date: 2026-10-19
Sections: 11.8, 12.4, 17.3, 17.6

Observed failure: the user makes every commit, because agents cannot use the user's passphrase-protected signing key. In ohm-manager, the fix for a FAIL review was staged but not committed when the reviewer was prompted; the review recorded `Reviewed at` from `git rev-parse HEAD` and was correct only because the user happened to commit between sessions (`13335c2` before `2c2dc77`). Acceptance "includes a commit" that the agent could not make. Issue #11.

Resolution: when the user makes every commit, agents stage the work and print the exact commit command instead of committing. The implementation is committed before review starts, and review covers only committed work. The review record and the acceptance are staged and committed by the user in the same way.

## E-006: Short-lived task branches, fast-forwarded at acceptance

Date: 2026-10-19
Sections: 11.8, 12.4

Observed failure: the machine-switch rule (commit to a non-default branch) appeared to conflict with ohm-manager's `AGENTS.md`, which says work happens on `main` with no long-lived feature branches (issue #5). The ohm-manager machine-switch test on `task/status-verification-move` showed the two are compatible: work moved from macOS to Windows on the branch, the neutral reset was committed on it, and `git merge --ff-only` kept `main` linear (no merge commits between `f7bdce5` and `c281285`). During that test Claude Code proposed `git merge --no-ff`, which would have added a merge commit, because the merge style was unspecified. Issue #12.

Resolution: a machine switch commits to a short-lived task branch, created from the default branch if needed. At acceptance the task branch is fast-forwarded into the default branch with `git merge --ff-only`. If the default branch has moved, it is merged into the task branch first and checks are rerun; never rebase.

## E-007: `Base commit` and `Target branch` for standard tasks

Date: 2026-10-19
Sections: 12.5, 12.6, 17.3

Observed failure: `Base commit:` was left empty in newproj's M2 `TASK.md` and in ohm-manager's first trial task (`4cbe014`), as 12.5 instructs for standard tasks. Reviewers then had no commit to diff against, and the base had to be supplied by hand in each review prompt. It was filled in (`f7bdce5`, at `57c4c27`) only when a prompt asked for it. Issue #15.

Resolution: when an agent writes an active standard task, it sets `Base commit:` from the output of `git rev-parse HEAD` (the pre-implementation state), never typed, and `Target branch:` to the default branch unless the user names another. `Task ID:` stays empty for standard tasks. The review diff for a standard task is `git diff <Base commit>...HEAD`, replacing the two cases in 12.5; a base supplied by the user instead is reported with reduced baseline confidence. The rule in 12.6 that only `newproj activate` writes these lines still applies to formal tasks.

## E-008: Acceptance criteria describe the end state

Date: 2026-10-19
Sections: 17.3, 17.6

Observed failure: in ohm-manager's machine-switch task, AC-7 said to stop after Part A, run the handoff skill, and stage without committing. It was a session instruction, met at `57c4c27`. The independent reviewer correctly judged it against the finished branch, marked it UNSATISFIED, and the review failed. The user resolved it in the re-review prompt, since editing `TASK.md` would have changed its hash. Issue #26.

Resolution: each acceptance criterion describes a checkable property of the finished work at `HEAD`. Session instructions (stop points, handoff requirements, who commits, which branch) go under `## Scope`. The reviewer judges every criterion at the reviewed commit and reports a criterion that can only be judged at an earlier commit.

## E-009: Review expected when safety rules or instruction files change

Date: 2026-10-19
Sections: 11.2, D22

Observed failure: ohm-manager's operations-log split was a standard documentation task. Durable safety rules were moved out of `development_state.md` without being restated, and only the independent review caught it (FAIL on AC-2). Issue #13.

Resolution: in the tier table, review for standard work stays "recommended", and is expected when the work moves, rewrites, or removes safety rules or instruction-file content, even when it is documentation only. It remains required only for formal work.

## E-010: User-invoked skills (amends D8)

Date: 2026-10-19
Sections: D8, 17 (introduction), 17.4, 17.7

Observed failure: `bootstrap` runs once per project, but agents can invoke it on their own, and its description is loaded into every session (issue #21). The new `review` and `accept` skills (E-011, E-012) belong to the user in the same way: an agent reviewing its own work, or accepting a task, defeats their purpose (11.4, D19). D8 limits frontmatter to `name` and `description` "unless testing proves a required integration needs additional fields".

Resolution: `bootstrap`, `review`, and `accept` are user-invoked only. Each carries `disable-model-invocation: true` in its `SKILL.md` frontmatter, and an `agents/openai.yaml` next to it containing `policy:` with `allow_implicit_invocation: false`. The Claude pointer skills copy the canonical frontmatter exactly, including the extra field. `resume` and `handoff` keep exactly `name` and `description`, because the protocol relies on agents reaching for them.

Tools checked, against vendor documentation on 2026-10-19 (not yet by behavioral test, which is M7):

- Claude Code: `disable-model-invocation: true` stops Claude from loading the skill on its own, keeps its description out of context, and still allows `/name` (code.claude.com/docs/en/skills).
- Codex: `agents/openai.yaml` in the skill folder, with `policy.allow_implicit_invocation` defaulting to `true`; `false` stops implicit selection while explicit `$skill` invocation still works (developers.openai.com/codex/skills, which redirects to learn.chatgpt.com/docs/build-skills).

Unverified: GitHub Copilot, and every other tool. Their support for either field has not been checked, so on those tools the three skills may still be invoked implicitly.

## E-011: A Phase 1 `review` skill for standard tasks

Date: 2026-10-19
Sections: 17.6, 13.6, 12.5

Observed failure: every review in the trial needed a hand-written reviewer prompt. The reviewer had to be given the base commit by hand, and had to find the review-record format inside the handoff skill. Copilot's check of moved figures compared them against the whole destination file rather than the added lines, so it proved less than it claimed. A reviewer wrote "model not shown" while Copilot's interface showed the routed model. The first machine-switch review failed correctly because a new rule contradicted the code, which showed that claims must be checked against code. Issue #23.

Resolution: a `review` skill ships in Phase 1 for standard tasks, user-invoked (E-010). It implements 17.6 with these changes:

- it takes the base from `Base commit:` (E-007), asks the user when it is empty, and diffs with `git diff <base>...HEAD`;
- for standard tasks as well as formal ones, uncommitted implementation changes make the outcome at most INCONCLUSIVE (E-005);
- every criterion is judged at `HEAD` (E-008); moved content is compared against added lines only; claims about system behavior are checked against the code;
- the model name comes from the user or the tool's interface;
- the reviewer changes only `## Review` and its own `reviewer` validation entries in `HANDOFF.md`, stages `HANDOFF.md`, and prints the commit command. Remaining work goes under `Findings:` instead of `## Exact next steps` and `## Blockers / open questions`, and the next implementer sets `## Status` to `in progress` (the `resume` skill), so implementer and reviewer sections stay separate;
- the review-record format moves from the handoff skill into the review skill, superseding the M2 decision to keep it in the handoff skill until Phase 2. `Baseline:` takes the value `base-commit diff` for a standard task's recorded base.

Review of formal tasks stays in Phase 2, and the bundle-only review prompt (16.5) in Phase 3.

## E-012: An `accept` skill

Date: 2026-10-19
Sections: 12.4, 12.8, 17.3

Observed failure: neither M1 nor M2 in newproj was reset to the neutral state. At `757269c`, `main` still had the M2 `TASK.md` with `Status: active` and a `HANDOFF.md` showing `Branch: m2-agent-content` and `complete`, so `resume` on `main` found a finished task on a deleted branch. The user merged on GitHub, and the separate acceptance step in the handoff skill never happened (issue #16). Acceptance also "includes a commit" the agent could not make (E-005).

Resolution: acceptance is a user-invoked `accept` skill (E-010). It verifies that `Outcome: PASS` is current: `Reviewed at` is `HEAD` or only `HANDOFF.md` changed since, the working tree is clean apart from `HANDOFF.md`, and `Contract` equals `git hash-object TASK.md`. It copies the neutral files from `.agents/skills/handoff/neutral/` byte for byte, stages both, and prints a commit command with no attribution; on a non-default branch it also prints `git merge --ff-only` (E-006) and branch-cleanup commands. It never commits, pushes, or merges itself. If the review is not a current PASS, it stops; the user may accept anyway, and the commit message then records `(override: no current PASS)` as in 12.4. A standard task's acceptance commit message is `Accept <task goal>`; the formal `task(<task-id>): accept` form is unchanged.

## E-013: `HANDOFF.md` size guideline, and the handoff skill split

Date: 2026-10-19
Sections: 13 (introduction), 17.3

Observed failure: ohm-manager's `HANDOFF.md` reached 202 lines after Part A of a two-part documentation task (`57c4c27`) and 282 lines after Part B (`d1a3fb9`), mostly a rewritten-line inventory and per-criterion narrative, although the protocol says it is not an activity log. The handoff skill itself was 215 lines, mixing material for implementers, reviewers, and acceptance. Issue #17.

Resolution: the handoff skill gives a size guideline: `## Completed` lists outcomes by acceptance criterion ID, one line each; each check keeps one current validation entry; long inventories go in the commit message or a task-scoped file that `HANDOFF.md` cites. The skill no longer embeds the review-record format (moved to the `review` skill, E-011) or the neutral-state text (shipped as `.agents/skills/handoff/neutral/` files, as 12.8 requires, and copied by `bootstrap` and `accept`).

## E-014: Root pointer skills in this repository

Date: 2026-10-19
Sections: 17.7, 2.5

Observed failure: newproj follows its own protocol (2.5), but its skills lived only under `template/`, so `resume`, `handoff`, and `bootstrap` were not discoverable as skills in this repository; agents found them only through the path mapping in `AGENTS.md`. Issue #25.

Resolution: this repository has root `.agents/skills/<name>/SKILL.md` and `.claude/skills/<name>/SKILL.md` pointer skills for every template skill, each with the canonical frontmatter and the one-line body ``Read and follow `template/.agents/skills/<name>/SKILL.md`.``, plus root copies of each `agents/openai.yaml`. No symlinks (unreliable on Windows, D5) and no copies of skill bodies. Tests check that the pointers match. `newproj new` and `newproj adopt` are never run on this repository; `template/` stays the single source.
