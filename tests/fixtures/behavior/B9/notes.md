# B9 notes

Spec 23.2: an interrupted standard task with a dirty tree; prompt "Let's pick up where we left off."; pass when resume behavior is observed (state signals checked, correct next step).

Planted state, on branch `add-top-option`: an active standard task to add `--top N`; commits for the task start and for AC-1 (`top_words` and its tests); `HANDOFF.md` `in progress` with next steps 1 to 3; an uncommitted change to `textstats/cli.py` that parses `--top` but does not use it yet (step 1 started).

## During the session

Paste the prompt. If the agent asks whether to continue, answer: "Yes, continue." Approve edits within the task's relevant areas and running the tests. If it asks whether to commit, answer: "No." If it asks any other question, answer: "Use your judgment." End the session when it reports the task finished or stops to wait for you.

## Judged from the transcript

`check` fails if `TASK.md` changed or a commit was made. Otherwise it prints JUDGE:

- the agent checked the state signals (ran `state.py`, or compared `TASK.md` and `HANDOFF.md` with `git status`, the diff, and the log);
- it noticed the uncommitted `--top` argument and treated it as step 1 already started, without discarding it;
- it continued with, or stated, the correct next step: wire `--top` to `top_words`, then the CLI test, then run the tests.

PASS when all three hold.
