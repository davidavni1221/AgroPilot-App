"""The irrigation engine: pure calculation, no network, no HTTP, no clock.

Every number in a plan comes from here. Same input, same output. The formulas and their sources
are in the irrigation-calc-reference skill and docs/research/fao56.md.
"""
from dataclasses import dataclass
from datetime import date

from crops import CROPS, IRRIGATE_BELOW, START_LEVEL, CropParams


class PlanError(Exception):
    """The plan cannot be calculated honestly from this input."""


@dataclass(frozen=True)
class ForecastDay:
    date: date
    et0_mm: float
    rain_mm: float


@dataclass(frozen=True)
class DayPlan:
    date: date
    et0_mm: float
    rain_mm: float
    kc: float
    etc_mm: float  # what the crop uses today
    need_mm: float  # irrigation depth to apply (mm over the plot); 0 when none
    litres: float
    run_minutes: float
    bucket_end_mm: float


def kc_for_day(crop: CropParams, day_number: int) -> float:
    """Single crop coefficient on day `day_number` of the season (1 = planting day). FAO-56 ch. 6, Eq. 66."""
    if day_number < 1:
        raise PlanError("the crop is not planted yet")
    dev_start = crop.l_ini
    mid_start = crop.l_ini + crop.l_dev
    late_start = mid_start + crop.l_mid
    season_end = late_start + crop.l_late
    if day_number <= dev_start:
        return crop.kc_ini
    if day_number <= mid_start:
        return crop.kc_ini + (day_number - dev_start) / crop.l_dev * (crop.kc_mid - crop.kc_ini)
    if day_number <= late_start:
        return crop.kc_mid
    if day_number <= season_end:
        return crop.kc_mid + (day_number - late_start) / crop.l_late * (crop.kc_end - crop.kc_mid)
    # CHOICE: after the season length the crop is assumed to still stand, at Kc end. The seed plots are planted months ago.
    return crop.kc_end


def water_day(level_mm: float, capacity_mm: float, etc_mm: float, rain_mm: float) -> tuple[float, float]:
    """One day of the soil bucket. Returns (irrigation_mm, level_at_end_of_day).

    Rain and irrigation come early in the morning, then the crop uses etc_mm (FAO-56 Annex 8).
    Rain above the top of the bucket is lost (Eq. 88). If the day would end below the threshold,
    CHOICE: irrigate what the crop uses that day, so the bucket stays where it was. This is frequent,
    small irrigation (FAO-56 Table 10 lists microirrigation under high frequency). The book's own
    rule refills the whole depletion (Ii = Dr), which on drip means many hours in one run.
    """
    level = min(capacity_mm, level_mm + rain_mm)
    if level - etc_mm < IRRIGATE_BELOW * capacity_mm:
        return etc_mm, level
    return 0.0, level - etc_mm


def run_minutes(need_mm: float, row_spacing_m: float, emitter_spacing_m: float, emitter_flow_lph: float) -> float:
    """Minutes to apply need_mm with drip. One emitter serves row_spacing x emitter_spacing m2, so
    1 mm there is that many litres (1 mm over 1 m2 = 1 L) and the plot area cancels out."""
    litres_per_emitter = need_mm * row_spacing_m * emitter_spacing_m
    return litres_per_emitter / emitter_flow_lph * 60


def plan(
    crop_id: str,
    planting_date: date,
    soil_mm_per_m: float,
    area_m2: float,
    row_spacing_m: float,
    emitter_spacing_m: float,
    emitter_flow_lph: float,
    forecast: list[ForecastDay],
) -> tuple[float, list[DayPlan]]:
    """Returns (bucket capacity in mm, one DayPlan per forecast day, in order)."""
    crop = CROPS.get(crop_id)
    if crop is None:
        raise PlanError(f"crop {crop_id!r} has no irrigation parameters")
    capacity = soil_mm_per_m * crop.root_depth_m  # TAW, FAO-56 Eq. 82
    level = START_LEVEL * capacity  # CHOICE: today starts at the irrigation line (see crops.py)

    days = []
    for day in forecast:
        kc = kc_for_day(crop, (day.date - planting_date).days + 1)
        etc = kc * day.et0_mm  # Eq. 56
        need, level = water_day(level, capacity, etc, day.rain_mm)
        days.append(DayPlan(
            date=day.date, et0_mm=day.et0_mm, rain_mm=day.rain_mm, kc=kc, etc_mm=etc,
            need_mm=need, litres=need * area_m2,
            run_minutes=run_minutes(need, row_spacing_m, emitter_spacing_m, emitter_flow_lph),
            bucket_end_mm=level,
        ))
    return capacity, days
