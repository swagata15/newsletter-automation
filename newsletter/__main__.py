"""Run the full pipeline: python -m newsletter [--dry-run]"""

from __future__ import annotations

import argparse
import logging
import os
from datetime import date
from pathlib import Path

import yaml
from dotenv import load_dotenv

from .fetch import fetch_stories
from .write import write_issue


def main() -> None:
    load_dotenv()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    parser = argparse.ArgumentParser(description="Generate and post the AI newsletter to Substack.")
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--dry-run", action="store_true", help="Write the issue locally; don't touch Substack.")
    parser.add_argument("--mode", choices=["draft", "publish"], default=os.getenv("PUBLISH_MODE", "draft"))
    args = parser.parse_args()

    config = yaml.safe_load(Path(args.config).read_text())
    settings = config["newsletter"]

    stories = fetch_stories(config["feeds"], settings["lookback_days"])
    logging.info("Collected %d candidate stories", len(stories))

    issue = write_issue(stories, settings)

    out_dir = Path("output")
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / f"{date.today():%Y-%m-%d}.md"
    out_file.write_text(f"# {issue.title}\n\n*{issue.subtitle}*\n\n{issue.markdown}\n")
    logging.info("Saved issue to %s", out_file)

    if args.dry_run:
        logging.info("Dry run: skipping Substack.")
        return

    from .publish import publish_issue

    publish_issue(issue, mode=args.mode, tags=settings.get("tags"))


if __name__ == "__main__":
    main()
