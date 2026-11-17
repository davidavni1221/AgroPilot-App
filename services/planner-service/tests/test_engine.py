"""Hand-calculated cases. The expected numbers are worked out in the comments, not by running the code.

NFR-2.5: within 0.5%.
"""
from datetime import date, timedelta

import pytest

from crops import CropParams
from engine import ForecastDay, PlanError, kc_for_day, plan, run_minutes, water_day

# The numbers the registry holds for these two crops (FAO-56), written out here so the checks do not depend on it.
TOMATO = CropParams(kc_ini=0.6, kc_mid=1.15, kc_end=0.80, l_ini=30, l_dev=40, l_mid=45, l_late=30, root_depth_m=0.7)
PEPPER = CropParams(kc_ini=0.6, kc_mid=1.05, kc_end=0.90, l_ini=30, l_dev=35, l_mid=40, l_late=20, root_depth_m=0.5)


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
    # Day 6: irrigate what the crop uses, 7 mm, so the day ends where it started, at 35.
    assert results[5] == (7.0, 35.0)


def test_rain_above_the_top_of_the_bucket_is_lost():
    # 100 + 50 mm of rain is capped at 122.5; the crop then uses 4 mm: 118.5, far above the line, so no irrigation.
    assert water_day(100.0, 122.5, 4.0, 50.0) == (0.0, 118.5)


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


# --- Case 2: pepper on sand in mid-season, 10 mm of rain on day 3 ---
# Sand 83 mm/m x 0.5 m = 41.5 mm. The line is 20.75 mm and today starts there. Mid Kc 1.05, ET0 6 -> ETc 6.3 mm/day.
# Days 1 and 2: the day would end at 20.75 - 6.3 = 14.45, below the line: irrigate 6.3 mm, the day ends at 20.75.
# Day 3: rain 10 mm lifts it to 30.75; 30.75 - 6.3 = 24.45 is above the line: no irrigation, ends at 24.45.
# Days 4-7: 24.45 - 6.3 = 18.15 is below the line: irrigate 6.3 mm, ends at 24.45.
# 400 m2: 6.3 mm = 2520 L. Emitters 1.2 m x 0.3 m = 0.36 m2 each: 400 / 0.36 = 1111.1 emitters x 2 L/h = 2222.2 L/h.
# 2520 / 2222.2 h = 1.134 h = 68.04 minutes (also 6.3 x 0.36 / 2 x 60).
def test_pepper_on_sand_in_mid_season_with_rain():
    start = date(2026, 6, 1) + timedelta(days=80)  # season day 81: inside the mid stage (days 66-105)
    rain = (0, 0, 10, 0, 0, 0, 0)
    capacity, days = plan(PEPPER, date(2026, 6, 1), 83, 400, 1.2, 0.3, 2.0, week(start, et0=6.0, rain=rain))
    assert capacity == approx(41.5)
    assert [d.kc for d in days] == [approx(1.05)] * 7
    assert [d.etc_mm for d in days] == [approx(6.3)] * 7
    assert [d.need_mm for d in days] == [approx(6.3), approx(6.3), 0, approx(6.3), approx(6.3), approx(6.3), approx(6.3)]
    assert [d.bucket_end_mm for d in days] == approx_list([20.75, 20.75, 24.45, 24.45, 24.45, 24.45, 24.45])
    assert days[0].litres == approx(2520)
    assert days[0].run_minutes == approx(68.04)
    assert days[2].litres == 0 and days[2].run_minutes == 0


def approx_list(values):
    return [pytest.approx(v, rel=0.005) for v in values]


# --- Case 3: tomato in development on loam, 20 mm of rain on day 3 ---
# Loam 175 mm/m x 0.7 m = 122.5 mm. The line is 61.25 mm and today starts there. Season day 50 on day 1, ET0 4 mm/day.
# Kc = 0.6 + (day - 30) x 0.01375: 0.875, 0.88875, 0.9025, 0.91625, 0.93, 0.94375, 0.9575.
# ETc = 4 x Kc: 3.5, 3.555, 3.61, 3.665, 3.72, 3.775, 3.83.
# Days 1 and 2: irrigate 3.5 and 3.555 mm, the bucket stays at 61.25.
# Day 3: 61.25 + 20 = 81.25; 81.25 - 3.61 = 77.64, above the line: no irrigation.
# Days 4-7: 77.64 - 3.665 = 73.975; - 3.72 = 70.255; - 3.775 = 66.48; - 3.83 = 62.65, all above 61.25: no irrigation.
# Day 1: 3.5 mm on 1000 m2 = 3500 L; emitters 1.5 x 0.4 = 0.6 m2 at 1 L/h: 3.5 x 0.6 x 60 = 126 minutes.
def test_tomato_in_development_with_rain():
    start = date(2026, 9, 1)
    planted = start - timedelta(days=49)
    capacity, days = plan(TOMATO, planted, 175, 1000, 1.5, 0.4, 1.0, week(start, et0=4.0, rain=(0, 0, 20, 0, 0, 0, 0)))
    assert capacity == approx(122.5)
    assert [d.kc for d in days] == approx_list([0.875, 0.88875, 0.9025, 0.91625, 0.93, 0.94375, 0.9575])
    assert [d.etc_mm for d in days] == approx_list([3.5, 3.555, 3.61, 3.665, 3.72, 3.775, 3.83])
    assert [d.need_mm for d in days] == [approx(3.5), approx(3.555), 0, 0, 0, 0, 0]
    assert [d.bucket_end_mm for d in days] == approx_list([61.25, 61.25, 77.64, 73.975, 70.255, 66.48, 62.65])
    assert days[0].litres == approx(3500)
    assert days[0].run_minutes == approx(126)


# --- Drip run time ---
def test_run_minutes_does_not_depend_on_the_plot_area():
    # 5.75 mm over 0.6 m2 (1.5 x 0.4) = 3.45 L per emitter; at 1 L/h that is 3.45 h = 207 minutes.
    assert run_minutes(5.75, 1.5, 0.4, 1.0) == approx(207)


def test_planting_after_the_forecast_start_cannot_be_planned():
    with pytest.raises(PlanError):
        plan(TOMATO, date(2026, 9, 5), 175, 100, 1.5, 0.4, 1.0, week(date(2026, 9, 1), 4.0))


def test_same_input_same_output():
    args = (TOMATO, date(2026, 3, 1), 175, 1000, 1.5, 0.4, 1.0, week(date(2026, 11, 16), 3.0))
    assert plan(*args) == plan(*args)
