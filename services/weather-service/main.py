from contextlib import asynccontextmanager

import httpx
from fastapi import Depends, FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

from config import get_settings
from forecast import ForecastService, ForecastUnavailable
from provider import SOURCE, OpenMeteoClient

settings = get_settings()  # a missing variable stops the service here, with a clear error


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with httpx.AsyncClient(timeout=settings.provider_timeout_seconds) as http:
        provider = OpenMeteoClient(http, settings.provider_base_url, settings.provider_api_key)
        app.state.service = ForecastService(
            provider,
            fresh_seconds=settings.forecast_fresh_seconds,
            max_stale_seconds=settings.forecast_max_stale_seconds,
            retries=settings.provider_retries,
        )
        yield


app = FastAPI(lifespan=lifespan)


def get_service(request: Request) -> ForecastService:
    return request.app.state.service


# --- Errors: application/problem+json with a `code` (VALIDATION, NOT_FOUND, UNAVAILABLE) ---
def problem_response(status_code: int, code: str, title: str, detail: str, headers: dict | None = None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"type": "about:blank", "title": title, "status": status_code, "detail": detail, "code": code},
        media_type="application/problem+json",
        headers=headers,
    )


@app.exception_handler(ForecastUnavailable)
def unavailable_handler(request: Request, exc: ForecastUnavailable):
    return problem_response(
        503, "UNAVAILABLE", "Service Unavailable", "The forecast provider is unavailable and there is no usable earlier forecast",
        headers={"Retry-After": str(settings.retry_after_seconds)},
    )


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
class ForecastDay(BaseModel):
    date: str
    et0_mm: float
    rain_mm: float


class ForecastResponse(BaseModel):
    lat: float
    lon: float
    source: str
    fetched_at: str
    stale: bool
    days: list[ForecastDay]


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/v1/forecast", response_model=ForecastResponse)
async def get_forecast(
    lat: float = Query(ge=-90, le=90),
    lon: float = Query(ge=-180, le=180),
    days: int = Query(default=7, ge=1, le=7),
    service: ForecastService = Depends(get_service),
):
    result = await service.get(lat, lon, days)
    return {
        "lat": lat,
        "lon": lon,
        "source": SOURCE,
        "fetched_at": result.fetched_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "stale": result.stale,
        "days": [{"date": d.date.isoformat(), "et0_mm": d.et0_mm, "rain_mm": d.rain_mm} for d in result.days],
    }
