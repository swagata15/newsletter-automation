"""Build a copy-paste page of all local issues for Substack.

Usage: python tools/paste_desk/build.py tools/paste_desk/template.html paste-desk.html
Images are linked from the public GitHub repo at the current commit, so push first.
"""
import json, re, subprocess, sys, html
from pathlib import Path
from markdown_it import MarkdownIt
repo = Path(__file__).resolve().parents[2]
sha = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
RAW = f"https://raw.githubusercontent.com/swagata15/newsletter-automation/{sha}/"
md = MarkdownIt("commonmark").enable("table")
labels = {"weekly": "This Week in AI", "psychology": "AI and the Mind", "tutorial": "Weekend Build"}
issues = []
for h in sorted(json.load(open(repo / "history.json")), key=lambda x: x["date"]):
    folder = h["folder"]; text = (repo / folder / "issue.md").read_text()
    lines = text.split("\n")
    title = lines[0].lstrip("# ").strip()
    m = re.match(r"^\*(.*)\*$", lines[2].strip()); subtitle = m.group(1) if m else ""
    body = "\n".join(lines[4:]).strip()
    rendered = md.render(body)
    # image paragraphs -> <figure> with absolute GitHub URLs, plus a preview placeholder version
    def fig(mt, preview):
        src, alt, cap = mt.group(1), html.unescape(mt.group(2)), html.unescape(mt.group(3) or "")
        if preview:
            kind = "Cover image" if src.startswith("cover") else ("Photo" if src.endswith((".jpg", ".webp")) and not src.startswith("v") or "Photo:" in cap else "Image")
            label = html.escape(cap or alt)
            return f'<div class="ph"><span class="ph-k">{html.escape(src)}</span><span>{label}</span></div>'
        cap_html = f"<figcaption>{html.escape(cap)}</figcaption>" if cap else ""
        return f'<figure><img src="{RAW}{folder}/{html.escape(src)}" alt="{html.escape(alt)}">{cap_html}</figure>'
    pat = re.compile(r'<p><img src="([^"]+)" alt="([^"]*)"(?: title="([^"]*)")? /></p>')
    copy_html = pat.sub(lambda m: fig(m, False), rendered)
    preview_html = pat.sub(lambda m: fig(m, True), rendered)
    assert "<img" not in preview_html, folder
    issues.append({"date": h["date"], "type": h["type"], "label": labels[h["type"]], "title": title,
                   "subtitle": subtitle, "copy": copy_html, "preview": preview_html,
                   "images": copy_html.count("<img"), "words": len(re.sub("<[^>]+>", " ", copy_html).split()),
                   "folder": folder})
tpl = open(sys.argv[1]).read()
out = tpl.replace("__DATA__", json.dumps(issues).replace("</", "<\\/"))
Path(sys.argv[2]).write_text(out)
print(len(issues), "issues,", len(out)//1024, "KB, sha", sha[:7])
