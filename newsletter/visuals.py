"""The graphics desk: every visual in the newsletter, drawn to the brand kit in BRAND.md.

Concept: "the marked-up printout". Ink on newsprint, grey-first data, one highlighter
swipe on what matters, one red-pen margin note, a coloured section tab, duotone photos.
"""

from __future__ import annotations

import logging
import re
import textwrap
from dataclasses import dataclass, field
from datetime import date
from html import unescape
from pathlib import Path
from urllib.parse import urljoin, urlparse

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import requests  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.colors import to_rgb  # noqa: E402
from matplotlib.patches import Circle, FancyBboxPatch, Polygon, Rectangle  # noqa: E402

from .models import Visual  # noqa: E402

log = logging.getLogger(__name__)

# ---------------------------------------------------------------- fonts
FONT_DIR = Path(__file__).parent / "fonts"
for _f in FONT_DIR.glob("*.ttf"):
    font_manager.fontManager.addfont(str(_f))
SANS, SLAB, COND, MONO, HAND = "Roboto", "Roboto Slab", "Roboto Condensed", "Roboto Mono", "Caveat"
plt.rcParams.update({"font.family": SANS, "font.size": 11, "axes.unicode_minus": False})

WIDTH_IN, DPI = 10.0, 150  # 1500 px wide, crisp in Substack's 728 px column on retina screens
UA = {"User-Agent": "Mozilla/5.0 (compatible; newsletter-automation/1.0)"}
IMAGE_TYPES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp", "image/gif": ".gif"}


@dataclass
class Theme:
    newsletter: str = "Swagata Ashwani"
    author: str = ""
    section: str = "This Week in AI"
    section_color: str = "#1B3A5C"
    paper: str = "#F4EFE6"
    card: str = "#FBF8F2"
    ink: str = "#161616"
    primary: str = "#1B3A5C"
    pencil: str = "#BDB4A5"
    graphite: str = "#6A645B"
    rule: str = "#D9D0C1"
    highlighter: str = "#F5D547"
    red_pen: str = "#C23B22"
    series: list[str] = field(default_factory=lambda: ["#1B3A5C", "#3A7D7C", "#C9973B", "#6A3B5A"])
    duotone_photos: bool = True

    @classmethod
    def from_config(cls, config: dict, kind: str) -> "Theme":
        brand = {k: v for k, v in (config.get("brand") or {}).items() if k in cls.__dataclass_fields__}
        issue = config["issues"][kind]
        return cls(newsletter=config["newsletter"]["name"], author=config["newsletter"].get("author", ""),
                   section=issue.get("label", kind),
                   section_color=issue.get("color", brand.get("primary", "#1B3A5C")), **brand)


# ---------------------------------------------------------------- shared devices
def _new_fig(t: Theme, height_in: float):
    fig = plt.figure(figsize=(WIDTH_IN, height_in), dpi=DPI)
    fig.patch.set_facecolor(t.paper)
    _grain(fig, t)
    return fig


def _grain(fig, t: Theme) -> None:
    """Very faint paper grain so graphics feel printed, not rendered."""
    w, h = int(fig.get_figwidth() * DPI), int(fig.get_figheight() * DPI)
    rng = np.random.default_rng(7)
    base = np.array(to_rgb(t.paper))
    noise = rng.normal(0, 0.012, (h, w, 1))
    fig.figimage(np.clip(base + noise, 0, 1), xo=0, yo=0, zorder=-10, origin="upper")


def _text_box(fig, artist):
    """Bounding box of a drawn text artist, in figure fraction coordinates."""
    r = fig.canvas.get_renderer()
    return artist.get_window_extent(renderer=r).transformed(fig.transFigure.inverted())


def _highlight(fig, t: Theme, x0, y0, x1, y1, seed=1, ax=None) -> None:
    """A slightly uneven highlighter stroke (figure coordinates), drawn behind text."""
    rng = np.random.default_rng(seed)
    h = y1 - y0
    x0, x1, y0, y1 = x0 - 0.006, x1 + 0.006, y0 + h * 0.06, y1 - h * 0.1
    n = 8
    xs = np.linspace(x0, x1, n)
    top = y1 + rng.normal(0, h * 0.04, n)
    bot = y0 + rng.normal(0, h * 0.04, n)
    pts = list(zip(xs, top)) + [(x1 + 0.004, (y0 + y1) / 2)] + list(zip(xs[::-1], bot[::-1])) + [(x0 - 0.003, (y0 + y1) / 2)]
    poly = Polygon(pts, closed=True, transform=fig.transFigure, fc=t.highlighter, ec="none", alpha=0.85,
                   zorder=3.5 if ax is not None else 0.5, clip_on=False)
    (ax.add_artist if ax is not None else fig.add_artist)(poly)


