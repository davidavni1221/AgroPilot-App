import pytest
from fastapi.testclient import TestClient

from forecast import ForecastService
from helpers import FAIL, NOON, TODAY, Clock, FakeProvider, week
from main import app, get_service


def make_client(provider):
    service = ForecastService(provider, fresh_seconds=10800, max_stale_seconds=86400, retries=2, now=Clock(NOON))
    app.dependency_overrides[get_service] = lambda: service
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()


def test_forecast_response_shape():
    client = make_client(FakeProvider(week(TODAY, et0=3.1)))
    response = client.get("/v1/forecast?lat=31.25&lon=34.79&days=7")
    assert response.status_code == 200
    body = response.json()
    assert body["lat"] == 31.25 and body["lon"] == 34.79
    assert body["source"] == "open-meteo" and body["stale"] is False
    assert body["fetched_at"] == "2026-11-12T12:00:00Z"
    assert len(body["days"]) == 7
    assert body["days"][0] == {"date": "2026-11-12", "et0_mm": 3.1, "rain_mm": 0.0}


def test_days_limits_the_answer_and_defaults_to_seven():
    client = make_client(FakeProvider(week(TODAY)))
    assert len(client.get("/v1/forecast?lat=31.25&lon=34.79&days=2").json()["days"]) == 2
    assert len(client.get("/v1/forecast?lat=31.25&lon=34.79").json()["days"]) == 7


@pytest.mark.parametrize(
    "query",
    [
        "lat=90.1&lon=0&days=1", "lat=-90.1&lon=0&days=1", "lat=0&lon=180.1&days=1", "lat=0&lon=-180.1&days=1",
        "lat=0&lon=0&days=0", "lat=0&lon=0&days=8", "lat=0&lon=0&days=-1", "lat=0&lon=0&days=1.5",
        "lon=0&days=1", "lat=0&days=1", "lat=abc&lon=0&days=1", "lat=nan&lon=0&days=1", "lat=inf&lon=0&days=1",
        "lat=&lon=0&days=1",
    ],
)
def test_invalid_input_is_422_validation(query):
    provider = FakeProvider(week(TODAY))
    response = make_client(provider).get(f"/v1/forecast?{query}")
    assert response.status_code == 422
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["code"] == "VALIDATION"
    assert provider.calls == []  # bad input never reaches the provider


@pytest.mark.parametrize("query", ["lat=90&lon=180&days=1", "lat=-90&lon=-180&days=7"])
def test_boundary_values_are_accepted(query):
    assert make_client(FakeProvider(week(TODAY))).get(f"/v1/forecast?{query}").status_code == 200


def test_provider_failure_without_earlier_forecast_is_503_with_retry_after():
    response = make_client(FakeProvider(FAIL)).get("/v1/forecast?lat=31.25&lon=34.79&days=7")
    assert response.status_code == 503
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.headers["retry-after"] == "60"
    assert response.json()["code"] == "UNAVAILABLE"
    assert "days" not in response.json()  # never a forecast of zeros


def test_stale_forecast_is_marked_stale():
    provider = FakeProvider(week(TODAY), FAIL)
    clock = Clock(NOON)
    service = ForecastService(provider, fresh_seconds=10800, max_stale_seconds=86400, retries=2, now=clock)
    app.dependency_overrides[get_service] = lambda: service
    client = TestClient(app)
    assert client.get("/v1/forecast?lat=31.25&lon=34.79&days=7").json()["stale"] is False
    clock.advance(hours=5)
    body = client.get("/v1/forecast?lat=31.25&lon=34.79&days=7").json()
    assert body["stale"] is True and body["fetched_at"] == "2026-11-12T12:00:00Z"
    assert len(body["days"]) == 7


def test_health_and_unknown_route():
    client = make_client(FakeProvider(week(TODAY)))
    assert client.get("/health").json() == {"status": "ok"}
    response = client.get("/nope")
    assert response.status_code == 404 and response.json()["code"] == "NOT_FOUND"
