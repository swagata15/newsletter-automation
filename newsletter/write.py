"""Turn a pile of stories into a finished newsletter issue with Claude."""

from __future__ import annotations

import logging
from datetime import date

import anthropic
from pydantic import BaseModel, Field

from .fetch import Story

log = logging.getLogger(__name__)

MODEL = "claude-opus-5-5"
# Story candidates sent to Claude; it picks the best `max_stories` of them.
MAX_CANDIDATES = 60


class Issue(BaseModel):
    title: str = Field(description="Catchy, specific headline for this issue (max ~70 chars)")
    subtitle: str = Field(description="One-sentence teaser shown under the title and in email previews")
    markdown: str = Field(
        description="Full newsletter body in Markdown. Do not repeat the title. "
        "Use ## for section headings and inline [links](url) to the original sources."
    )


SYSTEM_PROMPT = """You are the editor and writer of a weekly AI newsletter published on Substack.

Your job each week: read the candidate stories, pick the ones that genuinely matter to the readers, \
and write a polished, ready-to-send issue.

Editorial rules:
- Only report facts that appear in the provided stories. Never invent numbers, quotes, or releases.
- Link every story you mention to its original URL using Markdown links.
- Skip duplicates, minor updates, and pure marketing. Prefer substance over hype.
- For each story, say briefly what happened and why it matters to the reader.
- Open with a short, friendly intro (2-3 sentences) and close with a one-line sign-off.
- Use plain Markdown only: headings (##), paragraphs, bullet lists, bold, links. No tables, no HTML."""


def write_issue(stories: list[Story], settings: dict, client: anthropic.Anthropic | None = None) -> Issue:
    if not stories:
        raise ValueError("No stories to write about - check your feeds or increase lookback_days.")

    client = client or anthropic.Anthropic()
    candidates = "\n\n".join(s.to_prompt_block(i + 1) for i, s in enumerate(stories[:MAX_CANDIDATES]))
    sections = "\n".join(f"- {s}" for s in settings["sections"])

    user_prompt = f"""Newsletter: {settings['name']}
Date: {date.today():%B %d, %Y}
Audience: {settings['audience']}
Tone: {settings['tone']}
Pick at most {settings['max_stories']} stories.

Use these sections (drop a section if no story fits it):
{sections}

Candidate stories from the past {settings['lookback_days']} days:

{candidates}"""

    response = client.beta.messages.parse(
        model=MODEL,
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
        thinking={"type": "adaptive"},
        output_config={"effort": "high"},
        output_format=Issue,
        # If a safety classifier declines, retry server-side on Anthropic's recommended fallback model.
        fallbacks="default",
        betas=["server-side-fallback-2026-07-01"],
    )

    if response.stop_reason == "refusal":
        raise RuntimeError(f"Claude declined to write this issue: {response.stop_details}")
    if response.stop_reason == "max_tokens":
        raise RuntimeError("Issue was cut off (max_tokens). Reduce max_stories or MAX_CANDIDATES.")

    issue = response.parsed_output
    if issue is None:
        raise RuntimeError("Claude did not return a parsable issue.")
    log.info(
        "Wrote issue %r (%d input / %d output tokens)",
        issue.title,
        response.usage.input_tokens,
        response.usage.output_tokens,
    )
    return issue
