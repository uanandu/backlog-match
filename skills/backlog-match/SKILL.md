---
name: backlog-match
description: >-
  Use this when the user wants to find, start, or propose work on a
  BACKLOG.md item by name or informal description — phrases like "let's
  start on sessions," "is there a backlog item for the exercise library
  thing," or "let's do the meal tracking one." Matches the keyword against
  BACKLOG.md rows and hands off to /opsx:propose. Trigger on casual,
  conversational references to backlog work, not just explicit mentions
  of "backlog" or "BACKLOG.md."
allowed-tools: [Read]
license: MIT
metadata:
  author: Ananda Narayanan Udayakumar
  version: "1.0"
  generatedBy: "1.10.0"
---

Peer dependency: this skill hands off to `/opsx:propose`, which is not
bundled here. The consuming project must have OpenSpec's `opsx` commands
installed (see this plugin's README).

1. Read `BACKLOG.md` at the project root.
2. Match the user's phrase against a row's `Change` name or `What it does`
   description — informal/partial matches count (e.g. "meal tracking"
   matches a `meal-planner` row).
3. If no row matches, say so and ask the user to describe the work instead
   of guessing.
4. If a match is found, check its `Depends on` column against the other
   rows' `Status`. If any dependency is not yet `Proposed`/`Archived`,
   surface that gap to the user before proceeding — don't silently skip it.
5. Once the user confirms, hand off by invoking `/opsx:propose` with the
   matched item's name and description, e.g.
   `/opsx:propose "<name>: <what it does>"`.
