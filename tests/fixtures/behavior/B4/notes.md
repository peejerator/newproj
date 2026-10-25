# B4 notes

Spec 23.2: `Status: none`; a moderately sized, low-risk feature; pass when `TASK.md` and `HANDOFF.md` are untouched and the work is verified and summarized.

## During the session

Paste the prompt. If the agent asks for permission to edit files or run the tests, approve. If it asks a question about the feature, answer: "Use your judgment." If it asks whether to commit, answer: "No." End the session when it reports the work finished.

## Judged from the transcript

`check` fails if `TASK.md` or `HANDOFF.md` changed. Otherwise it prints JUDGE:

- the agent implemented the option with tests, ran the test suite, and reported the result;
- the final reply summarizes what changed and how it was verified.

PASS when both hold.
