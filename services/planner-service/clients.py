"""Calls to registry-service and weather-service. HTTP only, never their code.

Any failure to get a complete, valid answer raises UpstreamUnavailable naming the service.
A plan is never built from a partial answer.
"""
from datetime import date

import httpx
from pydantic import BaseModel, ValidationError

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
    area_m2: float
    crop_id: str
    planting_date: date
    soil_id: str
    row_spacing_m: float
    emitter_spacing_m: float
    emitter_id: str
    lat: float
    lon: float


class Soil(BaseModel):
    id: str
    available_water_mm_per_m: float


class Emitter(BaseModel):
    id: str
    flow_lph: float


class Crop(BaseModel):
    id: str


# --- What we read from weather-service ---
class ForecastDay(BaseModel):
    date: date
    et0_mm: float
    rain_mm: float


class Forecast(BaseModel):
    stale: bool
    days: list[ForecastDay]


class PlotData(BaseModel):
    plot: Plot
    soil: Soil
    emitter: Emitter
    crop: Crop


async def _get(http: httpx.AsyncClient, service: str, url: str, params: dict | None = None) -> httpx.Response:
    try:
        return await http.get(url, params=params)
    except httpx.TimeoutException:
        raise UpstreamUnavailable(service, "did not answer in time") from None
    except httpx.HTTPError as exc:
        raise UpstreamUnavailable(service, f"is not reachable ({type(exc).__name__})") from None


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
        response = await _get(self._http, REGISTRY, f"/v1/plots/{plot_id}")
        if response.status_code == 404:
            raise PlotNotFound()
        plot = _parse(REGISTRY, Plot, response)
        soil = _parse(REGISTRY, Soil, await _get(self._http, REGISTRY, f"/v1/soils/{plot.soil_id}"))
        emitter = _parse(REGISTRY, Emitter, await _get(self._http, REGISTRY, f"/v1/emitters/{plot.emitter_id}"))
        crop = _parse(REGISTRY, Crop, await _get(self._http, REGISTRY, f"/v1/crops/{plot.crop_id}"))
        return PlotData(plot=plot, soil=soil, emitter=emitter, crop=crop)


class WeatherClient:
    def __init__(self, http: httpx.AsyncClient):
        self._http = http

    async def forecast(self, lat: float, lon: float, days: int) -> Forecast:
        response = await _get(self._http, WEATHER, "/v1/forecast", {"lat": lat, "lon": lon, "days": days})
        forecast = _parse(WEATHER, Forecast, response)
        if len(forecast.days) != days:
            raise UpstreamUnavailable(WEATHER, f"sent {len(forecast.days)} days, expected {days}")
        return forecast
