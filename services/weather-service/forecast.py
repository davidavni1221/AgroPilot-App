"""Forecast cache and provider fallback. Knows coordinates and dates, nothing else."""
import asyncio
import math
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Protocol

from provider import Day, ProviderError, ProviderForecast, FORECAST_DAYS


class Provider(Protocol):
    async def fetch(self, lat: float, lon: float) -> ProviderForecast: ...


class ForecastUnavailable(Exception):
    """No forecast can be given honestly: the provider failed and there is no usable earlier one."""


@dataclass(frozen=True)
class Entry:
    forecast: ProviderForecast
    fetched_at: datetime


@dataclass(frozen=True)
class Result:
    days: list[Day]
    fetched_at: datetime
    stale: bool


def cell(lat: float, lon: float) -> tuple[int, int]:
    """The 0.1 degree grid cell of a point: both coordinates rounded down to a tenth."""
    # Decimal(str(x)) avoids float noise, e.g. 4.35 * 10 is not exactly 43.5
    return (
        math.floor(Decimal(str(lat)) * 10),
        math.floor(Decimal(str(lon)) * 10),
    )


def cell_center(key: tuple[int, int]) -> tuple[float, float]:
    return round(key[0] / 10 + 0.05, 2), round(key[1] / 10 + 0.05, 2)


class ForecastService:
    def __init__(
        self,
        provider: Provider,
        fresh_seconds: int,
        max_stale_seconds: int,
        retries: int,
        now: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
    ):
        self._provider = provider
        self._fresh = timedelta(seconds=fresh_seconds)
        self._max_stale = timedelta(seconds=max_stale_seconds)
        self._retries = retries
        self._now = now
        self._cache: dict[tuple[int, int], Entry] = {}  # in memory only; a restart empties it
        self._locks: defaultdict[tuple[int, int], asyncio.Lock] = defaultdict(asyncio.Lock)

    def _window(self, entry: Entry, days: int) -> list[Day] | None:
        """The `days` days starting today (local date at the point), or None if the entry can't cover them."""
        today = (self._now() + timedelta(seconds=entry.forecast.utc_offset_seconds)).date()
        window = [d for d in entry.forecast.days if d.date >= today][:days]
        if len(window) < days or window[0].date != today:
            return None
        return window

    def _answer(self, entry: Entry, days: int, max_age: timedelta, stale: bool) -> Result | None:
        if self._now() - entry.fetched_at > max_age:
            return None
        window = self._window(entry, days)
        return None if window is None else Result(window, entry.fetched_at, stale)

    async def get(self, lat: float, lon: float, days: int) -> Result:
        key = cell(lat, lon)
        entry = self._cache.get(key)
        if entry and (result := self._answer(entry, days, self._fresh, stale=False)):
            return result

        async with self._locks[key]:  # one provider call per cell, even with many waiting requests
            entry = self._cache.get(key)
            if entry and (result := self._answer(entry, days, self._fresh, stale=False)):
                return result
            try:
                new = await self._fetch(key)
            except ProviderError:
                if entry and (result := self._answer(entry, days, self._max_stale, stale=True)):
                    return result
                raise ForecastUnavailable() from None
            self._cache[key] = new
            result = self._answer(new, days, self._fresh, stale=False)
            if result is None:  # cannot happen: _fetch checked a full week from today
                raise ForecastUnavailable()
            return result

    async def _fetch(self, key: tuple[int, int]) -> Entry:
        lat, lon = cell_center(key)
        last: ProviderError | None = None
        for _ in range(1 + self._retries):
            try:
                forecast = await self._provider.fetch(lat, lon)
                entry = Entry(forecast, self._now())
                if self._window(entry, FORECAST_DAYS) is None:
                    raise ProviderError("forecast does not start today")
                return entry
            except ProviderError as exc:
                last = exc
        raise last  # type: ignore[misc]
