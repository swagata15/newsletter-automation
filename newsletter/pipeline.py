"""Build one issue end to end: research -> write -> clean up style -> render visuals -> save.

Issues are saved by category so they are easy to track:

    issues/
      README.md                     <- index of every issue, newest first, with status
      this-week-in-ai/2026-11-07-<slug>/
      ai-and-the-mind/2026-11-04-<slug>/
      weekend-build/2026-11-06-<slug>/
        issue.md  issue.json  research-notes.md  cover.png  v1.png ...
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import anthropic

from . import claude, photos, prompts, sources, visuals
from .models import Issue, Visual
from .style import find_slop, remove_dashes

log = logging.getLogger(__name__)

ISSUES_DIR = Path("issues")
HISTORY = Path("history.json")
KINDS = ("weekly", "psychology", "tutorial")


@dataclass
class Built:
    kind: str
    issue: Issue
    markdown: str          # final markdown with local image paths
    out_dir: Path


# ---------------------------------------------------------------- folders, history, index
def slugify(text: str, limit: int = 60) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:limit].rstrip("-") or "issue"


def category_dir(config: dict, kind: str) -> Path:
    return ISSUES_DIR / slugify(config["issues"][kind].get("label", kind))


def kind_for_today(config: dict) -> str:
    day = datetime.now(timezone.utc).strftime("%A").lower()
    kind = config.get("schedule", {}).get(day)
    if not kind:
        raise SystemExit(f"No issue scheduled for {day}. Pass --type to run one anyway.")
    return kind


def load_history() -> list[dict]:
    return json.loads(HISTORY.read_text()) if HISTORY.exists() else []


def record_history(built: Built, status: str, config: dict) -> None:
    history = load_history()
    entry = {"date": built.out_dir.name[:10], "type": built.kind, "title": built.issue.title,
             "topic": built.issue.topic, "folder": str(built.out_dir), "status": status}
    history = [h for h in history if h.get("folder") != entry["folder"]] + [entry]
    HISTORY.write_text(json.dumps(history, indent=2) + "\n")
    write_index(config)


def write_index(config: dict) -> None:
    """issues/README.md: one table per category, newest first, linking each issue."""
    history = load_history()
    lines = ["# Issues", "", "Generated automatically. Status: `local` = saved here only, "
             "`draft` = Substack draft created, `published` = sent to subscribers.", ""]
    for kind in KINDS:
        label = config["issues"][kind].get("label", kind)
        rows = sorted((h for h in history if h["type"] == kind and h.get("folder")), key=lambda h: h["date"],
                      reverse=True)
        lines += [f"## {label}", ""]
        if not rows:
            lines += ["_None yet._", ""]
            continue
        lines += ["| Date | Title | Status |", "|---|---|---|"]
        for h in rows:
            rel = Path(h["folder"]).relative_to(ISSUES_DIR) if h["folder"].startswith(str(ISSUES_DIR)) else h["folder"]
            lines.append(f"| {h['date']} | [{h['title']}]({rel}/issue.md) | {h.get('status', 'local')} |")
        lines.append("")
    ISSUES_DIR.mkdir(exist_ok=True)
    (ISSUES_DIR / "README.md").write_text("\n".join(lines))


def choose_topic(client, kind: str, cfg: dict, date_str: str) -> str:
    used = [h["topic"] for h in load_history() if h["type"] == kind]
    used_lower = {u.lower() for u in used}
    for topic in cfg.get("topic_backlog", []):
        if topic.lower() not in used_lower:
            return topic
    log.info("Topic backlog used up; asking Claude for a fresh %s topic.", kind)
    return claude.quick_answer(client, prompts.pick_topic(kind, used, date_str), web=True).splitlines()[0].strip()


# ---------------------------------------------------------------- grounding checks
def _norm_text(s: str) -> str:
    s = s.lower().replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"[^a-z0-9%.' ]+", " ", re.sub(r"\s+", " ", s)).strip()


def _number_variants(v: float) -> list[str]:
    out = {f"{v:g}"}
    if float(v).is_integer():
        out |= {str(int(v)), f"{int(v):,}"}
    else:
        out |= {f"{v:.1f}", f"{v:.2f}".rstrip("0"), f"{v:,.1f}"}
    return [o for o in out if o]


def _numbers_found(values: list[float], notes: str) -> tuple[int, int]:
    found = sum(any(re.search(rf"(?<![\d.]){re.escape(n)}(?![\d])", notes) for n in _number_variants(x))
                for x in values)
    return found, len(values)


def _source_ok(v: Visual, notes: str) -> bool:
    dom = urlparse(v.source_url).netloc.removeprefix("www.").lower() if v.source_url else ""
    return bool(dom) and dom in notes.lower()


def grounded(v: Visual, notes: str) -> tuple[bool, str]:
    """Every number or quote in a data visual must be traceable to the research notes."""
    if v.kind in ("chart", "stat", "waffle", "quote") and not _source_ok(v, notes):
        return False, f"source {v.source_url!r} not in research notes"
    if v.kind == "chart":
        found, total = _numbers_found([x for s in (v.series or []) for x in s.values], notes)
        return (total > 0 and found / total >= 0.75), f"{found}/{total} values found in notes"
    if v.kind == "stat":
        nums = [float(n.replace(",", "")) for s in (v.stats or []) for n in re.findall(r"\d[\d,]*\.?\d*", s.value)]
        nums = [n for n in nums if not (n < 10 and float(n).is_integer())]  # "1 in 3" style counts are fine
        found, total = _numbers_found(nums, notes)
        return found == total, f"{found}/{total} stat values found in notes"
    if v.kind == "waffle":
        found, _ = _numbers_found([v.waffle_value or -1], notes)
        return bool(found), "waffle value found" if found else "waffle value not in notes"
    if v.kind == "quote":
        ok = _norm_text(v.quote_text or "")[:120] in _norm_text(notes)
        return ok, "quote is verbatim in notes" if ok else "quote not found verbatim in notes"
    return True, ""


# ---------------------------------------------------------------- rendering
def _image_md(path: Path, alt: str, caption: str) -> str:
    caption = caption.replace('"', "'")
    alt = alt.replace("]", ")").replace("[", "(").replace('"', "'")
    return f'![{alt}]({path.resolve()} "{caption}")'


def _photo(key: str, query: str, out_dir: Path, approve) -> "photos.Photo | None":
    """Pinned photo from photos.json if there is one; otherwise search (+ review) and pin the result."""
    pins_file = out_dir / "photos.json"
    pins = json.loads(pins_file.read_text()) if pins_file.exists() else {}
    if key in pins:
        return photos.from_pin(pins[key], out_dir / f"{key}-raw") if pins[key] else None
    found = photos.find_photo(query, out_dir / f"{key}-raw", approve)
    if found:
        pins[key] = {"url": found.url, "credit": found.credit, "page": found.page_url, "query": query}
        pins_file.write_text(json.dumps(pins, indent=2) + "\n")
    return found


def render_visual(v: Visual, out_dir: Path, notes: str, theme: visuals.Theme, approve=None) -> str:
    stem = out_dir / v.id
    png = stem.with_suffix(".png")
    caption = v.caption
    if v.kind in ("chart", "stat", "waffle", "quote"):
        ok, why = grounded(v, notes)
        if not ok:
            raise ValueError(f"not grounded in research: {why}")
    if v.kind == "chart":
        path = visuals.render_chart(v, png, theme)
    elif v.kind == "stat":
        path = visuals.render_stat(v, png, theme)
    elif v.kind == "waffle":
        path = visuals.render_waffle(v, png, theme)
    elif v.kind == "quote":
        path = visuals.render_quote(v, png, theme)
    elif v.kind == "timeline":
        path = visuals.render_timeline(v, png, theme)
    elif v.kind == "diagram":
        path = visuals.render_diagram(v, png, theme)
    elif v.kind == "photo":
        found = _photo(v.id, v.photo_query or v.caption, out_dir, approve)
        if not found:
            raise ValueError("no photo found (check photo provider keys / network access)")
        path = visuals.duotone(found.path, png, theme, aspect=16 / 9, tint=theme.duotone_photos)
        caption = f"{v.caption} ({found.credit})"
    else:  # "image": the source's own preview image, credited
        path = visuals.fetch_source_image(v.source_url, stem)
        caption = f"{v.caption} (Image: {v.source_name})" if v.source_name else v.caption
    return _image_md(path, v.chart_title or v.caption, caption)


# ---------------------------------------------------------------- main build
def build(kind: str, config: dict, topic: str | None = None, client: anthropic.Anthropic | None = None) -> Built:
    if kind not in KINDS:
        raise ValueError(f"Unknown issue type {kind!r}; choose from {KINDS}")
    client = client or anthropic.Anthropic()
    nl, cfg = config["newsletter"], config["issues"][kind]
    theme = visuals.Theme.from_config(config, kind)
    date_str = date.today().strftime("%A, %B %d, %Y")

    # 1. Research
    if kind == "weekly":
        digest = sources.weekly_digest(config.get("feeds", []), cfg["lookback_days"])
        topic = topic or f"{cfg['label']}, week of {date.today():%B %d, %Y}"
        research_prompt = prompts.weekly_research(digest, cfg, nl, date_str)
    else:
        topic = topic or choose_topic(client, kind, cfg, date_str)
        research_prompt = (prompts.psychology_research(topic, date_str) if kind == "psychology"
                           else prompts.tutorial_research(topic, cfg, date_str))
    log.info("Issue type %s, topic: %s", kind, topic)
    notes = claude.research(client, research_prompt, effort=cfg.get("research_effort", cfg["effort"]),
                            max_searches=cfg["max_searches"], max_fetches=cfg["max_fetches"])

    # 2. Write
    write_prompt = {
        "weekly": lambda: prompts.weekly_write(notes, cfg, nl, date_str),
        "psychology": lambda: prompts.psychology_write(topic, notes, cfg, nl, date_str),
        "tutorial": lambda: prompts.tutorial_write(topic, notes, cfg, nl, date_str),
    }[kind]()
    issue = claude.write_issue(client, write_prompt, effort=cfg["effort"])
    issue.topic = topic
    return assemble(kind, config, issue, notes, client=client)


def assemble(kind: str, config: dict, issue: Issue, notes: str, client: anthropic.Anthropic | None = None,
             issue_date: date | None = None, out_dir: Path | None = None, approve=None,
             photo_pins: dict | None = None) -> Built:
    """Steps after writing: style clean-up, fact-checked visuals, cover, save. No API needed unless
    `client` is given (then stock AI phrases are rewritten by Claude; otherwise they are only reported)."""
    issue_date = issue_date or date.today()
    theme = visuals.Theme.from_config(config, kind)
    approve = approve or ((lambda path, query: claude.approve_photo(client, path, query)) if client else None)
    if approve is None:
        log.warning("No photo review available: photos are used unchecked. Review them before publishing.")
    out_dir = out_dir or category_dir(config, kind) / f"{issue_date:%Y-%m-%d}-{slugify(issue.title)}"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "research-notes.md").write_text(notes)
    if photo_pins is not None:  # photos chosen by hand ({"v4": {...}, "cover": {...}}, null = no photo)
        (out_dir / "photos.json").write_text(json.dumps(photo_pins, indent=2) + "\n")

    # 3. Style: strip dashes, rewrite stock AI phrases, strip dashes again
    issue.markdown = remove_dashes(issue.markdown)
    slop = find_slop(issue.markdown)
    if slop and client is None:
        log.warning("Stock phrases found (no API client to rewrite them): %s", slop)
    elif slop:
        log.info("Rewriting stock phrases: %s", slop)
        issue.markdown = remove_dashes(claude.revise_style(client, issue.markdown, slop))
        leftover = find_slop(issue.markdown)
        if leftover:
            log.warning("Still contains: %s (review before publishing)", leftover)
    issue.title, issue.subtitle = remove_dashes(issue.title), remove_dashes(issue.subtitle)
    for v in issue.visuals:
        for attr in ("caption", "chart_title", "y_label", "annotation", "waffle_label"):
            if getattr(v, attr):
                setattr(v, attr, remove_dashes(getattr(v, attr)))
        for s in v.stats or []:
            s.label = remove_dashes(s.label)
        for it in v.timeline or []:
            it.title, it.detail = remove_dashes(it.title), remove_dashes(it.detail)

    # 4. Visuals
    markdown = issue.markdown
    for v in issue.visuals:
        try:
            replacement = render_visual(v, out_dir, notes, theme, approve)
            log.info("Visual %s (%s) rendered", v.id, v.kind)
        except Exception as exc:
            log.warning("Skipping visual %s (%s): %s", v.id, v.kind, exc)
            replacement = ""
        markdown = markdown.replace(f"[[VISUAL:{v.id}]]", replacement)
    markdown = re.sub(r"^\s*\[\[VISUAL:[^\]]*\]\]\s*$", "", markdown, flags=re.M)
    markdown = re.sub(r"\n{3,}", "\n\n", markdown).strip()

    # 5. Cover (Substack uses the first image as the social preview)
    try:
        cover_photo = None
        found = _photo("cover", issue.cover_photo_query, out_dir, approve)
        if found:
            cover_photo = visuals.duotone(found.path, out_dir / "cover-photo.png", theme, width_px=900,
                                          aspect=visuals.COVER_PHOTO_ASPECT, tint=theme.duotone_photos)
        cover = visuals.render_cover(issue.title, issue.cover_highlight, out_dir / "cover.png", theme, cover_photo,
                                     issue_date=issue_date)
        credit = f' "{found.credit}"' if found else ""
        markdown = f"![{issue.title}]({cover.resolve()}{credit})\n\n{markdown}"
    except Exception as exc:
        log.warning("Cover image failed: %s", exc)

    readable = markdown.replace(f"{out_dir.resolve()}/", "")  # relative image paths, so it previews on GitHub
    (out_dir / "issue.md").write_text(f"# {issue.title}\n\n*{issue.subtitle}*\n\n{readable}\n")
    (out_dir / "issue.json").write_text(issue.model_dump_json(indent=2))
    log.info("Saved %s", out_dir / "issue.md")
    return Built(kind, issue, markdown, out_dir)


# ---------------------------------------------------------------- pre-made issues
def kind_of_folder(config: dict, folder: Path) -> str:
    for kind in KINDS:
        if category_dir(config, kind).resolve() == folder.resolve().parent:
            return kind
    raise ValueError(f"{folder} is not inside an issues/<category>/ folder")


def rerender(folder: Path, config: dict) -> Built:
    """Re-draw an existing issue from its issue.json and research notes (e.g. to add photos later)."""
    kind = kind_of_folder(config, folder)
    issue = Issue.model_validate_json((folder / "issue.json").read_text())
    notes = (folder / "research-notes.md").read_text()
    issue_date = date.fromisoformat(folder.name[:10])
    return assemble(kind, config, issue, notes, issue_date=issue_date, out_dir=folder)


def premade_for(kind: str, day: date) -> Path | None:
    """A pre-written issue scheduled for this day that hasn't been sent to Substack yet."""
    for h in load_history():
        if h["type"] == kind and h["date"] == day.isoformat() and h.get("status") == "local" and h.get("folder"):
            if Path(h["folder"], "issue.json").exists():
                return Path(h["folder"])
    return None
