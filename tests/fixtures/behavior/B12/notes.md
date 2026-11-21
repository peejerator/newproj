# B12: local-only new task

Run both start-task scenarios with `uv run python scripts/start_task_behavior.py <new-directory>`.
The runner sends prompt.txt to a fresh Claude Code session, answers numbered
recommendation rounds with yes, and explicitly confirms criteria after they are
shown. The output directory must be outside any Git repository.

## Judged from the transcript

None. Scripted checks require the skip explanation, a commit command without
push or PR commands, only TASK.md and HANDOFF.md staged, no implementation, no
new commit (including reflogs), the agreed branch, and valid activated state.
Transcripts and manifests stay outside the fixture project and are not committed.
