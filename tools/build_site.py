#!/usr/bin/env python3
"""Regenerate the dashboard (index.html) and interview/question-bank.html.

Inputs: progress/state.json, progress/scores.json, and the HTML files under
docs/, interview/ and progress/. Run at the end of every session:

    python3 tools/build_site.py
"""
import datetime as dt
import glob
import json
import os
import re

from sitekit import esc, page

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GATE = 2.5


def rel(p):
    return os.path.relpath(p, ROOT).replace(os.sep, "/")


def title_of(path):
    with open(path, encoding="utf-8") as f:
        m = re.search(r"<title>(.*?)</title>", f.read(4096), re.S | re.I)
    return m.group(1).strip() if m else os.path.basename(path)


def load(name):
    with open(os.path.join(ROOT, "progress", name)) as f:
        return json.load(f)


def module_averages(entries):
    by = {}
    for e in entries:
        if e["kind"] in ("oral", "mock", "repetition"):
            continue
        by.setdefault(e["module"], []).append(e["score"])
    return {m: (sum(s) / len(s), len(s)) for m, s in by.items()}


def bar_chart(modules, avgs):
    """Single-series bar chart of grill average per module, 0..3, with the 2.5 gate."""
    w, h = 700, 250
    left, right, top, bottom = 36, 12, 16, 40
    pw, ph = w - left - right, h - top - bottom
    slot = pw / len(modules)
    bw = min(30, slot * 0.6)
    y = lambda v: top + ph - (v / 3) * ph
    parts = [f'<svg viewBox="0 0 {w} {h}" width="100%" style="min-width:560px;max-width:{w}px" role="img" '
             f'aria-labelledby="chart-title"><title id="chart-title">Grill score average per module, 0 to 3</title>']
    for t in (0, 1, 2, 3):
        parts.append(f'<line x1="{left}" x2="{w-right}" y1="{y(t):.1f}" y2="{y(t):.1f}" '
                     f'stroke="var(--border)" stroke-width="1"/>'
                     f'<text x="{left-8}" y="{y(t)+4:.1f}" text-anchor="end" font-size="11">{t}</text>')
    parts.append(f'<line x1="{left}" x2="{w-right}" y1="{y(GATE):.1f}" y2="{y(GATE):.1f}" '
                 f'stroke="var(--warn)" stroke-width="1.5" stroke-dasharray="5 4"/>'
                 f'<text x="{w-right}" y="{y(GATE)-5:.1f}" text-anchor="end" font-size="11">gate 2.5</text>')
    for i, m in enumerate(modules):
        cx = left + slot * i + slot / 2
        parts.append(f'<text x="{cx:.1f}" y="{h-bottom+16}" text-anchor="middle" font-size="11">M{m["id"]}</text>')
        if m["id"] in avgs:
            v, n = avgs[m["id"]]
            yy = y(v)
            hh = max(top + ph - yy, 1)
            parts.append(f'<g><title>Module {m["id"]}: {v:.2f} average over {n} answers</title>'
                         f'<rect x="{cx-bw/2:.1f}" y="{yy:.1f}" width="{bw:.1f}" height="{hh:.1f}" rx="3" '
                         f'fill="var(--accent)"/>'
                         f'<rect x="{cx-slot/2:.1f}" y="{top}" width="{slot:.1f}" height="{ph}" fill="transparent"/></g>'
                         f'<text x="{cx:.1f}" y="{yy-5:.1f}" text-anchor="middle" font-size="11">{v:.1f}</text>')
        else:
            parts.append(f'<text x="{cx:.1f}" y="{top+ph-4}" text-anchor="middle" font-size="11" '
                         f'fill="var(--muted)">&ndash;</text>')
    parts.append(f'<text x="{left}" y="{h-6}" font-size="11">Bars: mean grill score (repetition, oral exams and mocks excluded). '
                 f'Dashed line: the mastery gate.</text></svg>')
    return '<div class="scroll">' + "".join(parts) + "</div>"


