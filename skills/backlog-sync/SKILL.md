---
name: backlog-sync
description: >-
  Use this when the user says an OpenSpec change has shipped, been archived, or is done and wants that reflected in Jira — phrases like "this shipped, sync it back to Jira," "mark PROJ-142 done," "update Jira for that change," or "close out the meal planner ticket." Finds the Jira issue the change came from, transitions it to a Done status, and posts a comment linking the PR/commit, after showing exactly what it will write and getting confirmation. Trigger on casual, conversational references to finishing backlog work, not just explicit mentions of "sync" or "Jira."
allowed-tools: [mcp__*, Read, Grep, Glob, "Bash(git:*)", "Bash(gh:*)"]
license: MIT
metadata:
  author: Ananda Narayanan Udayakumar
  version: "1.0.0"
---

Companion to `backlog-match`. That skill goes Jira → OpenSpec and only ever reads Jira (plus creating a new issue). This one closes the loop the other way: once an OpenSpec change is done, it pushes that state back to the Jira issue the change came from.

Every write this skill makes is to a real issue in a shared system, so it always shows the exact transition and comment and gets explicit confirmation first. It touches exactly one issue — the one the change originated from. It never searches for other issues to update, and it does not touch that issue's blockers or the issues it was blocking. Use `git` and `gh` only for reading (log, PR lookup); never commit, push, or open a PR from here.

Jira is the source of truth. If no Jira tool is reachable, say so and stop; don't record the sync anywhere else.

1. Find a usable Jira tool. Look through your available tools (including deferred/MCP tools reachable via tool search) for ones that can fetch an issue, list its available transitions, transition it, and add a comment — e.g. `getJiraIssue`, `getTransitionsForJiraIssue`, `transitionJiraIssue`, `addCommentToJiraIssue`, or the generic Atlassian `discover` / `executeRead` / `executeWrite` pattern. Different users have different Jira/Atlassian MCP servers, so discover the tools fresh each time rather than hardcoding names. If the tools needed to transition and comment aren't available, say so plainly and stop.
2. Identify the change. If the user named one, use it. Otherwise look under `openspec/changes/archive/` for the most recent entry (archived names are prefixed `YYYY-MM-DD-`). If several recent archives are plausible, list them and ask which — don't guess. If the user says something shipped but the change is still under `openspec/changes/` (not archived), say so and ask whether they want to sync anyway; a change that isn't archived may not be finished.
3. Recover the Jira issue key. OpenSpec does not record it for you, so check in this order and stop at the first hit:
   1. A key the user just stated ("mark PROJ-142 done").
   2. The change folder — search `proposal.md`, `design.md`, `tasks.md` and `.openspec.yaml` (and the folder name) for a Jira-style key (`[A-Z][A-Z0-9]+-[0-9]+`).
   3. Earlier in this conversation — the `/opsx:propose "<KEY>: <summary>"` handoff from `backlog-match`.
   4. Ask the user. Do not go searching Jira for a "probable" match yourself; the whole point of this skill's scope is that it only updates an issue someone explicitly tied to this change.
   If steps 2 or 3 turn up more than one distinct key, list them and ask which one.
4. Confirm the issue exists. Fetch it and check its summary and current status against the change. If the summary looks unrelated to the change, say so and ask before continuing — a wrong key means writing to the wrong ticket. If the issue's status is already in the Done category, tell the user and skip the transition; offer only the comment (step 8 then shows just the comment).
5. Gather the link for the comment, from the least to most effort, and never invent one:
   1. `gh pr list --state merged --search "<KEY or change name>"` or `gh pr view` for the current branch, to get a PR URL.
   2. Otherwise `git log --oneline --grep="<KEY>"` (and the change name), and build a commit URL from `git remote get-url origin` if it's a recognizable host.
   3. Otherwise ask the user for a link. If they have none, post the comment without one and say so in the confirmation.
6. Pick the transition. Fetch the issue's *available* transitions — Jira workflows differ per project, so "Done" is not a fixed operation. Choose the transition whose target status is in the Done category. If exactly one qualifies, use it. If several do (e.g. Done, Won't Do, Cancelled), list them and ask. If none is reachable directly (the workflow needs In Progress → In Review → Done, say), show the transitions that are available and ask what the user wants; never chain several transitions on your own.
7. Draft the comment. Keep it short and factual: the OpenSpec change name, that it was archived (with the date from the archive folder name if there is one), the PR/commit link from step 5, and one line of what shipped taken from the change's `proposal.md` "Why"/"What Changes" — don't embellish. Note that with most Jira MCP servers the comment posts under the user's own account.
8. Show the user exactly what you're about to write — issue key and summary, current status → target status (the transition name), and the full comment text — and get explicit confirmation before writing anything. If they want edits, redraft and confirm again.
9. Once confirmed, transition first, then comment. If the transition fails, do not post the comment (it would claim the issue is done when it isn't); report the error and stop. If the transition succeeds but the comment fails, say so and hand the user the comment text to post themselves. Report what actually happened — new status, comment posted or not — and the issue key. Don't say the sync is complete unless both steps you meant to do succeeded.
