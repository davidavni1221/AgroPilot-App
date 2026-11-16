from contextlib import asynccontextmanager

import httpx
from fastapi import Depends, FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

import engine
from clients import PlotNotFound, RegistryClient, UpstreamUnavailable, WeatherClient
from config import get_settings

settings = get_settings()  # a missing variable stops the service here, with a clear error


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with (
        httpx.AsyncClient(base_url=settings.registry_url, timeout=settings.registry_timeout_seconds) as registry_http,
        httpx.AsyncClient(base_url=settings.weather_url, timeout=settings.weather_timeout_seconds) as weather_http,
    ):
        app.state.registry = RegistryClient(registry_http)
        app.state.weather = WeatherClient(weather_http)
        yield


app = FastAPI(lifespan=lifespan)


def get_registry(request: Request) -> RegistryClient:
    return request.app.state.registry


def get_weather(request: Request) -> WeatherClient:
    return request.app.state.weather


# --- Errors: application/problem+json with a `code` ---
def problem_response(status_code: int, code: str, title: str, detail: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"type": "about:blank", "title": title, "status": status_code, "detail": detail, "code": code},
        media_type="application/problem+json",
    )


@app.exception_handler(PlotNotFound)
def plot_not_found_handler(request: Request, exc: PlotNotFound):
    return problem_response(404, "NOT_FOUND", "Not Found", "Plot not found")


@app.exception_handler(UpstreamUnavailable)
def upstream_handler(request: Request, exc: UpstreamUnavailable):
    # The detail says which service, so the user sees what to fix. Never a plan of zeros.
    return problem_response(503, "UPSTREAM_UNAVAILABLE", "Service Unavailable", f"{exc.service} {exc.reason}")


@app.exception_handler(engine.PlanError)
def plan_error_handler(request: Request, exc: engine.PlanError):
    return problem_response(422, "VALIDATION", "Unprocessable Entity", f"Cannot plan this plot: {exc}")


@app.exception_handler(StarletteHTTPException)
def http_error_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return problem_response(404, "NOT_FOUND", "Not Found", "Route not found")
    if exc.status_code == 405:
        return problem_response(405, "VALIDATION", "Method Not Allowed", "Method not allowed on this route")
    return problem_response(exc.status_code, "VALIDATION", "Error", str(exc.detail))


@app.exception_handler(RequestValidationError)
def validation_error_handler(request: Request, exc: RequestValidationError):
    details = []
    for err in exc.errors():
        field = ".".join(str(part) for part in err["loc"] if part not in ("body", "query", "path"))
        details.append(f"{field}: {err['msg']}" if field else err["msg"])
    return problem_response(422, "VALIDATION", "Unprocessable Entity", "; ".join(details))


# --- Endpoints ---
class PlanDay(BaseModel):
    date: str
    et0_mm: float
    rain_mm: float
    kc: float
    etc_mm: float
    need_mm: float
    litres: float
    run_minutes: float
    bucket_end_mm: float
    stale: bool


class Plan(BaseModel):
    plot_id: str
    crop_id: str
    bucket_capacity_mm: float
    stale: bool
    days: list[PlanDay]


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/v1/plots/{id}/plan", response_model=Plan)
async def get_plan(
    id: str,
    days: int = Query(default=7, ge=1, le=7),  # checked first, before any other service is called
    registry: RegistryClient = Depends(get_registry),
    weather: WeatherClient = Depends(get_weather),
):
    data = await registry.plot_data(id)
    forecast = await weather.forecast(data.plot.lat, data.plot.lon, days)
    capacity, plan_days = engine.plan(
        crop_id=data.crop.id,
        planting_date=data.plot.planting_date,
        soil_mm_per_m=data.soil.available_water_mm_per_m,
        area_m2=data.plot.area_m2,
        row_spacing_m=data.plot.row_spacing_m,
        emitter_spacing_m=data.plot.emitter_spacing_m,
        emitter_flow_lph=data.emitter.flow_lph,
        forecast=[engine.ForecastDay(d.date, d.et0_mm, d.rain_mm) for d in forecast.days],
    )
    return {
        "plot_id": data.plot.id,
        "crop_id": data.crop.id,
        "bucket_capacity_mm": round(capacity, 2),
        "stale": forecast.stale,
        "days": [
            {
                "date": d.date.isoformat(),
                "et0_mm": d.et0_mm,
                "rain_mm": d.rain_mm,
                "kc": round(d.kc, 3),
                "etc_mm": round(d.etc_mm, 2),
                "need_mm": round(d.need_mm, 2),
                "litres": round(d.litres, 1),
                "run_minutes": round(d.run_minutes, 1),
                "bucket_end_mm": round(d.bucket_end_mm, 2),
                "stale": forecast.stale,  # a stale forecast makes every day stale (FR-2.13)
            }
            for d in plan_days
        ],
    }
