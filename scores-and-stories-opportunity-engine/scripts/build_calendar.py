#!/usr/bin/env python3
"""Builds docs/calendar.html (3 month grid) and docs/wagner-prep-internal.ics
from state/opportunities.json and state/deadline-board.json.
Items need ISO date_start (and optionally date_end) to appear."""
import json, pathlib, datetime, calendar, html

root = pathlib.Path(__file__).resolve().parents[1]
opps = json.loads((root / "state" / "opportunities.json").read_text()).get("items", [])
board = json.loads((root / "state" / "deadline-board.json").read_text()).get("windows", [])
today = datetime.date.today()

def parse(d):
    try: return datetime.date.fromisoformat(str(d)[:10])
    except Exception: return None

# Collect dated entries: (date, label, kind, url, review_status)
entries = []
for i in opps:
    if i.get("status") == "expired": continue
    ds = parse(i.get("date_start"))
    if ds: entries.append((ds, i.get("name",""), "event", i.get("url",""), i.get("review_status","unreviewed")))
    de = parse(i.get("date_end"))
    if de and i.get("rung") == 4 or (de and "deadline" in str(i.get("when","")).lower()):
        entries.append((de, "DEADLINE: " + i.get("name",""), "deadline", i.get("url",""), i.get("review_status","unreviewed")))
for w in board:
    dc = parse(w.get("closes_iso") or w.get("closes"))
    if dc: entries.append((dc, "DEADLINE: " + w.get("program",""), "deadline", w.get("url",""), "unreviewed"))

bydate = {}
for d, label, kind, url, rs in entries:
    bydate.setdefault(d, []).append((label, kind, url, rs))

def month_grid(year, month):
    cal = calendar.Calendar(firstweekday=6)  # Sunday first
    rows = []
    for week in cal.monthdayscalendar(year, month):
        cells = []
        for day in week:
            if day == 0:
                cells.append("<td class='pad'></td>"); continue
            d = datetime.date(year, month, day)
            items = bydate.get(d, [])
            chips = "".join(
                f"<a class='chip {k}{' un' if rs=='unreviewed' else ''}' href='{html.escape(u) or '#'}' target='_blank' title='{html.escape(l)}'>{html.escape(l[:34])}</a>"
                for l, k, u, rs in items[:4]
            ) + (f"<span class='more'>+{len(items)-4} more</span>" if len(items) > 4 else "")
            tcls = " today" if d == today else ""
            cells.append(f"<td class='day{tcls}'><span class='num'>{day}</span>{chips}</td>")
        rows.append("<tr>" + "".join(cells) + "</tr>")
    name = datetime.date(year, month, 1).strftime("%B %Y")
    return f"<h2>{name}</h2><table><tr>" + "".join(f"<th>{d}</th>" for d in ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"]) + "</tr>" + "".join(rows) + "</table>"

months, y, m = [], today.year, today.month
for _ in range(3):
    months.append(month_grid(y, m))
    m += 1
    if m == 13: m, y = 1, y + 1

page = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>WP Internal Opportunity Calendar</title><style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700;800&family=Raleway:wght@400;600&display=swap');
body{{margin:0;background:#FBF3E6;font-family:'Raleway',sans-serif;color:#143757}}
.banner{{background:#8A2B2B;color:#fff;text-align:center;font-family:'Montserrat',sans-serif;font-weight:800;font-size:12px;letter-spacing:.14em;padding:8px}}
header{{background:#143757;padding:22px}} .wrap{{max-width:1100px;margin:0 auto;padding:0 16px 60px}}
h1{{font-family:'Montserrat',sans-serif;color:#fff;margin:0;font-size:24px}} .sub{{color:#C9D6E2;font-size:13px;margin:4px 0 0}}
h2{{font-family:'Montserrat',sans-serif;font-size:18px;margin:28px 0 8px}}
table{{width:100%;border-collapse:collapse;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(20,55,87,.08);table-layout:fixed}}
th{{background:#143757;color:#fff;font-family:'Montserrat',sans-serif;font-size:10px;letter-spacing:.08em;padding:8px}}
td{{vertical-align:top;border:1px solid #EFEAE0;height:86px;padding:4px;font-size:11px}}
td.pad{{background:#F6F0E2}} td.today{{background:#FDF1E3;outline:2px solid #ED7D14;outline-offset:-2px}}
.num{{font-family:'Montserrat',sans-serif;font-weight:700;font-size:11px;display:block;margin-bottom:3px}}
.chip{{display:block;margin:2px 0;padding:3px 5px;border-radius:6px;background:#DCE7F1;color:#143757;text-decoration:none;font-size:10px;line-height:1.25;overflow:hidden;white-space:nowrap;text-overflow:ellipsis}}
.chip.deadline{{background:#ED7D14;color:#fff;font-weight:600}}
.chip.un{{border-left:3px solid #8A2B2B}}
.more{{font-size:9.5px;color:#5A6E80}}
.legend{{margin-top:16px;font-size:12px;color:#5A6E80}} .sw{{display:inline-block;width:10px;height:10px;border-radius:3px;vertical-align:middle;margin:0 4px 0 12px}}
</style></head><body>
<div class="banner">INTERNAL DRAFT · NOT FOR PUBLICATION · VERIFY BEFORE ANY EXTERNAL USE</div>
<header><div class="wrap" style="padding:0 16px"><h1>Opportunity Calendar</h1>
<p class="sub">Generated {today.strftime('%B %d, %Y')} · {len(entries)} dated entries · subscribe via wagner-prep-internal.ics</p></div></header>
<div class="wrap">{''.join(months)}
<p class="legend">Legend: <span class="sw" style="background:#DCE7F1"></span> event <span class="sw" style="background:#ED7D14"></span> deadline <span class="sw" style="background:#fff;border-left:3px solid #8A2B2B;border-radius:0"></span> unreviewed (red edge = needs human vetting)</p>
</div></body></html>"""
(root / "docs" / "calendar.html").write_text(page)

# ICS
def ics_escape(s): return str(s).replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;")
lines = ["BEGIN:VCALENDAR","VERSION:2.0","PRODID:-//Wagner Prep//Opportunity Engine//EN",
         "X-WR-CALNAME:WP Internal Opportunities"]
for idx, (d, label, kind, url, rs) in enumerate(sorted(entries)):
    dt = d.strftime("%Y%m%d")
    lines += ["BEGIN:VEVENT", f"UID:wp-engine-{dt}-{idx}@wagnerprep",
              f"DTSTART;VALUE=DATE:{dt}",
              f"SUMMARY:WP INTERNAL: {ics_escape(label)}",
              f"DESCRIPTION:{ics_escape('Internal draft, verify before external use. ' + (url or ''))}",
              "END:VEVENT"]
lines.append("END:VCALENDAR")
(root / "docs" / "wagner-prep-internal.ics").write_text("\r\n".join(lines) + "\r\n")
print(f"Calendar built: {len(entries)} dated entries across 3 months. ICS written.")
