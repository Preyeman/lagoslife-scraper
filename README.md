# LagosLife Web Scraper

A Python web scraper that extracts live data from [lagoslife.app](https://lagoslife.app/) — a JavaScript-heavy virtual city game — and tracks its stats over time.

## What it does

- **Renders JavaScript-heavy pages** using Playwright (headless Chromium) — handles content that plain `requests` + BeautifulSoup can't reach
- **Extracts structured data**: 30+ map locations (with emoji + coming-soon flags), live stats (online users, visits, homes), and social links
- **Saves to multiple formats**: JSON (full snapshot) and CSV (locations list)
- **Tracks trends**: appends live stats to a time-series CSV on every run
- **Runs automatically**: scheduled hourly via Windows Task Scheduler

## Tech stack

- Python 3.14
- Playwright (headless browser automation)
- CSV / JSON output
- Windows Task Scheduler for automation

## Project structure

```
work.py                  — main scraper
run_scraper.bat          — wrapper for Task Scheduler
lagoslife.json           — latest full data snapshot
lagoslife_locations.csv  — locations spreadsheet
stats_history.csv        — time-series stats (grows every run)
scraper.log              — run logs
```

## How to run

```bash
pip install playwright
python -m playwright install chromium
python work.py
```

## Sample output

```
Scraped at: 2026-10-07T15:27:45
Stats: {'online': '124k', 'visits': '20667k', 'homes': '400'}
Locations found: 31
  🎷 Afrika Shrine
  🍲 Amala Shitta
  🏖️ Beach
  ...
```

## Challenges solved

- **Dynamic content**: the site renders everything via JavaScript with persistent network connections (`networkidle` never fires) — solved with `domcontentloaded` + timed waits
- **Windows console encoding**: emoji output crashed `cp1252` — fixed via UTF-8 stream reconfiguration
- **Automation**: scheduled hourly execution with log capture and missed-run catch-up
