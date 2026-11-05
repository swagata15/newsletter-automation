"""Collect what is trending in AI: news feeds, GitHub repos, papers and Hacker News.

Each source is best effort: if one is down, the others still feed the issue.
X (Twitter) has no free API, so X buzz is found by Claude's web search in the
research step instead.
"""

from __future__ import annotations

import calendar
import html
import logging
import os
import re
from datetime import datetime, timedelta, timezone

import feedparser
import requests

log = logging.getLogger(__name__)

UA = {"User-Agent": "newsletter-automation/1.0 (+https://github.com)"}
_TAG_RE = re.compile(r"<[^>]+>")


def _clean(text: str, limit: int = 400) -> str:
    text = html.unescape(_TAG_RE.sub(" ", text or ""))
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit] + ("..." if len(text) > limit else "")


def _get_json(url: str, **kwargs):
    resp = requests.get(url, headers={**UA, **kwargs.pop("headers", {})}, timeout=20, **kwargs)
    resp.raise_for_status()
    return resp.json()


# ---------------------------------------------------------------- RSS news
def news_from_feeds(feeds: list[str], since: datetime, per_feed: int = 12) -> list[dict]:
    items, seen = [], set()
    for url in feeds:
        try:
            parsed = feedparser.parse(url, agent=UA["User-Agent"])
        except Exception as exc:  # feedparser rarely raises, but be safe
            log.warning("Feed %s failed: %s", url, exc)
            continue
        if parsed.bozo and not parsed.entries:
            log.warning("Skipping feed %s: %s", url, parsed.get("bozo_exception"))
            continue
        source = parsed.feed.get("title", url)
        for entry in parsed.entries[:per_feed]:
            stamp = entry.get("published_parsed") or entry.get("updated_parsed")
            link, title = entry.get("link", ""), _clean(entry.get("title", ""), 200)
            if not (stamp and link and title):
                continue
            published = datetime.fromtimestamp(calendar.timegm(stamp), tz=timezone.utc)
            key = link.split("?")[0].rstrip("/").lower()
            if published < since or key in seen:
                continue
            seen.add(key)
            items.append({
                "title": title, "url": link, "source": source,
                "date": published.strftime("%Y-%m-%d"),
                "summary": _clean(entry.get("summary", "") or entry.get("description", "")),
            })
    items.sort(key=lambda i: i["date"], reverse=True)
    return items


# ---------------------------------------------------------------- GitHub
GITHUB_TOPICS = ["llm", "ai-agents", "agents", "generative-ai", "large-language-models", "rag", "mcp"]


def trending_repos(since: datetime, limit: int = 12) -> list[dict]:
    """Most starred AI repos created in the window (a proxy for GitHub trending)."""
    headers = {"Accept": "application/vnd.github+json"}
    if os.getenv("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    repos: dict[str, dict] = {}
    for topic in GITHUB_TOPICS:
        q = f"topic:{topic} created:>{since:%Y-%m-%d}"
        data = _get_json(
            "https://api.github.com/search/repositories",
            params={"q": q, "sort": "stars", "order": "desc", "per_page": 10},
            headers=headers,
        )
        for r in data.get("items", []):
            repos[r["full_name"]] = {
                "title": r["full_name"], "url": r["html_url"],
                "stars": r["stargazers_count"], "language": r.get("language") or "",
                "summary": _clean(r.get("description") or "", 300),
            }
    return sorted(repos.values(), key=lambda r: r["stars"], reverse=True)[:limit]


# ---------------------------------------------------------------- Papers
def trending_papers(days: int, limit: int = 10) -> list[dict]:
    """Most upvoted papers on Hugging Face Daily Papers over the window."""
    papers: dict[str, dict] = {}
    today = datetime.now(timezone.utc).date()
    for offset in range(days):
        day = today - timedelta(days=offset)
        try:
            entries = _get_json("https://huggingface.co/api/daily_papers", params={"date": day.isoformat()})
        except requests.RequestException as exc:
            log.debug("No papers for %s: %s", day, exc)
            continue
        for e in entries:
            p = e.get("paper", {})
            if not p.get("id"):
                continue
            papers[p["id"]] = {
                "title": _clean(p.get("title") or e.get("title", ""), 200),
                "url": f"https://huggingface.co/papers/{p['id']}",
                "arxiv": f"https://arxiv.org/abs/{p['id']}",
                "upvotes": p.get("upvotes", 0),
                "summary": _clean(p.get("summary", ""), 400),
            }
    return sorted(papers.values(), key=lambda p: p["upvotes"], reverse=True)[:limit]


# ---------------------------------------------------------------- Hacker News
HN_QUERIES = ["AI", "LLM", "OpenAI", "Anthropic", "Claude", "Gemini", "GPT", "agents"]


def hacker_news(since: datetime, limit: int = 15) -> list[dict]:
    stories: dict[str, dict] = {}
    for q in HN_QUERIES:
        data = _get_json(
            "https://hn.algolia.com/api/v1/search",
            params={
                "query": q, "tags": "story", "hitsPerPage": 20,
                "numericFilters": f"created_at_i>{int(since.timestamp())},points>80",
            },
        )
        for h in data.get("hits", []):
            stories[h["objectID"]] = {
                "title": h.get("title", ""),
                "url": h.get("url") or f"https://news.ycombinator.com/item?id={h['objectID']}",
                "discussion": f"https://news.ycombinator.com/item?id={h['objectID']}",
                "points": h.get("points", 0), "comments": h.get("num_comments", 0),
            }
    return sorted(stories.values(), key=lambda s: s["points"], reverse=True)[:limit]


# ---------------------------------------------------------------- Digest
def weekly_digest(feeds: list[str], lookback_days: int) -> str:
    """Gather every source into one text block for Claude to research from."""
    since = datetime.now(timezone.utc) - timedelta(days=lookback_days)
    sections = []

    def add(name, fn, fmt):
        try:
            rows = fn()
        except Exception as exc:
            log.warning("%s unavailable: %s", name, exc)
            return
        log.info("%s: %d items", name, len(rows))
        if rows:
            sections.append(f"## {name}\n" + "\n".join(fmt(r) for r in rows))

    add("News headlines (RSS)", lambda: news_from_feeds(feeds, since),
        lambda r: f"- [{r['date']}] {r['title']} ({r['source']}) {r['url']}\n  {r['summary']}")
    add("New GitHub repos gaining stars", lambda: trending_repos(since),
        lambda r: f"- {r['title']} ({r['stars']} stars, {r['language']}) {r['url']}\n  {r['summary']}")
    add("Trending papers (Hugging Face Daily Papers)", lambda: trending_papers(lookback_days),
        lambda r: f"- {r['title']} ({r['upvotes']} upvotes) {r['url']} | {r['arxiv']}\n  {r['summary']}")
    add("Hacker News top AI stories", lambda: hacker_news(since),
        lambda r: f"- {r['title']} ({r['points']} points, {r['comments']} comments) {r['url']} | discussion: {r['discussion']}")

    return "\n\n".join(sections) or "(No source data could be fetched this week; rely on web search.)"
