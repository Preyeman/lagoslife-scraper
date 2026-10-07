"""Generate a trend chart from stats_history.csv."""
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import csv
import sys
from datetime import datetime

import matplotlib
matplotlib.use("Agg")  # no display needed — save straight to file


def parse_count(value: str) -> float:
    """Convert '128k' / '20694k' / '400' to a plain number (in thousands)."""
    value = value.strip().lower()
    if value.endswith("k"):
        return float(value[:-1])
    return float(value) / 1000


timestamps, online, visits = [], [], []

with open("stats_history.csv", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        if not row["online"] or not row["visits"]:
            continue
        timestamps.append(datetime.fromisoformat(row["timestamp"]))
        online.append(parse_count(row["online"]))
        visits.append(parse_count(row["visits"]))

if not timestamps:
    sys.exit("No data in stats_history.csv yet.")

fig, ax1 = plt.subplots(figsize=(10, 5))

color1 = "#1f77b4"
ax1.plot(timestamps, online, marker="o", color=color1, label="Online users")
ax1.set_xlabel("Time")
ax1.set_ylabel("Online users (k)", color=color1)
ax1.tick_params(axis="y", labelcolor=color1)
ax1.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
fig.autofmt_xdate()

ax2 = ax1.twinx()
color2 = "#ff7f0e"
ax2.plot(timestamps, visits, marker="s", linestyle="--",
         color=color2, label="Total visits")
ax2.set_ylabel("Visits (k)", color=color2)
ax2.tick_params(axis="y", labelcolor=color2)

plt.title("LagosLife.app — Live Stats Over Time")
fig.tight_layout()
fig.savefig("stats_chart.png", dpi=150)
print(f"Chart saved: stats_chart.png ({len(timestamps)} data points)")
