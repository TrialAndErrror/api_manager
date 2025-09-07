from datetime import datetime

from pydantic import BaseModel, Field


class HourlyData(BaseModel):
    temperature_2m: list[float]
    time: list[datetime]


class HourlyUnits(BaseModel):
    temperature_2m: str
    time: str


class WeatherResult(BaseModel):
    hourly: HourlyData
    hourly_units: HourlyUnits

    elevation: float
    latitude: float
    longitude: float
    timezone: str
    timezone_abbreviation: str
    utc_offset_seconds: int
    generationtime_ms: float
