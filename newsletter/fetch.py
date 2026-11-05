"""Collect recent stories from RSS/Atom feeds."""

from __future__ import annotations

import calendar
import html
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import feedparser

log = logging.getLogger(__name__)

_TAG_RE = re.compile(r"<[^>]+>")


@dataclass
class Story:
    title: str
    link: str
    source: str
    published: datetime
    summary: str

    def to_prompt_block(self, idx: int) -> str:
        return (
            f"[{idx}] {self.title}\n"
            f"Source: {self.source} | Published: {self.published:%Y-%m-%d}\n"
            f"URL: {self.link}\n"
            f"Summary: {self.summary}"
        )


def _clean(text: str, limit: int = 600) -> str:
    text = html.unescape(_TAG_RE.sub(" ", text or ""))
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit] + ("…" if len(text) > limit else "")


def _published(entry) -> datetime | None:
    for key in ("published_parsed", "updated_parsed"):
        value = entry.get(key)
        if value:
            return datetime.fromtimestamp(calendar.timegm(value), tz=timezone.utc)
    return None


def fetch_stories(feeds: list[str], lookback_days: int, per_feed_limit: int = 15) -> list[Story]:
    """Return de-duplicated stories from the last `lookback_days`, newest first."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)
    stories: list[Story] = []
    seen: set[str] = set()

    for url in feeds:
        parsed = feedparser.parse(url, agent="newsletter-automation/1.0")
        if parsed.bozo and not parsed.entries:
            log.warning("Skipping feed %s: %s", url, parsed.get("bozo_exception"))
            continue
        source = parsed.feed.get("title", url)
        count = 0
        for entry in parsed.entries:
            if count >= per_feed_limit:
                break
            link = entry.get("link", "")
            title = _clean(entry.get("title", ""), 200)
            published = _published(entry)
            if not link or not title or published is None or published < cutoff:
                continue
            key = link.split("?")[0].rstrip("/").lower()
            if key in seen:
                continue
            seen.add(key)
            stories.append(
                Story(
                    title=title,
                    link=link,
                    source=source,
                    published=published,
                    summary=_clean(entry.get("summary", "") or entry.get("description", "")),
                )
            )
            count += 1
        log.info("Fetched %d stories from %s", count, source)

    stories.sort(key=lambda s: s.published, reverse=True)
    return stories
