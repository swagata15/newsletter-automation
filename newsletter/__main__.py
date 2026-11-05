"""Run the pipeline.

    python -m newsletter                       # picks today's issue type from config.yaml schedule
    python -m newsletter --type psychology     # force a type
    python -m newsletter --type tutorial --topic "Build a voice agent in a weekend"
    python -m newsletter --dry-run             # write files to output/ only, don't touch Substack
"""

from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

from .pipeline import KINDS, build, kind_for_today, record_history


def main() -> None:
    load_dotenv()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)

    p = argparse.ArgumentParser(description="Generate an AI newsletter issue and post it to Substack.")
    p.add_argument("--type", choices=("auto", *KINDS), default=os.getenv("ISSUE_TYPE") or "auto")
    p.add_argument("--topic", default=os.getenv("ISSUE_TOPIC") or None, help="Override the topic (psychology/tutorial).")
    p.add_argument("--config", default="config.yaml")
    p.add_argument("--dry-run", action="store_true", help="Write the issue locally; don't touch Substack.")
    p.add_argument("--mode", choices=["draft", "publish"], default=os.getenv("PUBLISH_MODE") or "draft")
    args = p.parse_args()

    config = yaml.safe_load(Path(args.config).read_text())
    kind = kind_for_today(config) if args.type == "auto" else args.type
    built = build(kind, config, topic=args.topic)

    if args.dry_run:
        logging.info("Dry run: open %s to review. Substack untouched.", built.out_dir / "issue.md")
        return

    from .publish import publish_issue

    publish_issue(built, mode=args.mode, tags=config["issues"][kind].get("tags"))
    record_history(kind, built.issue, built.issue.topic)


if __name__ == "__main__":
    main()
