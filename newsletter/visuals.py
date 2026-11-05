"""Turn Visual specs into image files: charts, diagrams, source images and a cover.

Look: newspaper graphics desk. Warm newsprint background, ink-black type, a muted
news palette, Roboto Slab headlines and Roboto labels (bundled in ./fonts).
"""

from __future__ import annotations

import logging
import re
import textwrap
from datetime import date
from html import unescape
from pathlib import Path
from urllib.parse import urljoin, urlparse

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import requests  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402

from .models import Visual  # noqa: E402

log = logging.getLogger(__name__)

# ---------------------------------------------------------------- theme
PAPER = "#F5F0E6"      # newsprint
CARD = "#FFFDF8"       # box fill on diagrams
INK = "#1A1A1A"
MUTED = "#5E5850"
RULE = "#D6CCBA"
NEWS_PALETTE = ["#1F3B57", "#A63A2B", "#2C6E6A", "#B98A2F", "#6E7B88", "#5E4A6B"]  # navy, brick, teal, ochre, slate, plum

FONT_DIR = Path(__file__).parent / "fonts"
for _f in FONT_DIR.glob("*.ttf"):
    font_manager.fontManager.addfont(str(_f))
SANS, SLAB = "Roboto", "Roboto Slab"
plt.rcParams.update({
    "font.family": SANS, "font.size": 11, "text.color": INK,
    "axes.edgecolor": RULE, "axes.labelcolor": MUTED, "xtick.color": INK, "ytick.color": INK,
    "axes.facecolor": PAPER, "figure.facecolor": PAPER, "savefig.facecolor": PAPER,
})

UA = {"User-Agent": "Mozilla/5.0 (compatible; newsletter-automation/1.0)"}
IMAGE_TYPES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp", "image/gif": ".gif"}


def _palette(accent: str) -> list[str]:
    # navy leads; the configured accent (default brick red) is the second series colour
    rest = [c for c in NEWS_PALETTE if c.lower() != accent.lower()]
    return [rest[0], accent] + rest[1:]


def _fmt(v: float, unit: str | None) -> str:
    s = f"{v:,.0f}" if abs(v) >= 100 or float(v).is_integer() else f"{v:,.1f}"
    return f"{s}{unit or ''}" if unit and len(unit) <= 2 else s


def _domain(url: str) -> str:
    return urlparse(url).netloc.removeprefix("www.")


def _header(fig, title: str, subtitle: str | None, accent: str) -> float:
    """Newspaper chart header: short accent rule, slab headline, sans dek. Returns y below it."""
    fig.add_artist(Rectangle((0.025, 0.955), 0.06, 0.012, transform=fig.transFigure, color=accent, lw=0))
    lines = textwrap.wrap(title, 62)
    fig.text(0.025, 0.93, "\n".join(lines), fontfamily=SLAB, fontweight="bold", fontsize=17, color=INK,
             va="top", linespacing=1.2)
    y = 0.93 - 0.068 * len(lines)
    if subtitle:
        fig.text(0.025, y, subtitle, fontsize=11.5, color=MUTED, va="top")
        y -= 0.06
    return y


def _footer(fig, v: Visual) -> None:
    fig.add_artist(Rectangle((0.025, 0.06), 0.95, 0.0015, transform=fig.transFigure, color=RULE, lw=0))
    credit = f"Source: {v.source_name}" + (f", {_domain(v.source_url)}" if v.source_url else "")
    fig.text(0.025, 0.025, credit, fontsize=9.5, color=MUTED)


