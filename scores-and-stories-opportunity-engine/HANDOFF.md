# HANDOFF: Wagner Prep Opportunity Engine
## Operator Brief for Claude Code

**Read this first, then CLAUDE.md, then the playbook.** This file is the contract between Sebastian and the engine. If anything here conflicts with another file, this file wins.

---

## 1. Mission

Run the research loop on schedule and keep a constantly updating set of internal deliverables filled with REAL, DATED, WELL BACKED opportunities for high school students in the NYC area. Bias toward the niche: the program nobody is writing about, the free thing buried three clicks deep on an institutional site, the outer borough gem. Anyone can list the famous stuff. The engine earns its keep on the rest.

## 2. The two standards every item must meet

**The niche standard.** Each cycle, at least a third of new items should be genuinely under the radar: not on the first page of generic "NYC teen programs" search results, not already saturated in parent media. The directory's deeper sections (outer boroughs, libraries, civic infrastructure, Ring 2) are where these live. Famous flagship items still belong in the feed, especially deadlines, but they are the floor, not the work.

**The backing standard.** Niche does not mean flimsy. Every item needs:
* A primary source confirmation retrieved this cycle (the operator institution's own page or an official government page), AND
* At least one corroborating signal for anything below household name status: a second institutional reference, press coverage, a listed funder, years of operation, named staff, or a verifiable track record.
Record the backing in the item's `backing` field in one line. An item with a primary source but no corroboration gets the `thin_backing` flag and sits in the verification queue until the next cycle finds more. Never let enthusiasm for a find outrun its evidence.

## 3. INTERNAL ONLY. This is not optional.

Everything this engine produces is an internal draft. Nothing here is publication ready, family ready, or blog ready as generated.

* Every generated document carries the header: **INTERNAL DRAFT. NOT FOR PUBLICATION. Verify before any external use.**
* Every item carries `review_status`: starts as `unreviewed`. Only a human sets `approved` or `rejected`. The engine NEVER sets approved.
* The dashboard and calendar visually mark unreviewed items.
* If asked to draft family facing or blog language, produce it clearly labeled as a draft for human review, and never represent it as checked.
* The publication gate (playbook Part 13.2) is a human action: reopen the source same day, confirm dates and eligibility verbatim, gut check. The engine prepares; humans vouch.

## 4. The loop

Default sprint interval is 45 minutes via `./scripts/loop.sh`; standard operation is every 3 days; daily during December through February deadline season. Runs under 30 minutes apart automatically downgrade to a light deadline refresh. Each full cycle follows the contract in CLAUDE.md and `.claude/commands/cycle.md`: rotate focus, search named directory sources, verify, score, dedupe, write state, regenerate ALL deliverables below, prepend the digest.

## 5. The deliverables menu

**Regenerated automatically every cycle:**
1. `docs/feed.html`  Filterable dashboard (field, ring, rung, ledger, free, new, review status, search, sorting) plus the deadline board.
2. `docs/map.html`  Live pin map (OpenStreetMap) of every located item across NYC and surrounding rings, color coded by field, popups with dates, cost, and source links, unreviewed items labeled.
3. `docs/calendar.html`  Month grid calendar for the current and next two months: events on their dates, application closes marked as deadlines. The at a glance view.
3. `docs/wagner-prep-internal.ics`  Calendar subscription file. Import into Google Calendar or Apple Calendar; every event and deadline appears in the team's actual calendars, titled with the WP INTERNAL prefix.
4. `docs/digest.md`  Dated cycle log, newest first: pulse, ranked items, deadline changes, content shortlist, verification queue, vetting log.
5. `state/*`  The memory: archive, deadline board, rotation.

**On demand (the operator asks, the engine produces):**
6. Weekly team brief  A one page summary of the week's cycles in What, so what, now what structure, saved to `docs/briefs/` as markdown. For pasting into the team channel.
7. Blog draft stubs  For any approved item: a draft post in the relevant editorial archetype (playbook Part 11), saved to `docs/drafts/`, headed INTERNAL DRAFT.
8. Deadline board export  CSV at `docs/exports/deadlines.csv` for the shared sheet.
9. Student match briefs  Via `/match`, confidential, never written into shared state.
10. Vetting briefs  Via `/vet`, logged to the digest's vetting log section.
11. Seasonal one pager  Next month's landmark calendar as a single page for counselor planning.

## 6. Schema additions (extends playbook Part 10)

Every item now also carries:
```
date_start:     ISO date (YYYY-MM-DD) the event occurs or window opens. Required for calendar placement.
date_end:       ISO date if a range or a window close. Use for deadlines.
backing:        One line of evidence: "Primary: org site (retrieved this cycle). Corroboration: funded by X / covered by Y / operating since Z."
review_status:  unreviewed | approved | rejected. Engine writes only unreviewed.
niche:          true if this clears the niche standard, false for flagship items.
```
Items without a parseable `date_start` still appear in the feed but not on the calendar; say so in the digest.

## 7. Operator quick reference

```
claude -p "/cycle"            one full cycle, all deliverables refresh
./scripts/loop.sh             45 minute loop (INTERVAL=259200 for 3 days)
claude -p "/weekend"          this Saturday and Sunday sweep
claude -p "/vet <name/url>"   pay to play vetting brief
claude -p "/match <profile>"  confidential single student run
claude -p "weekly brief"      What, so what, now what summary to docs/briefs/
claude -p "draft a Hidden Gem post for <approved item>"  blog stub to docs/drafts/
```

## 8. What success looks like

A counselor opens the calendar Monday morning and sees three things worth forwarding this week, each already backed and dated. Megan opens the digest and finds two angles she did not have. Nothing in either has ever been invented, and nothing leaves the building without a human signing off. Niche, backed, internal, on time. That is the whole job.
