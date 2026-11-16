import copy

import httpx
import pytest

from provider import FORECAST_DAYS, OpenMeteoClient, ProviderError, parse

BODY = {
    "utc_offset_seconds": 7200,
    "daily_units": {"time": "iso8601", "et0_fao_evapotranspiration": "mm", "precipitation_sum": "mm"},
    "daily": {
        "time": [f"2026-11-{12 + i}" for i in range(7)],
        "et0_fao_evapotranspiration": [3.1, 2.8, 2.5, 2.9, 3.0, 3.2, 2.2],
        "precipitation_sum": [0.0, 4.2, 0.0, 0.0, 0.1, 0.0, 0.3],
    },
}


def client(handler, api_key=""):
    http = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    return OpenMeteoClient(http, "http://provider.test/v1/forecast", api_key)


def mutated(change):
    body = copy.deepcopy(BODY)
    change(body)
    return body


def test_parse_translates_names_and_keeps_provider_zeros():
    forecast = parse(BODY)
    assert forecast.utc_offset_seconds == 7200
    assert len(forecast.days) == FORECAST_DAYS
    assert (forecast.days[0].date.isoformat(), forecast.days[0].et0_mm, forecast.days[0].rain_mm) == ("2026-11-12", 3.1, 0.0)
    assert forecast.days[1].rain_mm == 4.2


BAD_BODIES = {
    "null et0": mutated(lambda b: b["daily"]["et0_fao_evapotranspiration"].__setitem__(2, None)),
    "null rain": mutated(lambda b: b["daily"]["precipitation_sum"].__setitem__(0, None)),
    "string value": mutated(lambda b: b["daily"]["precipitation_sum"].__setitem__(0, "0.0")),
    "negative et0": mutated(lambda b: b["daily"]["et0_fao_evapotranspiration"].__setitem__(0, -1)),
    "missing et0": mutated(lambda b: b["daily"].pop("et0_fao_evapotranspiration")),
    "missing daily": mutated(lambda b: b.pop("daily")),
    "missing offset": mutated(lambda b: b.pop("utc_offset_seconds")),
    "six days": mutated(lambda b: [v.pop() for v in b["daily"].values()]),
    "uneven lists": mutated(lambda b: b["daily"]["precipitation_sum"].pop()),
    "wrong units": mutated(lambda b: b["daily_units"].__setitem__("et0_fao_evapotranspiration", "inch")),
    "gap in dates": mutated(lambda b: b["daily"]["time"].__setitem__(3, "2026-11-30")),
    "bad date": mutated(lambda b: b["daily"]["time"].__setitem__(0, "tomorrow")),
    "not an object": [],
}


@pytest.mark.parametrize("body", BAD_BODIES.values(), ids=BAD_BODIES.keys())
def test_parse_rejects_bad_bodies(body):
    with pytest.raises(ProviderError):
        parse(body)


async def test_fetch_sends_the_expected_request():
    seen = {}

    def handler(request):
        seen.update(request.url.params)
        return httpx.Response(200, json=BODY)

    await client(handler).fetch(31.25, 34.75)
    assert seen["latitude"] == "31.25" and seen["longitude"] == "34.75"
    assert seen["daily"] == "et0_fao_evapotranspiration,precipitation_sum"
    assert seen["forecast_days"] == "7" and seen["timezone"] == "auto"
    assert "apikey" not in seen


async def test_fetch_sends_api_key_when_set():
    seen = {}

    def handler(request):
        seen.update(request.url.params)
        return httpx.Response(200, json=BODY)

    await client(handler, api_key="secret").fetch(31.25, 34.75)
    assert seen["apikey"] == "secret"


@pytest.mark.parametrize(
    "handler",
    [
        lambda r: httpx.Response(500),
        lambda r: httpx.Response(429, json={"reason": "limit"}),
        lambda r: httpx.Response(200, text="<html>not json</html>"),
        lambda r: httpx.Response(200, json={"error": True, "reason": "bad"}),
        lambda r: (_ for _ in ()).throw(httpx.ReadTimeout("slow")),
        lambda r: (_ for _ in ()).throw(httpx.ConnectError("down")),
    ],
    ids=["500", "429", "not-json", "error-body", "timeout", "connect-error"],
)
async def test_fetch_failures_become_provider_errors(handler):
    with pytest.raises(ProviderError):
        await client(handler).fetch(31.25, 34.75)
