"""The only file that knows Open-Meteo. Its field names never leave this module."""
import math
from dataclasses import dataclass
from datetime import date, timedelta

import httpx

SOURCE = "open-meteo"
FORECAST_DAYS = 7  # always fetch a full week; callers slice what they need

ET0_FIELD = "et0_fao_evapotranspiration"  # mm per day
RAIN_FIELD = "precipitation_sum"  # mm per day, rain + showers + snow (water equivalent)


class ProviderError(Exception):
    """The provider failed: timeout, error status, bad JSON, or a missing or invalid value."""


@dataclass(frozen=True)
class Day:
    date: date
    et0_mm: float
    rain_mm: float


@dataclass(frozen=True)
class ProviderForecast:
    days: tuple[Day, ...]
    utc_offset_seconds: int  # local time at the point; decides which date is "today"


def _number(value, name: str) -> float:
    # null (missing day), strings and booleans are failures. We never fill a value in.
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ProviderError(f"{name}: expected a number, got {value!r}")
    if not math.isfinite(value) or value < 0:
        raise ProviderError(f"{name}: invalid value {value!r}")
    return float(value)


def parse(body) -> ProviderForecast:
    try:
        units = body["daily_units"]
        daily = body["daily"]
        times, et0, rain = daily["time"], daily[ET0_FIELD], daily[RAIN_FIELD]
        offset = body["utc_offset_seconds"]
    except (KeyError, TypeError) as exc:
        raise ProviderError(f"missing field: {exc!r}") from exc

    if units.get(ET0_FIELD) != "mm" or units.get(RAIN_FIELD) != "mm":
        raise ProviderError(f"unexpected units: {units!r}")
    if isinstance(offset, bool) or not isinstance(offset, int):
        raise ProviderError(f"utc_offset_seconds: {offset!r}")
    if not (isinstance(times, list) and isinstance(et0, list) and isinstance(rain, list)):
        raise ProviderError("daily values are not lists")
    if not (len(times) == len(et0) == len(rain) == FORECAST_DAYS):
        raise ProviderError(f"expected {FORECAST_DAYS} days, got {len(times)}/{len(et0)}/{len(rain)}")

    try:
        dates = [date.fromisoformat(t) for t in times]
    except (TypeError, ValueError) as exc:
        raise ProviderError(f"bad date: {exc}") from exc
    if any(b - a != timedelta(days=1) for a, b in zip(dates, dates[1:])):
        raise ProviderError("dates are not consecutive")

    days = tuple(
        Day(d, _number(e, f"et0[{d}]"), _number(r, f"rain[{d}]")) for d, e, r in zip(dates, et0, rain)
    )
    return ProviderForecast(days, offset)


class OpenMeteoClient:
    def __init__(self, http: httpx.AsyncClient, base_url: str, api_key: str):
        self._http = http
        self._base_url = base_url
        self._api_key = api_key

    async def fetch(self, lat: float, lon: float) -> ProviderForecast:
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": f"{ET0_FIELD},{RAIN_FIELD}",
            "forecast_days": FORECAST_DAYS,
            "timezone": "auto",
        }
        if self._api_key:
            params["apikey"] = self._api_key
        try:
            response = await self._http.get(self._base_url, params=params)
        except httpx.HTTPError as exc:
            raise ProviderError(f"request failed: {type(exc).__name__}") from exc
        if response.status_code != 200:
            raise ProviderError(f"status {response.status_code}")
        try:
            body = response.json()
        except ValueError as exc:
            raise ProviderError("body is not JSON") from exc
        return parse(body)