# ---------------------------------------------------------------- charts
def render_chart(v: Visual, path: Path, accent: str) -> Path:
    cats, series = v.categories or [], v.series or []
    if not cats or not series or any(len(s.values) != len(cats) for s in series):
        raise ValueError("chart needs categories and one value per category in every series")

    colors = _palette(accent)
    kind = v.chart_type or ("hbar" if max(len(c) for c in cats) > 14 else "bar")
    if kind == "grouped_bar" and len(series) == 1:
        kind = "bar"
    height = 5.8 if kind != "hbar" else max(4.6, 0.6 * len(cats) * max(1, len(series) * 0.7) + 2.4)
    fig, ax = plt.subplots(figsize=(10, height), dpi=150)
    subtitle = v.y_label if kind != "line" else (v.y_label or None)
    top = _header(fig, v.chart_title or v.caption, subtitle, accent)

    if len(series) > 1:  # inline legend as coloured squares, like a print graphic
        x = 0.025
        for i, s in enumerate(series):
            fig.add_artist(Rectangle((x, top - 0.032), 0.014, 0.024, transform=fig.transFigure,
                                     color=colors[i % len(colors)], lw=0))
            t = fig.text(x + 0.02, top - 0.02, s.name, fontsize=10.5, color=INK, va="center")
            x += 0.05 + 0.0085 * len(s.name)
        top -= 0.06

    if kind == "line":
        for i, s in enumerate(series):
            c = colors[i % len(colors)]
            ax.plot(cats, s.values, lw=2.4, color=c, solid_capstyle="round")
            ax.plot(cats[-1], s.values[-1], "o", ms=5.5, color=c)
            ax.annotate(_fmt(s.values[-1], v.unit), (len(cats) - 1, s.values[-1]), xytext=(7, 0),
                        textcoords="offset points", va="center", fontsize=10.5, fontweight="bold", color=c)
        ax.grid(axis="y", color=RULE, lw=0.8)
        ax.set_axisbelow(True)
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
        ax.spines["bottom"].set_color(INK)
        ax.tick_params(axis="y", length=0, labelcolor=MUTED)
        ax.tick_params(axis="x", length=4, color=INK)
        ax.yaxis.set_major_formatter(lambda y, _: _fmt(y, v.unit))
    else:
        horizontal = kind == "hbar"
        n = len(series)
        w = 0.78 / n
        for i, s in enumerate(series):
            offs = [p + (i - (n - 1) / 2) * w for p in range(len(cats))]
            draw = ax.barh if horizontal else ax.bar
            bars = draw(offs, s.values, w * 0.88, color=colors[i % len(colors)], lw=0)
            ax.bar_label(bars, labels=[_fmt(x, v.unit) for x in s.values], padding=4, fontsize=10.5, color=INK)
        if horizontal:
            ax.set_yticks(range(len(cats)), [textwrap.fill(c, 26) for c in cats])
            ax.invert_yaxis()
            ax.xaxis.set_visible(False)
            for side in ("top", "right", "bottom"):
                ax.spines[side].set_visible(False)
            ax.spines["left"].set_color(INK)
        else:
            ax.set_xticks(range(len(cats)), [textwrap.fill(c, 14) for c in cats])
            ax.yaxis.set_visible(False)
            for side in ("top", "right", "left"):
                ax.spines[side].set_visible(False)
            ax.spines["bottom"].set_color(INK)
        ax.tick_params(length=0, labelsize=11)
        ax.margins(x=0.08 if horizontal else 0.02, y=0.12 if not horizontal else 0.02)

    _footer(fig, v)
    fig.tight_layout(rect=(0.0, 0.07, 1, top + 0.01))
    fig.savefig(path)
    plt.close(fig)
    return path


# ---------------------------------------------------------------- diagrams
def _split_back_edges(nodes: list[str], edges: list[tuple[str, str]]):
    """DFS from the entry nodes; edges pointing back up the current path are feedback loops."""
    out = {n: [b for a, b in edges if a == n] for n in nodes}
    indeg = {n: sum(1 for _, b in edges if b == n) for n in nodes}
    order = [n for n in nodes if indeg[n] == 0] + [n for n in nodes if indeg[n] > 0]
    state, back = {}, set()

    def dfs(n):
        state[n] = 1
        for m in out[n]:
            if state.get(m) == 1:
                back.add((n, m))
            elif m not in state:
                dfs(m)
        state[n] = 2

    for n in order:
        if n not in state:
            dfs(n)
    return [e for e in edges if e not in back], back


def _layers(nodes: list[str], forward: list[tuple[str, str]]) -> dict[str, int]:
    """Longest-path layering of the acyclic part, top to bottom."""
    layer = {n: 0 for n in nodes}
    for _ in range(len(nodes)):
        changed = False
        for a, b in forward:
            if layer[b] < layer[a] + 1:
                layer[b] = layer[a] + 1
                changed = True
        if not changed:
            break
    return layer


