#!/usr/bin/env python3
"""Builds site/, a deploy ready folder for Netlify drag and drop.

index.html      The weekly page: this week's opportunities, clean and scannable.
behind.html     Everything else: engine views, drafts, briefs, methodology.
Plus copies of the live views, every markdown deliverable as HTML, and the PDFs.

Weekly rhythm: run a research cycle, then this script, then redeploy.
    claude -p "/cycle" && python3 scripts/build_site.py
"""
import datetime
import json
import pathlib
import re
import shutil

import markdown

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SITE = ROOT / "site"

BANNER = "INTERNAL DRAFT · NOT FOR PUBLICATION · VERIFY BEFORE ANY EXTERNAL USE"
SAMPLE_STRIP = (
    '<div style="background:#B8860B;color:#fff;text-align:center;'
    "font-family:'Montserrat',sans-serif;font-weight:700;font-size:11px;"
    'letter-spacing:.08em;padding:6px 10px;">TRIAL RUN DATA · live verified finds '
    'mixed with illustrative seed items · every item is unreviewed until a human '
    'approves it · <a href="index.html" style="color:#fff;">about this site</a></div>'
)

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700;800&family=Raleway:wght@400;500;600&display=swap');
:root { --navy:#143757; --orange:#ED7D14; --cream:#FBF3E6; --maroon:#8A2B2B; }
* { box-sizing:border-box; }
body { margin:0; background:var(--cream); font-family:'Raleway',sans-serif; color:var(--navy); }
.banner { background:var(--maroon); color:#fff; text-align:center; font-family:'Montserrat',sans-serif; font-weight:800; font-size:11px; letter-spacing:.14em; padding:8px 10px; }
header { background:var(--navy); padding:30px 22px 26px; }
.wrap { max-width:980px; margin:0 auto; padding:0 18px; }
.kicker { font-family:'Montserrat',sans-serif; font-weight:800; font-size:12px; letter-spacing:.18em; color:var(--orange); text-transform:uppercase; }
h1 { font-family:'Montserrat',sans-serif; font-weight:800; font-size:32px; color:#fff; margin:8px 0 4px; }
.sub { color:#C9D6E2; font-size:14.5px; margin:0; max-width:720px; line-height:1.55; }
.topnav { margin-top:16px; }
.topnav a { color:#C9D6E2; font-family:'Montserrat',sans-serif; font-weight:700; font-size:12px; letter-spacing:.06em; text-decoration:none; text-transform:uppercase; margin-right:18px; }
.topnav a:hover { color:var(--orange); }
h2 { font-family:'Montserrat',sans-serif; font-weight:700; font-size:19px; margin:34px 0 6px; }
h2 .n { color:#8FA3B5; font-weight:600; font-size:14px; }
h3 { font-family:'Montserrat',sans-serif; font-weight:700; font-size:14.5px; margin:24px 0 10px; letter-spacing:.02em; }
.lede { font-size:14px; color:#3D5468; line-height:1.65; margin:6px 0 4px; max-width:760px; }
.stats { display:flex; flex-wrap:wrap; gap:10px; margin:22px 0 0; }
.stat { background:rgba(255,255,255,.08); border:1px solid rgba(255,255,255,.16); border-radius:12px; padding:10px 16px; color:#fff; }
.stat b { font-family:'Montserrat',sans-serif; font-size:20px; display:block; color:var(--orange); }
.stat span { font-size:11.5px; color:#C9D6E2; letter-spacing:.04em; text-transform:uppercase; }
.notice { background:#FDF1DC; border:1.5px solid #E3B765; border-radius:12px; padding:14px 18px; font-size:13.5px; line-height:1.6; margin:22px 0 0; }
.urgent { background:#fff; border-left:5px solid var(--orange); border-radius:12px; padding:14px 18px; margin:22px 0 0; box-shadow:0 2px 10px rgba(20,55,87,.08); font-size:14px; line-height:1.6; }
.grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(235px,1fr)); gap:13px; }
a.card { display:block; background:#fff; border-radius:14px; padding:16px 18px; text-decoration:none; color:var(--navy); box-shadow:0 1px 6px rgba(20,55,87,.07); border:1.5px solid transparent; transition:border .15s; }
a.card:hover { border-color:var(--orange); }
a.card.primary { grid-column:1 / -1; background:var(--navy); color:#fff; padding:22px 24px; }
a.card.primary .desc { color:#C9D6E2; }
.card .name { font-family:'Montserrat',sans-serif; font-weight:700; font-size:15.5px; }
.card.primary .name { font-size:19px; color:#fff; }
.card .desc { font-size:12.8px; color:#5A6E80; margin-top:5px; line-height:1.5; }
.card .go { font-family:'Montserrat',sans-serif; font-weight:700; font-size:11px; letter-spacing:.08em; color:var(--orange); text-transform:uppercase; margin-top:9px; display:inline-block; }
footer { margin:46px 0 30px; font-size:12.5px; color:#5A6E80; line-height:1.7; }
.how { background:#fff; border-radius:14px; padding:18px 22px; box-shadow:0 1px 6px rgba(20,55,87,.07); font-size:13.8px; line-height:1.7; }
.pgrid { display:grid; grid-template-columns:repeat(auto-fill,minmax(330px,1fr)); gap:14px; }
.pick { background:#fff; border-radius:14px; padding:18px 20px; box-shadow:0 1px 6px rgba(20,55,87,.07); display:flex; flex-direction:column; gap:8px; }
.hook { font-family:'Montserrat',sans-serif; font-weight:800; font-size:11px; letter-spacing:.12em; color:var(--orange); text-transform:uppercase; }
.pname { font-family:'Montserrat',sans-serif; font-weight:700; font-size:16.5px; line-height:1.35; }
.porg { font-family:'Raleway',sans-serif; font-weight:500; font-size:13px; color:#5A6E80; }
.pwhen { font-size:13.2px; color:#3D5468; }
.pfit { font-size:13.2px; line-height:1.55; }
.pmeta { margin-top:auto; padding-top:8px; font-size:12px; color:#5A6E80; display:flex; gap:10px; flex-wrap:wrap; align-items:center; }
.free { font-family:'Montserrat',sans-serif; font-weight:800; font-size:10px; letter-spacing:.08em; background:#2E8B57; color:#fff; padding:3px 9px; border-radius:999px; }
.paid { font-family:'Montserrat',sans-serif; font-weight:800; font-size:10px; letter-spacing:.08em; background:#EFEAE0; color:var(--navy); padding:3px 9px; border-radius:999px; }
.un { font-size:10px; color:#A05252; letter-spacing:.05em; font-weight:600; }
.rot { display:flex; flex-wrap:wrap; gap:9px; margin-top:10px; }
.rot span { background:#fff; border:1.5px solid #D8D2C4; border-radius:999px; padding:8px 14px; font-size:12.5px; font-weight:600; }
.rot b { color:var(--orange); font-family:'Montserrat',sans-serif; margin-right:5px; }
.prow { display:flex; justify-content:space-between; align-items:center; }
.datechip { font-family:'Montserrat',sans-serif; font-weight:800; font-size:11px; letter-spacing:.08em; color:#fff; background:var(--navy); padding:4px 11px; border-radius:999px; }
.ftag { font-family:'Montserrat',sans-serif; font-weight:700; font-size:10px; letter-spacing:.08em; color:#8FA3B5; text-transform:uppercase; }
.itag { font-family:'Montserrat',sans-serif; font-weight:800; font-size:10px; letter-spacing:.05em; background:#7A5AA8; color:#fff; padding:3px 9px; border-radius:999px; }
.slist { display:flex; flex-direction:column; gap:9px; }
.srow { background:#fff; border-radius:12px; padding:13px 16px; box-shadow:0 1px 5px rgba(20,55,87,.06); display:flex; gap:14px; align-items:center; font-size:13.2px; }
.sdate { font-family:'Montserrat',sans-serif; font-weight:800; font-size:11.5px; color:var(--orange); min-width:54px; }
.sbody { flex:1; line-height:1.5; }
.snote { font-size:11.8px; color:#5A6E80; }
.vflag { font-family:'Montserrat',sans-serif; font-weight:800; font-size:9.5px; letter-spacing:.06em; background:var(--maroon); color:#fff; padding:3px 8px; border-radius:999px; white-space:nowrap; }
"""

MD_CSS = """
.mdwrap { max-width:840px; margin:0 auto; padding:8px 18px 60px; }
.mdbody { background:#fff; border-radius:14px; padding:28px 34px; box-shadow:0 1px 6px rgba(20,55,87,.07); line-height:1.65; font-size:14.5px; }
.mdbody h1 { color:var(--navy); font-size:23px; margin:18px 0 10px; }
.mdbody h2 { font-size:18px; border-bottom:2px solid var(--cream); padding-bottom:6px; }
.mdbody h3 { font-family:'Montserrat',sans-serif; font-size:15px; margin:20px 0 8px; }
.mdbody a { color:var(--orange); }
.mdbody table { border-collapse:collapse; width:100%; font-size:13px; margin:14px 0; }
.mdbody th { background:var(--navy); color:#fff; font-family:'Montserrat',sans-serif; font-size:11px; letter-spacing:.05em; padding:7px 9px; text-align:left; }
.mdbody td { border:1px solid #EFEAE0; padding:7px 9px; vertical-align:top; }
.mdbody blockquote { border-left:4px solid var(--orange); margin:14px 0; padding:4px 16px; background:var(--cream); border-radius:0 8px 8px 0; }
.mdbody code { background:var(--cream); padding:1px 5px; border-radius:5px; font-size:13px; }
.back { display:inline-block; margin:16px 0 6px; font-family:'Montserrat',sans-serif; font-weight:700; font-size:12px; letter-spacing:.06em; color:var(--orange); text-decoration:none; text-transform:uppercase; }
"""


def md_page(src: pathlib.Path, out_rel: str, title: str | None = None) -> str:
    """Convert a markdown file to a styled HTML page inside site/. Returns the page title."""
    text = src.read_text()
    m = re.search(r"^# (?!INTERNAL)(.+)$", text, re.M)
    page_title = title or (m.group(1).strip() if m else src.stem)
    body = markdown.markdown(text, extensions=["tables", "sane_lists"])
    depth = out_rel.count("/")
    home = "../" * depth + "index.html"
    html_doc = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{page_title} · Scores and Stories</title>
<style>{CSS}{MD_CSS}</style></head><body>
<div class="banner">{BANNER}</div>
<div class="mdwrap"><a class="back" href="{home}">&larr; Back to this week</a>
<div class="mdbody">{body}</div>
<footer>Scores and Stories · Wagner Prep · internal working document.</footer>
</div></body></html>"""
    dest = SITE / out_rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html_doc)
    return page_title


def copy_view(name: str) -> None:
    """Copy a live view into site/ with the trial data strip injected after <body>."""
    text = (DOCS / name).read_text()
    text = text.replace("<body>", "<body>" + SAMPLE_STRIP, 1)
    (SITE / name).write_text(text)


def main() -> None:
    SITE.mkdir(exist_ok=True)  # rebuild in place; files are overwritten

    for name in ["dashboard.html", "feed.html", "map.html", "calendar.html"]:
        copy_view(name)
    shutil.copy2(DOCS / "opportunities.js", SITE / "opportunities.js")
    shutil.copy2(DOCS / "wagner-prep-internal.ics", SITE / "wagner-prep-internal.ics")

    (SITE / "exports").mkdir(exist_ok=True)
    pdfs = sorted((DOCS / "exports").glob("*.pdf"))
    for p in pdfs:
        shutil.copy2(p, SITE / "exports" / p.name)

    md_page(ROOT / "MORNING-REPORT.md", "morning-report.html", "Morning Report · June 10, 2026")
    md_page(DOCS / "digest.md", "digest.html", "Cycle Digest")
    md_page(DOCS / "shift-log-2026-06-10.md", "shift-log.html", "Overnight Shift Log · June 10, 2026")

    draft_pitch = {
        "mailing-list-edition-01.md": "Mailing list v1, the seed edition in the age ladder format.",
        "mailing-list-edition-02-age-ladder-scores-and-stories.md": "Age ladder v2: first all fields edition with Scores and Stories ledger tags.",
        "mailing-list-edition-03-deadline-first.md": "Deadline first v3, factual titles, current data. The engine's pick to build the next send from.",
        "this-weekend-edition-01-june-13-14.md": "Weekend edition for June 13 to 14. Expires Sunday; send decision needed.",
        "blog-hidden-gem-01-bpl-branch-council.md": "Hidden Gem blog draft: BPL pays teens to produce its events. Ready for Megan's edit.",
        "blog-deadline-watch-01-june.md": "Deadline Watch blog draft: five real deadlines, June through October.",
        "research-and-competitions-edition-01.md": "Research and competitions brief No. 1, seeded by Michael's program links.",
        "research-and-competitions-edition-02.md": "Research and competitions brief No. 2.",
    }
    drafts = []
    for f in sorted((DOCS / "drafts").glob("*.md")):
        t = md_page(f, f"drafts/{f.stem}.html")
        drafts.append((f"drafts/{f.stem}.html", t, draft_pitch.get(f.name, "")))

    outbox_pitch = {
        "2026-06-10-0301-test-shift-starting.md": "3:01 AM · shift starting test message.",
        "2026-06-10-0445-cycle-2-top-finds.md": "4:45 AM · cycle 2 top finds.",
        "2026-06-10-0605-cycle-4-top-finds.md": "6:05 AM · cycle 4 top finds.",
        "2026-06-10-0655-morning-report.md": "6:55 AM · end of shift morning report.",
    }
    outbox = []
    for f in sorted((DOCS / "outbox").glob("*.md")):
        t = md_page(f, f"outbox/{f.stem}.html")
        outbox.append((f"outbox/{f.stem}.html", t, outbox_pitch.get(f.name, "")))

    opps = json.loads((ROOT / "state" / "opportunities.json").read_text())["items"]
    windows = json.loads((ROOT / "state" / "deadline-board.json").read_text())["windows"]
    rotation = json.loads((ROOT / "state" / "rotation.json").read_text())
    niche = sum(1 for i in opps if i.get("niche"))
    pins = sum(1 for i in opps if i.get("lat") and i.get("status") != "expired")

    today = datetime.date.today()

    # Most urgent unflagged deadline
    soonest = None
    for w in windows:
        iso = w.get("closes_iso")
        if not iso:
            continue
        if "vetting risk" in (w.get("eligibility", "") + w.get("note", "")).lower():
            continue  # never headline a flagged pay to play item
        try:
            d = datetime.date.fromisoformat(iso)
        except ValueError:
            continue
        if d >= today and (soonest is None or d < soonest[0]):
            soonest = (d, w)

    urgent_html = ""
    if soonest:
        d, w = soonest
        urgent_html = (
            f'<div class="urgent"><b style="font-family:Montserrat">Most urgent deadline:</b> '
            f'{w["program"]} closes <b>{w["closes"]}</b>. {w.get("eligibility", "")} '
            f'<a href="{w["url"]}" target="_blank" style="color:var(--orange);font-weight:600">Source &rarr;</a></div>'
        )

    # Stories first: free, dated, attendable. Scores live on the deadline board.
    FIELD_SHORT = {
        "Arts and Film": "Arts",
        "STEM and Tech": "STEM",
        "Humanities and History": "Humanities",
        "Civic and Social Impact": "Civic",
        "Business and Entrepreneurship": "Business",
        "Health and Science of Care": "Health",
    }

    def pdate(s):
        try:
            return datetime.date.fromisoformat(s) if s else None
        except ValueError:
            return None

    def is_free(i):
        return (i.get("cost") or "").strip().lower().startswith(("free", "tuition free"))

    horizon = today + datetime.timedelta(days=14)
    soon, later, open_now = [], [], []
    for i in opps:
        if i.get("status") == "expired" or (i.get("score") or 0) < 60:
            continue
        if "vetting" in " ".join(i.get("flags") or []).lower():
            continue
        if i.get("ledger") not in ("Stories", "Both"):
            continue
        ds, de = pdate(i.get("date_start")), pdate(i.get("date_end"))
        if ds is None and de is None:
            open_now.append(i)
            continue
        running = ds and ds <= today and de and de >= today
        nxt = today if running else (ds if ds and ds >= today else (de if de and de >= today else None))
        if nxt is None:
            continue  # past
        i["_nxt"], i["_running"] = nxt, bool(running)
        (soon if nxt <= horizon else later).append(i)
    soon.sort(key=lambda x: (not is_free(x), x["_nxt"], -(x.get("score") or 0)))
    later.sort(key=lambda x: (not is_free(x), x["_nxt"], -(x.get("score") or 0)))
    open_now.sort(key=lambda x: (not is_free(x), -(x.get("score") or 0)))

    def datechip(i):
        if i.get("_running"):
            de = pdate(i.get("date_end"))
            return "NOW · thru " + de.strftime("%b %d") if de else "NOW"
        n = i.get("_nxt")
        if not n:
            return "OPEN"
        return "TODAY" if n == today else n.strftime("%a %b %d").upper()

    def pick_cards(items, chip=True):
        out = []
        for i in items:
            cost = (i.get("cost") or "").strip()
            badge = ('<span class="free">FREE</span>' if is_free(i)
                     else f'<span class="paid">{cost.split(";")[0][:38]}</span>')
            fit = f'<div class="pfit"><b>Good fit:</b> {i["student_fit"]}</div>' if i.get("student_fit") else ""
            elig = f'<div class="pwhen">{i["eligibility"]}</div>' if i.get("eligibility") else ""
            interest = "".join(f'<span class="itag">matches {f.split(":", 1)[1]}</span>'
                               for f in (i.get("flags") or []) if f.startswith("interest:"))
            chip_html = f'<span class="datechip">{datechip(i) if chip else "OPEN"}</span>'
            out.append(
                f'<div class="pick"><div class="prow">{chip_html}'
                f'<span class="ftag">{FIELD_SHORT.get(i.get("field"), "")}</span></div>'
                f'<div class="pname">{i["name"]} <span class="porg">· {i.get("org", "")}</span></div>'
                f'<div class="pwhen"><b>{i.get("when", "")}</b></div>{elig}{fit}'
                f'<div class="pmeta">{badge}{interest}<span class="un">unreviewed</span>'
                f'<a href="{i.get("url", "#")}" target="_blank" style="color:var(--orange);font-weight:600">Source &rarr;</a></div></div>'
            )
        return "\n".join(out)

    def score_rows():
        def key(w):
            d = pdate(w.get("closes_iso"))
            return (d is None, d or today)
        out = []
        for w in sorted(windows, key=key):
            flagged = "vetting risk" in (w.get("eligibility", "") + w.get("note", "")).lower()
            d = pdate(w.get("closes_iso"))
            chip = d.strftime("%b %d").upper() if d else "OPEN"
            flag = '<span class="vflag">VETTING FLAG</span>' if flagged else ""
            out.append(
                f'<div class="srow"><span class="sdate">{chip}</span>'
                f'<div class="sbody"><b>{w["program"]}</b> · {w.get("eligibility", "")}'
                f'<div class="snote">{w.get("closes", "")}{" · " + w["note"] if w.get("note") else ""}</div></div>'
                f'{flag}<a href="{w.get("url", "#")}" target="_blank" style="color:var(--orange);font-weight:600;white-space:nowrap">Source &rarr;</a></div>'
            )
        return "\n".join(out)

    def cards(items):
        return "\n".join(
            f'<a class="card" href="{href}"><div class="name">{name}</div>'
            f'<div class="desc">{desc}</div><span class="go">Open &rarr;</span></a>'
            for href, name, desc in items
        )

    generated = today.strftime("%B %d, %Y")
    week_label = "Week of " + today.strftime("%B %d, %Y")
    nav = ('<nav class="topnav"><a href="index.html">This week</a><a href="feed.html">All opportunities</a>'
           '<a href="calendar.html">Calendar</a><a href="map.html">Map</a><a href="behind.html">Behind it</a></nav>')

    # ---------------- index.html: the weekly page ----------------
    index = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Scores and Stories · {week_label}</title>
<style>{CSS}</style></head><body>
<div class="banner">{BANNER}</div>
<header><div class="wrap">
<div class="kicker">Wagner Prep · Scores and Stories</div>
<h1>{week_label}</h1>
<p class="sub">Real, dated NYC opportunities, verified at the source, refreshed every week. Stories first: the free, one off experiences a student can actually go do. Scores below: the deadlines.</p>
{nav}
</div></header>
<div class="wrap">
{urgent_html}

<h2>Stories · go soon <span class="n">{len(soon)}</span></h2>
<p class="lede">Free, dated, attendable in the next two weeks. The experiences that become essay material.</p>
<div class="pgrid">{pick_cards(soon)}</div>

<h2>Stories · always open <span class="n">{len(open_now)}</span></h2>
<p class="lede">Drop ins and rolling programs. No deadline, just show up or apply any time.</p>
<div class="pgrid">{pick_cards(open_now, chip=False)}</div>

<h2>Stories · further out <span class="n">{len(later)}</span></h2>
<div class="pgrid">{pick_cards(later)}</div>

<h2>Scores · the deadline board <span class="n">{len(windows)}</span></h2>
<p class="lede">The credential side: every open application window, sorted by close date.</p>
<div class="slist">{score_rows()}</div>

<footer>Every item verified at a primary source and unreviewed until a counselor approves it. Trial run data: live finds mixed with illustrative seed items.<br>
Generated {generated} · refreshed weekly from a research cycle · map: {pins} pins and growing, <a href="map.html" style="color:var(--orange)">see it</a> · <a href="behind.html" style="color:var(--orange)">how this gets made</a> · <a href="wagner-prep-internal.ics" style="color:var(--orange)">calendar subscription</a></footer>
</div></body></html>"""
    (SITE / "index.html").write_text(index)

    # ---------------- behind.html: everything else ----------------
    view_cards = cards([
        ("feed.html", "Feed", "Every item as a filterable card: search, field, ring, rung, Scores/Stories ledger, free only, new this week, plus the deadline board."),
        ("map.html", "Map", f"{pins} pins across the five boroughs, color coded by field, popups with dates, cost, and source links."),
        ("calendar.html", "Calendar", "Month grids for June through August: events on their dates, application closes marked as deadlines."),
        ("wagner-prep-internal.ics", "Calendar subscription (.ics)", "Import into Google or Apple Calendar; every event and deadline lands in your real calendar, prefixed WP INTERNAL."),
    ])
    shift_cards = cards([
        ("morning-report.html", "Morning Report", "The one page summary of the overnight shift: cycles, best finds, judgment calls, and the day's most urgent deadline."),
        ("digest.html", "Cycle Digest", "The dated cycle log, newest first: pulse, top items, deadline changes, and the verification queue."),
        ("shift-log.html", "Shift Log", "The engine's own overnight record: setup, judgment calls, and cycle by cycle decisions."),
    ] + outbox)
    draft_cards = cards(drafts)
    pdf_cards = cards([
        (f"exports/{p.name}", p.stem.replace("-", " ").title(), "One card per item with a takeaways page." + (" Current version." if p == pdfs[-1] else " Kept for format comparison."))
        for p in pdfs
    ])

    behind = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Behind it · Scores and Stories</title>
<style>{CSS}</style></head><body>
<div class="banner">{BANNER}</div>
<header><div class="wrap">
<div class="kicker">Wagner Prep · Scores and Stories</div>
<h1>Behind it</h1>
<p class="sub">The research engine that fills the weekly page: how it runs, what it produced last night, and the edition drafts waiting for a voice.</p>
{nav}
<div class="stats">
<div class="stat"><b>{len(opps)}</b><span>items in the feed</span></div>
<div class="stat"><b>{niche}</b><span>niche finds</span></div>
<div class="stat"><b>{pins}</b><span>map pins</span></div>
<div class="stat"><b>{len(windows)}</b><span>open deadline windows</span></div>
<div class="stat"><b>334</b><span>sources monitored</span></div>
<div class="stat"><b>{rotation.get("cycles_completed", "")}</b><span>cycles completed</span></div>
</div>
</div></header>
<div class="wrap">
<div class="notice"><b>Trial run data.</b> Live verified finds from the June 10 overnight shift mixed with earlier illustrative seed items. Every institution named is real, every item stays <code>unreviewed</code> until a human approves it, and nothing reaches a family without the publication gate: reopen the source same day, confirm dates and eligibility verbatim, gut check.</div>

<h2>How the week manifests</h2>
<div class="how">
Once a week (daily in deadline season) the engine runs a cycle: it rotates through six fields and three library systems plus an outer borough anchor, searches the 334 entry source directory, verifies every item at a primary source, scores it with the house rubric, and rebuilds this site. The team opens the weekly page, really looks at the opportunities, picks four or five, and a writer puts a voice on top. Unverifiable items wait in a verification queue, never the page. Operator commands: <code>/cycle</code>, <code>/weekend</code>, <code>/vet</code> a program a parent asked about, <code>/match</code> for confidential single student runs. Then <code>python3 scripts/build_site.py</code> and redeploy.
</div>

<h2>The rotation</h2>
<p class="lede">Rotating weekly knowledge, 7th through 12th grade, with picks at the bottom of every edition so everyone always has a reason to open.</p>
<div class="rot"><span><b>Wk 1</b> Admissions trends, what to know now</span><span><b>Wk 2</b> Middle school and SHSAT</span><span><b>Wk 3</b> Lower high school</span><span><b>Wk 4</b> Upper high school</span></div>

<h2>Edition candidates already drafted</h2>
<p class="lede">Eight drafts in the agreed formats, ready for a voice pass. The weekend edition expires Sunday; deadline first v3 is the engine's pick to build the next send from.</p>
<div class="grid">{draft_cards}</div>

<h2>The live views</h2>
<div class="grid">
<a class="card primary" href="dashboard.html"><div class="name">Open the Dashboard</div>
<div class="desc">Feed, map, and calendar as tabs in one self contained file. The thing to put on the screen.</div><span class="go">Open &rarr;</span></a>
{view_cards}
</div>

<h3>From last night's shift</h3>
<div class="grid">{shift_cards}</div>

<h3>Team briefs (PDF)</h3>
<div class="grid">{pdf_cards}</div>

<footer>Scores and Stories · Wagner Prep · generated {generated} · internal only, not for publication.<br>
Free first. Niche, backed, internal, on time.</footer>
</div></body></html>"""
    (SITE / "behind.html").write_text(behind)

    pages = len(list(SITE.rglob("*.html")))
    print(f"Built site/ with {pages} HTML pages, {len(pdfs)} PDFs, {len(opps)} feed items. "
          f"Stories soon/open/later = {len(soon)}/{len(open_now)}/{len(later)}; "
          f"deadline board = {len(windows)} windows; map pins = {pins}.")


if __name__ == "__main__":
    main()
