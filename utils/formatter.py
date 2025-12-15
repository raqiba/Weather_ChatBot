"""
Utility functions for formatting weather data into markdown
"""

import pandas as pd
from datetime import datetime
from typing import Dict, Any, List


def format_current_weather_md(data: Dict[str, Any]) -> str:
    """Return markdown string for current weather (with emojis)."""
    unit_sym = "°C" if data.get("units") == "metric" else "°F" if data.get("units")=="imperial" else "K"
    updated_ts = data.get("updated")
    updated_str = datetime.fromtimestamp(updated_ts).strftime("%Y-%m-%d %H:%M") if updated_ts else "N/A"
    temp = data.get("temp")
    cond = (data.get("condition") or "Unknown").title()
    humidity = data.get("humidity")
    wind = data.get("wind_speed")

    md = f"""
**📍 {data.get('city')}**  
**🌡 Temperature:** `{temp:.1f}{unit_sym}`  
**☁ Condition:** {cond}  
**💧 Humidity:** {humidity}%  
**💨 Wind:** {wind} m/s  
> _Updated:_ {updated_str}
"""
    return md


def format_forecast_markdown(city: str, units: str, forecast_list: List[Dict], days: int = 3) -> str:
    """Group forecast_list by day and return markdown. forecast_list expected to be OWM 'list' items."""
    unit_sym = "°C" if units == "metric" else "°F" if units=="imperial" else "K"
    # convert to DataFrame for easy grouping
    rows = []
    for item in forecast_list:
        ts = int(item.get("dt", 0))
        dt = datetime.fromtimestamp(ts)
        date = dt.strftime("%Y-%m-%d")
        time = dt.strftime("%H:%M")
        temp = item.get("main", {}).get("temp")
        desc = item.get("weather", [{}])[0].get("description", "").title()
        rows.append({"date": date, "time": time, "temp": temp, "desc": desc})

    df = pd.DataFrame(rows)
    if df.empty:
        return "No forecast available."

    md = f"**🌤 {days}-day forecast for {city}**\n\n"
    for date, g in df.groupby("date"):
        md += f"**📅 {date}** — Min: {g['temp'].min():.1f}{unit_sym}, Max: {g['temp'].max():.1f}{unit_sym}\n\n"
        # show only a few times per day (e.g., 00:00, 08:00, 14:00, 20:00) to avoid huge lists
        times_to_show = ["00:00", "08:00", "14:00", "20:00"]
        # pick nearest times present
        shown = g[g['time'].isin(times_to_show)]
        if shown.empty:
            shown = g.head(4)
        for _, row in shown.iterrows():
            md += f"- {row['time']}: {row['temp']:.1f}{unit_sym}, {row['desc']}\n"
        md += "\n"
    return md