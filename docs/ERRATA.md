# Errata to the specification

`docs/spec.md` (revision 10) is frozen. Changes found during implementation are recorded here instead of editing it, and folded into the next spec revision at the end of the phase. Append only.

Each entry names the spec section, the problem, and the resolution.

## E-001: Open decisions resolved, and Copier minimum verified

Date: 2026-10-09
Sections: 19.2, 27

Resolutions of the decisions section 27 left open:

| Decision | Resolution |
|---|---|
| GitHub owner | `peejerator` |
| Template repository name | `newproj` |
| Template repository visibility | public |
| Default license for generated projects | none |
| Minimum Copier version | 9.18.2 |

Verification of section 19.2 on Copier 9.18.2, using `_skip_if_exists` together with an `_exclude` entry conditional on `_copier_operation == 'update'`:

- a project-owned file edited in the project was left untouched by `copier update`;
- a project-owned file deleted in the project was not recreated by `copier update`;
- a template-managed file was updated;
- control: with `_skip_if_exists` alone, the deleted file was recreated, confirming the conditional exclusion is necessary;
- adoption (`copier copy` into an existing repository) preserved an existing `AGENTS.md` and added missing files.

Additional finding: setting `_exclude` replaces Copier's default exclusions, so `copier.yml` restates them (`copier.yml`, `copier.yaml`, `~*`, `*.py[co]`, `__pycache__`, `.git`, `.DS_Store`, `.svn`). Verified that `.DS_Store` and `__pycache__` in `template/` are not rendered.

## E-002: Development-only template source

Date: 2026-10-09
Sections: 20 (introduction)

Problem: section 20 says each CLI version renders the template at its own release tag. During development no tags exist, and tests need to render the working tree.

Resolution: `newproj new` and `newproj adopt` accept a hidden `--template-path <dir>` option that renders from a local directory instead of the tagged remote. It is omitted from `--help`, used only by tests and development, and never documented as normal usage. Projects rendered this way record the local path in `.copier-answers.yml`, so `newproj doctor` reports them as development renders.
