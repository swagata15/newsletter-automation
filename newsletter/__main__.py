"""Run the pipeline.

    python -m newsletter                                  # today's scheduled issue -> Substack draft
    python -m newsletter --type psychology                # force a category
    python -m newsletter --type tutorial --topic "Build a voice agent in a weekend"
    python -m newsletter --type psychology --count 3      # bulk: next 3 topics from the backlog
    python -m newsletter --type all --count 2 --dry-run   # bulk: 2 per category, saved locally only
    python -m newsletter --render issues/ai-and-the-mind/2026-11-10-*   # re-draw visuals (e.g. add photos)
    python -m newsletter --from-json draft.json --notes notes.md --type psychology --date 2026-11-10

On a scheduled day, if a pre-written issue exists for that day (status "local"), it is posted
instead of generating a new one.

Every issue is saved under issues/<category>/<date>-<title>/ and listed in issues/README.md.
"""

from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

from datetime import date, datetime, timezone

from .models import Issue
from .pipeline import (KINDS, assemble, build, kind_for_today, premade_for, record_history, rerender,
                       write_index)


def main() -> None:
    load_dotenv()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    for noisy in ("httpx", "httpx2", "matplotlib", "urllib3"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    p = argparse.ArgumentParser(description="Generate AI newsletter issues and post them to Substack.")
    p.add_argument("--type", choices=("auto", "all", *KINDS), default=os.getenv("ISSUE_TYPE") or "auto")
    p.add_argument("--topic", default=os.getenv("ISSUE_TOPIC") or None, help="Override the topic (one issue).")
    p.add_argument("--count", type=int, default=int(os.getenv("ISSUE_COUNT") or 1),
                   help="Issues per category (bulk). Topics come from the backlog in config.yaml.")
    p.add_argument("--config", default="config.yaml")
    p.add_argument("--dry-run", action="store_true", help="Save issues locally only; don't touch Substack.")
    p.add_argument("--mode", choices=["draft", "publish"], default=os.getenv("PUBLISH_MODE") or "draft")
    p.add_argument("--render", nargs="+", metavar="FOLDER", help="Re-draw existing issue folders, then exit.")
    p.add_argument("--from-json", metavar="FILE", help="Assemble a hand-written issue.json (no API calls).")
    p.add_argument("--notes", metavar="FILE", help="Research notes for --from-json (used to fact-check visuals).")
    p.add_argument("--date", help="Issue date YYYY-MM-DD for --from-json (folder name and cover).")
    args = p.parse_args()

    config = yaml.safe_load(Path(args.config).read_text())

    if args.render:
        for folder in args.render:
            built = rerender(Path(folder), config)
            logging.info("Re-rendered %s", built.out_dir)
        write_index(config)
        return

    if args.from_json:
        if args.type not in KINDS:
            raise SystemExit("--from-json needs --type weekly|psychology|tutorial")
        issue = Issue.model_validate_json(Path(args.from_json).read_text())
        notes = Path(args.notes).read_text() if args.notes else ""
        built = assemble(args.type, config, issue, notes,
                         issue_date=date.fromisoformat(args.date) if args.date else None)
        status = "local"
        if not args.dry_run:
            from .publish import publish_issue
            publish_issue(built, mode=args.mode, tags=config["issues"][args.type].get("tags"))
            status = "published" if args.mode == "publish" else "draft"
        record_history(built, status, config)
        logging.info("Saved %s (%s)", built.out_dir, status)
        return

    if args.type == "auto" and not args.dry_run:
        kind = kind_for_today(config)
        folder = premade_for(kind, datetime.now(timezone.utc).date())
        if folder:
            logging.info("Posting the pre-written issue scheduled for today: %s", folder)
            from .publish import publish_issue
            built = rerender(folder, config)  # also picks up photos if a Pexels key is now set
            publish_issue(built, mode=args.mode, tags=config["issues"][kind].get("tags"))
            record_history(built, "published" if args.mode == "publish" else "draft", config)
            return
    kinds = list(KINDS) if args.type == "all" else [kind_for_today(config) if args.type == "auto" else args.type]

    jobs = []
    for kind in kinds:
        n = args.count
        if kind == "weekly" and n > 1:
            logging.warning("Only one 'This Week in AI' issue makes sense per week; generating 1, not %d.", n)
            n = 1
        jobs += [kind] * n
    if args.topic and len(jobs) > 1:
        raise SystemExit("--topic sets a single issue; use it without --count / --type all.")

    done, failed = [], []
    for i, kind in enumerate(jobs, 1):
        logging.info("=== Issue %d of %d: %s ===", i, len(jobs), kind)
        try:
            built = build(kind, config, topic=args.topic)
            status = "local"
            if not args.dry_run:
                from .publish import publish_issue
                publish_issue(built, mode=args.mode, tags=config["issues"][kind].get("tags"))
                status = "published" if args.mode == "publish" else "draft"
            record_history(built, status, config)  # also reserves the topic so bulk runs move on
            done.append(f"{kind}: {built.issue.title} -> {built.out_dir}")
        except Exception as exc:  # keep going in bulk mode; report at the end
            logging.exception("Issue %d (%s) failed", i, kind)
            failed.append(f"{kind}: {exc}")

    write_index(config)
    logging.info("Finished: %d issue(s) created, %d failed.", len(done), len(failed))
    for line in done:
        logging.info("  OK  %s", line)
    for line in failed:
        logging.error("  FAIL %s", line)
    if failed and not done:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
