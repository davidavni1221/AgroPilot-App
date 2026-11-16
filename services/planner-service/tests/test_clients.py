import httpx
import pytest

from clients import PlotNotFound, RegistryClient, UpstreamUnavailable, WeatherClient

PLOT = {"id": "p1", "farm_id": "f", "name": "North", "area_m2": 1000, "crop_id": "tomato", "planting_date": "2026-03-01",
        "soil_id": "loam", "row_spacing_m": 1.5, "emitter_spacing_m": 0.4, "emitter_id": "dripnet-pc-1.0", "lat": 31.25, "lon": 34.79}
SOIL = {"id": "loam", "name": "Loam", "available_water_mm_per_m": 175}
EMITTER = {"id": "dripnet-pc-1.0", "name": "DripNet PC", "flow_lph": 1.0}
CROP = {"id": "tomato", "name": "Tomato"}
FORECAST = {"lat": 31.25, "lon": 34.79, "source": "open-meteo", "fetched_at": "2026-11-12T06:00:00Z", "stale": False,
            "days": [{"date": f"2026-11-{12 + i}", "et0_mm": 3.0, "rain_mm": 0.0} for i in range(3)]}


def http(handler):
    return httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://upstream.test")


def registry_handler(overrides=None):
    answers = {"/v1/plots/p1": PLOT, "/v1/soils/loam": SOIL, "/v1/emitters/dripnet-pc-1.0": EMITTER, "/v1/crops/tomato": CROP}
    answers.update(overrides or {})

    def handler(request):
        answer = answers.get(request.url.path)
        if isinstance(answer, httpx.Response):
            return answer
        return httpx.Response(404, json={"code": "NOT_FOUND"}) if answer is None else httpx.Response(200, json=answer)

    return handler


async def test_registry_returns_plot_soil_emitter_and_crop():
    data = await RegistryClient(http(registry_handler())).plot_data("p1")
    assert data.plot.area_m2 == 1000 and data.soil.available_water_mm_per_m == 175 and data.emitter.flow_lph == 1.0


async def test_unknown_plot_is_plot_not_found():
    with pytest.raises(PlotNotFound):
        await RegistryClient(http(registry_handler())).plot_data("nope")


@pytest.mark.parametrize(
    "overrides",
    [
        {"/v1/plots/p1": httpx.Response(503, json={"code": "UNAVAILABLE"})},
        {"/v1/plots/p1": httpx.Response(200, text="not json")},
        {"/v1/plots/p1": {**PLOT, "area_m2": None}},
        {"/v1/soils/loam": httpx.Response(500)},
        {"/v1/soils/loam": None},  # a plot whose soil is missing is broken data, not a reason to guess
        {"/v1/emitters/dripnet-pc-1.0": {"id": "x"}},
        {"/v1/crops/tomato": httpx.Response(503)},
    ],
)
async def test_registry_problems_name_the_registry(overrides):
    with pytest.raises(UpstreamUnavailable) as caught:
        await RegistryClient(http(registry_handler(overrides))).plot_data("p1")
    assert caught.value.service == "registry-service"


@pytest.mark.parametrize("error", [httpx.ReadTimeout("slow"), httpx.ConnectError("down")], ids=["timeout", "unreachable"])
async def test_registry_timeout_or_down_names_the_registry(error):
    def handler(request):
        raise error

    with pytest.raises(UpstreamUnavailable) as caught:
        await RegistryClient(http(handler)).plot_data("p1")
    assert caught.value.service == "registry-service"


async def test_weather_returns_the_forecast():
    client = WeatherClient(http(lambda r: httpx.Response(200, json=FORECAST)))
    forecast = await client.forecast(31.25, 34.79, 3)
    assert forecast.stale is False and [d.et0_mm for d in forecast.days] == [3.0, 3.0, 3.0]


async def test_weather_request_carries_the_plot_coordinates_and_days():
    seen = {}

    def handler(request):
        seen.update(request.url.params)
        return httpx.Response(200, json=FORECAST)

    await WeatherClient(http(handler)).forecast(31.25, 34.79, 3)
    assert seen == {"lat": "31.25", "lon": "34.79", "days": "3"}


@pytest.mark.parametrize(
    "response",
    [
        httpx.Response(503, json={"code": "UNAVAILABLE"}),
        httpx.Response(422, json={"code": "VALIDATION"}),
        httpx.Response(200, text="<html>"),
        httpx.Response(200, json={"stale": False}),
        httpx.Response(200, json={**FORECAST, "days": [{"date": "2026-11-12", "et0_mm": None, "rain_mm": 0}] * 3}),
        httpx.Response(200, json={**FORECAST, "days": FORECAST["days"][:2]}),  # fewer days than asked
    ],
    ids=["503", "422", "not-json", "no-days", "null-et0", "too-few-days"],
)
async def test_weather_problems_name_the_weather_service(response):
    with pytest.raises(UpstreamUnavailable) as caught:
        await WeatherClient(http(lambda r: response)).forecast(31.25, 34.79, 3)
    assert caught.value.service == "weather-service"


@pytest.mark.parametrize("error", [httpx.ReadTimeout("slow"), httpx.ConnectError("down")], ids=["timeout", "unreachable"])
async def test_weather_timeout_or_down_names_the_weather_service(error):
    def handler(request):
        raise error

    with pytest.raises(UpstreamUnavailable) as caught:
        await WeatherClient(http(handler)).forecast(31.25, 34.79, 3)
    assert caught.value.service == "weather-service"
