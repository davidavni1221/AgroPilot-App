"""Hand-calculated cases. The expected numbers are worked out in the comments, not by running the code.

NFR-2.5: within 0.5%.
"""
from datetime import date, timedelta

import pytest

from crops import CROPS
from engine import ForecastDay, PlanError, kc_for_day, plan, run_minutes, water_day

TOMATO = CROPS["tomato"]  # 30 / 40 / 45 / 30 days, Kc 0.6 / 1.15 / 0.80
PEPPER = CROPS["bell-pepper"]  # 30 / 35 / 40 / 20 days, Kc 0.6 / 1.05 / 0.90


def approx(value):
    return pytest.approx(value, rel=0.005)


def week(start: date, et0: float, rain=(0,) * 7):
    return [ForecastDay(start + timedelta(days=i), et0, rain[i]) for i in range(7)]


# --- The task's own example: a 70 mm bucket that loses 7 mm a day ---
def test_task_example_bucket():
    # Days 1-5: 63, 56, 49, 42, 35 (exactly half, still no irrigation). Day 6 would end at 28, below 35: irrigate.
    level, results = 70.0, []
    for _ in range(6):
        results.append(water_day(level, 70.0, 7.0, 0.0))
        level = results[-1][1]
    assert [r[1] for r in results[:5]] == [63, 56, 49, 42, 35]
    assert [r[0] for r in results[:5]] == [0, 0, 0, 0, 0]
    # Day 6: the morning level is 35, so the refill is 70 - 35 = 35 mm, and the day ends at 70 - 7 = 63.
    assert results[5] == (35.0, 63.0)


# --- Case 1: Kc along the season (tomato: initial to day 30, development to 70, mid to 115, late to 145) ---
@pytest.mark.parametrize(
    "day, expected",
    [
        (1, 0.6),
        (30, 0.6),
        (31, 0.6 + 1 / 40 * 0.55),  # 0.61375
        (50, 0.6 + 20 / 40 * 0.55),  # 0.6 + 0.275 = 0.875
        (70, 1.15),
        (100, 1.15),
        (115, 1.15),
        (130, 1.15 + 15 / 30 * (0.80 - 1.15)),  # 1.15 - 0.175 = 0.975
        (145, 0.80),
        (200, 0.80),  # after the season: held at Kc end (a choice, documented)
    ],
)
def test_kc_along_the_tomato_season(day, expected):
    assert kc_for_day(TOMATO, day) == approx(expected)


def test_kc_not_planted_yet():
    with pytest.raises(PlanError):
        kc_for_day(TOMATO, 0)


# --- Case 2: pepper on sand in mid-season: a small bucket, water on days 4 and 7 ---
# Sand 83 mm/m x 0.5 m = 41.5 mm. Threshold 20.75 mm. Mid Kc 1.05, ET0 6 -> ETc 6.3 mm/day.
# End of day: 35.2, 28.9, 22.6 (no water). Day 4 would end at 16.3 < 20.75: the morning level is 22.6,
# refill 41.5 - 22.6 = 18.9 mm, day ends at 41.5 - 6.3 = 35.2. Then 28.9, 22.6, and day 7 again 18.9 mm.
# 400 m2: 18.9 mm = 7560 L. Emitters 1.2 m x 0.3 m = 0.36 m2 each: 400 / 0.36 = 1111.1 emitters x 2 L/h = 2222.2 L/h.
# 7560 / 2222.2 h = 3.402 h = 204.12 minutes.
def test_pepper_on_sand_in_mid_season():
    start = date(2026, 6, 1) + timedelta(days=80)  # season day 81: inside the mid stage (days 66-105)
    capacity, days = plan("bell-pepper", date(2026, 6, 1), 83, 400, 1.2, 0.3, 2.0, week(start, et0=6.0))
    assert capacity == approx(41.5)
    assert [d.kc for d in days] == [approx(1.05)] * 7
    assert [d.etc_mm for d in days] == [approx(6.3)] * 7
    assert [d.need_mm for d in days] == [0, 0, 0, approx(18.9), 0, 0, approx(18.9)]
    assert [d.bucket_end_mm for d in days] == approx_list([35.2, 28.9, 22.6, 35.2, 28.9, 22.6, 35.2])
    assert days[3].litres == approx(7560)
    assert days[3].run_minutes == approx(204.12)
    assert days[0].run_minutes == 0 and days[0].litres == 0


def approx_list(values):
    return [pytest.approx(v, rel=0.005) for v in values]


# --- Case 3: tomato in development on loam, with rain; the bucket is never below half ---
# Loam 175 mm/m x 0.7 m = 122.5 mm. Season day 50 on day 1 (planted 49 days before). ET0 4 mm/day.
# Kc = 0.6 + (day - 30) x 0.01375: 0.875, 0.88875, 0.9025, 0.91625, 0.93, 0.94375, 0.9575.
# ETc = 4 x Kc: 3.5, 3.555, 3.61, 3.665, 3.72, 3.775, 3.83 (sum 25.655).
# Rain 20 mm on day 3: 122.5 - 3.5 - 3.555 = 115.445 at the end of day 2; +20 caps at 122.5; day 3 ends at 122.5 - 3.61 = 118.89.
# Then 118.89 - 3.665 - 3.72 - 3.775 - 3.83 = 103.9.
def test_tomato_in_development_with_rain():
    start = date(2026, 9, 1)
    planted = start - timedelta(days=49)
    capacity, days = plan("tomato", planted, 175, 1000, 1.5, 0.4, 1.0, week(start, et0=4.0, rain=(0, 0, 20, 0, 0, 0, 0)))
    assert capacity == approx(122.5)
    assert [d.kc for d in days] == approx_list([0.875, 0.88875, 0.9025, 0.91625, 0.93, 0.94375, 0.9575])
    assert [d.etc_mm for d in days] == approx_list([3.5, 3.555, 3.61, 3.665, 3.72, 3.775, 3.83])
    assert days[1].bucket_end_mm == approx(122.5 - 3.5 - 3.555)
    assert days[2].bucket_end_mm == approx(122.5 - 3.61)  # the rain overflows: the extra is lost
    assert days[6].bucket_end_mm == approx(103.9)
    assert all(d.need_mm == 0 for d in days)


# --- Drip run time ---
def test_run_minutes_does_not_depend_on_the_plot_area():
    # 5.75 mm over 0.6 m2 (1.5 x 0.4) = 3.45 L per emitter; at 1 L/h that is 3.45 h = 207 minutes.
    assert run_minutes(5.75, 1.5, 0.4, 1.0) == approx(207)


def test_unknown_crop_cannot_be_planned():
    with pytest.raises(PlanError):
        plan("banana", date(2026, 1, 1), 175, 100, 1.5, 0.4, 1.0, week(date(2026, 9, 1), 4.0))


def test_planting_after_the_forecast_start_cannot_be_planned():
    with pytest.raises(PlanError):
        plan("tomato", date(2026, 9, 5), 175, 100, 1.5, 0.4, 1.0, week(date(2026, 9, 1), 4.0))


def test_same_input_same_output():
    args = ("tomato", date(2026, 3, 1), 175, 1000, 1.5, 0.4, 1.0, week(date(2026, 11, 16), 3.0))
    assert plan(*args) == plan(*args)
