---
name: accept
description: Use when the user accepts the current task, to verify a current PASS review, reset TASK.md and HANDOFF.md to the neutral state, and stage the acceptance commit on the task's branch.
disable-model-invocation: true
---

# Accept

Record the user's acceptance of the current task. Acceptance belongs to the user: run this skill only on the user's explicit instruction. Never commit, push, or merge yourself; stage the files and print the commands for the user. The rules this skill applies are in `docs/AGENT_PROTOCOL.md`.

## Steps

1. Read `TASK.md` and `HANDOFF.md`. Note the task's goal, `Target branch:`, and the current branch (`git branch --show-current`).
2. Verify that the review is a current PASS. Run each command and compare its output:
   - `## Review` in `HANDOFF.md` has `Outcome: PASS`;
   - `git rev-parse HEAD` equals `Reviewed at:`, or `git diff --name-only <Reviewed at> HEAD` lists only `HANDOFF.md`;
   - `git status --short` shows no changes outside `HANDOFF.md`;
   - `git hash-object TASK.md` equals `Contract:`.
3. If any check fails, report which one and stop. Continue only if the user then explicitly accepts without a current PASS, and record that in the commit message (step 6). Never make that choice yourself. For formal-risk work, say that a current PASS is required for normal acceptance.
4. Copy the neutral files byte for byte, never retyping them:
   - `.agents/skills/handoff/neutral/TASK.md` to `TASK.md`;
   - `.agents/skills/handoff/neutral/HANDOFF.md` to `HANDOFF.md`.

   Copy with a tool that preserves bytes (`cp` in bash or zsh, `Copy-Item` in PowerShell). Then check that `git hash-object` gives the same result for each copy and its source.
5. Stage both files: `git add TASK.md HANDOFF.md`.
6. Print the commit command for the user, with no AI attribution:

   ```text
   git commit -m "Accept <task goal in a few words>"
   ```

   If the user accepted without a current PASS, use `git commit -m "Accept <task goal in a few words> (override: no current PASS)"`, adding the user's stated reason as a second `-m` paragraph if given.
7. If the current branch is not the default branch, also print the integration commands, with the real branch names:

   ```text
   git push
   git switch <target branch>
   git pull --ff-only
   git merge --ff-only <task branch>
   git push
   git branch -d <task branch>
   git push origin --delete <task branch>
   ```

   If `git merge --ff-only` fails because the target branch has moved, the user merges the target branch into the task branch first (`git switch <task branch>`, then `git merge <target branch>`), reruns the checks, and fast-forwards again. Never rebase. A merge that changes files outside `TASK.md` and `HANDOFF.md` makes the review historical; tell the user, so they can decide whether to review again. Pushing the fast-forwarded default branch also marks an open pull request for the task branch as merged on GitHub.
8. Report to the user what was staged and the commands to run, in order.
