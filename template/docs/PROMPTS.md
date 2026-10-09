# Prompts

Short prompts for sessions without repository access, such as a chat app you upload files to. Such a session cannot run skills or commands, so each prompt points it at the same rules a repo-aware agent follows. Repo-aware agents use the skills in `.agents/skills/` instead.

## What to upload

Upload these files by hand:

- `AGENTS.md`, `docs/AGENT_PROTOCOL.md`, `TASK.md`, and `HANDOFF.md`;
- the output of `git status` and `git diff --stat`;
- the skill the prompt names (`.agents/skills/resume/SKILL.md`, `.agents/skills/handoff/SKILL.md`, or `.agents/skills/bootstrap/SKILL.md`);
- any files relevant to the work, and for bootstrap the output of `git log --oneline -30`.

Review everything before uploading it. Do not upload secrets, credentials, or private data unless you have decided to (`docs/AGENT_PROTOCOL.md`, Trust boundaries and authority). Results come back as text: paste them into the repository yourself, or give them to a repo-aware agent.

## Resume

```text
The uploaded files are the source of truth for this repository. You have no direct access to it, so do not invent its state. If several versions of a file were uploaded, use the newest. TASK.md is the contract; HANDOFF.md is a report against it, not proof. Apply docs/AGENT_PROTOCOL.md and .agents/skills/resume/SKILL.md as far as a session that cannot run commands can.

1. Summarize the active task in a few lines.
2. List any inconsistencies between TASK.md, HANDOFF.md, and the uploaded git output.
3. If the state is coherent, continue the work from HANDOFF.md's exact next steps.
4. Ask me only when a material ambiguity blocks safe progress.
```

## Handoff

```text
Produce a complete, updated HANDOFF.md that a repo-aware agent with no access to this chat can continue from correctly. Follow the format and rules in the uploaded .agents/skills/handoff/SKILL.md and docs/AGENT_PROTOCOL.md. Do not change TASK.md; put any concern about the task under ## Blockers / open questions. Leave ## Review exactly as it is. Record a check as PASS or FAIL only if the uploaded output shows its result. Output the file as a single Markdown code block.
```

## Bootstrap

```text
Draft the agent files for this existing project, following the uploaded .agents/skills/bootstrap/SKILL.md and docs/AGENT_PROTOCOL.md. Inspect the uploaded code, README and docs, Git history, and build and test configuration, then draft:

- a project-specific AGENTS.md;
- TASK.md: the neutral state, or a draft (Status: draft) of the current work I describe;
- HANDOFF.md;
- suggestions for architecture or roadmap documents, only if warranted.

Mark every uncertain conclusion with (unverified) for my review. Where a file already exists, propose additions rather than replacing it, and list every collision. Output each file as its own Markdown code block.
```
