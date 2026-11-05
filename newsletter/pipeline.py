"""Build one issue end to end: research -> write -> clean up style -> render visuals."""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import anthropic

from . import claude, prompts, sources, visuals
from .models import Issue, Visual
from .style import find_slop, remove_dashes

log = logging.getLogger(__name__)

HISTORY = Path("history.json")
KINDS = ("weekly", "psychology", "tutorial")


@dataclass
class Built:
    kind: str
    issue: Issue
    markdown: str          # final markdown with local image paths
    out_dir: Path
    cover: Path | None


# ---------------------------------------------------------------- helpers
def kind_for_today(config: dict) -> str:
    day = datetime.now(timezone.utc).strftime("%A").lower()
    kind = config.get("schedule", {}).get(day)
    if not kind:
        raise SystemExit(f"No issue scheduled for {day}. Pass --type to run one anyway.")
    return kind


def load_history() -> list[dict]:
    return json.loads(HISTORY.read_text()) if HISTORY.exists() else []


def record_history(kind: str, issue: Issue, topic: str) -> None:
    history = load_history()
    history.append({"date": date.today().isoformat(), "type": kind, "title": issue.title, "topic": topic})
    HISTORY.write_text(json.dumps(history, indent=2) + "\n")


def choose_topic(client, kind: str, cfg: dict, date_str: str) -> str:
    used = [h["topic"] for h in load_history() if h["type"] == kind]
    used_lower = {u.lower() for u in used}
    for topic in cfg.get("topic_backlog", []):
        if topic.lower() not in used_lower:
            return topic
    log.info("Topic backlog used up; asking Claude for a fresh %s topic.", kind)
    return claude.quick_answer(client, prompts.pick_topic(kind, used, date_str), web=True).splitlines()[0].strip()


def _norm(url: str) -> str:
    return url.split("#")[0].split("?")[0].rstrip("/").lower().removeprefix("https://").removeprefix("http://")


def _number_variants(v: float) -> list[str]:
    out = {f"{v:g}", f"{v:,.0f}" if float(v).is_integer() else f"{v:,.1f}"}
    if float(v).is_integer():
        out.add(str(int(v)))
    else:
        out.update({f"{v:.1f}", f"{v:.2f}".rstrip("0")})
    return [o for o in out if o]


def chart_is_grounded(v: Visual, notes: str) -> bool:
    """Reject charts whose source or numbers don't appear in the research notes."""
    notes_l = notes.lower()
    if not v.source_url or urlparse(v.source_url).netloc.removeprefix("www.").lower() not in notes_l:
        log.warning("Dropping chart %s: source %r not in research notes", v.id, v.source_url)
        return False
    if _norm(v.source_url) not in notes_l.replace("https://", "").replace("http://", ""):
        log.info("Chart %s: exact source URL not in notes, but domain is", v.id)
    values = [x for s in (v.series or []) for x in s.values]
    found = sum(any(re.search(rf"(?<![\d.]){re.escape(n)}(?![\d])", notes) for n in _number_variants(x)) for x in values)
    if not values or found / len(values) < 0.75:
        log.warning("Dropping chart %s: only %d/%d values found in research notes", v.id, found, len(values))
        return False
    return True


def _image_md(path: Path, alt: str, caption: str) -> str:
    caption = caption.replace('"', "'")
    alt = alt.replace("]", ")").replace("[", "(")
    return f'![{alt}]({path.resolve()} "{caption}")'


# ---------------------------------------------------------------- main build
def build(kind: str, config: dict, topic: str | None = None, client: anthropic.Anthropic | None = None) -> Built:
    if kind not in KINDS:
        raise ValueError(f"Unknown issue type {kind!r}; choose from {KINDS}")
    client = client or anthropic.Anthropic()
    nl, cfg = config["newsletter"], config["issues"][kind]
    date_str = date.today().strftime("%A, %B %d, %Y")
    out_dir = Path("output") / f"{date.today():%Y-%m-%d}-{kind}"
    out_dir.mkdir(parents=True, exist_ok=True)

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
    notes = claude.research(
        client, research_prompt,
        effort=cfg.get("research_effort", cfg["effort"]),
        max_searches=cfg["max_searches"], max_fetches=cfg["max_fetches"],
    )
    (out_dir / "research-notes.md").write_text(notes)

    # 2. Write
    write_prompt = {
        "weekly": lambda: prompts.weekly_write(notes, cfg, nl, date_str),
        "psychology": lambda: prompts.psychology_write(topic, notes, cfg, nl, date_str),
        "tutorial": lambda: prompts.tutorial_write(topic, notes, cfg, nl, date_str),
    }[kind]()
    issue = claude.write_issue(client, write_prompt, effort=cfg["effort"])

    # 3. Style: strip dashes, rewrite stock AI phrases, strip dashes again
    issue.markdown = remove_dashes(issue.markdown)
    slop = find_slop(issue.markdown)
    if slop:
        log.info("Rewriting stock phrases: %s", slop)
        issue.markdown = remove_dashes(claude.revise_style(client, issue.markdown, slop))
        leftover = find_slop(issue.markdown)
        if leftover:
            log.warning("Still contains: %s (review before publishing)", leftover)
    issue.title, issue.subtitle = remove_dashes(issue.title), remove_dashes(issue.subtitle)
    for v in issue.visuals:
        v.caption = remove_dashes(v.caption)

    # 4. Visuals
    brand = nl.get("accent_color", "#A63A2B")
    markdown = issue.markdown
    for v in issue.visuals:
        stem = out_dir / v.id
        try:
            if v.kind == "chart":
                if not chart_is_grounded(v, notes):
                    raise ValueError("chart data not grounded in research")
                path = visuals.render_chart(v, stem.with_suffix(".png"), brand)
                caption = v.caption
            elif v.kind == "diagram":
                path = visuals.render_diagram(v, stem.with_suffix(".png"), brand)
                caption = v.caption
            else:
                path = visuals.fetch_source_image(v.source_url, stem)
                caption = f"{v.caption} (Image: {v.source_name})" if v.source_name else v.caption
            replacement = _image_md(path, v.chart_title or v.caption, caption)
            log.info("Visual %s (%s) -> %s", v.id, v.kind, path.name)
        except Exception as exc:
            log.warning("Skipping visual %s (%s): %s", v.id, v.kind, exc)
            replacement = ""
        markdown = markdown.replace(f"[[VISUAL:{v.id}]]", replacement)
    markdown = re.sub(r"^\s*\[\[VISUAL:[^\]]*\]\]\s*$", "", markdown, flags=re.M)  # unknown ids
    markdown = re.sub(r"\n{3,}", "\n\n", markdown).strip()

    cover = None
    try:
        cover = visuals.render_cover(issue.title, cfg["label"], nl["name"], out_dir / "cover.png", brand)
        markdown = f"![{issue.title}]({cover.resolve()})\n\n{markdown}"
    except Exception as exc:
        log.warning("Cover image failed: %s", exc)

    (out_dir / "issue.md").write_text(f"# {issue.title}\n\n*{issue.subtitle}*\n\n{markdown}\n")
    (out_dir / "issue.json").write_text(issue.model_dump_json(indent=2))
    log.info("Saved %s", out_dir / "issue.md")
    issue.topic = topic
    return Built(kind, issue, markdown, out_dir, cover)
