# backlog-match

A Claude Code skill that matches a casual, conversational reference to a
`BACKLOG.md` item (e.g. "let's do the meal tracking one") and hands off to
OpenSpec's `/opsx:propose` command to start formal planning on it.

## Prerequisites

Before installing, the consuming project needs both of these:

1. **OpenSpec initialized in the project, with its `opsx` commands
   present.** This plugin does **not** bundle or initialize OpenSpec itself
   — the consuming project must already have run OpenSpec's own init/setup
   step, which scaffolds `.claude/commands/opsx/`. At minimum
   `/opsx:propose` must exist there, and ideally the full workflow
   (`/opsx:new`, `/opsx:apply`, `/opsx:verify`, `/opsx:archive`, etc.) for
   the backlog-to-implementation loop to work end-to-end. See
   `.claude/commands/opsx/` in the `openspec-workout` project for a
   reference implementation of what needs to be present.
2. **A `BACKLOG.md` at the project root** using a row-based table format
   with at least these columns: `Change`, `What it does`, `Priority`,
   `Depends on`, `Status`, `Notes`. This skill reads that file directly — it
   does not parse any other format.

Without both, the skill can still match a phrase to a row, but the final
`/opsx:propose` handoff (or the dependency-gap check against `Status`) will
have nothing to run against.

## Install

Via marketplace (recommended):

```
/plugin marketplace add uanandu/backlog-match
/plugin install backlog-match@uanandu-backlog-match
```

Or manually: copy this repo into the consuming project's
`.claude/plugins/backlog-match/` directory.

## Local testing

To try changes without publishing, point Claude Code at this repo directly
from inside a project that has a `BACKLOG.md`:

```
claude --plugin-dir /path/to/backlog-match
```

Then just talk to it naturally (e.g. "let's do the meal tracking one") —
the skill triggers on casual phrasing, not just explicit commands.

Or exercise the real install path with a local marketplace:

```
/plugin marketplace add /path/to/backlog-match
/plugin install backlog-match@uanandu-backlog-match
/plugin list
```