def render_diagram(v: Visual, path: Path, accent: str) -> Path:
    nodes = {n.id: n.label for n in (v.nodes or [])}
    edges = [(e.source, e.target, e.label) for e in (v.edges or []) if e.source in nodes and e.target in nodes]
    if len(nodes) < 2:
        raise ValueError("diagram needs at least two nodes")

    forward, back = _split_back_edges(list(nodes), [(a, b) for a, b, _ in edges])
    layer = _layers(list(nodes), forward)
    rows: dict[int, list[str]] = {}
    for n in nodes:
        rows.setdefault(layer[n], []).append(n)
    for r in sorted(rows)[1:]:  # order each row by its parents' positions to reduce crossings
        prev = {n: i for i, n in enumerate(rows[r - 1])} if r - 1 in rows else {}

        def bary(n, prev=prev):
            ps = [prev[a] for a, b in forward if b == n and a in prev]
            return sum(ps) / len(ps) if ps else len(prev)
        rows[r].sort(key=bary)
    widest = max(len(r) for r in rows.values())
    loops = [(a, b, l) for a, b, l in edges if (a, b) in back]

    box_w, box_h, gap_x, gap_y = 2.5, 0.8, 0.7, 0.95
    margin = (1.1 + 0.45 * len(loops)) if loops else 0.4
    width = max(widest * (box_w + gap_x) - gap_x, 6) + 2 * margin
    height = len(rows) * (box_h + gap_y) - gap_y + 0.5
    title_space = 0.9
    fig, ax = plt.subplots(figsize=(width * 0.85, (height + title_space) * 0.85), dpi=150)
    ax.set_position((0, 0, 1, height / (height + title_space)))
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.axis("off")
    fig.add_artist(Rectangle((0.03, 1 - 0.32 / (height + title_space)), 0.07, 0.07 / (height + title_space) * 1.2,
                             transform=fig.transFigure, color=accent, lw=0))
    if v.chart_title:
        fig.text(0.03, 1 - 0.45 / (height + title_space), v.chart_title, fontfamily=SLAB, fontweight="bold",
                 fontsize=15, color=INK, va="top")

    pos = {}
    for r, ids in rows.items():
        y = height - 0.25 - r * (box_h + gap_y) - box_h / 2
        span = len(ids) * box_w + (len(ids) - 1) * gap_x
        x0 = (width - span) / 2
        for i, n in enumerate(ids):
            pos[n] = (x0 + i * (box_w + gap_x) + box_w / 2, y)

    arrow = dict(arrowstyle="-|>", color=INK, lw=1.2, mutation_scale=13, shrinkA=1, shrinkB=1)

    def edge_label(x, y, text):
        if text:
            ax.text(x, y, textwrap.fill(text, 16), fontsize=9, color=MUTED, ha="center",
                    va="center", bbox=dict(boxstyle="square,pad=0.15", fc=PAPER, ec="none"), zorder=4)

    right_edge = max(x for x, _ in pos.values()) + box_w / 2
    left_edge = min(x for x, _ in pos.values()) - box_w / 2
    centre = (left_edge + right_edge) / 2
    used = {True: 0, False: 0}
    for a, b, label in sorted(loops, key=lambda e: abs(pos[e[0]][1] - pos[e[1]][1])):
        # feedback loop: out of the side nearest the source, along an outer lane, back in at the target
        (xa, ya), (xb, yb) = pos[a], pos[b]
        right = xa >= centre if abs(xa - centre) > 1e-6 else used[True] <= used[False]
        k = used[right]
        used[right] += 1
        lane = right_edge + 0.55 + 0.45 * k if right else left_edge - 0.55 - 0.45 * k
        sa = xa + box_w / 2 if right else xa - box_w / 2
        sb = xb + box_w / 2 if right else xb - box_w / 2
        ax.plot([sa, lane, lane], [ya, ya, yb], color=MUTED, lw=1.1, ls=(0, (3, 2.5)), zorder=1)
        ax.annotate("", xy=(sb, yb), xytext=(lane, yb), arrowprops={**arrow, "color": MUTED, "linestyle": (0, (3, 2.5))})
        edge_label(lane, (ya + yb) / 2, label)

    for a, b, label in edges:
        if (a, b) in back:
            continue
        (xa, ya), (xb, yb) = pos[a], pos[b]
        if abs(ya - yb) < 1e-6:
            d = 1 if xa < xb else -1
            start, end = (xa + d * box_w / 2, ya), (xb - d * box_w / 2, yb)
        else:
            start, end = (xa, ya - box_h / 2), (xb, yb + box_h / 2)
        ax.annotate("", xy=end, xytext=start, arrowprops=arrow)
        edge_label((start[0] + end[0]) / 2, (start[1] + end[1]) / 2, label)

    first_row = set(rows.get(0, []))
    navy = NEWS_PALETTE[0]
    for n, (x, y) in pos.items():
        entry = n in first_row
        ax.add_patch(FancyBboxPatch((x - box_w / 2, y - box_h / 2), box_w, box_h,
                                    boxstyle="square,pad=0", fc=navy if entry else CARD,
                                    ec=navy if entry else INK, lw=1.1, zorder=3))
        ax.text(x, y, textwrap.fill(nodes[n], 22), ha="center", va="center", fontsize=10.5,
                fontweight="medium", color="white" if entry else INK, zorder=5)

    fig.savefig(path)
    plt.close(fig)
    return path