def _highlight_text(fig, t: Theme, artist, seed=1, ax=None) -> None:
    bb = _text_box(fig, artist)
    _highlight(fig, t, bb.x0, bb.y0, bb.x1, bb.y1, seed, ax)


def _tab(fig, t: Theme, x=0.035, y=0.93) -> float:
    """Coloured index tab with the series name. Returns the y just below it."""
    txt = fig.text(x + 0.012, y, t.section.upper(), fontfamily=COND, fontweight="bold", fontsize=10.5,
                   color="white", va="center", zorder=3)
    bb = _text_box(fig, txt)
    pad_y = 0.09 / fig.get_figheight()
    fig.add_artist(Rectangle((x, bb.y0 - pad_y), bb.width + 0.024, bb.height + 2 * pad_y,
                             transform=fig.transFigure, fc=t.section_color, ec="none", zorder=2))
    return bb.y0 - pad_y - 0.22 / fig.get_figheight()


def _headline(fig, t: Theme, title: str, y: float, subtitle: str | None = None, width=58, size=19) -> float:
    lines = textwrap.wrap(title, width)
    txt = fig.text(0.035, y, "\n".join(lines), fontfamily=SLAB, fontweight="bold", fontsize=size,
                   color=t.ink, va="top", linespacing=1.15)
    y = _text_box(fig, txt).y0 - 0.12 / fig.get_figheight()
    if subtitle:
        s = fig.text(0.035, y, subtitle, fontsize=12, color=t.graphite, va="top")
        y = _text_box(fig, s).y0 - 0.15 / fig.get_figheight()
    return y


def _source_line(fig, t: Theme, name: str, url: str = "") -> None:
    fh = fig.get_figheight()
    fig.add_artist(Rectangle((0.035, 0.42 / fh), 0.93, 0.008 / fh, transform=fig.transFigure, color=t.rule, lw=0))
    dom = urlparse(url).netloc.removeprefix("www.") if url else ""
    bits = [b for b in (name, dom) if b]
    if bits:
        fig.text(0.035, 0.2 / fh, "SOURCE · " + " · ".join(bits), fontfamily=MONO, fontweight="medium", fontsize=8.5, color=t.graphite)
    extra = t.author and t.author.strip().lower() != t.newsletter.strip().lower()
    sign = t.newsletter.upper() + (f"  ·  {t.author.upper()}" if extra else "")
    fig.text(0.965, 0.2 / fh, sign, fontfamily=COND, fontweight="bold", fontsize=9, color=t.graphite, ha="right")


def _pen_note(ax, t: Theme, text: str, target, dx=0.0, dy=0.0, rad=-0.3, text_pos=None, ha="center"):
    """Handwritten red-pen margin note with a hand-drawn arrow to `target` (data coords).

    The note sits at an offset (dx, dy, in axes fractions) from the target, kept inside the plot."""
    if text_pos is None:
        tx, ty = ax.transAxes.inverted().transform(ax.transData.transform(target))
        text_pos = (min(max(tx + dx, 0.14), 0.86), min(max(ty + dy, 0.1), 0.92))
    ann = ax.annotate(
        textwrap.fill(text, 22), xy=target, xycoords="data", xytext=text_pos, textcoords="axes fraction",
        fontfamily=HAND, fontweight="bold", fontsize=18, color=t.red_pen, ha=ha, va="center",
        linespacing=0.95, zorder=6, annotation_clip=False,
        arrowprops=dict(arrowstyle="-|>,head_length=0.6,head_width=0.3", color=t.red_pen, lw=1.8,
                        connectionstyle=f"arc3,rad={rad}", shrinkA=10, shrinkB=8),
    )
    ann.arrow_patch.set_sketch_params(scale=0.9, length=80, randomness=8)
    return ann


def _fmt(v: float, unit: str | None) -> str:
    """Show values with the precision the source used (up to 2 decimals), never rounded away."""
    s = f"{v:,.0f}" if float(v).is_integer() else f"{v:,.2f}".rstrip("0").rstrip(".")
    return f"{s}{unit}" if unit and len(unit) <= 2 else s


