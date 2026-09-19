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
allowed-tools: [Read, Write]
license: MIT
metadata:
  author: Ananda Narayanan Udayakumar
  version: "1.0.0"
  generatedBy: "1.10.0"
---

Peer dependency: this skill hands off to `/opsx:propose`, which is not
bundled here. The consuming project must have OpenSpec's `opsx` commands
installed (see this plugin's README).

1. Read `BACKLOG.md` at the project root. If it doesn't exist, don't guess
   at backlog items from memory or other files — instead offer to
   scaffold one from this template, and stop until the user confirms:

   ```markdown
   # <Project Name> — Backlog & Working Notes

   ## Backlog

   **Priority:** MVP (needed for a first usable version) · V1 (right after) ·
   V2 (nice-to-have) · Stretch (maybe never)
   **Status:** Not proposed · Proposed · In progress · Archived

   ### 1. <Category Name>

   | Change | What it does | Priority | Depends on | Status | Notes |
   |---|---|---|---|---|---|
   | `<change-slug>` | <one-line description of what this change does> | MVP | — | Not proposed | |

   ### 2. <Category Name>

   | Change | What it does | Priority | Depends on | Status | Notes |
   |---|---|---|---|---|---|
   | `<change-slug>` | <one-line description of what this change does> | MVP | `<change-slug>` | Not proposed | |

   ---

   If the user confirms, write it to BACKLOG.md and ask them to fill in
   real rows before matching against it — don't invent rows yourself.
2. Match the user's phrase against a row's `Change` name or `What it does`
   description — informal/partial matches count (e.g. "meal tracking"
   matches a `meal-planner` row).
3. If no row matches, say so and ask the user to describe the work instead
   of guessing.
4. If more than one row plausibly matches, don't guess — list the
   candidates (name + what it does) and ask the user which one they mean.
5. If a match is found, check its `Depends on` column against the other
   rows' `Status`. If any dependency is not yet `Proposed`/`Archived`,
   surface that gap to the user before proceeding — don't silently skip it.
6.  Once the user confirms, hand off by running `/opsx:propose` yourself as
   the next turn — output the command with the matched item's name and
   description, e.g. `/opsx:propose "<name>: <what it does>"`. This is a
   conversational handoff, not a guaranteed programmatic one: skills have
   no mechanism to invoke another slash command directly, so if it doesn't
   fire, tell the user to run it themselves.
