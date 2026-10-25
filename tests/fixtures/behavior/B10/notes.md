# B10 notes

Spec 23.2: a project with all skills; list or invoke each skill; record the invocation syntax, duplicates, and whether pointers double-load content. The results fill the invocation table in `template/docs/PROMPTS.md` (issue #33).

Claude Code reads the pointer skills in `.claude/skills/`; Codex reads `.agents/skills/` (ERRATA E-014). Each pointer tells the agent to read the canonical `.agents/skills/<name>/SKILL.md`.

## During the session

1. Paste the prompt and record the agent's answer. Answer nothing.
2. Open the tool's skill or command menu (in Claude Code type `/`; in Codex type `$` and, separately, `/`) and record which of the six skills appear and how many times each.
3. For each skill (`resume`, `handoff`, `bootstrap`, `start-task`, `review`, `accept`), in the same session, type the tool's invocation (`/<name>` in Claude Code, `$<name>` in Codex) and press Enter. Record whether the skill ran or a built-in command did, and which files the agent read first. Interrupt it (Escape in Claude Code, Escape or Ctrl+C once in Codex) as soon as it has read the skill, before it writes anything. Deny any file edit.
4. For any skill a built-in command overrode, try the plain-language form "Run the `<name>` skill." and record whether it ran the skill.

## Judged from the transcript

`check` prints JUDGE only. Record in the results row's note:

- the working invocation for each of the six skills, and the plain-language form for any a built-in command overrides;
- duplicates: any skill listed twice in the answer or the menu;
- double-loading: whether invoking a skill loads the pointer and then the canonical `SKILL.md` once each, or either twice.

PASS when every skill could be invoked one way or another, none is listed twice, and no content loads twice. Otherwise FAIL, naming the problem. A skill that must be renamed to work is a blocker for M7: record it and stop.
