#!/usr/bin/env python3
"""Builds docs/dashboard.html: one self contained file combining the feed, map,
and calendar as tabs, with opportunities.js inlined so it opens anywhere (phone
included) with no sibling files to download. Map tiles and fonts still load from
their CDNs over the internet. Run after the other build scripts each cycle."""
import pathlib, html, datetime

root = pathlib.Path(__file__).resolve().parents[1]
docs = root / "docs"
data_js = (docs / "opportunities.js").read_text()

def page_with_data(name):
    t = (docs / name).read_text()
    return t.replace('<script src="opportunities.js"></script>', f"<script>\n{data_js}\n</script>")

feed = page_with_data("feed.html")
mp = page_with_data("map.html")
cal = (docs / "calendar.html").read_text()  # data already inlined

def srcdoc(s):
    return html.escape(s, quote=True)

today = datetime.date.today().strftime("%B %d, %Y")
out = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Wagner Prep Opportunity Dashboard</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700;800&family=Raleway:wght@400;600&display=swap');
*{{box-sizing:border-box;}} html,body{{margin:0;height:100%;}}
body{{font-family:'Raleway',sans-serif;background:#143757;display:flex;flex-direction:column;height:100vh;}}
.banner{{background:#8A2B2B;color:#fff;text-align:center;font-family:'Montserrat',sans-serif;font-weight:800;font-size:11px;letter-spacing:.12em;padding:6px;}}
.tabs{{display:flex;background:#143757;padding:0 8px;gap:4px;align-items:center;flex-wrap:wrap;}}
.tabs .title{{color:#fff;font-family:'Montserrat',sans-serif;font-weight:800;font-size:14px;margin-right:14px;padding:8px 4px;}}
.tab{{appearance:none;border:none;cursor:pointer;font-family:'Montserrat',sans-serif;font-weight:700;font-size:13px;
     color:#C9D6E2;background:transparent;padding:12px 16px;border-radius:10px 10px 0 0;}}
.tab.on{{color:#143757;background:#FBF3E6;}}
.meta{{margin-left:auto;color:#9DB2C6;font-size:11px;padding:8px;}}
.frames{{flex:1;position:relative;background:#FBF3E6;}}
iframe{{position:absolute;inset:0;width:100%;height:100%;border:none;display:none;}}
iframe.on{{display:block;}}
</style></head><body>
<div class="banner">INTERNAL DRAFT · NOT FOR PUBLICATION · VERIFY BEFORE ANY EXTERNAL USE</div>
<div class="tabs">
  <span class="title">WP Opportunity Dashboard</span>
  <button class="tab on" data-f="f-feed">Feed</button>
  <button class="tab" data-f="f-map">Map</button>
  <button class="tab" data-f="f-cal">Calendar</button>
  <span class="meta">Generated {today} · single file, open anywhere</span>
</div>
<div class="frames">
  <iframe id="f-feed" class="on" srcdoc="{srcdoc(feed)}"></iframe>
  <iframe id="f-map" srcdoc="{srcdoc(mp)}"></iframe>
  <iframe id="f-cal" srcdoc="{srcdoc(cal)}"></iframe>
</div>
<script>
document.querySelectorAll('.tab').forEach(function(b){{
  b.addEventListener('click',function(){{
    document.querySelectorAll('.tab').forEach(function(x){{x.classList.remove('on');}});
    document.querySelectorAll('iframe').forEach(function(x){{x.classList.remove('on');}});
    b.classList.add('on');
    document.getElementById(b.dataset.f).classList.add('on');
  }});
}});
</script>
</body></html>"""
(docs / "dashboard.html").write_text(out)
print(f"Wrote docs/dashboard.html ({len(out)//1024} KB, self contained)")
