"""Push a finished issue (text + images) to Substack.

Substack has no official public API; this uses the community `python-substack`
library, which talks to the same endpoints the Substack web editor uses.
Local images referenced in the markdown are uploaded to Substack's image host.
"""

from __future__ import annotations

import logging
import os

from substack import Api

from .pipeline import Built

log = logging.getLogger(__name__)


def _api() -> Api:
    publication_url = os.environ["SUBSTACK_PUBLICATION_URL"]
    cookies = os.getenv("SUBSTACK_COOKIES")
    if cookies:
        return Api(cookies_string=cookies, publication_url=publication_url)
    email, password = os.getenv("SUBSTACK_EMAIL"), os.getenv("SUBSTACK_PASSWORD")
    if email and password:
        return Api(email=email, password=password, publication_url=publication_url)
    raise RuntimeError("Set SUBSTACK_COOKIES (recommended) or SUBSTACK_EMAIL + SUBSTACK_PASSWORD.")


def publish_issue(built: Built, mode: str = "draft", tags: list[str] | None = None) -> dict:
    """mode='draft' leaves it in Substack for review; 'publish' posts and emails subscribers."""
    if mode not in ("draft", "publish"):
        raise ValueError(f"PUBLISH_MODE must be 'draft' or 'publish', got {mode!r}")
    issue = built.issue
    result = _api().create_draft_from_markdown(
        title=issue.title,
        subtitle=issue.subtitle,
        markdown=built.markdown,
        tags=tags or None,
        prepublish=mode == "publish",
        publish=mode == "publish",
        send=True,
    )
    log.info("Substack %s created (draft id %s)", "post" if mode == "publish" else "draft",
             result["draft"].get("id"))
    return result
