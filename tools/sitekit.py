"""Shared look-and-feel for every generated HTML page in this repo.

Every page must be a single offline file, so the stylesheet is embedded into
each page rather than linked. Hand-written docs copy the same CSS block.
"""
import html

CSS = """
:root {
  --bg: #fbfaf7; --surface: #ffffff; --surface-2: #f1efe9; --border: #dcd8cf;
  --text: #1d1c1a; --text-2: #4a4741; --muted: #77736b;
  --accent: #1f5fae; --accent-soft: #e3ecf8;
  --good: #2e7d32; --warn: #a15c00; --bad: #b3261e;
  --locked: #8a867d; --code-bg: #f4f2ed;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #15161a; --surface: #1d1f24; --surface-2: #262930; --border: #363a43;
    --text: #ebe9e4; --text-2: #c2bfb8; --muted: #8f8b83;
    --accent: #7fb0f0; --accent-soft: #23314a;
    --good: #7cc47f; --warn: #e3a64f; --bad: #f08a80;
    --locked: #7a776f; --code-bg: #20232a;
  }
}
* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body {
  margin: 0; background: var(--bg); color: var(--text);
  font: 16px/1.6 system-ui, -apple-system, "Segoe UI", Roboto, Ubuntu, "Helvetica Neue", Arial, sans-serif;
}
main { max-width: 980px; margin: 0 auto; padding: 24px 16px 64px; }
h1 { font-size: 1.9rem; line-height: 1.2; margin: 0 0 4px; }
h2 { font-size: 1.35rem; margin: 40px 0 12px; padding-top: 8px; border-top: 1px solid var(--border); }
h3 { font-size: 1.1rem; margin: 24px 0 8px; }
a { color: var(--accent); }
.meta { color: var(--muted); font-size: .9rem; margin: 0 0 16px; }
.home { display: inline-block; margin-bottom: 16px; font-size: .9rem; }
nav.toc { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 12px 16px; margin: 16px 0 8px; }
nav.toc ol { margin: 4px 0 0; padding-left: 20px; }
.card { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 14px 16px; margin: 12px 0; }
.scroll { overflow-x: auto; max-width: 100%; }
table { border-collapse: collapse; width: 100%; font-size: .95rem; }
th, td { text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--border); vertical-align: top; }
th { background: var(--surface-2); font-weight: 600; white-space: nowrap; }
td.num, th.num { text-align: right; font-variant-numeric: tabular-nums; }
pre { background: var(--code-bg); border: 1px solid var(--border); border-radius: 6px; padding: 12px; overflow-x: auto; font-size: .88rem; line-height: 1.45; }
code { font-family: ui-monospace, "Cascadia Code", "SF Mono", Menlo, Consolas, "DejaVu Sans Mono", monospace; font-size: .92em; }
.pill { display: inline-block; padding: 1px 10px; border-radius: 999px; font-size: .8rem; font-weight: 600; border: 1px solid currentColor; white-space: nowrap; }
.pill.locked { color: var(--locked); }
.pill.in_progress { color: var(--warn); }
.pill.passed { color: var(--good); }
.pill.not_started { color: var(--locked); }
.pill.complete { color: var(--good); }
.pill.pending { color: var(--warn); }
.stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; }
.stat { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 12px 14px; }
.stat .k { color: var(--muted); font-size: .85rem; }
.stat .v { font-size: 1.6rem; font-weight: 650; font-variant-numeric: tabular-nums; }
.note { border-left: 3px solid var(--accent); background: var(--accent-soft); padding: 10px 14px; border-radius: 0 6px 6px 0; margin: 12px 0; }
.empty { color: var(--muted); font-style: italic; }
svg text { fill: var(--text-2); font-family: inherit; }
"""


def esc(s):
    return html.escape(str(s), quote=True)


def page(title, updated, toc, body, home_href="index.html", description=""):
    """Return a complete offline HTML page.

    toc: list of (anchor_id, label) tuples.
    """
    toc_items = "".join(f'<li><a href="#{esc(a)}">{esc(l)}</a></li>' for a, l in toc)
    home = "" if home_href is None else f'<a class="home" href="{esc(home_href)}">&larr; Back to dashboard (index.html)</a>'
    desc = f'<meta name="description" content="{esc(description)}">' if description else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
{desc}
<title>{esc(title)}</title>
<style>{CSS}</style>
</head>
<body>
<main>
{home}
<h1>{esc(title)}</h1>
<p class="meta">Last updated: {esc(updated)}</p>
<nav class="toc" aria-label="Contents"><strong>Contents</strong><ol>{toc_items}</ol></nav>
{body}
</main>
</body>
</html>
"""
