---
name: irrigation-calc-reference
description: The formulas, units and agronomy choices behind the AgroPilot daily irrigation plan (Kc by growth stage, soil bucket, irrigate-at-half rule, drip run time), with three hand-calculated cases. Use whenever you write, change, review or test the irrigation engine or the plan numbers in services/planner-service, or explain a plan value, so you do not re-derive the domain from memory.
---

# Irrigation calculation reference

The plan is the engine's output and nothing else: no AI model computes or adjusts an irrigation number. The engine is `services/planner-service/engine.py` (pure functions) and the crop numbers come from the registry (`GET /v1/crops/{id}`). The two irrigation rules are in `crops.py`. The sources are in `services/planner-service/docs/research/fao56.md` (FAO-56, with chapter, table and equation numbers). Read that file before changing a number here. It also lists what could not be read, so check those against the printed book.

## Units

- Water is a depth in mm. 1 mm over 1 m² is 1 litre, so `litres = need_mm × area_m2`.
- ET0, rain, ETc, the bucket and the irrigation depth are all mm per day or mm, over the whole plot.
- Dates are `YYYY-MM-DD`. "Today" is the first date of the weather forecast, which is local to the plot.

## Formulas, in the order the engine uses them, for each forecast day

1. **Season day.** `day_number = (date - planting_date) + 1`. Planting day is day 1.
2. **Kc** (single crop coefficient, FAO-56 ch. 6, Eq. 66). Constant `kc_ini` up to `l_ini`. Then a straight line to `kc_mid` over `l_dev` days. Constant `kc_mid` over `l_mid` days. Then a straight line to `kc_end` over `l_late` days. After the season, hold `kc_end`.
   `kc = kc_prev + (day_number - days_before_stage) / stage_length × (kc_next - kc_prev)`
3. **Crop use.** `etc_mm = kc × et0_mm` (Eq. 56).
4. **Bucket size.** `capacity_mm = available_water_mm_per_m × root_depth_m` (Eq. 82). The root depth comes from the crop record in the registry.
5. **Water bucket, one day** (`water_day`). Rain and irrigation come early in the morning, then the crop uses `etc_mm`.
   - `level = min(capacity, level_start + rain_mm)`. Rain above the top is lost.
   - If `level - etc_mm < 0.5 × capacity`, irrigate: `need_mm = etc_mm` (replace what the crop uses) and `bucket_end_mm = level`.
   - Otherwise `need_mm = 0` and `bucket_end_mm = level - etc_mm`.
   - Exactly half is not below half, so no irrigation.
   - Today starts with `level_start = 0.5 × capacity`.
6. **Drip run time.** One emitter serves `row_spacing_m × emitter_spacing_m` m², so
   `run_minutes = need_mm × row_spacing_m × emitter_spacing_m / flow_lph × 60`. The plot area cancels out.

## Choices the book leaves open (change them in `crops.py` / `engine.py`, or for tomato and bell pepper in the registry seeds, and in this file)

- Today starts with the bucket **at the irrigation line, half of its capacity** (`START_LEVEL` in `crops.py`). The registry has no soil moisture.
- **Irrigate below half** of the bucket. FAO-56 says to use p per crop (tomato 0.40, pepper 0.30, Table 22). `p = 0.5` is only "commonly used". The task asked for half.
- **A watering day applies what the crop uses that day**, not a refill to the top. FAO-56's rule is `Ii = Dr` (refill the depletion). From half a bucket that is 30 to 60 mm per run, 7 to 36 hours of drip, which no grower would run in one go. Table 10 lists microirrigation under high-frequency application, so small daily amounts fit.
- Root depth is the small end of Table 22: tomato 0.7 m, pepper 0.5 m.
- Tomato `kc_end` 0.80, the middle of the printed range 0.70–0.90.
- Pepper `l_ini` 30 days (Table 11 prints "25/30"; 30 matches the printed total 125).
- After the end of the season the Kc stays at `kc_end`. The seed plots were planted months ago, so they are in this case.
- All rain counts. The book ignores rain under about 0.2 × ET0 and has no "effective rain" term.
- No Ks (stress) factor, no drip efficiency loss, no wetted-fraction correction of Kc.

## Three cases calculated by hand (they are tests in `tests/test_engine.py`)

**Case 1, Kc along the tomato season** (30 / 40 / 45 / 30 days, Kc 0.6 / 1.15 / 0.80). Day 50: `0.6 + (50-30)/40 × (1.15-0.6) = 0.875`. Day 100: `1.15`. Day 130: `1.15 + (130-115)/30 × (0.80-1.15) = 0.975`. Day 200: `0.80`.

**Case 2, pepper on sand, mid-season, 10 mm of rain on day 3.** Sand 83 mm/m × 0.5 m = 41.5 mm. The line is 20.75 mm and today starts there. Mid Kc 1.05, ET0 6, so ETc 6.3. Days 1 and 2: the day would end at 14.45, below the line, so irrigate **6.3 mm** and the day ends at 20.75. Day 3: rain lifts the level to 30.75, and 30.75 - 6.3 = 24.45 is above the line, so no irrigation. Days 4 to 7: 24.45 - 6.3 = 18.15 is below the line, so irrigate 6.3 mm again, ending at 24.45. For 400 m², rows 1.2 m, emitters 0.3 m apart, 2 L/h: 6.3 × 400 = **2520 L** and `6.3 × 1.2 × 0.3 / 2 × 60 = 68.04 min`. Check: 400 / 0.36 = 1111.1 emitters × 2 L/h = 2222.2 L/h, and 2520 / 2222.2 × 60 = 68.04.

**Case 3, tomato in development on loam, 20 mm rain on day 3.** Loam 175 × 0.7 = 122.5 mm, line 61.25 mm, today starts there. Day 50 on day 1, ET0 4: Kc `0.6 + (day-30) × 0.01375` = 0.875 … 0.9575, ETc = 3.5, 3.555, 3.61, 3.665, 3.72, 3.775, 3.83. Days 1 and 2: irrigate 3.5 and 3.555 mm (day 1: 3500 L on 1000 m², and `3.5 × 1.5 × 0.4 / 1 × 60 = 126 min`). Day 3: 61.25 + 20 = 81.25, minus 3.61 = 77.64, above the line, no irrigation. Days 4 to 7: 73.975, 70.255, 66.48 and **62.65 mm**, all above 61.25, so no irrigation.

Also the task's own example: a 70 mm bucket losing 7 mm a day ends days 1–5 at 63, 56, 49, 42, 35. Day 6 would end at 28, below 35, so it irrigates 7 mm and ends at 35.

## Tolerance

Calculated values must match these hand values within 0.5% (NFR-2.5). The API rounds to 1–3 decimals for display only.
