from datetime import date, datetime, timedelta, timezone

from provider import Day, ProviderError, ProviderForecast


def week(start: date, offset: int = 0, et0: float = 3.0, rain: float = 0.0) -> ProviderForecast:
    days = tuple(Day(start + timedelta(days=i), et0 + i / 10, rain) for i in range(7))
    return ProviderForecast(days, offset)


class Clock:
    def __init__(self, now: datetime):
        self.now = now

    def __call__(self) -> datetime:
        return self.now

    def advance(self, **kwargs) -> None:
        self.now += timedelta(**kwargs)


class FakeProvider:
    """Answers from a list, in order; an item that is a ProviderError is raised. The last item repeats."""

    def __init__(self, *answers):
        self.answers = list(answers)
        self.calls: list[tuple[float, float]] = []

    async def fetch(self, lat, lon):
        self.calls.append((lat, lon))
        answer = self.answers.pop(0) if len(self.answers) > 1 else self.answers[0]
        if isinstance(answer, ProviderError):
            raise answer
        return answer


NOON = datetime(2026, 11, 12, 12, 0, tzinfo=timezone.utc)
TODAY = NOON.date()
FAIL = ProviderError("boom")
