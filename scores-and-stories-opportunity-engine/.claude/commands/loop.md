# /loop: the overnight autonomous shift protocol

Run an unattended overnight shift of repeated research cycles. The operator is asleep. Make judgment calls yourself and log every one of them in the shift log. Never wait for operator input.

## Schedule
* Up to 10 cycles, one roughly every 45 minutes.
* Stop at 7:00 AM operator local time (America/New_York) or after 10 cycles, whichever comes first. Convert from system time if the machine runs UTC.
* If web searches fail 3 times in a row, pause 30 minutes, retry once, and if still failing, stop the loop gracefully and write the morning report with what you have.

## Each cycle, in order
1. Run the standard /cycle contract from .claude/commands/cycle.md in full: establish the real date, advance the rotation in state/rotation.json, search named directory sources, verify every item at a primary source, score per playbook Part 6, dedupe against state/opportunities.json, update state, rebuild dashboard, calendar, ICS, and map data via scripts/build_dashboard.py and scripts/build_calendar.py, and prepend a dated digest entry to docs/digest.md.
2. Geocode venues: every new item with a confirmed physical venue gets lat and lng from the address on its primary source page. Never guess a coordinate. If the venue is uncertain, virtual, or citywide, omit the pin and say so in the digest. As Ring 2 items appear, the map widens beyond the five boroughs naturally.
3. Produce ONE deliverable variant, saved versioned in docs/drafts/, never overwriting a previous version. Rotate through this wheel, then repeat with improved versions that fold in everything newly found:
   1. Mailing list edition in the four section age ladder format (next version number).
   2. Mailing list edition in a deadline first format.
   3. A "this weekend" edition.
   4. One Hidden Gem blog draft from the strongest niche item so far.
   5. One Deadline Watch blog draft.
   6. A Free Beats Paid comparison, only if the material genuinely supports one.
4. After every SECOND cycle, send the operator a short update with subject "WP Engine cycle N: top finds": pulse, top 3 new items with links, which variant was produced. Maximum 5 update emails per night. If no sending email tool works, write the email as a send ready file in docs/outbox/ instead and note the fallback in the morning report.

## Once per night
Sanity check the map pins: confirm every pin falls where its stated borough says it should, remove pins from citywide, virtual, or uncertain venue items, and log any corrections.

## Guardrails, non negotiable
* Real opportunities only. Primary source verification or the item goes to the verification queue, never the feed or the drafts.
* Everything is INTERNAL DRAFT, unreviewed. Never mark anything approved.
* No dashes of any kind in any prose: no em dashes, no en dashes, no hyphens used as dashes. Rewrite around them.
* Email only sebastian@wagnerprep.com. Never send, publish, or post anything anywhere else.

## At shift end
Write MORNING-REPORT.md in the project root: cycles completed, items added with the flagship versus niche ratio, the 5 best finds with one line each, every deliverable version produced with file paths and a one line pitch for which version to choose and why, a one line map summary (pins total, pins added tonight, most geographically surprising find), judgment calls made, anything broken, and the single most urgent deadline to act on today. Send it (or outbox it) with subject "WP Engine: morning report" and stop.
