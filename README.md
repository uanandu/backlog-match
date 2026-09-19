# backlog-match

A Claude Code skill that matches a casual, conversational reference to a
`BACKLOG.md` item (e.g. "let's do the meal tracking one") and hands off to
OpenSpec's `/opsx:propose` command to start formal planning on it.

## Peer dependency

This plugin does **not** bundle OpenSpec's `opsx` commands. The consuming
project must already have them installed — at minimum `/opsx:propose`, and
ideally the full workflow (`/opsx:new`, `/opsx:apply`, `/opsx:verify`,
`/opsx:archive`, etc.) for the backlog-to-implementation loop to work
end-to-end. See `.claude/commands/opsx/` in the `openspec-workout` project
for a reference implementation of what needs to be present.

## Requires

A `BACKLOG.md` at the project root using a row-based table format with at
least these columns: `Change`, `What it does`, `Priority`, `Depends on`,
`Status`, `Notes`. This skill reads that file directly — it does not parse
any other format.

## Install

Copy `plugins/backlog-match/` into the consuming project's
`.claude/plugins/` directory (or install it via a marketplace, if you set
one up — not covered here).
