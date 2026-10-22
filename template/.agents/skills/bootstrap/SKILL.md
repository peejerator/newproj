---
name: bootstrap
description: Use once, when adopting this template into an existing project, to draft or reconcile AGENTS.md, CLAUDE.md, TASK.md, and HANDOFF.md from the project's code, documentation, and Git history. Not for new projects or ordinary sessions.
disable-model-invocation: true
---

# Bootstrap

Fit the template's agent files to an existing project without losing anything the project already has. The rules this skill applies are in `docs/AGENT_PROTOCOL.md`.

## Rules

- Never overwrite existing project-owned content without the user's review. Add to existing files; propose any replacement or deletion and wait for approval.
- Create each missing required file (`AGENTS.md`, `TASK.md`, `HANDOFF.md`, `docs/DECISIONS.md`); doctor fails without them.
- Every other proposal (renames, mapping lines, pointers, edits to existing files) is applied only with the user's approval.
- Surface collisions explicitly: an existing file, section, rule, or term that conflicts with what the template expects is listed for the user, never silently resolved.
- Mark every conclusion you could not verify with `(unverified)` so the user can review it.
- Do not commit unless the user asks.

## Steps

1. Inspect the project:
   - code layout and languages;
   - `README` and anything under `docs/`;
   - Git history: `git log --oneline -30` and `git branch -a`;
   - build, test, lint, and CI configuration (for example `pyproject.toml`, `package.json`, `Makefile`, `CMakeLists.txt`, `.github/workflows/`);
   - existing agent instruction files (for example `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, `.github/copilot-instructions.md`);
   - whether `newproj adopt` ran: it leaves `.copier-answers.yml` and prints which files need this review.
2. Identify the project's conventions: style, commit messages, branch use, module boundaries, generated or vendored files, and platform constraints.
3. Terminology. Search the existing instruction files and `docs/` (not the template's own `docs/AGENT_PROTOCOL.md` and `docs/PROMPTS.md`) for the protocol's terms, for example `git grep -n -i -w -E 'tasks?|handoffs?|reviews?|validation|decisions?|accept|acceptance|milestones?' -- <files>`. A use that means something other than the protocol's meaning is a collision, for example a document called the "canonical handoff" that is not `HANDOFF.md`, or a `TASK.md` that holds a backlog. Report each one with a proposed rename or a mapping line for `AGENTS.md` (for example ``- `docs/development_state.md` describes what is implemented; it is not the protocol's `HANDOFF.md`.``). Uses that match the protocol's meaning are not collisions.
4. Durable documents. The protocol sends durable findings to the locations `AGENTS.md` names, or to `docs/research/` and `docs/specs/` if it names none. Look for existing homes for such findings, such as topic documents directly under `docs/` or a `docs/notes/` folder. If there are any, propose one mapping line under `AGENTS.md` "Where to find more" covering both defaults (for example ``- Durable findings: topic documents under `docs/`, which serve as the protocol's `docs/research/` and `docs/specs/`.``), or one line per kind. Mapped locations must be inside the repository; report external stores (wikis, Notion, issue trackers) as collisions instead of mapping them. Security assumptions go in `security.md` at the `docs/research/` location, or its mapping. If nothing exists, propose nothing: the defaults apply.
5. Decisions. `docs/DECISIONS.md` is the fixed decision log and is never mapped elsewhere. If it is missing, create it as a byte-for-byte copy of `references/DECISIONS.md` in this skill's folder. If the project keeps an ADR directory (for example `docs/adr/` or `docs/decisions/`), report it and propose a pointer to it in `docs/DECISIONS.md`.
6. Draft or reconcile `AGENTS.md`. Keep it under about 150 lines, with these sections:
   - `## Project`: name and a one-paragraph description;
   - `## Agent protocol`: exactly the line ``At the start of every session, read and follow `docs/AGENT_PROTOCOL.md`.``;
   - `## Commands`: build, test, run, and lint or format, taken from the configuration you inspected;
   - `## Environment`: only where the repository makes requirements evident (runtime and toolchain versions, lockfiles, OS requirements, environment variable names but never values, external services and their test doubles, and what each environment can and cannot run);
   - `## Conventions`: including who makes commits, if the user makes every commit;
   - `## Project-specific rules`: including any areas that always count as formal tier for this project;
   - `## Where to find more`: `TASK.md`, `HANDOFF.md`, `docs/AGENT_PROTOCOL.md`, `docs/DECISIONS.md`, any architecture or roadmap documents, and the mapping lines from steps 3 and 4 once approved.

   If `AGENTS.md` is missing, create it. If it exists, keep its content, add the `## Agent protocol` line if it is missing, and propose the other additions.
7. `CLAUDE.md`: if it exists, add the lines `@AGENTS.md` and `@docs/AGENT_PROTOCOL.md` where they are missing, at the top, keeping the rest. If it does not exist, create it with exactly those two lines.
8. `TASK.md`. If an existing `TASK.md` is not the protocol's (step 3), propose a rename and wait for approval before writing. Then:
   - If the user has stated current work that is standard, write it as an active task, as the `handoff` skill describes under Writing a task.
   - If the stated work is formal-risk, write it the same way but with `Status: draft`, and ask the user to confirm its acceptance criteria before anyone implements it.
   - Otherwise copy `.agents/skills/handoff/neutral/TASK.md` byte for byte.
9. `HANDOFF.md`, after the same collision check: a byte-for-byte copy of `.agents/skills/handoff/neutral/HANDOFF.md` if `TASK.md` is neutral; otherwise the `handoff` skill's format with `## Status` set to `not started` and `Outcome: none` under `## Review`.
10. Hygiene files. Report, but do not create or edit:
    - a missing LF rule: `git check-attr text eol -- probe.txt` should show `text: auto` (or `set`) and `eol: lf`, as `* text=auto eol=lf` in `.gitattributes` gives. If committed files would change (`git ls-files --eol` shows `i/crlf` or `i/mixed`), say that the fix needs its own commit with `git add --renormalize .`;
    - missing required `.gitignore` entries: `.env`, `.env.*`, `!.env.example`, and `context.md` (`git check-ignore --no-index <path>` tests them).

    Recommend `newproj adopt` if it has not run, or the manual fix.
11. If the project would benefit, suggest `docs/ARCHITECTURE.md` or `docs/ROADMAP.md`. Do not write them unless the user asks.
12. Report to the user: each required file you created, files changed and how, collisions (terminology, external stores, an ADR directory), proposals awaiting approval, hygiene findings, and every `(unverified)` item.
