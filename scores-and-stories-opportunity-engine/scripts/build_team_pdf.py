#!/usr/bin/env python3
"""Builds a team facing PDF brief from state/opportunities.json.
Style rules (operator directive June 10, 2026): factual, no opinion, no filler
text, less is more per page. Each item card: data bullets, the Wagner angle,
grade group, and type (ledger and rung). Output is versioned, never overwritten.
Usage: python3 scripts/build_team_pdf.py [version_label]
"""
import json, pathlib, sys, datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Paragraph,
                                Spacer, KeepTogether)

root = pathlib.Path(__file__).resolve().parents[1]
items = json.loads((root / "state" / "opportunities.json").read_text())["items"]
board = json.loads((root / "state" / "deadline-board.json").read_text())["windows"]

version = sys.argv[1] if len(sys.argv) > 1 else "v1"
today = datetime.date.today()
out = root / "docs" / "exports" / f"team-brief-{today.isoformat()}-{version}.pdf"
if out.exists():
    raise SystemExit(f"Refusing to overwrite {out}; bump the version label.")

NAVY, ORANGE, RED, CREAM = HexColor("#143757"), HexColor("#ED7D14"), HexColor("#8A2B2B"), HexColor("#FBF3E6")

def banner(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(RED)
    canvas.rect(0, letter[1] - 0.35 * inch, letter[0], 0.35 * inch, stroke=0, fill=1)
    canvas.setFillColor(HexColor("#FFFFFF"))
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawCentredString(letter[0] / 2, letter[1] - 0.24 * inch,
        "INTERNAL DRAFT  ·  NOT FOR PUBLICATION  ·  VERIFY BEFORE ANY EXTERNAL USE")
    canvas.setFillColor(NAVY)
    canvas.setFont("Helvetica", 7)
    canvas.drawCentredString(letter[0] / 2, 0.4 * inch,
        f"Wagner Prep Opportunity Engine  ·  {today.strftime('%B %d, %Y')}  ·  {version}  ·  page {doc.page}")
    canvas.restoreState()

doc = BaseDocTemplate(str(out), pagesize=letter,
    leftMargin=0.9 * inch, rightMargin=0.9 * inch, topMargin=0.8 * inch, bottomMargin=0.7 * inch)
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")
doc.addPageTemplates([PageTemplate(id="p", frames=[frame], onPage=banner)])

H1 = ParagraphStyle("H1", fontName="Helvetica-Bold", fontSize=22, leading=26, textColor=NAVY)
H2 = ParagraphStyle("H2", fontName="Helvetica-Bold", fontSize=13, leading=16, textColor=NAVY, spaceBefore=14)
NAME = ParagraphStyle("NAME", fontName="Helvetica-Bold", fontSize=10.5, leading=14, textColor=NAVY, spaceBefore=10)
META = ParagraphStyle("META", fontName="Helvetica-Bold", fontSize=8, leading=11, textColor=ORANGE)
BULLET = ParagraphStyle("BULLET", fontName="Helvetica", fontSize=9, leading=12.5, textColor=NAVY,
                        leftIndent=10, bulletIndent=2)
SMALL = ParagraphStyle("SMALL", fontName="Helvetica", fontSize=8.5, leading=11.5, textColor=HexColor("#5A6E80"))

def grade_group(it):
    fit = (it.get("student_fit") or "")
    for token in ("9th to 12th", "10th to 12th", "9th to 11th", "8th to 11th", "8th to 10th", "10th and 11th"):
        if token in fit: return "Grades " + token.replace("th", "").replace(" to ", " to ")
    return {1: "All grades", 2: "Grades 8 to 11", 3: "Grades 10 to 12", 4: "Grades 10 to 12"}.get(it.get("rung"), "All grades")

def card(it):
    rung_names = {1: "Exposure", 2: "Engagement", 3: "Production", 4: "Credential"}
    typ = f"{it.get('ledger','')} · Rung {it.get('rung','')} {rung_names.get(it.get('rung'),'')}"
    flags = [f for f in it.get("flags", []) if f != "verified"]
    parts = [Paragraph(f"{it['name']} — {it['org']}", NAME),
             Paragraph(f"{grade_group(it)}  ·  {typ}  ·  {it.get('field','')}"
                       + ("  ·  " + ", ".join(flags).upper() if flags else ""), META)]
    for label, key in (("When", "when"), ("Where", "location"), ("Cost", "cost"), ("Eligibility", "eligibility")):
        v = it.get(key)
        if v: parts.append(Paragraph(f"<bullet>•</bullet><b>{label}:</b> {v}", BULLET))
    parts.append(Paragraph(f"<bullet>•</bullet><b>Wagner angle:</b> {it.get('blog_angle','')}", BULLET))
    parts.append(Paragraph(f"<bullet>•</bullet><b>Source:</b> {it.get('url','')}  ·  status: {it.get('review_status','unreviewed')}", BULLET))
    return KeepTogether(parts)

story = [Spacer(1, 1.6 * inch),
         Paragraph("Opportunity Brief", H1),
         Paragraph(today.strftime("%B %d, %Y") + " · overnight research cycle output · " + version, SMALL),
         Spacer(1, 0.3 * inch),
         Paragraph("Every item: verified at a primary source this cycle, tagged Scores or Stories "
                    "(the framework), grade group, and ladder rung. Unreviewed until a counselor signs off.", SMALL)]

new_items = [i for i in items if i.get("first_seen") == today.isoformat() and "verified" in i.get("flags", [])]
deadline_items = sorted([i for i in new_items if i.get("date_end")], key=lambda i: i["date_end"])
dated = sorted([i for i in new_items if i.get("date_start") and not i.get("date_end")], key=lambda i: i["date_start"])
open_now = [i for i in new_items if not i.get("date_start")]

for title, group in (("Deadlines and closing windows", deadline_items),
                     ("Dated events", dated),
                     ("Open now, no deadline", open_now)):
    if not group: continue
    story.append(Paragraph(title, H2))
    for it in group:
        story.append(card(it))

story.append(Paragraph("Professional takeaways", H2))
takeaways = [
    "Paid teen roles at named institutions are the strongest current pattern: BPL Branch Council (16 to 19, rolling), NYSCI Explainers (rolling), Bronx Museum Teen Council (fall posting pending).",
    "Hospital volunteering is applied for in winter, not summer: NYP's window is January 1 to March 31 for the following summer. Calendar it for juniors now.",
    "The World Cup fan zones are free, official, and time bound: Bronx June 13 to 14 only; Queens needs an advance reservation (code QUEENSHQ).",
    "August 23 is the single most actionable deadline in the feed (Student Historian, paid, entering grades 10 to 12).",
    "One paid program deadline this week carries a pay to play flag (NYU Career Edge, June 12, $2,579 per week); free alternatives at equal or better selectivity exist in this brief.",
]
for t in takeaways:
    story.append(Paragraph(f"<bullet>•</bullet>{t}", BULLET))

doc.build(story)
print(f"Wrote {out}")
