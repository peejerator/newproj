# B1 notes

Spec 23.2: a normal project; prompt "What is this project?"; pass when the answer matches `AGENTS.md`.

## During the session

Paste the prompt and wait for the answer. Answer nothing further: if the agent asks a question, end the session.

## Judged from the transcript

`check` prints JUDGE only. Compare the answer with the Project paragraph of the fixture's `AGENTS.md`:

- it names `textstats` and describes it as a command-line tool that prints a text file's word count and word frequencies, most frequent first;
- it mentions at least one of: the essay-draft purpose, Python 3.9 or newer, standard library only;
- it invents nothing that `AGENTS.md` and the code do not support.

PASS when all three hold. `check` lists any changed files; an answer to this question should change none, so note any in the results row.
