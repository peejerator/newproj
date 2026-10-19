---
name: review
description: Use when the user asks for an independent review of a standard task's committed work against TASK.md, recording the outcome in the Review section of HANDOFF.md.
disable-model-invocation: true
---

# Review

Check committed work against its contract and record the outcome. You are the reviewer, not the implementer: never modify source code or `TASK.md`. The rules this skill applies are in `docs/AGENT_PROTOCOL.md`.

## Before you start

- A review in the same session, agent, or model that implemented the work is weak evidence. If you are that agent, say so to the user and recommend a different agent or model, preferably a different model family. Where the tool offers no choice of model, this is advice only.
- Take your model name from the user or from the tool's interface. If neither shows it, ask the user. Never guess it.

## Steps

1. Read `AGENTS.md`, `TASK.md`, and `HANDOFF.md`. If `TASK.md` has no active task, report that there is nothing to review and stop.
2. Pin the base. Take the commit from `Base commit:` in `TASK.md`; if it is empty, ask the user for it. Check it with `git cat-file -t <base>`, which must print `commit`. If it does not, report it and stop.
3. Check what is committed. Run `git status --short`. Changes outside `HANDOFF.md` mean the implementation is not fully committed: tell the user to commit first. If you continue, the outcome is at most INCONCLUSIVE.
4. Compute the review diff, excluding the task files:

   ```text
   git diff --stat <base>...HEAD -- . ":(exclude)TASK.md" ":(exclude)HANDOFF.md"
   git diff <base>...HEAD -- . ":(exclude)TASK.md" ":(exclude)HANDOFF.md"
   ```

   If the diff is empty, report it and stop. Read the complete diff and the changed files. A truncated or partial reading makes artifact coverage partial.
5. Check every acceptance criterion separately, by ID, judged at `HEAD`. A criterion that can only be judged at an earlier commit (for example a step for one session) is reported as such in its evidence and under `Findings:`; it is not met or failed at `HEAD` by inference.
6. Rerun the checks yourself: the commands under `## Validation` in `TASK.md` and the test commands in `AGENTS.md`, where the environment allows. Record each one under `## Validation` in `HANDOFF.md` in the handoff skill's entry format, with `reviewer` provenance. A CI run on the exact reviewed commit counts too, with `CI` provenance and its run URL or ID.
7. Check content that the diff moves from one file to another against the added lines only (`+` lines of the diff), never against the whole destination file, which may already have contained it. Check that rules removed from one place are restated where they moved.
8. Check claims about system behavior against the code, especially claims the implementer listed as unverified.
9. Separately from the criteria, check the diff against `AGENTS.md` rules and project conventions, and look for regressions, omissions, scope creep (changes outside the task's scope or outside `## Relevant areas`), and unsupported completion claims. Never treat `complete` in `HANDOFF.md`, or an implementer-reported `PASS`, as proof, and never infer PASS from the absence of found problems.
10. Capture the snapshot from command output: run `git rev-parse HEAD` and `git hash-object TASK.md`, and copy their output into `Reviewed at:` and `Contract:`. Never type or abbreviate them.
11. Write the review record (below). Change only `## Review` and your own `reviewer` validation entries in `HANDOFF.md`; leave every other section, and every other file, unchanged.
12. Stage `HANDOFF.md` alone with `git add HANDOFF.md` and print the commit command for the user, for example `git commit -m "Record review of <task>: <outcome>"`, with no AI attribution. Commit it yourself only if the user asked you to.
13. Report the outcome to the user with the status of every criterion.

## Review record

Replace the whole `## Review` section with:

```markdown
## Review

Outcome: <PASS | FAIL | INCONCLUSIVE>
Reviewer: <tool/model>, YYYY-MM-DD
Reviewed at: <literal output of git rev-parse HEAD>
Contract: <literal output of git hash-object TASK.md>
Working tree clean at review: <yes | no>
Baseline: <base-commit diff | reduced confidence>
Artifact coverage: <complete | partial (what was missing)>
Validation provenance: <reviewer-executed | CI-confirmed | implementer-reported only | none>

- AC-1: <VERIFIED | INFERRED | UNSATISFIED | NOT CHECKED> | <evidence>

Findings:
- <finding, or None.>
```

- `Baseline:` is `base-commit diff` when step 2 resolved `Base commit:` from `TASK.md`, and `reduced confidence` when the user supplied the base or it is in doubt.
- VERIFIED: supported by the complete relevant code and, for runtime behavior, by `reviewer` or `CI` checks. INFERRED: probably satisfied, but the evidence is indirect or implementer-reported only. UNSATISFIED: demonstrably not met. NOT CHECKED: evidence missing, truncated, or not runnable.
- PASS: every criterion VERIFIED, artifact coverage complete, no blocking findings, and the implementation committed (step 3). FAIL: at least one criterion UNSATISFIED, or a blocking regression found. INCONCLUSIVE: anything else.
- After FAIL or INCONCLUSIVE, put the remaining work and missing evidence under `Findings:`, specific enough to act on. The next implementer treats them as the next work (the `resume` skill).
- Always note under `Findings:` that the implementer wrote the acceptance criteria of a standard task, so the evidence is weaker than for user-confirmed criteria, and note a same-session or same-model review where it applies.
