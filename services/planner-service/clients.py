"""Calls to registry-service and weather-service. HTTP only, never their code.

Any failure to get a complete, valid answer raises UpstreamUnavailable naming the service.
A plan is never built from a partial answer.
"""
import asyncio
from datetime import date, timedelta
from urllib.parse import quote

import httpx
from pydantic import BaseModel, Field, ValidationError

REGISTRY = "registry-service"
WEATHER = "weather-service"


class UpstreamUnavailable(Exception):
    def __init__(self, service: str, reason: str):
        super().__init__(f"{service}: {reason}")
        self.service = service
        self.reason = reason


class PlotNotFound(Exception):
    pass


# --- What we read from registry-service (only the fields the plan needs) ---
class Plot(BaseModel):
    id: str
    area_m2: float = Field(gt=0)
    crop_id: str
    planting_date: date
    soil_id: str
    row_spacing_m: float = Field(gt=0)
    emitter_spacing_m: float = Field(gt=0)
    emitter_id: str
    lat: float
    lon: float


class Soil(BaseModel):
    id: str
    available_water_mm_per_m: float = Field(gt=0)


class Emitter(BaseModel):
    id: str
    flow_lph: float = Field(gt=0)


# --- What we read from weather-service ---
class ForecastDay(BaseModel):
    date: date
    et0_mm: float = Field(ge=0, allow_inf_nan=False)
    rain_mm: float = Field(ge=0, allow_inf_nan=False)


class Forecast(BaseModel):
    stale: bool
    days: list[ForecastDay]


class PlotData(BaseModel):
    plot: Plot
    soil: Soil
    emitter: Emitter


async def _get(http: httpx.AsyncClient, service: str, url: str, params: dict | None = None) -> httpx.Response:
    try:
        return await http.get(url, params=params)
    except httpx.TimeoutException:
        raise UpstreamUnavailable(service, "did not answer in time") from None
    except httpx.HTTPError as exc:
        raise UpstreamUnavailable(service, "is not reachable") from None


def _parse(service: str, model, response: httpx.Response):
    if response.status_code != 200:
        raise UpstreamUnavailable(service, f"answered with status {response.status_code}")
    try:
        return model.model_validate(response.json())
    except (ValueError, ValidationError):
        raise UpstreamUnavailable(service, "sent an answer that cannot be used") from None


class RegistryClient:
    def __init__(self, http: httpx.AsyncClient):
        self._http = http

    async def plot_data(self, plot_id: str) -> PlotData:
        response = await _get(self._http, REGISTRY, f"/v1/plots/{quote(plot_id, safe='')}")
        if response.status_code == 404:
            raise PlotNotFound()
        plot = _parse(REGISTRY, Plot, response)
        soil_response, emitter_response = await asyncio.gather(
            _get(self._http, REGISTRY, f"/v1/soils/{quote(plot.soil_id, safe='')}"),
            _get(self._http, REGISTRY, f"/v1/emitters/{quote(plot.emitter_id, safe='')}"),
        )
        return PlotData(
            plot=plot,
            soil=_parse(REGISTRY, Soil, soil_response),
            emitter=_parse(REGISTRY, Emitter, emitter_response),
        )


class WeatherClient:
    def __init__(self, http: httpx.AsyncClient):
        self._http = http

    async def forecast(self, lat: float, lon: float, days: int) -> Forecast:
        response = await _get(self._http, WEATHER, "/v1/forecast", {"lat": lat, "lon": lon, "days": days})
        forecast = _parse(WEATHER, Forecast, response)
        if len(forecast.days) != days:
            raise UpstreamUnavailable(WEATHER, f"sent {len(forecast.days)} days, expected {days}")
        dates = [d.date for d in forecast.days]
        if any(b - a != timedelta(days=1) for a, b in zip(dates, dates[1:])):
            raise UpstreamUnavailable(WEATHER, "sent days that are not consecutive")
        return forecast
