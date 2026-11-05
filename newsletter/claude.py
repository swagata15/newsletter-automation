"""All Claude API calls: web research, structured writing, and style revision."""

from __future__ import annotations

import logging

import anthropic

from .models import Issue
from .prompts import RESEARCH_SYSTEM, REVISE_PROMPT, WRITER_SYSTEM

log = logging.getLogger(__name__)

MODEL = "claude-opus-5-5"
# If a safety classifier declines a request, retry it server-side on Anthropic's recommended fallback model.
FALLBACK = {"fallbacks": "default", "betas": ["server-side-fallback-2026-07-01"]}
MAX_CONTINUATIONS = 6


def _check(msg) -> None:
    if msg.stop_reason == "refusal":
        raise RuntimeError(f"Claude declined the request: {msg.stop_details}")
    if msg.stop_reason == "max_tokens":
        raise RuntimeError("Response hit max_tokens and was cut off.")


def _text(msg) -> str:
    return "".join(b.text for b in msg.content if b.type == "text")


def research(client: anthropic.Anthropic, prompt: str, *, effort: str, max_searches: int, max_fetches: int) -> str:
    """Let Claude search and read the web, and return its research notes as text."""
    tools = [
        {"type": "web_search_20260209", "name": "web_search", "max_uses": max_searches},
        {"type": "web_fetch_20260209", "name": "web_fetch", "max_uses": max_fetches},
    ]
    messages = [{"role": "user", "content": prompt}]
    notes = []
    for _ in range(MAX_CONTINUATIONS):
        with client.beta.messages.stream(
            model=MODEL,
            max_tokens=64000,
            system=RESEARCH_SYSTEM,
            messages=messages,
            tools=tools,
            thinking={"type": "adaptive"},
            output_config={"effort": effort},
            **FALLBACK,
        ) as stream:
            msg = stream.get_final_message()
        notes.append(_text(msg))
        if msg.stop_reason != "pause_turn":  # long server-tool turns pause; send them back to continue
            break
        messages.append({"role": "assistant", "content": msg.content})
    _check(msg)
    result = "\n".join(n for n in notes if n.strip())
    log.info("Research done: %d chars of notes (%d output tokens in last turn)", len(result), msg.usage.output_tokens)
    return result


def quick_answer(client: anthropic.Anthropic, prompt: str, *, web: bool = False) -> str:
    tools = [{"type": "web_search_20260209", "name": "web_search", "max_uses": 5}] if web else []
    messages = [{"role": "user", "content": prompt}]
    for _ in range(MAX_CONTINUATIONS):
        with client.beta.messages.stream(
            model=MODEL, max_tokens=16000, messages=messages, tools=tools,
            thinking={"type": "adaptive"}, output_config={"effort": "medium"}, **FALLBACK,
        ) as stream:
            msg = stream.get_final_message()
        if msg.stop_reason != "pause_turn":
            break
        messages.append({"role": "assistant", "content": msg.content})
    _check(msg)
    return _text(msg).strip()


def write_issue(client: anthropic.Anthropic, prompt: str, *, effort: str) -> Issue:
    with client.beta.messages.stream(
        model=MODEL,
        max_tokens=64000,
        system=WRITER_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
        thinking={"type": "adaptive"},
        output_config={"effort": effort},
        output_format=Issue,
        **FALLBACK,
    ) as stream:
        msg = stream.get_final_message()
    _check(msg)
    issue = msg.parsed_output
    if issue is None:
        raise RuntimeError("Claude did not return a parsable issue.")
    log.info("Wrote %r: %d words, %d visuals", issue.title, len(issue.markdown.split()), len(issue.visuals))
    return issue


def approve_photo(client: anthropic.Anthropic, path, query: str) -> bool:
    """Look at a candidate photo: does it match the brief and is it appropriate for a newsletter?"""
    import base64
    data = base64.standard_b64encode(open(path, "rb").read()).decode()
    media = "image/png" if str(path).endswith(".png") else "image/jpeg"
    prompt = (f"A newsletter needs a photo of: {query}\n"
              "Answer YES only if this photo (1) clearly matches that description, (2) is realistic and good "
              "quality, (3) is appropriate for a professional newsletter: no nudity, suggestive poses, violence, "
              "visible logos as the main subject, or text overlays/watermarks. Otherwise answer NO. "
              "Reply with YES or NO, then one short reason.")
    msg = client.messages.create(
        model=MODEL, max_tokens=2000, output_config={"effort": "low"},
        messages=[{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": media, "data": data}},
            {"type": "text", "text": prompt}]}],
    )
    if msg.stop_reason == "refusal":
        return False
    answer = _text(msg).strip().upper()
    log.info("Photo review for %r: %s", query, _text(msg).strip()[:120])
    return answer.startswith("YES")


def revise_style(client: anthropic.Anthropic, markdown: str, phrases: list[str]) -> str:
    return quick_answer(client, REVISE_PROMPT.format(phrases=", ".join(f'"{p}"' for p in phrases), markdown=markdown))
