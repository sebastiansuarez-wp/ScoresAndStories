Run one full research cycle per the cycle contract in CLAUDE.md.

Steps, in order:
1. Get today's real date (run `date` if needed). All windows compute forward from it.
2. Read state/rotation.json. Use its focus_field, library_system, and outer_borough values for this cycle. Then advance each pointer (wrap around) and write the file back with last_run set to now.
3. Read playbook/research-playbook.md Part 7 and Part 8, and the matching field section of playbook/source-directory.md.
4. Execute the searches: baseline sweep (deadlines closing or opening within 21 days, all fields; the rotation's library system; the rotation's outer borough anchor; TED format and lecture listings 14 days out) plus the focus field deep sweep against named directory sources.
4b. Read state/interests.json. For each entry with active true, run one or two targeted searches combining its keywords, grade band, and boroughs. Tag any resulting item's flags with interest:CODE (for example interest:EXAMPLE-10-BK). Never write a student's name or identifying combination anywhere; codenames only. Note interest matches in the digest under an Interest matches line.
5. Verify, dedupe against state/opportunities.json, score per Part 6, tag per the Part 10 schema.
6. Update state/opportunities.json and state/deadline-board.json. Every item must include the HANDOFF.md schema additions: ISO date_start (date_end for windows), a one line backing field (primary source plus corroboration), review_status set to unreviewed, niche true/false, and lat/lng coordinates geocoded from the venue address on the primary source (omit for virtual or citywide items; never guess a pin). At least a third of new items should clear the niche standard; say so in the digest if the cycle fell short. Then run `python3 scripts/build_dashboard.py` and `python3 scripts/build_calendar.py` to regenerate the dashboard, the calendar, and the ICS file.
7. Prepend a dated digest entry to docs/digest.md: pulse (2 sentences), top 5 items with scores, deadline board changes, content shortlist for Megan, verification queue.
8. Reply with a two line operator summary: items added, top item, next rotation focus.

Hard rules from CLAUDE.md and HANDOFF.md apply (internal only, niche standard, backing standard), especially: real items only, primary source verification, no dashes in prose, quality over quota.
