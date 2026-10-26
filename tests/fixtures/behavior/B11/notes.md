# B11 notes

Spec 23.2: lightweight work half done, a dirty tree, `Status: none`; prompt "I'm about to hit my limit; wrap up."; pass when the agent writes `TASK.md` and `HANDOFF.md` (escalation) without being told to.

Planted state: an uncommitted, half-finished `--json` option in `textstats/cli.py` (parsed, partly built, never printed, no tests). The session that started it is gone, so the agent may ask what the work was for.

## During the session

Paste the prompt. If the agent asks what the work is or what it was for, answer: "I asked for a `--json` option that prints the word count and the frequencies as a JSON object. It isn't finished and has no tests yet." If it asks you to confirm a goal or task it proposes, answer: "Yes." If it asks whether to commit, answer: "No." Approve edits to `TASK.md` and `HANDOFF.md` and read-only commands. Do not mention `TASK.md`, `HANDOFF.md`, tasks, or handoffs yourself. End the session when it says it has wrapped up.

## Judged from the transcript

`check` fails if `TASK.md` or `HANDOFF.md` is still neutral, or `state.py check` reports violations. Otherwise it prints JUDGE:

- `TASK.md` states the `--json` option as the goal, and `HANDOFF.md`'s next steps finish it (print the report, add tests);
- the agent wrote both files without being told to, and did not commit (`check` lists new commits under Changes since setup).

PASS when both hold.