def docs_by_module(modules):
    groups = []
    general = [p for p in ("docs/syllabus.html", "docs/handbook.html", "docs/glossary.html")
               if os.path.exists(os.path.join(ROOT, p))]
    groups.append(("Course-wide", [(p, title_of(os.path.join(ROOT, p))) for p in general]))
    for m in modules:
        files = sorted(glob.glob(os.path.join(ROOT, "docs", m["slug"], "*.html")))
        groups.append((f'Module {m["id"]} &mdash; {esc(m["title"])}', [(rel(f), title_of(f)) for f in files]))
    for label, pattern in (("Interview", "interview/*.html"), ("Mock interviews", "interview/mock-transcripts/*.html"),
                           ("Progress", "progress/*.html")):
        files = sorted(glob.glob(os.path.join(ROOT, pattern)))
        groups.append((label, [(rel(f), title_of(f)) for f in files]))
    return groups


def build_index(state, scores, today):
    start = dt.date.fromisoformat(scores["course_start"])
    week = max(1, (today - start).days // 7 + 1)
    modules = state["modules"]
    labs = state["labs"]
    avgs = module_averages(scores["entries"])
    done = sum(1 for l in labs if l["status"] == "complete")
    current = next((m for m in modules if m["status"] == "in_progress"), None)
    all_scores = [e["score"] for e in scores["entries"] if e["kind"] not in ("oral", "mock", "repetition")]
    overall = f"{sum(all_scores)/len(all_scores):.2f}" if all_scores else "&ndash;"
    queue = sorted(scores["repetition_queue"], key=lambda q: q["next_due"])
    due_now = sum(1 for q in queue if dt.date.fromisoformat(q["next_due"]) <= today)

    stats = f"""<div class="stats">
<div class="stat"><div class="k">Week</div><div class="v">{week} / 16</div></div>
<div class="stat"><div class="k">Current module</div><div class="v">{('M' + str(current['id'])) if current else '&ndash;'}</div></div>
<div class="stat"><div class="k">Labs complete</div><div class="v">{done} / {len(labs)}</div></div>
<div class="stat"><div class="k">Overall grill avg</div><div class="v">{overall}</div></div>
<div class="stat"><div class="k">Repetition due now</div><div class="v">{due_now}</div></div>
</div>
<p class="meta">Labs counted are those defined so far; later modules add more as they unlock.</p>"""

    label = {"locked": "locked", "in_progress": "in progress", "passed": "passed"}
    rows = []
    for m in modules:
        a = avgs.get(m["id"])
        avg = f"{a[0]:.2f} ({a[1]})" if a else "&ndash;"
        rows.append(f'<tr><td class="num">{m["id"]}</td><td>{esc(m["title"])}</td><td>{esc(m["weeks"])}</td>'
                    f'<td><span class="pill {m["status"]}">{label[m["status"]]}</span></td><td class="num">{avg}</td></tr>')
    module_table = ('<div class="scroll"><table><thead><tr><th class="num">#</th><th>Module</th><th>Weeks</th>'
                    '<th>Status</th><th class="num">Grill avg (n)</th></tr></thead><tbody>'
                    + "".join(rows) + "</tbody></table></div>")

    lab_rows = "".join(
        f'<tr><td><a href="labs/{esc(l["id"])}/README.md">{esc(l["id"])}</a></td><td class="num">{l["module"]}</td>'
        f'<td>{esc(l["title"])}</td><td><span class="pill {l["status"]}">{l["status"].replace("_", " ")}</span></td></tr>'
        for l in labs)
    lab_table = ('<div class="scroll"><table><thead><tr><th>Lab</th><th class="num">Module</th><th>What it proves</th>'
                 '<th>Status</th></tr></thead><tbody>' + lab_rows + "</tbody></table></div>")

    if queue:
        qrows = "".join(
            f'<tr><td>{esc(q["next_due"])}{" <strong>(due)</strong>" if dt.date.fromisoformat(q["next_due"]) <= today else ""}</td>'
            f'<td class="num">{q["module"]}</td><td>{esc(q["topic"])}</td><td class="num">{q["streak"]} / 2</td></tr>'
            for q in queue)
        queue_html = ('<div class="scroll"><table><thead><tr><th>Due</th><th class="num">Module</th><th>Topic</th>'
                      '<th class="num">Streak of 3s</th></tr></thead><tbody>' + qrows + "</tbody></table></div>")
    else:
        queue_html = '<p class="empty">Queue is empty. Nothing has scored below 3 yet, because nothing has been graded yet.</p>'

    groups = []
    for label_, files in docs_by_module(modules):
        items = "".join(f'<li><a href="{esc(p)}">{esc(t)}</a> <span class="meta">{esc(p)}</span></li>' for p, t in files)
        groups.append(f'<h3>{label_}</h3>' + (f"<ul>{items}</ul>" if items else '<p class="empty">No documents yet.</p>'))

    body = f"""
<p>Sixteen-week course in embedded systems security and secure boot. Contract: <code>CLAUDE.md</code>.
Plan: <a href="docs/syllabus.html">syllabus</a>.</p>
<h2 id="status">Status</h2>
{stats}
<h2 id="modules">Modules</h2>
<p>A module passes only when every lab runs, the grill average is at least 2.5, and the 20-question oral exam averages at least 2.5.</p>
{module_table}
<h2 id="scores">Grill average per module</h2>
{bar_chart(modules, avgs)}
<h2 id="queue">Spaced-repetition queue</h2>
<p>Anything scored below 3 comes back after 3, 10 and 30 days, until it scores 3 twice in a row.</p>
{queue_html}
<h2 id="labs">Labs</h2>
{lab_table}
<h2 id="documents">Documents</h2>
{''.join(groups)}
"""
    toc = [("status", "Status"), ("modules", "Modules"), ("scores", "Grill average per module"),
           ("queue", "Spaced-repetition queue"), ("labs", "Labs"), ("documents", "Documents")]
    return page("Secure Boot Bootcamp — Dashboard", today.isoformat(), toc, body, home_href=None,
                description="Live progress dashboard for the secure boot course.")


def build_question_bank(scores, today):
    entries = scores["entries"]
    by_mod = {}
    for e in entries:
        by_mod.setdefault(e["module"], []).append(e)
    toc = [("how", "How to use this bank")] + [(f"m{m}", f"Module {m}") for m in sorted(by_mod)]
    body = ['<h2 id="how">How to use this bank</h2><p>Every question asked in a grill, repetition check, '
            'oral exam or mock, with the score given and a model answer phrased the way a strong candidate '
            'would say it out loud. Practise by covering the model answer and answering aloud first.</p>'
            '<p>Scale: 0 = blank, 1 = wrong direction, 2 = right idea but missing detail, 3 = would pass an interview.</p>']
    if not by_mod:
        body.append('<p class="empty">No questions asked yet. The first grill is at the end of session 1.</p>')
    for m in sorted(by_mod):
        body.append(f'<h2 id="m{m}">Module {m}</h2>')
        for e in by_mod[m]:
            ans = esc(e.get("model_answer") or "Model answer to be written.")
            body.append(f'<div class="card"><p class="meta">{esc(e["date"])} &middot; {esc(e["kind"])} &middot; '
                        f'{esc(e["topic"])} &middot; score <strong>{e["score"]}/3</strong></p>'
                        f'<p><strong>Q.</strong> {esc(e["question"])}</p>'
                        f'<details><summary>Model answer</summary><p>{ans}</p></details></div>')
    return page("Interview Question Bank", today.isoformat(), toc, "".join(body), home_href="../index.html",
                description="Every question asked in the course, with scores and spoken-style model answers.")


def main():
    today = dt.date.today()
    state, scores = load("state.json"), load("scores.json")
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
        f.write(build_index(state, scores, today))
    with open(os.path.join(ROOT, "interview", "question-bank.html"), "w", encoding="utf-8") as f:
        f.write(build_question_bank(scores, today))
    print("wrote index.html and interview/question-bank.html")


if __name__ == "__main__":
    main()
