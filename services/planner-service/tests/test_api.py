import httpx
import pytest
from fastapi.testclient import TestClient

from clients import RegistryClient, WeatherClient
from main import app, get_registry, get_weather

PLOT = {"id": "p1", "farm_id": "f", "name": "North", "area_m2": 400, "crop_id": "bell-pepper", "planting_date": "2026-06-01",
        "soil_id": "sand", "row_spacing_m": 1.2, "emitter_spacing_m": 0.3, "emitter_id": "e2", "lat": 31.25, "lon": 34.79}
ROUTES = {"/v1/plots/p1": PLOT, "/v1/soils/sand": {"id": "sand", "name": "Sand", "available_water_mm_per_m": 83},
          "/v1/emitters/e2": {"id": "e2", "name": "E", "flow_lph": 2.0}, "/v1/crops/bell-pepper": {"id": "bell-pepper", "name": "Bell pepper"}}


def forecast_body(stale=False, days=7):
    # Season day 81 on the first day: the mid stage, Kc 1.05. ET0 6 mm/day.
    return {"lat": 31.25, "lon": 34.79, "source": "open-meteo", "fetched_at": "2026-08-20T05:00:00Z", "stale": stale,
            "days": [{"date": f"2026-08-{20 + i}", "et0_mm": 6.0, "rain_mm": 0.0} for i in range(days)]}


def make_client(registry=None, weather=None, calls=None):
    def registry_handler(request):
        if calls is not None:
            calls.append("registry")
        answer = ROUTES.get(request.url.path)
        return httpx.Response(404, json={"code": "NOT_FOUND"}) if answer is None else httpx.Response(200, json=answer)

    def weather_handler(request):
        if calls is not None:
            calls.append("weather")
        return httpx.Response(200, json=forecast_body(days=int(request.url.params["days"])))

    app.dependency_overrides[get_registry] = lambda: RegistryClient(
        httpx.AsyncClient(transport=httpx.MockTransport(registry or registry_handler), base_url="http://r.test"))
    app.dependency_overrides[get_weather] = lambda: WeatherClient(
        httpx.AsyncClient(transport=httpx.MockTransport(weather or weather_handler), base_url="http://w.test"))
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()


def test_plan_for_a_plot():
    response = make_client().get("/v1/plots/p1/plan?days=7")
    assert response.status_code == 200
    body = response.json()
    assert body["plot_id"] == "p1" and body["crop_id"] == "bell-pepper" and body["stale"] is False
    assert body["bucket_capacity_mm"] == 41.5
    assert len(body["days"]) == 7
    assert body["days"][0] == {"date": "2026-08-20", "et0_mm": 6.0, "rain_mm": 0.0, "kc": 1.05, "etc_mm": 6.3, "need_mm": 0.0,
                               "litres": 0.0, "run_minutes": 0.0, "bucket_end_mm": 35.2, "stale": False}
    assert body["days"][3]["need_mm"] == 18.9 and body["days"][3]["litres"] == 7560.0 and body["days"][3]["run_minutes"] == 204.1


def test_days_defaults_to_seven_and_limits_the_plan():
    client = make_client()
    assert len(client.get("/v1/plots/p1/plan").json()["days"]) == 7
    assert len(client.get("/v1/plots/p1/plan?days=3").json()["days"]) == 3


@pytest.mark.parametrize("days", ["0", "8", "-1", "abc", "1.5"])
def test_bad_days_is_422_and_no_other_service_is_called(days):
    calls = []
    response = make_client(calls=calls).get(f"/v1/plots/p1/plan?days={days}")
    assert response.status_code == 422
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["code"] == "VALIDATION"
    assert calls == []


def test_unknown_plot_is_404():
    response = make_client().get("/v1/plots/nope/plan")
    assert response.status_code == 404 and response.json()["code"] == "NOT_FOUND"


def test_stale_forecast_still_gives_a_plan_with_every_day_stale():
    def weather(request):
        return httpx.Response(200, json=forecast_body(stale=True, days=int(request.url.params["days"])))

    body = make_client(weather=weather).get("/v1/plots/p1/plan").json()
    assert body["stale"] is True and all(d["stale"] is True for d in body["days"])
    assert body["days"][3]["run_minutes"] == 204.1  # the numbers are the same, only marked


@pytest.mark.parametrize(
    "weather_response",
    [httpx.Response(503, json={"code": "UNAVAILABLE"}), httpx.Response(200, text="oops"), httpx.Response(500)],
    ids=["503", "not-json", "500"],
)
def test_weather_down_is_503_naming_weather_service(weather_response):
    response = make_client(weather=lambda r: weather_response).get("/v1/plots/p1/plan")
    assert response.status_code == 503
    assert response.headers["content-type"].startswith("application/problem+json")
    body = response.json()
    assert body["code"] == "UPSTREAM_UNAVAILABLE" and "weather-service" in body["detail"]
    assert "days" not in body  # never a plan of zeros


def test_weather_timeout_is_503_naming_weather_service():
    def weather(request):
        raise httpx.ReadTimeout("slow")

    body = make_client(weather=weather).get("/v1/plots/p1/plan").json()
    assert body["code"] == "UPSTREAM_UNAVAILABLE" and "weather-service" in body["detail"]


def test_registry_down_is_503_naming_registry_and_weather_is_not_called():
    calls = []

    def registry(request):
        calls.append("registry")
        return httpx.Response(503, json={"code": "UNAVAILABLE"})

    response = make_client(registry=registry, calls=calls).get("/v1/plots/p1/plan")
    assert response.status_code == 503
    assert "registry-service" in response.json()["detail"]
    assert "weather" not in calls


def test_plot_with_unsupported_crop_is_422():
    routes = {**ROUTES, "/v1/plots/p1": {**PLOT, "crop_id": "banana"}, "/v1/crops/banana": {"id": "banana", "name": "Banana"}}

    def registry(request):
        answer = routes.get(request.url.path)
        return httpx.Response(404) if answer is None else httpx.Response(200, json=answer)

    response = make_client(registry=registry).get("/v1/plots/p1/plan")
    assert response.status_code == 422 and response.json()["code"] == "VALIDATION"
    assert "banana" in response.json()["detail"]


def test_health_and_unknown_route():
    client = make_client()
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/nope").json()["code"] == "NOT_FOUND"
