# Wagner Prep Opportunity Engine
A Claude Code project that runs the recurring opportunity research system on a schedule and maintains a constantly updating, filterable feed for the team.

## Start here
Read HANDOFF.md: the operator contract covering the loop, the niche and backing standards, the internal only policy, and the full deliverables menu.

## What you get
* **docs/feed.html**  The living dashboard. Open it in any browser. Filters: search, field, ring, rung, Scores/Stories ledger, free only, new this week, plus sorting. Includes the deadline board.
* **docs/calendar.html**  Month grid calendar (3 months) with events and deadlines on their dates; unreviewed items carry a red edge.
* **docs/wagner-prep-internal.ics**  Subscribe or import so events and deadlines land in the team's real calendars.
* **docs/digest.md**  Human readable cycle log, newest on top. The thing to skim or paste into the team channel.
* **state/**  The engine's memory: archive, deadline board, rotation position.
* **playbook/**  The full methodology and the 334 entry source directory. The engine reads these every cycle.
* **site/**  Deploy ready Netlify folder built by `python3 scripts/build_site.py`: an index.html hub linking the dashboard, every markdown deliverable converted to HTML, and the team brief PDFs. Deploy by dragging the `site` folder onto https://app.netlify.com/drop. Rebuild after every cycle so the deploy matches the data.

## Setup (one time)
1. Install Claude Code and authenticate: https://docs.claude.com/en/docs/claude-code
2. Unzip this folder anywhere, then from inside it run a first cycle:
   ```
   claude -p "/cycle"
   ```
3. Open docs/feed.html in a browser. Bookmark it. It refreshes every cycle.

## Running on a loop
**Sprint mode (every 45 minutes), as a foreground loop:**
```
./scripts/loop.sh
```
**Custom interval:** `INTERVAL=259200 ./scripts/loop.sh` runs every 3 days (the playbook's standard floor).

**Scheduled instead of looped (recommended for unattended use):**
* macOS launchd or cron calling `scripts/run_once.sh`. Example cron for twice a day:
  ```
  0 9,17 * * *  cd /path/to/wp-engine && ./scripts/run_once.sh >> cycle.log 2>&1
  ```
* Note that plain cron cannot express a true 45 minute interval cleanly; use loop.sh for that, or launchd's StartInterval 2700 on Mac.

## A note on the 45 minute cadence
Each cycle runs 10 to 25 web searches. At 45 minute intervals that is roughly 30 cycles and several hundred searches a day, which costs real usage and will mostly rediscover the same items, since the NYC opportunity ecosystem updates daily, not hourly. The engine handles this gracefully (runs under 30 minutes apart automatically downgrade to a light deadline refresh), but the practical sweet spots are: every 3 days normally, daily during December through February deadline season, and 45 minute sprints only when you are actively watching for a specific drop. The interval is yours to set.

## Commands
| Command | What it does |
|---|---|
| `claude -p "/cycle"` | Full research cycle: rotate focus, search, verify, rank, update dashboard and digest |
| `claude -p "/weekend"` | This Saturday and Sunday, free first, all boroughs |
| `claude -p "/vet Acme Leadership Summit"` | Pay to play vetting brief plus free alternatives |
| `claude -p "/match 10th grader, film and stop motion, Queens, needs a summer plan"` | Confidential single student run (never enters shared state) |

## The weekly rhythm (how the site stays current)
1. Every 2 days at 7:30 AM a scheduled Cowork task ("scores-and-stories-brief") refreshes deadlines, runs the interests funnel from state/interests.json, grows the map, rebuilds site/, builds a fresh team PDF, commits, pushes if a remote exists, and drafts a brief email to Sebastian. It runs while the Claude desktop app is open; if the app was closed it runs on next launch.
2. Mondays count as the weekly edition: the run says so and the weekly page (site/index.html, titled by week) is the deliverable.
3. Deploy: connect this repo to Netlify once (Add new site → Import from GitHub, publish directory `site`). After that every push deploys itself. Fallback: drag the `site` folder onto https://app.netlify.com/drop.
4. Deeper research still comes from `claude -p "/cycle"`; the scheduled task is the keep it fresh layer, not a replacement for full cycles.

## The interests funnel
Counselors add codename entries to state/interests.json (grade band, boroughs, keywords; never names). Every cycle and every scheduled run searches those interests and tags matches with `interest:CODE`, which surface on the weekly page with a purple chip. Confidential single student work stays in `/match` and never touches shared state.

## Review discipline
The feed is internal. Before anything reaches a family or the blog: reopen the primary source that day, confirm the date and eligibility verbatim, and apply the gut check from playbook Part 13. The engine researches; humans vouch.

## Extending
* Add sources: append to playbook/source-directory.md (rule: two Lead tier finds earns an entry).
* Adjust ranking: edit Part 6 weights in the playbook; the engine reads them live.
* Push the digest to Slack or email: add a notification step to scripts/run_once.sh.
* Student matching into TutorCruncher prep: pipe /match output into your session workflow.