def _fade(hex_colour: str, t: Theme, amount=0.6) -> tuple:
    c, p = np.array(to_rgb(hex_colour)), np.array(to_rgb(t.paper))
    return tuple(c * (1 - amount) + p * amount)


def _save(fig, path: Path) -> Path:
    fig.savefig(path, facecolor=fig.get_facecolor())
    plt.close(fig)
    return path


# ---------------------------------------------------------------- charts
def render_chart(v: Visual, path: Path, t: Theme) -> Path:
    cats, series = v.categories or [], v.series or []
    if not cats or not series or any(len(s.values) != len(cats) for s in series):
        raise ValueError("chart needs categories and one value per category in every series")
    kind = v.chart_type or ("hbar" if max(len(c) for c in cats) > 14 else "bar")
    if kind == "grouped_bar" and len(series) == 1:
        kind = "bar"
    hi = cats.index(v.highlight) if v.highlight in cats else None
    multi = len(series) > 1

    plot_h = 3.4 if kind != "hbar" else max(2.4, 0.48 * len(cats) * (1 + 0.6 * (len(series) - 1)))
    fig_h = plot_h + 2.6
    fig = _new_fig(t, fig_h)
    y = _tab(fig, t)
    y = _headline(fig, t, v.chart_title or v.caption, y, v.y_label)

    if multi:  # print-style legend: coloured squares
        x = 0.035
        for i, s in enumerate(series):
            fig.add_artist(Rectangle((x, y - 0.2 / fig_h), 0.013, 0.15 / fig_h, transform=fig.transFigure,
                                     color=t.series[i % len(t.series)], lw=0))
            lab = fig.text(x + 0.02, y - 0.125 / fig_h, s.name, fontsize=11, color=t.ink, va="center")
            x = _text_box(fig, lab).x1 + 0.03
        y -= 0.4 / fig_h

    left = 0.035 if kind != "hbar" else 0.27
    ax = fig.add_axes((left, 0.75 / fig_h, 0.965 - left - 0.02, y - 0.85 / fig_h))
    ax.set_facecolor("none")

    def colour(si, ci):
        if multi:
            c = t.series[si % len(t.series)]
            return c if hi is None or ci == hi else _fade(c, t)
        if hi is None:
            return t.primary
        return t.primary if ci == hi else t.pencil

    target = None
    if kind == "line":
        for i, s in enumerate(series):
            c = t.series[i % len(t.series)] if multi else t.primary
            ax.plot(range(len(cats)), s.values, lw=2.6, color=c, solid_capstyle="round", zorder=3)
            ax.plot(len(cats) - 1, s.values[-1], "o", ms=6, color=c, zorder=4)
            ax.annotate(_fmt(s.values[-1], v.unit), (len(cats) - 1, s.values[-1]), xytext=(8, 0),
                        textcoords="offset points", va="center", fontsize=11.5, fontweight="bold", color=c)
        ax.set_xticks(range(len(cats)), cats)
        ax.grid(axis="y", color=t.rule, lw=0.8)
        ax.set_axisbelow(True)
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
        ax.spines["bottom"].set_color(t.ink)
        ax.tick_params(axis="y", length=0, labelcolor=t.graphite, labelsize=10.5)
        ax.tick_params(axis="x", length=4, color=t.ink, labelsize=11, labelcolor=t.ink)
        ax.yaxis.set_major_formatter(lambda val, _: _fmt(val, v.unit))
        ti = hi if hi is not None else len(cats) - 1
        target = (ti, max(s.values[ti] for s in series))
        ax.margins(x=0.06, y=0.2)
    else:
        horizontal = kind == "hbar"
        n = len(series)
        w = 0.78 / n
        value_labels = []
        for i, s in enumerate(series):
            offs = [p + (i - (n - 1) / 2) * w for p in range(len(cats))]
            cols = [colour(i, c) for c in range(len(cats))]
            bars = (ax.barh if horizontal else ax.bar)(offs, s.values, w * 0.86, color=cols, lw=0, zorder=3)
            value_labels.append(ax.bar_label(bars, labels=[_fmt(x, v.unit) for x in s.values], padding=6,
                                             fontsize=12, color=t.ink, fontweight="bold", zorder=4))
            if hi is not None and i == 0:
                target = ((s.values[hi] * 0.8, offs[hi] + w * 0.43) if horizontal
                          else (offs[hi] + (-1 if hi > (len(cats) - 1) / 2 else 1) * w * 0.43, s.values[hi] * 0.85))
        if horizontal:
            ax.set_yticks(range(len(cats)), [textwrap.fill(c, 28) for c in cats])
            ax.invert_yaxis()
            ax.xaxis.set_visible(False)
            for side in ("top", "right", "bottom"):
                ax.spines[side].set_visible(False)
            ax.spines["left"].set_color(t.ink)
            ax.margins(x=0.75 if v.annotation else 0.1, y=0.03)
        else:
            ax.set_xticks(range(len(cats)), [textwrap.fill(c, max(14, 60 // len(cats))) for c in cats])
            ax.yaxis.set_visible(False)
            for side in ("top", "right", "left"):
                ax.spines[side].set_visible(False)
            ax.spines["bottom"].set_color(t.ink)
            ax.margins(x=0.03, y=0.55 if v.annotation else 0.12)
        ax.tick_params(length=0, labelsize=11.5, labelcolor=t.ink)
        if hi is not None:
            fig.canvas.draw()
            for lab in (ax.get_yticklabels() if horizontal else ax.get_xticklabels()):
                if lab.get_text().replace("\n", " ") == cats[hi]:
                    lab.set_fontweight("bold")
            _highlight_text(fig, t, value_labels[0][hi], seed=3, ax=ax)

    if v.annotation and target is not None:
        fig.canvas.draw()
        tx, _ = ax.transAxes.inverted().transform(ax.transData.transform(target))
        side = -1 if tx > 0.55 else 1  # write the note on the roomier side
        if kind == "hbar":
            lab = _text_box(fig, value_labels[0][hi])  # figure coords of the highlighted value label
            disp = fig.transFigure.transform((lab.x1, (lab.y0 + lab.y1) / 2))
            tgt = tuple(ax.transData.inverted().transform(disp))
            ax_x, ax_y = ax.transAxes.inverted().transform(disp)
            _pen_note(ax, t, v.annotation, tgt, rad=0.0, ha="left",
                      text_pos=(ax_x + 0.07, min(max(ax_y, 0.08), 0.92)))
        elif kind == "line":
            _pen_note(ax, t, v.annotation, target, dx=side * 0.24, dy=0.2, rad=0.3 * side)
        else:
            tallest = max(x for ser in series for x in ser.values)
            top_frac = ax.transAxes.inverted().transform(ax.transData.transform((0, tallest)))[1]
            _, ty = ax.transAxes.inverted().transform(ax.transData.transform(target))
            _pen_note(ax, t, v.annotation, target, rad=0.3 * side,
                      text_pos=(min(max(tx + side * 0.24, 0.14), 0.86), min(max(ty + 0.3, top_frac + 0.16), 0.93)))

    _source_line(fig, t, v.source_name, v.source_url)
    return _save(fig, path)


# ---------------------------------------------------------------- big-number stat card
def render_stat(v: Visual, path: Path, t: Theme) -> Path:
    stats = (v.stats or [])[:3]
    if not stats:
        raise ValueError("stat card needs at least one stat")
    longest = max(len(s.label) for s in stats) / {1: 60, 2: 34, 3: 24}[len(stats)]
    fig_h = (3.5 if v.chart_title else 2.9) + 0.25 * min(int(longest), 3)
    fig = _new_fig(t, fig_h)
    y = _tab(fig, t)
    if v.chart_title:
        y = _headline(fig, t, v.chart_title, y, size=16, width=70)
    n = len(stats)
    col_w = 0.93 / n
    for i, s in enumerate(stats):
        x = 0.035 + i * col_w
        if i:
            fig.add_artist(Rectangle((x - 0.015, 0.7 / fig_h), 0.0012, y - 0.8 / fig_h, transform=fig.transFigure,
                                     color=t.rule, lw=0))
        size = 66 if n == 1 else 54 if n == 2 else 44
        num = fig.text(x + 0.004, y - 0.08 / fig_h, s.value, fontfamily=SLAB, fontweight="bold", fontsize=size,
                       color=t.ink, va="top", zorder=3)
        if i == 0:
            _highlight_text(fig, t, num, seed=11)
        nb = _text_box(fig, num)
        fig.text(x + 0.004, nb.y0 - 0.2 / fig_h, textwrap.fill(s.label, {1: 60, 2: 34, 3: 24}[n]),
                 fontsize=13.5 if n < 3 else 12.5, color=t.ink, va="top", linespacing=1.3)
    _source_line(fig, t, v.source_name, v.source_url)
    return _save(fig, path)


# ---------------------------------------------------------------- pictogram: 100 people
def _person(ax, x, y, colour, s=1.0):
    ax.add_patch(Circle((x, y + 0.24 * s), 0.13 * s, fc=colour, ec="none"))
    ax.add_patch(FancyBboxPatch((x - 0.21 * s, y - 0.34 * s), 0.42 * s, 0.42 * s,
                                boxstyle=f"round,pad=0,rounding_size={0.18 * s}", fc=colour, ec="none"))


def render_waffle(v: Visual, path: Path, t: Theme) -> Path:
    if v.waffle_value is None or not 0 <= v.waffle_value <= 100:
        raise ValueError("waffle needs a percentage between 0 and 100")
    k = int(round(v.waffle_value))
    fig_h = 5.6
    fig = _new_fig(t, fig_h)
    y = _tab(fig, t)
    if v.chart_title:
        y = _headline(fig, t, v.chart_title, y, size=17, width=64)

    num = fig.text(0.035, y - 0.3 / fig_h, f"{v.waffle_value:g}%", fontfamily=SLAB, fontweight="bold",
                   fontsize=60, color=t.ink, va="top", zorder=3)
    _highlight_text(fig, t, num, seed=5)
    nb = _text_box(fig, num)
    fig.text(0.035, nb.y0 - 0.2 / fig_h, textwrap.fill(v.waffle_label or "", 24), fontsize=15, color=t.ink,
             va="top", linespacing=1.3)
    fig.text(0.035, 0.7 / fig_h, "Each figure is 1 in 100.", fontsize=10, color=t.graphite)

    ax = fig.add_axes((0.42, 0.6 / fig_h, 0.56, y - 0.62 / fig_h))
    pitch = 1.3
    ax.set_xlim(-0.6, 9.6)
    ax.set_ylim(-0.6, 9 * pitch + 0.55)
    ax.set_aspect("equal")
    ax.axis("off")
    for idx in range(100):
        r, c = divmod(idx, 10)
        _person(ax, c, (9 - r) * pitch, t.section_color if idx < k else t.pencil, s=1.15)
    _source_line(fig, t, v.source_name, v.source_url)
    return _save(fig, path)


# ---------------------------------------------------------------- pull quote
def render_quote(v: Visual, path: Path, t: Theme) -> Path:
    if not v.quote_text:
        raise ValueError("quote needs text")
    text = v.quote_text.strip().strip('"“”')
    lines = textwrap.wrap(text, 44)
    fig_h = 2.9 + 0.5 * len(lines)
    fig = _new_fig(t, fig_h)
    y = _tab(fig, t)
    fig.text(0.03, y + 0.15 / fig_h, "“", fontfamily=SLAB, fontweight="bold", fontsize=96,
             color=t.section_color, va="top")
    q = fig.text(0.115, y - 0.2 / fig_h, "\n".join(lines), fontfamily=SLAB, fontsize=23, color=t.ink, va="top",
                 linespacing=1.35)
    qb = _text_box(fig, q)
    fig.add_artist(Rectangle((0.115, qb.y0 - 0.3 / fig_h), 0.05, 0.025 / fig_h, transform=fig.transFigure,
                             color=t.ink, lw=0))
    fig.text(0.115, qb.y0 - 0.42 / fig_h, (v.quote_author or v.source_name or "").upper(), fontfamily=COND,
             fontweight="bold", fontsize=11.5, color=t.ink, va="top")
    _source_line(fig, t, v.source_name, v.source_url)
    return _save(fig, path)


# ---------------------------------------------------------------- timeline
def render_timeline(v: Visual, path: Path, t: Theme) -> Path:
    items = (v.timeline or [])[:8]
    if len(items) < 2:
        raise ValueError("timeline needs at least two items")
    fig_h = 2.5 + 0.72 * len(items)
    fig = _new_fig(t, fig_h)
    y = _tab(fig, t)
    if v.chart_title:
        y = _headline(fig, t, v.chart_title, y, size=17, width=64)
    top, bottom = y - 0.3 / fig_h, 0.95 / fig_h
    step = (top - bottom) / (len(items) - 1)
    line_x = 0.2
    fig.add_artist(Rectangle((line_x - 0.0012, bottom), 0.0024, top - bottom, transform=fig.transFigure,
                             color=t.ink, lw=0, zorder=1))
    for i, it in enumerate(items):
        yy = top - i * step
        fig.text(line_x - 0.025, yy, it.when.upper(), fontfamily=MONO, fontweight="medium", fontsize=10.5, color=t.section_color,
                 ha="right", va="center")
        dot = Circle((line_x * WIDTH_IN, yy * fig_h), 0.07, transform=fig.dpi_scale_trans, fc=t.paper, ec=t.ink,
                     lw=1.8, zorder=3)
        fig.add_artist(dot)
        title = fig.text(line_x + 0.03, yy, it.title, fontsize=14, fontweight="bold", color=t.ink,
                         va="bottom" if it.detail else "center", zorder=3)
        if i == 0:
            _highlight_text(fig, t, title, seed=9)
        if it.detail:
            fig.text(line_x + 0.03, yy - 0.06 / fig_h, textwrap.fill(it.detail, 82), fontsize=11, color=t.graphite,
                     va="top")
    _source_line(fig, t, v.source_name, v.source_url)
    return _save(fig, path)


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


def render_diagram(v: Visual, path: Path, t: Theme) -> Path:
    nodes = {n.id: n.label for n in (v.nodes or [])}
    edges = [(e.source, e.target, e.label) for e in (v.edges or []) if e.source in nodes and e.target in nodes]
    if len(nodes) < 2:
        raise ValueError("diagram needs at least two nodes")

    forward, back = _split_back_edges(list(nodes), [(a, b) for a, b, _ in edges])
    layer = _layers(list(nodes), forward)
    rows: dict[int, list[str]] = {}
    for n in nodes:
        rows.setdefault(layer[n], []).append(n)
    for r in sorted(rows)[1:]:
        prev = {n: i for i, n in enumerate(rows[r - 1])} if r - 1 in rows else {}

        def bary(n, prev=prev):
            ps = [prev[a] for a, b in forward if b == n and a in prev]
            return sum(ps) / len(ps) if ps else len(prev)
        rows[r].sort(key=bary)
    widest = max(len(r) for r in rows.values())
    loops = [(a, b, l) for a, b, l in edges if (a, b) in back]

    box_w, box_h, gap_x, gap_y = 2.5, 0.8, 0.8, 1.0
    margin = (2.0 + 0.5 * len(loops)) if loops else 0.5
    width = max(widest * (box_w + gap_x) - gap_x + 2 * margin, 9.5)
    below = 0.45 if loops else 0.0  # room for loops that run under the bottom row
    height = len(rows) * (box_h + gap_y) - gap_y + 0.4 + below
    scale = WIDTH_IN * 0.93 / width
    fig_h = height * scale + 2.0
    fig = _new_fig(t, fig_h)
    y = _tab(fig, t)
    y = _headline(fig, t, v.chart_title or v.caption, y, size=17, width=64)
    ax = fig.add_axes((0.035, 0.6 / fig_h, 0.93, y - 0.7 / fig_h))
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.axis("off")

    pos = {}
    for r, ids in rows.items():
        yy = height - 0.2 - r * (box_h + gap_y) - box_h / 2
        span = len(ids) * box_w + (len(ids) - 1) * gap_x
        x0 = (width - span) / 2
        for i, n in enumerate(ids):
            pos[n] = (x0 + i * (box_w + gap_x) + box_w / 2, yy)

    arrow = dict(arrowstyle="-|>,head_length=0.5,head_width=0.25", color=t.ink, lw=1.3, shrinkA=1, shrinkB=1)

    def mono_label(x, yy, text):
        if text:
            ax.text(x, yy, text.upper(), fontfamily=MONO, fontweight="medium", fontsize=8, color=t.graphite, ha="center", va="center",
                    bbox=dict(boxstyle="square,pad=0.2", fc=t.paper, ec="none"), zorder=4)

    right_edge = max(x for x, _ in pos.values()) + box_w / 2
    left_edge = min(x for x, _ in pos.values()) - box_w / 2
    centre = (left_edge + right_edge) / 2
    used = {True: 0, False: 0}
    for a, b, label in sorted(loops, key=lambda e: abs(pos[e[0]][1] - pos[e[1]][1])):
        # feedback loops are drawn by hand in red pen, out along an outer lane and back in
        (xa, ya), (xb, yb) = pos[a], pos[b]
        right = xa >= centre if abs(xa - centre) > 1e-6 else used[True] <= used[False]
        k = used[right]
        used[right] += 1
        lane = right_edge + 0.55 + 0.5 * k if right else left_edge - 0.55 - 0.5 * k
        sa = xa + box_w / 2 if right else xa - box_w / 2
        sb = xb + box_w / 2 if right else xb - box_w / 2
        blocked = any(abs(py - ya) < 1e-6 and n != a and ((px > xa) if right else (px < xa))
                      for n, (px, py) in pos.items())
        if blocked:  # a box sits between the source and the lane: leave from the bottom, run under the row
            drop = ya - box_h / 2 - 0.35
            xs_, ys_ = [xa, xa, lane, lane], [ya - box_h / 2, drop, drop, yb]
        else:  # clear path: leave from the side
            xs_, ys_ = [sa, lane, lane], [ya, ya, yb]
        (ln,) = ax.plot(xs_, ys_, color=t.red_pen, lw=1.7, zorder=1, solid_capstyle="round")
        ln.set_sketch_params(scale=1.2, length=50, randomness=20)
        ann = ax.annotate("", xy=(sb, yb), xytext=(lane, yb), arrowprops={**arrow, "color": t.red_pen, "lw": 1.7})
        ann.arrow_patch.set_sketch_params(scale=1.2, length=50, randomness=20)
        if label:
            ax.text(lane + (0.12 if right else -0.12), (ya + yb) / 2, textwrap.fill(label, 12), fontfamily=HAND,
                    fontweight="bold", fontsize=16, color=t.red_pen, ha="left" if right else "right",
                    va="center", zorder=4)

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
        mono_label((start[0] + end[0]) / 2, (start[1] + end[1]) / 2, label)

    first_row = set(rows.get(0, []))
    for n, (x, yy) in pos.items():
        entry = n in first_row
        ax.add_patch(FancyBboxPatch((x - box_w / 2, yy - box_h / 2), box_w, box_h, boxstyle="square,pad=0",
                                    fc=t.section_color if entry else t.card, ec=t.section_color if entry else t.ink,
                                    lw=1.2, zorder=3))
        ax.text(x, yy, textwrap.fill(nodes[n], 20), ha="center", va="center", fontsize=11, fontweight="medium",
                color="white" if entry else t.ink, zorder=5)

    _source_line(fig, t, "", "")
    return _save(fig, path)


# ---------------------------------------------------------------- photos
def duotone(src: Path, dst: Path, t: Theme, width_px=1500, aspect: float | None = None, tint: bool = True) -> Path:
    """Crop a photo to `aspect` (width/height) and re-ink it in the series colour on paper.

    The duotone is what makes stock photos from anywhere look like ours. tint=False only crops."""
    img = plt.imread(str(src))
    if img.dtype == np.uint8:
        img = img / 255.0
    rgb = img[..., :3] if img.ndim == 3 else np.stack([img] * 3, -1)
    if aspect:  # centre crop to width/height ratio
        h, w = rgb.shape[:2]
        if w / h > aspect:
            nw = int(h * aspect)
            rgb = rgb[:, (w - nw) // 2:(w - nw) // 2 + nw]
        else:
            nh = int(w / aspect)
            rgb = rgb[(h - nh) // 2:(h - nh) // 2 + nh, :]
    if tint:
        lum = rgb @ np.array([0.299, 0.587, 0.114])
        lo, hi = np.percentile(lum, (2, 98))
        lum = np.clip((lum - lo) / max(hi - lo, 1e-6), 0, 1) ** 0.9
        dark, light = np.array(to_rgb(t.section_color)) * 0.6, np.array(to_rgb(t.paper))
        rgb = dark[None, None, :] * (1 - lum[..., None]) + light[None, None, :] * lum[..., None]
    h, w = rgb.shape[:2]
    fig = plt.figure(figsize=(width_px / DPI, width_px / DPI * h / w), dpi=DPI)
    ax = fig.add_axes((0, 0, 1, 1))
    ax.imshow(np.clip(rgb, 0, 1), aspect="auto", interpolation="lanczos")
    ax.axis("off")
    fig.savefig(dst)
    plt.close(fig)
    return dst


COVER_PHOTO_ASPECT = (1 - 0.56) * WIDTH_IN / 5.6  # right-hand panel of the cover


# ---------------------------------------------------------------- source images (news items)
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
    if gh:
        image_url = f"https://opengraph.githubassets.com/1/{gh.group(1)}/{gh.group(2)}"
    else:
        resp = requests.get(page_url, headers=UA, timeout=20)
        resp.raise_for_status()
        ctype = resp.headers.get("content-type", "").split(";")[0]
        image_url = page_url if ctype in IMAGE_TYPES else _og_image(resp.text[:300_000], resp.url)
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
def render_cover(title: str, highlight: str, path: Path, t: Theme, photo: Path | None = None,
                 issue_date: date | None = None) -> Path:
    """Section front: masthead, tab, slab headline with one highlighted phrase, duotone photo panel."""
    issue_date = issue_date or date.today()
    fig_h = 5.6
    fig = _new_fig(t, fig_h)
    split = 0.56

    pax = fig.add_axes((split, 0, 1 - split, 1))
    pax.axis("off")
    if photo is not None:  # already duotoned and cropped to the panel's aspect
        pax.imshow(plt.imread(str(photo)), aspect="auto")
    else:  # halftone field in the series colour, like a newsprint photo plate
        pax.set_xlim(0, 1)
        pax.set_ylim(0, 1)
        pax.add_patch(Rectangle((0, 0), 1, 1, color=t.section_color))
        for i in range(19):
            for j in range(24):
                r = 0.003 + 0.017 * (j / 24) ** 1.5
                pax.add_patch(Circle((0.03 + i * 0.053 + (0.026 if j % 2 else 0), 0.02 + j * 0.042), r,
                                     color=t.paper, alpha=0.85, lw=0))

    # masthead
    fig.text(0.04, 0.905, t.newsletter.upper(), fontfamily=SLAB, fontweight="bold", fontsize=13, color=t.ink,
             va="bottom")
    fig.add_artist(Rectangle((0.04, 0.88), split - 0.075, 0.006, transform=fig.transFigure, color=t.ink, lw=0))
    fig.add_artist(Rectangle((0.04, 0.868), split - 0.075, 0.0015, transform=fig.transFigure, color=t.ink, lw=0))
    fig.text(split - 0.035, 0.905, f"{issue_date:%b} {issue_date.day}, {issue_date:%Y}".upper(), fontfamily=MONO,
             fontsize=9.5, color=t.graphite, ha="right", va="bottom")

    y = _tab(fig, t, x=0.04, y=0.79)

    # headline, line by line so the highlight phrase can be marked
    lines = textwrap.wrap(title, 22 if len(title) > 50 else 20)
    size = 34 if len(lines) <= 3 else 29 if len(lines) == 4 else 25
    available_pt = (split - 0.08) * WIDTH_IN * 72  # width of the text column in points
    size = min(size, available_pt / (0.58 * max(len(l) for l in lines)))  # long lines shrink to fit
    line_h = size / 72 * 1.2 / fig_h
    joined = " ".join(lines).lower()
    start = joined.find(highlight.lower().strip()) if highlight else -1
    end = start + len(highlight.strip()) if start >= 0 else -1
    offset = 0
    for i, line in enumerate(lines):
        yy = y - 0.02 - i * line_h
        txt = fig.text(0.04, yy, line, fontfamily=SLAB, fontweight="bold", fontsize=size, color=t.ink, va="top",
                       zorder=3)
        a, b = max(start - offset, 0), min(end - offset, len(line))
        if start >= 0 and a < b:
            full = _text_box(fig, txt)
            meas = lambda s: _text_box(fig, fig.text(0.04, yy, s, fontfamily=SLAB, fontweight="bold",  # noqa: E731
                                                     fontsize=size, alpha=0, va="top")).x1
            x0 = meas(line[:a]) if a else full.x0
            _highlight(fig, t, x0, full.y0, meas(line[:b]), full.y1, seed=20 + i)
        offset += len(line) + 1

    if t.author and t.author.strip().lower() != t.newsletter.strip().lower():
        by = fig.text(0.04, 0.075, f"BY {t.author.upper()}", fontfamily=COND, fontweight="bold", fontsize=12.5,
                      color=t.ink, va="bottom")
        fig.add_artist(Rectangle((0.04, 0.065), _text_box(fig, by).width, 0.004, transform=fig.transFigure,
                                 color=t.section_color, lw=0))
    has_byline = t.author and t.author.strip().lower() != t.newsletter.strip().lower()
    fig.text(split - 0.035 if has_byline else 0.04, 0.075, "THE EVIDENCE, MARKED UP.", fontfamily=MONO,
             fontweight="medium", fontsize=8.5, color=t.graphite, ha="right" if has_byline else "left", va="bottom")
    return _save(fig, path)
