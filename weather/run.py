from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import requests

from weather.location import get_longitude_and_latitude_for_address
from weather.types import WeatherResult


def run_weather_request(address: str):
    base_url = "https://api.open-meteo.com/v1/forecast"

    lat, long = get_longitude_and_latitude_for_address(address=address)
    params = {
        "latitude": lat,
        "longitude": long,
        "hourly": "temperature_2m",
        "models": "gfs_seamless",
        "temperature_unit": "fahrenheit"
    }
    
    response = requests.get(base_url, params=params)

    response.raise_for_status()

    data = response.json()
    return WeatherResult(**data)


def show_graph(times: list[datetime], temps: list[float], location: str):
    fig, ax = plt.subplots(figsize=(8, 4.5))

    # Plot with styling
    ax.plot(
        times,
        temps,
        marker="o",
        linestyle="-",
        linewidth=2,
        markersize=6,
        color="#1f77b4",
    )

    # Title & labels
    ax.set_title(f"Temperature for {location}", fontsize=14, pad=15)
    ax.set_xlabel("Date / Time", fontsize=12, labelpad=10)
    ax.set_ylabel("Temperature (°F)", fontsize=12, labelpad=10)

    # Format x-axis dates (simpler format)
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))  # e.g. "Sep 06"
    fig.autofmt_xdate(rotation=30)

    # Gentle grid
    ax.grid(True, linestyle="--", alpha=0.6)

    plt.tight_layout()
    plt.show()