# ---------------------------------------------------------------- source images
_META = re.compile(r"<meta\s+[^>]*>", re.IGNORECASE)


def _og_image(page_html: str, base: str) -> str | None:
    for tag in _META.findall(page_html):
        key = re.search(r'(?:property|name)\s*=\s*["\']([^"\']+)["\']', tag, re.I)
        val = re.search(r'content\s*=\s*["\']([^"\']+)["\']', tag, re.I)
        if key and val and key.group(1).lower() in ("og:image", "og:image:url", "og:image:secure_url", "twitter:image", "twitter:image:src"):
            return urljoin(base, unescape(val.group(1)))
    return None


def fetch_source_image(page_url: str, path_stem: Path) -> Path:
    """Download the preview image (og:image) of a page, or the URL itself if it is an image."""
    if not page_url.startswith("http"):
        raise ValueError("no source URL")
    gh = re.match(r"https?://github\.com/([^/]+)/([^/#?]+)", page_url)
    if gh:  # GitHub's social card for a repo
        image_url = f"https://opengraph.githubassets.com/1/{gh.group(1)}/{gh.group(2)}"
    else:
        resp = requests.get(page_url, headers=UA, timeout=20)
        resp.raise_for_status()
        ctype = resp.headers.get("content-type", "").split(";")[0]
        if ctype in IMAGE_TYPES:
            image_url = page_url
        else:
            image_url = _og_image(resp.text[:300_000], resp.url)
            if not image_url:
                raise ValueError(f"no preview image on {page_url}")

    img = requests.get(image_url, headers=UA, timeout=30)
    img.raise_for_status()
    ctype = img.headers.get("content-type", "").split(";")[0]
    if ctype not in IMAGE_TYPES or len(img.content) < 5_000:
        raise ValueError(f"not a usable image ({ctype}, {len(img.content)} bytes)")
    path = path_stem.with_suffix(IMAGE_TYPES[ctype])
    path.write_bytes(img.content)
    return path


# ---------------------------------------------------------------- cover
def render_cover(title: str, label: str, newsletter: str, path: Path, accent: str,
                 issue_date: date | None = None) -> Path:
    """A print-style section front: masthead rules, kicker, slab headline, dateline."""
    issue_date = issue_date or date.today()
    fig = plt.figure(figsize=(11.2, 5.6), dpi=150)
    ax = fig.add_axes((0, 0, 1, 1))
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # masthead
    ax.add_patch(Rectangle((0.06, 0.885), 0.88, 0.006, color=INK, lw=0))
    ax.add_patch(Rectangle((0.06, 0.872), 0.88, 0.0015, color=INK, lw=0))
    ax.text(0.06, 0.915, newsletter.upper(), fontfamily=SLAB, fontweight="bold", fontsize=13, color=INK,
            va="bottom")
    ax.text(0.94, 0.915, f"{issue_date:%A, %B} {issue_date.day}, {issue_date:%Y}", fontsize=11, color=MUTED,
            va="bottom", ha="right")

    # kicker + headline
    ax.add_patch(Rectangle((0.06, 0.765), 0.012, 0.05, color=accent, lw=0))
    ax.text(0.082, 0.79, label.upper(), fontsize=13, fontweight="bold", color=accent, va="center")
    lines = textwrap.wrap(title, 30 if len(title) > 60 else 26)
    size = 38 if len(lines) <= 2 else 32 if len(lines) == 3 else 27
    ax.text(0.06, 0.72, "\n".join(lines), fontfamily=SLAB, fontweight="bold", fontsize=size, color=INK,
            va="top", linespacing=1.12)

    # footer rule
    ax.add_patch(Rectangle((0.06, 0.09), 0.88, 0.0015, color=RULE, lw=0))
    fig.savefig(path)
    plt.close(fig)
    return path
