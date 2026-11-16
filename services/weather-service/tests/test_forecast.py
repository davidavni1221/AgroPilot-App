import asyncio
from datetime import datetime, timezone

import pytest

from forecast import ForecastService, ForecastUnavailable, cell, cell_center
from helpers import FAIL, NOON, TODAY, Clock, FakeProvider, week
from provider import ProviderError


def make(provider, clock=None, retries=2):
    clock = clock or Clock(NOON)
    return ForecastService(provider, fresh_seconds=10800, max_stale_seconds=86400, retries=retries, now=clock), clock


def test_cell_rounds_down_to_a_tenth():
    assert cell(31.25, 34.79) == (312, 347)
    assert cell(31.299, 34.7) == (312, 347)
    assert cell(4.35, 0.3) == (43, 3)  # float noise must not move 4.35 or 0.3
    assert cell(-0.05, -180) == (-1, -1800)
    assert cell_center((312, 347)) == (31.25, 34.75)


async def test_fresh_forecast_is_served_without_calling_the_provider_again():
    provider = FakeProvider(week(TODAY))
    service, clock = make(provider)
    first = await service.get(31.25, 34.79, 7)
    clock.advance(hours=2, minutes=59)
    second = await service.get(31.25, 34.79, 7)
    assert len(provider.calls) == 1
    assert first == second and not second.stale


async def test_same_cell_shares_one_forecast_and_other_cells_do_not():
    provider = FakeProvider(week(TODAY))
    service, _ = make(provider)
    await service.get(31.21, 34.70, 7)
    await service.get(31.29, 34.79, 7)
    assert provider.calls == [(31.25, 34.75)]  # the provider is asked about the cell center
    await service.get(31.31, 34.79, 7)
    assert len(provider.calls) == 2


async def test_forecast_older_than_fresh_time_is_fetched_again():
    provider = FakeProvider(week(TODAY))
    service, clock = make(provider)
    await service.get(31.25, 34.79, 7)
    clock.advance(hours=3, seconds=1)
    await service.get(31.25, 34.79, 7)
    assert len(provider.calls) == 2


async def test_days_slices_the_cached_week():
    service, _ = make(FakeProvider(week(TODAY)))
    result = await service.get(31.25, 34.79, 3)
    assert [d.date for d in result.days] == [TODAY, TODAY.replace(day=13), TODAY.replace(day=14)]


async def test_provider_is_retried_twice_then_succeeds():
    provider = FakeProvider(FAIL, FAIL, week(TODAY))
    service, _ = make(provider)
    result = await service.get(31.25, 34.79, 7)
    assert len(provider.calls) == 3 and not result.stale


async def test_provider_failure_without_earlier_forecast_is_unavailable():
    provider = FakeProvider(FAIL)
    service, _ = make(provider)
    with pytest.raises(ForecastUnavailable):
        await service.get(31.25, 34.79, 7)
    assert len(provider.calls) == 3  # first try + 2 retries


async def test_provider_failure_serves_the_last_forecast_as_stale():
    provider = FakeProvider(week(TODAY), FAIL)
    service, clock = make(provider)
    fresh = await service.get(31.25, 34.79, 7)
    clock.advance(hours=4)
    stale = await service.get(31.25, 34.79, 7)
    assert stale.stale and not fresh.stale
    assert stale.fetched_at == fresh.fetched_at  # the old time, so the caller can see how old it is
    assert stale.days == fresh.days
    assert len(provider.calls) == 4  # 1 + (1 try + 2 retries)


async def test_forecast_too_old_is_not_served_even_as_stale():
    provider = FakeProvider(week(TODAY), FAIL)
    service, clock = make(provider)
    await service.get(31.25, 34.79, 7)
    clock.advance(hours=24, seconds=1)
    with pytest.raises(ForecastUnavailable):
        await service.get(31.25, 34.79, 7)


async def test_stale_forecast_after_midnight_serves_only_days_from_today_never_fewer_than_asked():
    late = datetime(2026, 11, 12, 23, 0, tzinfo=timezone.utc)
    provider = FakeProvider(week(TODAY), FAIL)
    service, clock = make(provider, Clock(late))
    await service.get(31.25, 34.79, 7)
    clock.advance(hours=4)  # now 03:00 on the 13th: the cached week has only 6 days left
    result = await service.get(31.25, 34.79, 6)
    assert result.stale and result.days[0].date == TODAY.replace(day=13) and len(result.days) == 6
    with pytest.raises(ForecastUnavailable):
        await service.get(31.25, 34.79, 7)


async def test_today_follows_the_local_time_of_the_point():
    # 22:30 UTC on the 12th is already the 13th at UTC+2
    late = datetime(2026, 11, 12, 22, 30, tzinfo=timezone.utc)
    provider = FakeProvider(week(TODAY.replace(day=13), offset=7200))
    service, _ = make(provider, Clock(late))
    result = await service.get(31.25, 34.79, 7)
    assert result.days[0].date == TODAY.replace(day=13)


async def test_forecast_that_does_not_start_today_is_a_provider_failure():
    provider = FakeProvider(week(TODAY.replace(day=5)))
    service, _ = make(provider)
    with pytest.raises(ForecastUnavailable):
        await service.get(31.25, 34.79, 7)


async def test_waiting_requests_for_one_cell_cause_one_provider_call():
    class Slow(FakeProvider):
        async def fetch(self, lat, lon):
            await asyncio.sleep(0.05)
            return await super().fetch(lat, lon)

    provider = Slow(week(TODAY))
    service, _ = make(provider)
    await asyncio.gather(*[service.get(31.25, 34.79, 7) for _ in range(5)])
    assert len(provider.calls) == 1


async def test_zero_retries_means_one_attempt():
    provider = FakeProvider(ProviderError("x"))
    service, _ = make(provider, retries=0)
    with pytest.raises(ForecastUnavailable):
        await service.get(31.25, 34.79, 7)
    assert len(provider.calls) == 1
