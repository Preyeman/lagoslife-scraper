from playwright._impl._errors import TimeoutError as PwTimeout
from playwright.sync_api import sync_playwright
import csv
import json
import os
import re
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


URL = "https://lagoslife.app/"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    try:
        page.goto(URL, wait_until="domcontentloaded", timeout=60000)
    except PwTimeout:
        print("goto timed out, extracting whatever loaded...", flush=True)
    page.wait_for_timeout(5000)  # let JavaScript render the content

    body_text = page.locator("body").inner_text()

    # --- Parse locations (emoji + name pairs) ---
    lines = [line.strip() for line in body_text.splitlines() if line.strip()]
    locations = []
    i = 0
    while i < len(lines) - 1:
        # An emoji line (1-4 chars, no letters) followed by a name line
        if len(lines[i]) <= 4 and not re.search(r"[a-zA-Z0-9@]", lines[i]):
            name = lines[i + 1]
            coming_soon = "Coming soon" in name
            # Skip non-location lines (e.g. the cookie notice)
            if len(name) < 40 and not name.lower().startswith(("we use", "essential")):
                locations.append({
                    "emoji": lines[i],
                    "name": name.replace("🚧", "").replace("· Coming soon", "").strip(),
                    "coming_soon": coming_soon,
                })
            i += 2
        else:
            i += 1

    # --- Parse live stats ---
    stats = {}
    for line in lines:
        m = re.search(r"([\d.]+k?) online", line, re.I)
        if m:
            stats["online"] = m.group(1)
        m = re.search(r"👀\s*([\d.k]+)\s*visits", line, re.I)
        if m:
            stats["visits"] = m.group(1)
        m = re.search(r"(\d+)\s*homes", line, re.I)
        if m:
            stats["homes"] = m.group(1)

    # --- Parse links ---
    links = [
        {"text": (link.inner_text().strip() or "(no text)"),
         "href": link.get_attribute("href")}
        for link in page.locator("a[href]").all()
    ]

    browser.close()

# --- Save results ---
timestamp = datetime.now().isoformat(timespec="seconds")
result = {
    "scraped_at": timestamp,
    "url": URL,
    "stats": stats,
    "locations": locations,
    "links": links,
}

with open("lagoslife.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

with open("lagoslife_locations.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=["emoji", "name", "coming_soon"])
    writer.writeheader()
    writer.writerows(locations)

# --- Append stats to history log ---
history_file = "stats_history.csv"
write_header = not os.path.exists(history_file)
with open(history_file, "a", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(
        f, fieldnames=["timestamp", "online", "visits", "homes"])
    if write_header:
        writer.writeheader()
    writer.writerow({
        "timestamp": timestamp,
        "online": stats.get("online", ""),
        "visits": stats.get("visits", ""),
        "homes": stats.get("homes", ""),
    })

# --- Summary ---
print(f"Scraped at: {timestamp}")
print(f"Stats: {stats}")
print(f"Locations found: {len(locations)}")
for loc in locations:
    tag = " (coming soon)" if loc["coming_soon"] else ""
    print(f"  {loc['emoji']} {loc['name']}{tag}")
print(f"\nSaved: lagoslife.json, lagoslife_locations.csv, {history_file}")
