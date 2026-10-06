"""CLI entry point.

Usage:
    python main.py scrape profiles/books.json
    python main.py schedule profiles/books.json --minutes 60
    python main.py export exports/data.csv
    python main.py serve
"""
from __future__ import annotations

import argparse
import sys

from scraper.config import SiteProfile
from scraper.core import Scraper
from scraper.exporter import export_csv
from scraper.logconf import setup_logging
from scraper.scheduler import start as start_scheduler
from scraper.storage import Storage


def cmd_scrape(args) -> None:
    profile = SiteProfile.from_json(args.profile)
    storage = Storage(args.db)
    with Scraper(profile) as scraper:
        items = scraper.run()
    inserted, skipped = storage.save_items(items)
    export_csv(storage.all_rows(), f"exports/{profile.name}.csv")
    print(f"Done: {len(items)} scraped, {inserted} new, {skipped} duplicates.")


def cmd_schedule(args) -> None:
    profile = SiteProfile.from_json(args.profile)
    storage = Storage(args.db)
    start_scheduler(profile, storage, interval_minutes=args.minutes)


def cmd_export(args) -> None:
    storage = Storage(args.db)
    path = export_csv(storage.all_rows(), args.out)
    print(f"Exported to {path}")


def cmd_serve(args) -> None:
    import uvicorn

    uvicorn.run("api:app", host="127.0.0.1", port=args.port, reload=False)


def main() -> None:
    parser = argparse.ArgumentParser(prog="main.py", description="Ethical web scraper")
    parser.add_argument("--db", default="scraper.db", help="SQLite database path")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("scrape", help="Run a one-off scrape")
    p.add_argument("profile")
    p.set_defaults(func=cmd_scrape)

    p = sub.add_parser("schedule", help="Run periodically")
    p.add_argument("profile")
    p.add_argument("--minutes", type=int, default=60)
    p.set_defaults(func=cmd_schedule)

    p = sub.add_parser("export", help="Export DB to CSV")
    p.add_argument("out", nargs="?", default="exports/export.csv")
    p.set_defaults(func=cmd_export)

    p = sub.add_parser("serve", help="Start the API + UI")
    p.add_argument("--port", type=int, default=8000)
    p.set_defaults(func=cmd_serve)

    args = parser.parse_args()
    setup_logging()
    args.func(args)


if __name__ == "__main__":
    sys.exit(main())
