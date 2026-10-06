# Ethical Web Scraper

A clean, ethical, config-driven web scraping project: extract structured data
(title, price/date, link, category) from almost any site, store it in SQLite,
export to CSV, and query it through a REST API + simple web UI.

## Features

- **Config-driven** — add any site by writing a small JSON profile (CSS selectors).
- **Polite scraping** — sends an honest User-Agent, rate-limits requests,
  retries with exponential backoff, respects HTTP 429.
- **Pagination** — follows a `{page}` URL template up to `max_pages`.
- **Storage** — SQLite with de-duplication by URL.
- **CSV export** — one-click export of everything.
- **FastAPI** — REST endpoints to query/filter data, trigger scrapes, export CSV.
- **Scheduling** — APScheduler runs scrapes on an interval.
- **Logging** — Python `logging` to console + `scraper.log`.

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
# scrape once (uses profiles/books.json)
python main.py scrape profiles/books.json

# scrape every 60 minutes
python main.py schedule profiles/books.json --minutes 60

# export DB to CSV
python main.py export exports/data.csv

# start API + UI at http://127.0.0.1:8000
python main.py serve
```

## Adding a new site

Copy `profiles/books.json` and change:

```json
{
  "name": "mysite",
  "start_urls": ["https://example.com/list"],
  "pagination_url": "https://example.com/list?page={page}",
  "max_pages": 3,
  "rate_limit_seconds": 2,
  "selectors": {
    "item": ".card",          // one element per record
    "title": "h2 a",
    "price": ".price",        // or remove if not applicable
    "date": "time",
    "date_attr": "datetime",
    "link": "h2 a",
    "category": ".cat"
  }
}
```

Then run `python main.py scrape profiles/mysite.json`.

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/items?search=&category=&source=&limit=&offset=` | List items |
| POST | `/api/scrape?profile_path=profiles/books.json` | Trigger a scrape |
| GET | `/api/export.csv` | Download all data as CSV |
| GET | `/api/stats` | Counts by source/category |
| GET | `/` | Web UI |

## Ethics

- Keep `rate_limit_seconds` reasonable (≥ 2s).
- Only scrape sites whose `robots.txt`/terms allow it.
- Identify your bot honestly in `user_agent`.

## Tests

```bash
python -m pytest tests/
```
