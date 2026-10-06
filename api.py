"""FastAPI app: query scraped data, trigger runs, download CSV."""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from scraper.config import SiteProfile
from scraper.core import Scraper
from scraper.exporter import export_csv
from scraper.logconf import setup_logging
from scraper.storage import Storage

setup_logging()
app = FastAPI(title="Ethical Scraper API", version="1.0.0")
storage = Storage()

BASE = Path(__file__).parent
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")


@app.get("/", response_class=HTMLResponse)
def index():
    return (BASE / "static" / "index.html").read_text(encoding="utf-8")


@app.get("/api/items")
def list_items(
    source: str | None = None,
    category: str | None = None,
    search: str | None = None,
    limit: int = Query(100, le=1000),
    offset: int = 0,
):
    return {"total": storage.count(), "items": storage.query(source, category, search, limit, offset)}


@app.post("/api/scrape")
def trigger_scrape(profile_path: str):
    """Run a scrape using a profile JSON file (e.g. profiles/books.json)."""
    path = Path(profile_path)
    if not path.exists():
        raise HTTPException(404, f"Profile not found: {profile_path}")
    try:
        profile = SiteProfile.from_json(path)
        with Scraper(profile) as scraper:
            items = scraper.run()
        inserted, skipped = storage.save_items(items)
        export_csv(storage.all_rows(), f"exports/{profile.name}.csv")
        return {"profile": profile.name, "scraped": len(items), "inserted": inserted, "skipped": skipped}
    except Exception as exc:
        raise HTTPException(500, str(exc))


@app.get("/api/export.csv")
def download_csv():
    rows = storage.all_rows()
    if not rows:
        raise HTTPException(404, "No data to export")
    path = export_csv(rows, "exports/export.csv")
    return FileResponse(path, media_type="text/csv", filename="export.csv")


@app.get("/api/stats")
def stats():
    rows = storage.all_rows()
    by_source: dict[str, int] = {}
    by_category: dict[str, int] = {}
    for r in rows:
        by_source[r["source"]] = by_source.get(r["source"], 0) + 1
        by_category[r["category"]] = by_category.get(r["category"], 0) + 1
    return {"total": len(rows), "by_source": by_source, "by_category": by_category}
